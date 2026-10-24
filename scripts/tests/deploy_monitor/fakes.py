"""deploy-monitor 테스트 도우미: 가짜 명령(osascript/aws 등)을 만들고 실행한다."""

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL_BIN = (
    ROOT / "product/.claude/skills/demiurge/skills/deploy-monitor/bin"
)


def make_fake_bin(dirpath: Path, name: str, script: str) -> Path:
    """dirpath 안에 실행 권한이 있는 가짜 명령 name을 만든다."""
    path = Path(dirpath) / name
    path.write_text(script)
    path.chmod(0o755)
    return path


def env_with(dirpath: Path, **extra) -> dict:
    """PATH 맨 앞에 dirpath를 둔 환경 변수 dict를 돌려준다."""
    env = dict(os.environ)
    env["PATH"] = f"{dirpath}{os.pathsep}{env.get('PATH', '')}"
    env.update(extra)
    return env


def run(cmd: list, env: dict, stdin: str = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, env=env, input=stdin, capture_output=True, text=True, timeout=30
    )
