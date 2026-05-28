import json
import re
from demi.plugin_stats.models import Asset, GradedAsset
from demi.plugin_stats.reporter import build_snapshot, render_markdown, write_snapshot


def _g(id, type, grade, calls=0):
    a = Asset(id=id, type=type, source="global", aliases=frozenset({id}))
    return GradedAsset(asset=a, calls=calls, last_used=None, grade=grade, referenced_by=[])


def test_build_snapshot_totals_and_generated_at():      # [Happy]
    snap = build_snapshot([_g("x", "skill", "active", 3), _g("y", "skill", "dead")],
                          since="2025-11-28", until="2026-05-28", days=183)
    assert snap["totals"]["skill"]["active"] == 1 and snap["totals"]["skill"]["dead"] == 1
    assert snap["window"]["days"] == 183
    assert re.match(r"\d{4}-\d{2}-\d{2}T", snap["generated_at"])


def test_build_snapshot_empty():                        # [Boundary]
    snap = build_snapshot([], since="a", until="b", days=1)
    assert snap["assets"] == [] and snap["totals"] == {} and "generated_at" in snap


def test_render_markdown_sections():                    # [Happy]
    snap = build_snapshot([_g("x", "skill", "active", 3), _g("y", "agent", "dead")],
                          since="a", until="b", days=1)
    md = render_markdown(snap)
    assert "demi plugin-stats" in md and "dead" in md and "x" in md


def test_render_markdown_no_prev_trend_na():            # [Boundary]
    snap = build_snapshot([_g("x", "skill", "active", 1)], since="a", until="b", days=1)
    md = render_markdown(snap, prev=None)
    assert "N/A" in md or "이전 스냅샷 없음" in md


def test_write_snapshot_roundtrip(tmp_path):            # [Happy]
    snap = build_snapshot([_g("x", "skill", "active", 1)], since="a", until="b", days=1)
    out = tmp_path / "snap.json"
    write_snapshot(snap, out)
    assert json.loads(out.read_text())["assets"][0]["id"] == "x"


def test_write_snapshot_missing_parent(tmp_path):       # [Error]
    snap = build_snapshot([], since="a", until="b", days=1)
    out = tmp_path / "deep" / "nested" / "snap.json"
    write_snapshot(snap, out)
    assert out.exists()
