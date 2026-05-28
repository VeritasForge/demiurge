from demi.plugin_stats.collector import parse_frontmatter, scan_inventory


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
