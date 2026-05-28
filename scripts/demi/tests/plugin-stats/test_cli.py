from typer.testing import CliRunner

from demi.cli import app

runner = CliRunner()


def test_help_lists_plugin_stats():  # [Happy]
    r = runner.invoke(app, ["--help"])
    assert r.exit_code == 0 and "plugin-stats" in r.output


def test_plugin_stats_help_lists_commands():  # [Happy]
    r = runner.invoke(app, ["plugin-stats", "--help"])
    assert r.exit_code == 0
    for c in ("report", "usage", "unused", "inventory", "diff"):
        assert c in r.output


def test_inventory_runs_hermetic(monkeypatch, tmp_path):  # [Boundary] 6-tuple monkeypatch로 외부 의존 0
    import demi.plugin_stats.commands as cmd

    # (home, project, projects_root, reports, claude_json, repo_root)
    monkeypatch.setattr(
        cmd,
        "_resolve_paths",
        lambda: (
            tmp_path,
            tmp_path,
            tmp_path,
            tmp_path,
            tmp_path / "claude.json",
            tmp_path,
        ),
    )
    r = runner.invoke(app, ["plugin-stats", "inventory"])
    assert r.exit_code == 0


def test_unknown_command_errors():  # [Error]
    r = runner.invoke(app, ["plugin-stats", "nope"])
    assert r.exit_code != 0


def test_unused_invalid_grade_exits_nonzero(monkeypatch, tmp_path):  # [Error] grade typo
    """`--grade` 오타가 silent fail로 빈 출력을 내지 않고 exit≠0으로 명확히 실패해야 함."""
    import demi.plugin_stats.commands as cmd

    monkeypatch.setattr(
        cmd,
        "_resolve_paths",
        lambda: (
            tmp_path,
            tmp_path,
            tmp_path,
            tmp_path,
            tmp_path / "claude.json",
            tmp_path,
        ),
    )
    r = runner.invoke(app, ["plugin-stats", "unused", "--grade", "DEAD"])
    assert r.exit_code != 0
