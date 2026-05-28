from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from .models import GradedAsset


def build_snapshot(graded: list[GradedAsset], since: str, until: str, days: int,
                   generated_at: str | None = None,
                   timeline: dict[str, dict[str, int]] | None = None) -> dict:
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
    snap = {"generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
            "window": {"since": since, "until": until, "days": days},
            "totals": {k: dict(v) for k, v in totals.items()},
            "assets": assets}
    if timeline is not None:
        snap["timeline"] = timeline
    return snap


def write_snapshot(snapshot: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")


CHART_TOP_N = 15
CHART_BAR_WIDTH = 30


def _ascii_bar(value: int, max_value: int, width: int = CHART_BAR_WIDTH) -> str:
    """`█` 채움 + `░` 빈칸 — 정규화된 막대."""
    if max_value <= 0:
        return "░" * width
    n = round(width * value / max_value)
    n = max(1, n) if value > 0 else 0  # 작은 값도 최소 1칸 보이게 (0은 그대로)
    n = min(width, n)
    return "█" * n + "░" * (width - n)


def _render_bar_chart(
    items: list[tuple[str, int]],
    title: str,
    top_n: int = CHART_TOP_N,
) -> list[str]:
    """(name, count) 튜플 리스트 → 마크다운 코드블록 안 ASCII bar chart."""
    items = [(n, v) for n, v in items if v > 0][:top_n]
    block = ["", f"### {title}"]
    if not items:
        block += ["```", "(데이터 없음)", "```"]
        return block
    max_v = max(v for _, v in items)
    name_w = max(len(n) for n, _ in items)
    block += ["```"]
    for name, v in items:
        block.append(f"  {name:<{name_w}}  {_ascii_bar(v, max_v)}  {v}")
    block += ["```"]
    return block


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

    # ── 사용 빈도 그래프 (Top N) — 통합 + skill/agent/command 별도 ──
    lines += ["", f"## 사용 빈도 그래프 (Top {CHART_TOP_N})"]
    assets = snapshot["assets"]
    SAC = ("skill", "agent", "command")  # 그래프 대상 유형

    combined = sorted(
        [(a["id"], a["calls"]) for a in assets if a["type"] in SAC],
        key=lambda x: -x[1],
    )
    lines += _render_bar_chart(combined, "통합 (skill + agent + command)")

    for typ in SAC:
        only = sorted(
            [(a["id"], a["calls"]) for a in assets if a["type"] == typ],
            key=lambda x: -x[1],
        )
        lines += _render_bar_chart(only, f"{typ}s")

    # ── 시간 추이 (월별 / 주별) ──
    timeline = snapshot.get("timeline") or {}
    monthly = timeline.get("monthly", {})
    weekly = timeline.get("weekly", {})
    if monthly or weekly:
        lines += ["", "## 시간 추이 (호출량)"]
        if monthly:
            items = sorted(monthly.items())  # ISO key — lexicographic = chronological
            lines += _render_bar_chart(items, "월별 (chronological)", top_n=24)
        if weekly:
            # 너무 길어지지 않게 최근 20주만
            items = sorted(weekly.items())[-20:]
            lines += _render_bar_chart(items, "주별 — 최근 20주", top_n=20)

    lines += ["", "## 활성 자산 (active)"]
    active = [a for a in assets if a["grade"] == "active"]
    if active:
        for a in sorted(active, key=lambda x: (x["type"], x["id"])):
            lines.append(f"- 🟢 `{a['id']}` ({a['type']}, {a['source']}, calls={a['calls']})")
    else:
        lines.append("- 없음")
    lines += ["", "## 정리 후보 (dead)"]
    dead = [a for a in assets if a["grade"] == "dead"]
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
