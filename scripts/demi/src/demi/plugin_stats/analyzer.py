from __future__ import annotations

from .models import Asset, CallStat, GradedAsset


def _calls_for(asset: Asset, calls: dict[str, CallStat]) -> CallStat | None:
    for key in asset.aliases | {asset.id}:
        if key in calls:
            return calls[key]
    return None


def grade_assets(assets: list[Asset], calls: dict[str, CallStat]) -> list[GradedAsset]:
    ids = {a.id for a in assets}
    id_by_alias: dict[str, str] = {}
    for a in assets:
        for al in a.aliases | {a.id}:
            id_by_alias.setdefault(al, a.id)
    referenced_by: dict[str, list[str]] = {a.id: [] for a in assets}
    for src in assets:
        for tgt in src.refs:
            tgt_id = id_by_alias.get(tgt, tgt)
            if tgt_id == src.id or tgt_id not in ids:
                continue
            referenced_by[tgt_id].append(src.id)
    out: list[GradedAsset] = []
    for a in assets:
        cs = _calls_for(a, calls)
        count = cs.count if cs else 0
        last = cs.last_used if cs else None
        refby = sorted(set(referenced_by[a.id]))
        grade = "active" if count > 0 else ("live" if refby else "dead")
        out.append(GradedAsset(asset=a, calls=count, last_used=last,
                               grade=grade, referenced_by=refby))
    return out
