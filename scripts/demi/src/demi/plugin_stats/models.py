from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

AssetType = Literal["plugin", "skill", "agent", "mcp_server", "command"]
Grade = Literal["active", "live", "dead"]


@dataclass(frozen=True)
class Asset:
    id: str
    type: AssetType
    source: str
    aliases: frozenset[str] = field(default_factory=frozenset)
    refs: frozenset[str] = field(default_factory=frozenset)


@dataclass
class CallStat:
    asset_id: str
    count: int
    last_used: str | None


@dataclass
class GradedAsset:
    asset: Asset
    calls: int
    last_used: str | None
    grade: Grade
    referenced_by: list[str]
