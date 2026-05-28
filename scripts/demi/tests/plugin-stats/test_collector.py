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
