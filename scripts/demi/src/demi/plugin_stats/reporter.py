from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from .models import GradedAsset


def build_snapshot(graded: list[GradedAsset], since: str, until: str, days: int,
                   generated_at: str | None = None) -> dict:
    totals: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "active": 0, "live": 0, "dead": 0})
    assets = []
    for g in graded:
        t = totals[g.asset.type]
        t["total"] += 1
        t[g.grade] += 1
        assets.append({"id": g.asset.id, "type": g.asset.type, "source": g.asset.source,
                       "calls": g.calls, "last_used": g.last_used, "grade": g.grade,
                       "referenced_by": g.referenced_by})
    return {"generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
            "window": {"since": since, "until": until, "days": days},
            "totals": {k: dict(v) for k, v in totals.items()},
            "assets": assets}


def write_snapshot(snapshot: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")


def render_markdown(snapshot: dict, prev: dict | None = None) -> str:
    w = snapshot["window"]
    lines = ["# demi plugin-stats 리포트", "",
             f"- 생성: {snapshot.get('generated_at','-')}",
             f"- 윈도우: {w['since']} ~ {w['until']} ({w['days']}일)", "",
             "## 요약 (유형별 등급)",
             "| 유형 | total | active | live | dead |",
             "|---|---:|---:|---:|---:|"]
    for typ, t in sorted(snapshot["totals"].items()):
        lines.append(f"| {typ} | {t['total']} | {t['active']} | {t['live']} | {t['dead']} |")
    lines += ["", "## 활성 자산 (active)"]
    active = [a for a in snapshot["assets"] if a["grade"] == "active"]
    if active:
        for a in sorted(active, key=lambda x: (x["type"], x["id"])):
            lines.append(f"- 🟢 `{a['id']}` ({a['type']}, {a['source']}, calls={a['calls']})")
    else:
        lines.append("- 없음")
    lines += ["", "## 정리 후보 (dead)"]
    dead = [a for a in snapshot["assets"] if a["grade"] == "dead"]
    if dead:
        for a in sorted(dead, key=lambda x: (x["type"], x["id"])):
            lines.append(f"- 🔴 `{a['id']}` ({a['type']}, {a['source']})")
    else:
        lines.append("- 없음")
    lines += ["", "## 추세 (이전 스냅샷 대비)"]
    if prev is None:
        lines.append("- N/A (이전 스냅샷 없음)")
    else:
        prev_dead = {a["id"] for a in prev["assets"] if a["grade"] == "dead"}
        newly = sorted({a["id"] for a in dead} - prev_dead)
        lines.append(f"- 신규 dead: {', '.join(newly) if newly else '없음'}")
    return "\n".join(lines) + "\n"
