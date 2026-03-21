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

# 심링크 생성
echo "🔗 Linking product → ~/.claude..."
cd "$(dirname "$0")"
just link

echo ""
echo "🎉 Done! Run 'just' for available commands."
