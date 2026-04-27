#!/bin/bash
set -e

echo "🚀 Demiurge AI Harness Setup"
echo ""

# Homebrew 확인
if ! command -v brew &>/dev/null; then
    echo "❌ Homebrew required: https://brew.sh"
    exit 1
fi

# 의존성 설치
for tool in stow just; do
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
echo "🔗 Linking product → ~/.claude, bin → ~/.local/bin..."
cd "$(dirname "$0")"
just link

echo ""
echo "🎉 Done! Run 'just' for available commands."
