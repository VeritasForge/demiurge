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
    stow -v -R --no-folding --ignore='\.DS_Store$' -t "$DEMIURGE_DEPLOY_TARGET" product bin
    @echo "✅ Claude·Codex 지침과 공용 CLI 링크 생성/갱신 완료"

# 전역 심링크 해제
unlink:
    stow -v -D --no-folding --ignore='\.DS_Store$' -t "$DEMIURGE_DEPLOY_TARGET" product bin
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

# 최신 버전을 받아 로컬에 반영 (pull → link → 깨진 심링크·빈 폴더 정리 → 훅 등록 → 검증)
update:
    #!/usr/bin/env bash
    set -euo pipefail
    # pull.rebase=true 환경에서는 커밋 안 된 변경이 있으면 pull이 막히므로 rebase를 끈다
    git pull --ff-only
    just link
    # pull이 소스를 먼저 지운 파일은 stow가 추적하지 못하므로, 이 레포를 가리키던 깨진 심링크만 직접 지운다
    repo=$(pwd -P)
    for d in .claude .codex .local/bin; do
        [ -d "$DEMIURGE_DEPLOY_TARGET/$d" ] || continue
        find "$DEMIURGE_DEPLOY_TARGET/$d" -type l ! -exec test -e {} \; -print
    done | while IFS= read -r link; do
        target=$(readlink "$link")
        case "$target" in
            /*) p=$target ;;
            *) p="$(dirname "$link")/$target" ;;
        esac
        # 대상이 사라졌으니, 남아 있는 가장 가까운 상위 폴더가 레포 안인지로 판정한다
        while [ ! -d "$p" ]; do p=$(dirname "$p"); done
        case "$(cd "$p" && pwd -P)/" in
            "$repo"/*) rm "$link"; echo "🧹 깨진 심링크 삭제: $link" ;;
        esac
    done
    if [ -d "$DEMIURGE_DEPLOY_TARGET/.claude/skills/demiurge" ]; then
        find "$DEMIURGE_DEPLOY_TARGET/.claude/skills/demiurge" -depth -type d -empty -delete
    fi
    just setup-hooks
    deployed=$(ls "$DEMIURGE_DEPLOY_TARGET/.claude/skills/demiurge/skills" | wc -l | tr -d ' ')
    source=$(ls product/.claude/skills/demiurge/skills | wc -l | tr -d ' ')
    if [ "$deployed" != "$source" ]; then
        echo "❌ 스킬 개수 불일치: 배포 $deployed / 소스 $source"
        exit 1
    fi
    echo "✅ 업데이트 완료 (스킬 $deployed개)"

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

# AskUserQuestion 카드 차단 훅을 settings.json에 비파괴적으로 병합 (같은 matcher가 있으면 갱신만, 다른 훅·키는 보존)
setup-hooks:
    #!/usr/bin/env bash
    set -euo pipefail
    SETTINGS=~/.claude/settings.json
    [ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
    CMD='printf '"'"'%s\n'"'"' '"'"'{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"AskUserQuestion 카드는 쓰지 않는다. 같은 질문을 평문 채팅으로 물어라."}}'"'"''
    TMP=$(mktemp)
    jq --arg cmd "$CMD" '
      .hooks.PreToolUse = ((.hooks.PreToolUse // []) | map(select(.matcher != "AskUserQuestion")))
        + [{matcher: "AskUserQuestion", hooks: [{type: "command", command: $cmd}]}]
    ' "$SETTINGS" > "$TMP"
    jq empty "$TMP"
    mv "$TMP" "$SETTINGS"
    chmod 600 "$SETTINGS"
    echo "✅ AskUserQuestion 차단 훅 → $SETTINGS"

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
