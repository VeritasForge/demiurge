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


def test_render_markdown_includes_charts():             # [Happy] 4 chart 섹션 + bar 문자
    snap = build_snapshot([
        _g("alpha", "skill", "active", 10),
        _g("beta", "skill", "active", 5),
        _g("gamma", "agent", "active", 7),
        _g("delta", "command", "active", 3),
    ], since="a", until="b", days=1)
    md = render_markdown(snap)
    # 그래프 섹션 헤더
    assert "사용 빈도 그래프" in md
    assert "통합 (skill + agent + command)" in md
    assert "### skills" in md and "### agents" in md and "### commands" in md
    # 막대 문자 + 자산 id 포함
    assert "█" in md
    assert "alpha" in md and "gamma" in md and "delta" in md


def test_render_markdown_chart_handles_no_data():       # [Boundary] 빈 자산
    snap = build_snapshot([], since="a", until="b", days=1)
    md = render_markdown(snap)
    # 4개 차트 모두 "(데이터 없음)" 출력
    assert md.count("(데이터 없음)") == 4
    # bar는 없어야
    assert "█" not in md


def test_render_markdown_chart_top_n_limit():           # [Boundary] Top N 절단
    from demi.plugin_stats.reporter import CHART_TOP_N
    items = [_g(f"s{i}", "skill", "active", calls=100 - i) for i in range(CHART_TOP_N + 5)]
    snap = build_snapshot(items, since="a", until="b", days=1)
    md = render_markdown(snap)
    # "s0".."s(N-1)"은 포함, "s(N+4)"는 차트에 없음 (active 자산 섹션엔 있을 수 있음)
    # 차트 코드블록만 검사
    skills_section = md.split("### skills")[1].split("###")[0]
    assert "s0" in skills_section
    # N개 이후는 차트에서 잘림 — s(N), s(N+1) 등은 안 보임
    assert f"s{CHART_TOP_N + 4}" not in skills_section
