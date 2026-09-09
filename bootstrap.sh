#!/bin/bash
set -e

echo "🚀 Demiurge AI Harness Setup"
echo "Claude·Codex 전역 지침을 함께 배포합니다. 기존 일반 파일은 덮어쓰지 않습니다."
echo "~/.codex/AGENTS.md가 이미 있으면 README의 'Codex 최초 전환'을 먼저 확인하세요."
echo ""

# Homebrew 확인
if ! command -v brew &>/dev/null; then
    echo "❌ Homebrew required: https://brew.sh"
    exit 1
fi

# 의존성 설치
for tool in stow just jq; do
    if ! command -v $tool &>/dev/null; then
        echo "📦 Installing $tool..."
        brew install $tool
    else
        echo "✅ $tool already installed ($(which $tool))"
    fi
done

echo ""

# ~/.local/bin 준비 + shell PATH 처리
echo "📁 Preparing ~/.local/bin..."
mkdir -p ~/.local/bin

if command -v fish &>/dev/null; then
    fish -c 'fish_add_path -U ~/.local/bin' 2>/dev/null || true
    echo "✅ fish: ~/.local/bin registered in fish_user_paths"
fi

case "$SHELL" in
    */bash) rc=~/.bashrc ;;
    */zsh)  rc=~/.zshrc ;;
    *)      rc="" ;;
esac
if [ -n "$rc" ] && ! grep -q '\.local/bin' "$rc" 2>/dev/null; then
    echo "⚠️  $SHELL: add this line to $rc"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""

# 심링크 생성
echo "🔗 Linking product → ~/.claude + ~/.codex, bin → ~/.local/bin..."
cd "$(dirname "$0")"
just link

echo ""
echo "🩺 Configuring status line..."
if jq -e '.statusLine' ~/.claude/settings.json >/dev/null 2>&1; then
    if [ -t 0 ]; then
        read -p "⚠️  statusLine 설정이 이미 존재합니다. 덮어쓸까요? [y/N] " answer
        case "$answer" in
            [Yy]*) just setup-statusline ;;
            *) echo "⏭️  기존 statusLine 설정 유지" ;;
        esac
    else
        echo "⏭️  statusLine 설정이 이미 있어 건너뜁니다 (비대화형 실행)"
    fi
else
    just setup-statusline
fi

echo ""
echo "🎉 배포 완료. just status로 링크를 확인하고 새 Codex 세션에서 지침 적용을 확인하세요."
echo "Codex 모델·권한·MCP·인증·플러그인 설정은 변경하지 않았습니다."
