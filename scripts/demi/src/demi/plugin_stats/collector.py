from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .models import Asset

# frontmatter는 보통 < 1KB이므로 텍스트 앞부분만 검사하여 큰 파일 비용을 제한.
# 이 한계를 넘기는 frontmatter는 silently 무시되므로, 진단성을 위해 명명된 상수로 둔다.
_MAX_FRONTMATTER_SCAN = 4000

# \A anchored: 파일 시작에서만 (선택적 '# Title\n\n' 허용 후) frontmatter 매칭
_FRONTMATTER_RE = re.compile(
    r'\A(?:[ \t]*\n)*(?:#[^\n]*\n[ \t]*\n)?---\s*\n(.*?)\n---\s*(?:\n|$)',
    re.DOTALL,
)
_NAME_RE = re.compile(r'^name:\s*["\']?([^"\'\n]+)', re.M)
_INLINE_LIST_RE = re.compile(r'^(skills|tools|agents):\s*\[([^\]]*)\]', re.M)
_BLOCK_LIST_RE = re.compile(
    r'^(skills|tools|agents):\s*\n((?:[ \t]+-[ \t]+.+\n?)+)', re.M
)


def parse_frontmatter(path: Path) -> dict:
    """파일 시작 또는 첫 '# Title\\n\\n' 직후의 ---...--- 블록만 frontmatter로 인정.
    inline `[a, b]`와 block list `- a\\n- b` 모두 지원.
    본문의 horizontal-rule 사이 텍스트는 frontmatter로 잡지 않음."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    m = _FRONTMATTER_RE.match(text[:_MAX_FRONTMATTER_SCAN])
    if not m:
        return {}
    body = m.group(1)
    fm: dict = {}
    if (nm := _NAME_RE.search(body)):
        fm["name"] = nm.group(1).strip()
    for key, inner in _INLINE_LIST_RE.findall(body):
        fm[key] = [x.strip().strip('"\'') for x in inner.split(",") if x.strip()]
    for key, block in _BLOCK_LIST_RE.findall(body):
        items = [
            ln.split("-", 1)[1].strip().strip('"\'')
            for ln in block.splitlines()
            if "-" in ln
        ]
        fm.setdefault(key, items)
    return fm


def _refs_from_fm(fm: dict) -> frozenset[str]:
    out: set[str] = set()
    for key in ("skills", "tools", "agents"):
        out.update(fm.get(key, []))
    return frozenset(out)


def scan_inventory(home: Path, project: Path) -> list[Asset]:
    """전역 skills/agents + 로컬·전역 commands."""
    assets: list[Asset] = []
    for sk in (
        sorted((home / "skills").glob("*/SKILL.md"))
        if (home / "skills").is_dir()
        else []
    ):
        dname = sk.parent.name
        fm = parse_frontmatter(sk)
        name = fm.get("name", dname)
        assets.append(
            Asset(
                id=dname,
                type="skill",
                source="global",
                aliases=frozenset({dname, name}),
                refs=_refs_from_fm(fm),
            )
        )
    for ag in (
        sorted((home / "agents").glob("*.md"))
        if (home / "agents").is_dir()
        else []
    ):
        base = ag.stem
        fm = parse_frontmatter(ag)
        name = fm.get("name", base)
        assets.append(
            Asset(
                id=name,
                type="agent",
                source="global",
                aliases=frozenset({base, name}),
                refs=_refs_from_fm(fm),
            )
        )
    for cm in (
        sorted((project / "commands").glob("*.md"))
        if (project / "commands").is_dir()
        else []
    ):
        assets.append(
            Asset(
                id=cm.stem,
                type="command",
                source="local",
                aliases=frozenset({cm.stem}),
            )
        )
    have = {a.id for a in assets if a.type == "command"}
    for cm in (
        sorted((home / "commands").glob("*.md"))
        if (home / "commands").is_dir()
        else []
    ):
        if cm.stem in have:
            continue
        assets.append(
            Asset(
                id=cm.stem,
                type="command",
                source="global",
                aliases=frozenset({cm.stem}),
            )
        )
    return assets


BUILTIN_AGENTS = (
    "general-purpose",
    "Explore",
    "Plan",
    "claude",
    "claude-code-guide",
    "statusline-setup",
)


def scan_plugins(installed_plugins_json: Path) -> list[Asset]:
    try:
        data = json.loads(installed_plugins_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [
        Asset(
            id=key.split("@")[0],
            type="plugin",
            source="plugin:" + key.split("@")[0],
            aliases=frozenset({key.split("@")[0]}),
        )
        for key in (data.get("plugins") or {})
    ]


def scan_plugin_skills_agents(installed_plugins_json: Path) -> list[Asset]:
    """각 플러그인 installPath 아래 skills/SKILL.md와 agents/*.md 수집.
    id='<plugin>:<dname_or_name>', aliases에 bare 이름도 포함."""
    try:
        data = json.loads(installed_plugins_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    out: list[Asset] = []
    for key, entries in (data.get("plugins") or {}).items():
        pname = key.split("@")[0]
        for entry in entries:
            ip = entry.get("installPath")
            if not ip:
                continue
            root = Path(ip)
            if not root.is_dir():
                continue
            for sk in sorted(root.rglob("SKILL.md")):
                dname = sk.parent.name
                fm = parse_frontmatter(sk)
                nm = fm.get("name", dname)
                full = f"{pname}:{dname}"
                out.append(
                    Asset(
                        id=full,
                        type="skill",
                        source=f"plugin:{pname}",
                        aliases=frozenset({full, f"{pname}:{nm}", dname, nm}),
                        refs=_refs_from_fm(fm),
                    )
                )
            for ag in sorted(root.rglob("*.md")):
                # path 분리자에 의존하지 않게 부모 디렉토리 이름으로 판정
                if "agents" not in {p.name for p in ag.parents}:
                    continue
                base = ag.stem
                fm = parse_frontmatter(ag)
                nm = fm.get("name", base)
                full = f"{pname}:{nm}"
                out.append(
                    Asset(
                        id=full,
                        type="agent",
                        source=f"plugin:{pname}",
                        aliases=frozenset({full, f"{pname}:{base}", nm, base}),
                        refs=_refs_from_fm(fm),
                    )
                )
    return out


def _read_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def scan_mcp_servers(
    claude_json: Path | None = None,
    extra_mcp_jsons: list[Path] | None = None,
    installed_plugins_json: Path | None = None,
) -> list[Asset]:
    """MCP 서버 인벤토리를 다중 소스에서 수집:
       1) ~/.claude.json (top + projects)
       2) 추가 .mcp.json (예: repo 루트 demiurge/.mcp.json)
       3) 각 플러그인 installPath의 .mcp.json (재귀)
    alias에 원본 + 소문자형을 둘 다 등록해 collect_calls의 정규화(소문자) 키와 매칭."""
    names: set[str] = set()
    if claude_json:
        data = _read_json(claude_json)
        names.update((data.get("mcpServers") or {}).keys())
        for proj in (data.get("projects") or {}).values():
            names.update((proj.get("mcpServers") or {}).keys())
    for extra in extra_mcp_jsons or []:
        names.update((_read_json(extra).get("mcpServers") or {}).keys())
    if installed_plugins_json:
        pdata = _read_json(installed_plugins_json)
        for entries in (pdata.get("plugins") or {}).values():
            for entry in entries:
                ip = entry.get("installPath")
                if not ip:
                    continue
                root = Path(ip)
                if not root.is_dir():
                    continue
                for mp in root.rglob(".mcp.json"):
                    names.update((_read_json(mp).get("mcpServers") or {}).keys())
    return [
        Asset(
            id=n,
            type="mcp_server",
            source="mcp",
            aliases=frozenset({n, n.lower()}),
        )
        for n in sorted(names)
    ]


def scan_builtin_agents() -> list[Asset]:
    return [
        Asset(id=n, type="agent", source="builtin", aliases=frozenset({n}))
        for n in BUILTIN_AGENTS
    ]
