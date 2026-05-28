from __future__ import annotations
import json, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import typer
from . import collector, analyzer, reporter

plugin_stats_app = typer.Typer(help="플러그인/스킬/에이전트/MCP/커맨드 사용 통계")
DEFAULT_DAYS = 183


def _resolve_paths():
    """6-tuple. 외부 경로를 모두 반환하여 테스트가 한 곳에서 monkeypatch 가능.
    layout: scripts/demi/src/demi/plugin_stats/commands.py
    parents[3]=scripts/demi (proj root) → reports
    parents[5]=demiurge (repo root) → product/.claude, .mcp.json"""
    here = Path(__file__).resolve()
    home = Path.home() / ".claude"
    project = here.parents[5] / "product" / ".claude"
    projects_root = home / "projects"
    reports = here.parents[3] / "reports" / "plugin-stats"
    claude_json = Path.home() / ".claude.json"
    repo_root = here.parents[5]
    if not project.is_dir():
        sys.stderr.write(f"[demi:warn] project path not found: {project}\n")
    return home, project, projects_root, reports, claude_json, repo_root


def _gather(days: int):
    home, project, projects_root, _, claude_json, repo_root = _resolve_paths()
    plugins_json = home / "plugins" / "installed_plugins.json"
    demiurge_mcp = repo_root / ".mcp.json"
    extras = [demiurge_mcp] if demiurge_mcp.is_file() else None
    assets = (collector.scan_inventory(home, project)
              + collector.scan_builtin_agents()
              + collector.scan_plugins(plugins_json)
              + collector.scan_plugin_skills_agents(plugins_json)
              + collector.scan_mcp_servers(claude_json=claude_json if claude_json.is_file() else None,
                                           extra_mcp_jsons=extras,
                                           installed_plugins_json=plugins_json
                                                if plugins_json.is_file() else None))
    calls = collector.collect_calls(projects_root, since_days=days)
    return analyzer.grade_assets(assets, calls)


def _load_prev(snap_dir: Path, exclude: str) -> dict | None:
    if not snap_dir.is_dir():
        return None
    files = sorted(p for p in snap_dir.glob("*.json") if p.name != exclude)
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text())
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(f"[demi:warn] previous snapshot unreadable ({files[-1].name}): {e}\n")
        return None


@plugin_stats_app.command()
def report(since_days: int = DEFAULT_DAYS):
    """전체 집계 → 마크다운 + JSON 스냅샷 저장."""
    _, _, _, reports, _, _ = _resolve_paths()
    graded = _gather(since_days)
    until = datetime.now(timezone.utc); since = until - timedelta(days=since_days)
    snap = reporter.build_snapshot(graded, since.date().isoformat(),
                                   until.date().isoformat(), since_days)
    date = until.date().isoformat()
    reporter.write_snapshot(snap, reports / "snapshots" / f"{date}.json")
    prev = _load_prev(reports / "snapshots", exclude=f"{date}.json")
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "latest.md").write_text(reporter.render_markdown(snap, prev), encoding="utf-8")
    typer.echo(f"리포트 저장: {reports/'latest.md'}")


@plugin_stats_app.command()
def usage(since_days: int = DEFAULT_DAYS):
    for g in sorted(_gather(since_days), key=lambda g: g.calls, reverse=True)[:40]:
        typer.echo(f"{g.calls:>5}  {g.asset.type:<11} {g.asset.id}")


_VALID_GRADES = ("active", "live", "dead")


@plugin_stats_app.command()
def unused(
    grade: str = typer.Option("dead", "--grade", help="필터할 등급: active|live|dead"),
):
    """지정한 등급의 자산을 출력 (기본 dead — 정리 후보)."""
    if grade not in _VALID_GRADES:
        typer.echo(f"오류: --grade는 {'|'.join(_VALID_GRADES)} 중 하나여야 합니다. 입력: {grade!r}", err=True)
        raise typer.Exit(code=2)
    for g in _gather(DEFAULT_DAYS):
        if g.grade == grade:
            typer.echo(f"{g.grade:<6} {g.asset.type:<11} {g.asset.id}")


@plugin_stats_app.command()
def inventory():
    from collections import Counter
    c = Counter(g.asset.type for g in _gather(DEFAULT_DAYS))
    for typ, n in sorted(c.items()):
        typer.echo(f"{typ:<12} {n}")


@plugin_stats_app.command()
def diff(a: str, b: str):
    sa = json.loads(Path(a).read_text()); sb = json.loads(Path(b).read_text())
    da = {x["id"] for x in sa["assets"] if x["grade"] == "dead"}
    db = {x["id"] for x in sb["assets"] if x["grade"] == "dead"}
    typer.echo(f"신규 dead: {sorted(db - da)}")
    typer.echo(f"해소 dead: {sorted(da - db)}")
