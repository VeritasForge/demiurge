import json

from demi.plugin_stats.collector import (
    BUILTIN_AGENTS,
    parse_frontmatter,
    scan_builtin_agents,
    scan_inventory,
    scan_mcp_servers,
    scan_plugin_skills_agents,
    scan_plugins,
)


def test_parse_frontmatter_inline_list(tmp_path):       # [Happy]
    f = tmp_path / "SKILL.md"
    f.write_text("---\nname: foo\nskills: [a, b]\n---\nbody")
    fm = parse_frontmatter(f)
    assert fm["name"] == "foo" and fm["skills"] == ["a", "b"]


def test_parse_frontmatter_block_list(tmp_path):        # [Boundary]
    f = tmp_path / "agent.md"
    f.write_text("# Title\n\n---\nname: foo\nskills:\n  - a\n  - b\n---\nbody")
    fm = parse_frontmatter(f)
    assert fm["name"] == "foo" and fm["skills"] == ["a", "b"]


def test_parse_frontmatter_non_leading_delim(tmp_path):  # [Boundary]
    f = tmp_path / "agent.md"
    f.write_text("# Hello\n\n---\nname: bar\n---\n")
    assert parse_frontmatter(f)["name"] == "bar"


def test_parse_frontmatter_rejects_body_yaml_between_hr(tmp_path):  # [Boundary] phantom 거부
    f = tmp_path / "page.md"
    f.write_text("# Title\n\nbody intro\n\n---\nagents:\n  - phantom\n---\nrest")
    fm = parse_frontmatter(f)
    # frontmatter는 파일 시작 또는 # Title 직후만 인정 → 'agents'는 잡히지 않아야 함
    assert fm.get("agents") is None or fm.get("agents") == []


def test_parse_frontmatter_missing(tmp_path):           # [Boundary]
    f = tmp_path / "x.md"
    f.write_text("no fm here")
    assert parse_frontmatter(f) == {}


def test_parse_frontmatter_unreadable(tmp_path):        # [Error]
    assert parse_frontmatter(tmp_path / "nope.md") == {}


def test_scan_inventory_collects_types(fake_home):      # [Happy]
    assets = scan_inventory(
        home=fake_home / ".claude",
        project=fake_home / "product" / ".claude",
    )
    ids = {a.id for a in assets}
    types = {a.type for a in assets}
    assert {"skill", "agent", "command"} <= types
    assert {"deep-research", "llm-architect", "commit", "save_obsi", "humanize-writing"} <= ids


def test_scan_inventory_block_refs(fake_home):          # [Boundary] block-list refs 수집
    a = {
        x.id: x
        for x in scan_inventory(
            home=fake_home / ".claude",
            project=fake_home / "product" / ".claude",
        )
    }
    assert "deep-research" in a["llm-architect"].refs
    assert "llm-gateway" in a["llm-architect"].refs
    # phantom 거부: humanize-writing은 본문의 'agents: - phantom-agent'를 포함하지 않아야 함
    assert "phantom-agent" not in a["humanize-writing"].refs


def test_scan_inventory_empty(tmp_path):                # [Error]
    assert scan_inventory(home=tmp_path / "nope", project=tmp_path / "none") == []


def test_scan_plugins(tmp_path):                        # [Happy]
    pj = tmp_path / "installed_plugins.json"
    pj.write_text(json.dumps({"plugins": {
        "superpowers@official": [{"installPath": str(tmp_path / "sp")}]
    }}))
    (tmp_path / "sp").mkdir()
    assert any(a.id == "superpowers" and a.type == "plugin" for a in scan_plugins(pj))


def test_scan_plugins_missing(tmp_path):                # [Error]
    assert scan_plugins(tmp_path / "nope.json") == []


def test_scan_plugin_skills_agents(tmp_path):           # [Happy]
    pr = tmp_path / "sp" / "1.0"
    (pr / "skills" / "writing-plans").mkdir(parents=True)
    (pr / "skills" / "writing-plans" / "SKILL.md").write_text("---\nname: writing-plans\n---\n")
    (pr / "agents").mkdir(parents=True)
    (pr / "agents" / "code-reviewer.md").write_text("---\nname: code-reviewer\n---\n")
    pj = tmp_path / "installed_plugins.json"
    pj.write_text(json.dumps({"plugins": {"superpowers@official": [{"installPath": str(pr)}]}}))
    out = scan_plugin_skills_agents(pj)
    ids = {a.id for a in out}
    assert "superpowers:writing-plans" in ids and "superpowers:code-reviewer" in ids
    assert any("writing-plans" in a.aliases for a in out)


