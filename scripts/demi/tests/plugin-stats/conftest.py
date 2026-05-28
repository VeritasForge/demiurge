import json
import textwrap

import pytest


@pytest.fixture
def fake_home(tmp_path):
    """~/.claude 유사 구조 + 다양한 frontmatter 변종."""
    claude = tmp_path / ".claude"
    # 전역 skill — name=디렉토리명
    sk = claude / "skills" / "deep-research"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text("---\nname: deep-research\n---\n# deep research\n")
    # 전역 agent — '# Title' 후 frontmatter + block-list refs
    ag = claude / "agents"
    ag.mkdir(parents=True)
    (ag / "llm-architect.md").write_text(textwrap.dedent("""\
        # LLM Architect

        ---
        name: llm-architect
        skills:
          - deep-research
          - llm-gateway
        ---
        body
    """))
    # 본문에 horizontal-rule이 많은 skill (phantom frontmatter 회귀 테스트)
    hw = claude / "skills" / "humanize-writing"
    hw.mkdir(parents=True)
    (hw / "SKILL.md").write_text(textwrap.dedent("""\
        ---
        name: humanize-writing
        ---
        # body

        Section A

        ---

        Section B with looks-like-yaml:
        agents:
          - phantom-agent

        ---
        end
    """))
    # 전역 command
    (claude / "commands").mkdir(parents=True)
    (claude / "commands" / "save_obsi.md").write_text("---\ndescription: x\n---\n")
    # 플러그인 정보(Task 2.5)
    (claude / "plugins").mkdir(parents=True)
    (claude / "plugins" / "installed_plugins.json").write_text(
        json.dumps({"version": 2, "plugins": {}})
    )
    # 프로젝트 로컬 command
    proj = tmp_path / "product" / ".claude" / "commands"
    proj.mkdir(parents=True)
    (proj / "commit.md").write_text("---\ndescription: x\n---\n")
    return tmp_path
