from demi.plugin_stats.models import Asset, CallStat, GradedAsset


def test_asset_defaults():                              # [Happy]
    a = Asset(id="deep-research", type="skill", source="global")
    assert a.aliases == frozenset() and a.refs == frozenset()


def test_asset_with_aliases_and_refs():                 # [Boundary]
    a = Asset(id="x", type="agent", source="global",
              aliases=frozenset({"x", "x-alias"}), refs=frozenset({"y"}))
    assert "x-alias" in a.aliases and "y" in a.refs


def test_callstat_optional_last_used():                 # [Boundary]
    c = CallStat(asset_id="x", count=0, last_used=None)
    assert c.count == 0 and c.last_used is None


def test_graded_asset():                                # [Happy]
    a = Asset(id="x", type="command", source="local")
    g = GradedAsset(asset=a, calls=3, last_used="2026-05-20", grade="active", referenced_by=[])
    assert g.grade == "active"