def test_scan_plugin_skills_agents_dedup_same_name(tmp_path):  # [Boundary] 같은 plugin 내 중복 경로
    """ouroboros처럼 한 installPath 안에 동일 dname의 SKILL.md가 여러 경로(.claude-plugin/skills/qa, skills/qa)에 있을 때 1개만 등록."""
    pr = tmp_path / "ouro" / "0.39.2"
    (pr / "skills" / "qa").mkdir(parents=True)
    (pr / "skills" / "qa" / "SKILL.md").write_text("---\nname: qa\n---\n")
    (pr / ".claude-plugin" / "skills" / "qa").mkdir(parents=True)
    (pr / ".claude-plugin" / "skills" / "qa" / "SKILL.md").write_text("---\nname: qa\n---\n")
    pj = tmp_path / "installed_plugins.json"
    pj.write_text(json.dumps({"plugins": {"ouroboros@ouroboros": [{"installPath": str(pr)}]}}))
    out = scan_plugin_skills_agents(pj)
    qa_entries = [a for a in out if a.id == "ouroboros:qa"]
    assert len(qa_entries) == 1, f"expected 1, got {len(qa_entries)}: {qa_entries}"


def test_scan_mcp_servers_top_and_projects(tmp_path):   # [Happy] top + projects
    cj = tmp_path / ".claude.json"
    cj.write_text(json.dumps({
        "mcpServers": {"mcp-atlassian": {}},
        "projects": {"/x": {"mcpServers": {"playwright": {}}}},
    }))
    ids = {a.id for a in scan_mcp_servers(claude_json=cj)}
    assert {"mcp-atlassian", "playwright"} <= ids


def test_scan_mcp_servers_extra_and_plugin(tmp_path):   # [Boundary] 다중 소스 통합
    extra = tmp_path / ".mcp.json"
    extra.write_text(json.dumps({"mcpServers": {"local-extra": {}}}))
    pr = tmp_path / "plugin" / "1.0"
    (pr).mkdir(parents=True)
    (pr / ".mcp.json").write_text(json.dumps({"mcpServers": {"context7": {}}}))
    pj = tmp_path / "installed_plugins.json"
    pj.write_text(json.dumps({"plugins": {"context7@official": [{"installPath": str(pr)}]}}))
    out = scan_mcp_servers(claude_json=None, extra_mcp_jsons=[extra],
                           installed_plugins_json=pj)
    ids = {a.id for a in out}
    assert {"local-extra", "context7"} <= ids
    # alias에 .lower()도 포함되어 호출 키(소문자)와 매칭 가능
    assert any("context7" in a.aliases for a in out)


def test_scan_mcp_servers_all_missing():                # [Error]
    assert scan_mcp_servers(claude_json=None) == []


def test_builtin_agents_present():                      # [Boundary]
    assert "general-purpose" in BUILTIN_AGENTS
    assert any(a.id == "general-purpose" for a in scan_builtin_agents())


from datetime import datetime, timezone, timedelta
from demi.plugin_stats.collector import collect_calls

def _line(ts, name, inp, tid="t1"):
    return json.dumps({"timestamp": ts, "message": {"content": [
        {"type": "tool_use", "id": tid, "name": name, "input": inp}]}})

def test_collect_calls_counts(tmp_path):                # [Happy]
    log = tmp_path / "a.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    log.write_text("\n".join([
        _line(now, "Skill", {"skill": "deep-research"}, "1"),
        _line(now, "Skill", {"skill": "deep-research"}, "2"),
        _line(now, "Task", {"subagent_type": "llm-architect"}, "3"),
    ]))
    stats = collect_calls(tmp_path, since_days=183)
    assert stats["deep-research"].count == 2 and stats["llm-architect"].count == 1

def test_collect_calls_mcp_server_key(tmp_path):        # [Boundary]
    log = tmp_path / "m.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    log.write_text("\n".join([
        _line(now, "mcp__context7__query_docs", {}, "m1"),
        _line(now, "mcp__plugin_Notion_notion__find", {}, "m2"),
    ]))
    stats = collect_calls(tmp_path, since_days=183)
    assert "context7" in stats and "notion" in stats

def test_collect_calls_agent_name_fallback(tmp_path):   # [Boundary]
    log = tmp_path / "a.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    log.write_text(_line(now, "Agent", {"name": "specialist", "prompt": "x"}, "n1"))
    assert "specialist" in collect_calls(tmp_path, since_days=183)

def test_collect_calls_window_excludes_old(tmp_path):   # [Boundary]
    log = tmp_path / "o.jsonl"
    old = (datetime.now(timezone.utc) - timedelta(days=400)).isoformat()
    log.write_text(_line(old, "Skill", {"skill": "deep-research"}, "o1"))
    assert "deep-research" not in collect_calls(tmp_path, since_days=183)

def test_collect_calls_dedup(tmp_path):                 # [Boundary]
    log = tmp_path / "d.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    line = _line(now, "Skill", {"skill": "deep-research"}, "dup")
    log.write_text(line + "\n" + line)
    assert collect_calls(tmp_path, since_days=183)["deep-research"].count == 1

