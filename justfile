# Demiurge AI Harness — Task Runner

set shell := ["bash", "-cu"]

# 사용 가능한 명령 목록
default:
    @just --list

# 전역 심링크 생성/갱신
link:
    stow -v -R --no-folding -t ~ product
    @echo "✅ product → ~/.claude linked"

# 전역 심링크 해제
unlink:
    stow -v -D --no-folding -t ~ product
    @echo "🔓 symlinks removed"

# 심링크 상태 확인
status:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "=== Skills (symlinked) ==="
    for d in ~/.claude/skills/*/; do
        name=$(basename "$d")
        if [ -L "${d%/}" ]; then
            echo "  ✅ $name"
        else
            echo "  ⚠️  $name (not from product)"
        fi
    done
    echo ""
    echo "=== Commands (symlinked) ==="
    for f in ~/.claude/commands/*; do
        [ -e "$f" ] || continue
        name=$(basename "$f")
        if [ -L "$f" ]; then
            echo "  ✅ $name"
        else
            echo "  ⚠️  $name (not from product)"
        fi
    done
    echo ""
    echo "=== Agents (symlinked) ==="
    if [ -d ~/.claude/agents ]; then
        for f in ~/.claude/agents/*; do
            [ -e "$f" ] || continue
            name=$(basename "$f")
            if [ -L "$f" ]; then
                echo "  ✅ $name"
            else
                echo "  ⚠️  $name (not from product)"
            fi
        done
    else
        echo "  ❌ agents/ not found"
    fi

# 새 스킬 생성 + 심링크
new-skill name:
    mkdir -p product/.claude/skills/{{name}}
    @printf '%s\n' '---' 'name: {{name}}' 'description: "TODO: 설명을 작성하세요"' '---' '' '# {{name}}' '' 'TODO: 스킬 내용을 작성하세요.' > product/.claude/skills/{{name}}/SKILL.md
    just link
    @echo "🆕 product/.claude/skills/{{name}}/SKILL.md created"

# 새 커맨드 생성 + 심링크
new-command name:
    @printf '%s\n' '---' 'description: "TODO: 설명을 작성하세요"' 'allowed-tools: Read, Grep, Glob, Bash' '---' '' 'TODO: 커맨드 내용을 작성하세요.' > product/.claude/commands/{{name}}.md
    just link
    @echo "🆕 product/.claude/commands/{{name}}.md created"
