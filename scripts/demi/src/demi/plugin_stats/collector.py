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
    id='<plugin>:<dname_or_name>', aliases에 bare 이름도 포함.

    같은 플러그인 안에 동일 이름의 skill/agent가 여러 위치에 있을 때
    (예: ouroboros가 `skills/qa/` 와 `.claude-plugin/skills/qa/` 둘 다 가짐)
    첫 발견을 우선하여 중복 등록을 방지한다."""
    try:
        data = json.loads(installed_plugins_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    out: list[Asset] = []
    seen_ids: set[str] = set()
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
                full = f"{pname}:{dname}"
                if full in seen_ids:
                    continue
                seen_ids.add(full)
                fm = parse_frontmatter(sk)
                nm = fm.get("name", dname)
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
                if full in seen_ids:
                    continue
                seen_ids.add(full)
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


# src/demi/plugin_stats/collector.py (이어서)
from datetime import datetime, timezone, timedelta
from .models import CallStat

def _normalize_mcp_key(name: str) -> str | None:
    """mcp__<server>__<tool> 또는 mcp__plugin_<plugin>_<server>__<tool> → 서버 토큰(소문자)."""
    parts = name.split("__")
    if len(parts) < 2:
        return None
    server = parts[1]
    if server.startswith("plugin_"):
        tokens = server.split("_")
        server = tokens[-1] if len(tokens) >= 3 else server[len("plugin_"):]
    return server.lower()

# 사용자 직접 slash command는 user message 안에 <command-name>/cmd</command-name> wrapper로 기록됨.
# Skill tool_use로 변환되지 않는 경우(/save_obsi 등)를 카운트하기 위해 추출.
_USER_CMD_RE = re.compile(r'<command-name>/?([\w:-]+)</command-name>')


def collect_calls(projects_root: Path, since_days: int = 183) -> dict[str, CallStat]:
    """tool_use Skill/Task/MCP + user-direct slash command(<command-name>) 합산.

    합산 정책 (옵션 B, v1.1):
      - tool_use는 `tool_use.id`로 dedup
      - user-direct wrapper는 (user message uuid, command) 튜플로 dedup
      - 같은 명령이 양쪽에서 보이면 *둘 다* 카운트 (의도된 이중 카운트, README에 명시)
        → save_obsi처럼 wrapper로만 호출되는 케이스의 false-dead를 막는 데 우선
    """
    since = datetime.now(timezone.utc) - timedelta(days=since_days)
    counts: dict[str, int] = {}
    last: dict[str, str] = {}
    seen_tool: set[str] = set()
    seen_user: set[tuple] = set()
    if not projects_root.is_dir():
        return {}
    for fp in projects_root.rglob("*.jsonl"):
        try:
            with fp.open(encoding="utf-8", errors="replace") as f:
                for line in f:
                    # 사전 필터 — tool_use 라인 또는 slash wrapper 라인만 파싱
                    if '"tool_use"' not in line and '<command-name>' not in line:
                        continue
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ts = d.get("timestamp")
                    if not ts:
                        continue
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    except ValueError:
                        continue
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if dt < since:
                        continue
                    msg = d.get("message") or {}
                    iso = dt.date().isoformat()

                    def _bump(key: str) -> None:
                        if not key:
                            return
                        counts[key] = counts.get(key, 0) + 1
                        if key not in last or iso > last[key]:
                            last[key] = iso

                    # (A) tool_use 분기 (기존)
                    content = msg.get("content")
                    if isinstance(content, list):
                        for it in content:
                            if not isinstance(it, dict) or it.get("type") != "tool_use":
                                continue
                            tid = it.get("id")
                            if tid in seen_tool:
                                continue
                            seen_tool.add(tid)
                            name = it.get("name")
                            inp = it.get("input") or {}
                            if name == "Skill":
                                _bump(inp.get("skill"))
                            elif name in ("Task", "Agent"):
                                _bump(inp.get("subagent_type") or inp.get("name") or "general-purpose")
                            elif isinstance(name, str) and name.startswith("mcp__"):
                                _bump(_normalize_mcp_key(name))

                    # (B) user-direct slash wrapper 분기 — role=user 메시지에서 <command-name>
                    if msg.get("role") == "user":
                        texts: list[str] = []
                        if isinstance(content, str):
                            texts.append(content)
                        elif isinstance(content, list):
                            for it in content:
                                if isinstance(it, dict) and it.get("type") == "text":
                                    texts.append(it.get("text", "") or "")
                                elif isinstance(it, str):
                                    texts.append(it)
                        uuid = d.get("uuid")
                        for txt in texts:
                            for m in _USER_CMD_RE.finditer(txt):
                                cmd = m.group(1)
                                dedup_key = (uuid, cmd)
                                if dedup_key in seen_user:
                                    continue
                                seen_user.add(dedup_key)
                                _bump(cmd)
        except OSError:
            continue
    return {k: CallStat(asset_id=k, count=v, last_used=last.get(k)) for k, v in counts.items()}
