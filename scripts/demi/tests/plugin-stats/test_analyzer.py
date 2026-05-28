from demi.plugin_stats.models import Asset, CallStat
from demi.plugin_stats.analyzer import grade_assets


def _a(id, refs=(), aliases=None):
    return Asset(id=id, type="skill", source="global",
                 aliases=frozenset(aliases or {id}), refs=frozenset(refs))


def test_active_when_called():                          # [Happy]
    g = {ga.asset.id: ga for ga in grade_assets([_a("x")],
            {"x": CallStat("x", 5, "2026-05-20")})}
    assert g["x"].grade == "active" and g["x"].calls == 5


def test_live_when_referenced_but_not_called():         # [Happy] 핵심
    g = {ga.asset.id: ga for ga in grade_assets([_a("orch", refs=["arch"]), _a("arch")], {})}
    assert g["arch"].grade == "live" and "orch" in g["arch"].referenced_by


def test_dead_when_isolated():                          # [Happy]
    g = {ga.asset.id: ga for ga in grade_assets([_a("lonely")], {})}
    assert g["lonely"].grade == "dead"


def test_alias_matches_call_key():                      # [Boundary]
    a = Asset(id="hw", type="skill", source="global",
              aliases=frozenset({"hw", "humanize-writing"}), refs=frozenset())
    g = {ga.asset.id: ga for ga in grade_assets([a],
            {"humanize-writing": CallStat("humanize-writing", 2, "2026-05-01")})}
    assert g["hw"].grade == "active"


def test_ref_via_alias():                               # [Boundary] alias로 참조
    src = Asset(id="src", type="agent", source="global",
                aliases=frozenset({"src"}), refs=frozenset({"hw"}))
    tgt = Asset(id="humanize-writing", type="skill", source="global",
                aliases=frozenset({"hw", "humanize-writing"}), refs=frozenset())
    g = {ga.asset.id: ga for ga in grade_assets([src, tgt], {})}
    assert g["humanize-writing"].grade == "live"


def test_self_reference_not_live():                     # [Boundary]
    g = {ga.asset.id: ga for ga in grade_assets([_a("self", refs=["self"])], {})}
    assert g["self"].grade == "dead"


def test_ref_to_unknown_id_ignored():                   # [Boundary]
    g = {ga.asset.id: ga for ga in grade_assets([_a("a", refs=["ghost"])], {})}
    assert g["a"].grade == "dead"


def test_empty_inventory():                             # [Error]
    assert grade_assets([], {}) == []