def test_collect_calls_broken_line(tmp_path):           # [Error]
    log = tmp_path / "b.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    log.write_text("{broken\n" + _line(now, "Skill", {"skill": "deep-research"}, "g1"))
    assert collect_calls(tmp_path, since_days=183)["deep-research"].count == 1

def test_collect_calls_no_logs(tmp_path):               # [Error]
    assert collect_calls(tmp_path / "nope", since_days=183) == {}


def _user_line(ts, text, uuid="u1"):
    return json.dumps({"timestamp": ts, "uuid": uuid,
                       "message": {"role": "user", "content": text}})


def test_collect_calls_user_slash_wrapper(tmp_path):    # [Boundary] /save_obsi 같은 user-direct
    log = tmp_path / "u.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    log.write_text("\n".join([
        _user_line(now, "<command-message>save_obsi</command-message>\n<command-name>/save_obsi</command-name>", "u1"),
        _user_line(now, "<command-name>/save_obsi</command-name>", "u2"),
        _user_line(now, "<command-name>/clear</command-name>", "u3"),
    ]))
    stats = collect_calls(tmp_path, since_days=183)
    assert stats["save_obsi"].count == 2
    assert stats["clear"].count == 1


def test_collect_calls_user_wrapper_dedup(tmp_path):    # [Boundary] 같은 uuid는 한 번만
    log = tmp_path / "u.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    line = _user_line(now, "<command-name>/save_obsi</command-name>", "dup-uuid")
    log.write_text(line + "\n" + line)  # 동일 라인 두 번 (예: 재플레이)
    assert collect_calls(tmp_path, since_days=183)["save_obsi"].count == 1


def test_collect_calls_tool_use_and_wrapper_both_count(tmp_path):  # [Boundary] 합산 (옵션 B)
    log = tmp_path / "x.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    log.write_text("\n".join([
        _user_line(now, "<command-name>/rl-verify</command-name>", "u1"),
        _line(now, "Skill", {"skill": "rl-verify"}, "t1"),
    ]))
    # wrapper 1 + tool_use 1 → 합산 2 (의도된 이중 카운트, README 명시)
    assert collect_calls(tmp_path, since_days=183)["rl-verify"].count == 2


def test_collect_calls_wrapper_ignored_when_role_not_user(tmp_path):  # [Error] role=assistant면 무시
    log = tmp_path / "a.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    log.write_text(json.dumps({"timestamp": now, "uuid": "u1",
                               "message": {"role": "assistant",
                                           "content": "<command-name>/save_obsi</command-name>"}}))
    assert "save_obsi" not in collect_calls(tmp_path, since_days=183)


# ──────────────── collect_timeline ────────────────
from demi.plugin_stats.collector import collect_timeline


def test_collect_timeline_buckets(tmp_path):            # [Happy]
    """tool_use + wrapper 호출이 같은 주/월 bucket에 합산."""
    log = tmp_path / "t.jsonl"
    now = datetime.now(timezone.utc)
    iso = now.isoformat()
    log.write_text("\n".join([
        _line(iso, "Skill", {"skill": "a"}, "t1"),
        _line(iso, "Skill", {"skill": "b"}, "t2"),
        _user_line(iso, "<command-name>/save_obsi</command-name>", "u1"),
    ]))
    tl = collect_timeline(tmp_path, since_days=183)
    iso_y, iso_w, _ = now.isocalendar()
    wk = f"{iso_y:04d}-W{iso_w:02d}"
    mn = f"{now.year:04d}-{now.month:02d}"
    assert tl["weekly"][wk] == 3
    assert tl["monthly"][mn] == 3


def test_collect_timeline_empty(tmp_path):              # [Boundary]
    log = tmp_path / "e.jsonl"
    log.write_text("")
    tl = collect_timeline(tmp_path, since_days=183)
    assert tl == {"weekly": {}, "monthly": {}}


def test_collect_timeline_window_excludes_old(tmp_path):  # [Boundary]
    log = tmp_path / "o.jsonl"
    old = (datetime.now(timezone.utc) - timedelta(days=400)).isoformat()
    log.write_text(_line(old, "Skill", {"skill": "x"}, "o1"))
    tl = collect_timeline(tmp_path, since_days=183)
    assert tl == {"weekly": {}, "monthly": {}}


def test_collect_timeline_no_dir(tmp_path):             # [Error]
    tl = collect_timeline(tmp_path / "nope", since_days=183)
    assert tl == {"weekly": {}, "monthly": {}}


def test_collect_calls_sets_asset_timeline(tmp_path):   # [Happy] 자산별 weekly/monthly bucket
    log = tmp_path / "a.jsonl"
    now = datetime.now(timezone.utc)
    iso = now.isoformat()
    log.write_text("\n".join([
        _line(iso, "Skill", {"skill": "foo"}, "t1"),
        _line(iso, "Skill", {"skill": "foo"}, "t2"),
        _line(iso, "Skill", {"skill": "bar"}, "t3"),
    ]))
    stats = collect_calls(tmp_path, since_days=183)
    iso_y, iso_w, _ = now.isocalendar()
    wk = f"{iso_y:04d}-W{iso_w:02d}"
    mn = f"{now.year:04d}-{now.month:02d}"
    assert stats["foo"].weekly[wk] == 2
    assert stats["foo"].monthly[mn] == 2
    assert stats["bar"].weekly[wk] == 1
    assert stats["bar"].monthly[mn] == 1
