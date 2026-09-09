"""실제 just/Stow의 배포 계약 검증. 사용자 홈과 설정은 변경하지 않는다."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CODEX_FILES = (
    ".codex/AGENTS.md",
    ".codex/demiurge/communication.md",
    ".codex/demiurge/engineering.md",
)


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="demiurge-deployment-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base / "repo with spaces"
        self.target = self.base / "target with spaces"
        self.repo.mkdir()
        self.target.mkdir()
        for name in ("product", "bin", "scripts"):
            shutil.copytree(ROOT / name, self.repo / name, ignore=shutil.ignore_patterns(
                ".venv", "__pycache__", "reports", ".pytest_cache"))
        shutil.copy2(ROOT / "justfile", self.repo / "justfile")

    def run_just(self, recipe, success=True):
        result = subprocess.run(
            ["just", f"deploy_target={self.target}", recipe],
            cwd=self.repo, text=True, capture_output=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_joint_install_and_reinstall_preserve_unmanaged_files(self):
        for relative in (".codex/config.toml", ".codex/auth.json", ".codex/plugins/cache/keep"):
            file = self.target / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("기존 사용자 파일", encoding="utf-8")
        for _ in range(2):
            self.run_just("link")
            for relative in CODEX_FILES + (".claude/CLAUDE.md",):
                link = self.target / relative
                self.assertTrue(link.is_symlink(), relative)
                self.assertEqual(link.resolve(), self.repo / "product" / relative)
            self.assertTrue((self.target / ".local/bin/git-cleanup-worktrees").is_symlink())
            self.run_just("status")
        self.assertFalse((self.target / ".codex").is_symlink())
        for relative in (".codex/config.toml", ".codex/auth.json", ".codex/plugins/cache/keep"):
            self.assertEqual((self.target / relative).read_text(), "기존 사용자 파일")

    def test_codex_conflict_does_not_partially_deploy_claude_or_bin(self):
        self.run_just("link")
        claude = self.target / ".claude/CLAUDE.md"
        old_link = claude.readlink()
        # 충돌 전 이미 있던 링크도 그대로 보존해야 한다.
        (self.target / ".codex/AGENTS.md").unlink()
        (self.target / ".codex/AGENTS.md").write_text("기존 지침")
        (self.repo / "bin/.local/bin/new-tool").write_text("새 자산")
        self.assertIn("conflict", self.run_just("link", success=False).lower())
        self.assertEqual((self.target / ".codex/AGENTS.md").read_text(), "기존 지침")
        self.assertEqual(claude.readlink(), old_link)
        self.assertFalse((self.target / ".local/bin/new-tool").exists())

    def test_bin_conflict_does_not_partially_deploy_product(self):
        conflict = self.target / ".local/bin/git-cleanup-worktrees"
        conflict.parent.mkdir(parents=True)
        conflict.write_text("사용자 도구")
        self.assertIn("conflict", self.run_just("link", success=False).lower())
        self.assertFalse((self.target / ".claude/CLAUDE.md").exists())
        self.assertFalse((self.target / ".codex/AGENTS.md").exists())
        self.assertEqual(conflict.read_text(), "사용자 도구")

    def test_status_rejects_missing_broken_wrong_and_regular_files(self):
        self.run_just("status", success=False)
        self.run_just("link")
        self.run_just("status")
        for relative in CODEX_FILES:
            link = self.target / relative
            expected = self.repo / "product" / relative
            for kind in ("missing", "broken", "wrong", "regular"):
                with self.subTest(relative=relative, kind=kind):
                    link.unlink()
                    if kind == "broken":
                        link.symlink_to(self.base / "absent")
                    elif kind == "wrong":
                        # 내용이 같은 다른 파일도 올바른 배포로 판정하면 안 된다.
                        wrong = self.base / "wrong-source"
                        shutil.copy2(expected, wrong)
                        link.symlink_to(wrong)
                    elif kind == "regular":
                        shutil.copy2(expected, link)
                    self.run_just("status", success=False)
                    if link.exists() or link.is_symlink():
                        link.unlink()
                    link.symlink_to(expected)

    def test_override_warns_without_claiming_link_failure(self):
        self.run_just("link")
        override = self.target / ".codex/AGENTS.override.md"
        override.write_text("임시 우선 지침")
        self.assertIn("AGENTS.override.md", self.run_just("status"))
        override.write_text("")
        self.assertNotIn("AGENTS.override.md", self.run_just("status"))

    def test_unlink_preserves_sources_and_unmanaged_files(self):
        self.run_just("link")
        keep = self.target / ".codex/local-note.md"
        keep.write_text("보존")
        self.run_just("unlink")
        for relative in CODEX_FILES + (".claude/CLAUDE.md",):
            self.assertFalse((self.target / relative).is_symlink())
            self.assertFalse((self.target / relative).exists())
            self.assertTrue((self.repo / "product" / relative).is_file())
        self.assertFalse((self.target / ".local/bin/git-cleanup-worktrees").exists())
        self.assertEqual(keep.read_text(), "보존")
        self.run_just("status", success=False)


if __name__ == "__main__":
    unittest.main()
