# Demiurge AI Harness — Task Runner

set shell := ["bash", "-cu"]

# 기본은 사용자 홈. 임시 배포 검증은 `just deploy_target=/절대/경로 link`로 실행한다.
deploy_target := env_var("HOME")
export DEMIURGE_DEPLOY_TARGET := deploy_target

# 사용 가능한 명령 목록
default:
    @just --list

# 전역 심링크 생성/갱신
link:
    stow -v -R --no-folding -t "$DEMIURGE_DEPLOY_TARGET" product bin
    @echo "✅ Claude·Codex 지침과 공용 CLI 링크 생성/갱신 완료"

# 전역 심링크 해제
unlink:
    stow -v -D --no-folding -t "$DEMIURGE_DEPLOY_TARGET" product bin
    @echo "🔓 symlinks removed"

# 심링크 상태 확인
status:
    #!/usr/bin/env bash
    set -euo pipefail
    shopt -s nullglob
    echo "=== Skills (symlinked) ==="
    for d in "$DEMIURGE_DEPLOY_TARGET"/.claude/skills/*/; do
        name=$(basename "$d")
        # --no-folding: 디렉토리 자체가 심링크이거나, 내부에 심링크 파일이 있으면 OK
        if [ -L "${d%/}" ] || [ -L "${d}SKILL.md" ] || find "${d}" -maxdepth 2 -type l -print -quit 2>/dev/null | grep -q .; then
            echo "  ✅ $name"
        else
            echo "  ⚠️  $name (not from product)"
        fi
    done
    echo ""
    echo "=== Commands (symlinked) ==="
    for f in "$DEMIURGE_DEPLOY_TARGET"/.claude/commands/*; do
        [ -e "$f" ] || continue
        name=$(basename "$f")
        if [ -L "$f" ]; then
            echo "  ✅ $name"
        else
            echo "  ⚠️  $name (not from product)"
        fi
    done
    echo ""
    echo "=== CLAUDE.md ==="
    if [ -L "$DEMIURGE_DEPLOY_TARGET/.claude/CLAUDE.md" ]; then
        echo "  ✅ CLAUDE.md (symlinked)"
    else
        echo "  ⚠️  CLAUDE.md (not from product)"
    fi
    echo ""
    echo "=== Agents (symlinked) ==="
    if [ -d "$DEMIURGE_DEPLOY_TARGET/.claude/agents" ]; then
        for f in "$DEMIURGE_DEPLOY_TARGET"/.claude/agents/*; do
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
    echo ""
    echo "=== Bin (~/.local/bin, symlinked from product) ==="
    if [ -d "$DEMIURGE_DEPLOY_TARGET/.local/bin" ]; then
        found=false
        for f in "$DEMIURGE_DEPLOY_TARGET"/.local/bin/*; do
            [ -e "$f" ] || [ -L "$f" ] || continue
            name=$(basename "$f")
            if [ -L "$f" ] && [[ "$f" -ef "bin/.local/bin/$name" ]]; then
                echo "  ✅ $name"
                found=true
            fi
        done
        if [ "$found" = "false" ]; then
            echo "  ❌ no demiurge bin links found"
        fi
    else
        echo "  ❌ ~/.local/bin not found"
    fi
    echo ""
    bash scripts/check-codex-links.sh "$(pwd -P)" "$DEMIURGE_DEPLOY_TARGET"

# statusLine 설정을 settings.json에 비파괴적으로 병합 (statusLine 키만 갱신, 다른 키는 보존)
setup-statusline:
    #!/usr/bin/env bash
    set -euo pipefail
    SETTINGS=~/.claude/settings.json
    [ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
    TMP=$(mktemp)
    jq '.statusLine = {"type": "command", "command": "~/.claude/statusline.sh"}' "$SETTINGS" > "$TMP"
    mv "$TMP" "$SETTINGS"
    echo "✅ statusLine → ~/.claude/statusline.sh registered in $SETTINGS"

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

# 개발환경 사용 통계 리포트 생성 (demi plugin-stats report)
stats:
    cd scripts/demi && uv sync && uv run demi plugin-stats report

# 미사용(dead) 자산 목록 출력
stats-unused:
    cd scripts/demi && uv run demi plugin-stats unused --grade dead
