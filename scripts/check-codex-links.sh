#!/usr/bin/env bash
# 읽기 전용 검사: 사용자 파일이나 링크를 수정하지 않는다.
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "사용법: bash scripts/check-codex-links.sh <저장소 루트> <배포 대상>" >&2
    exit 2
fi

repo_root=$1
deploy_root=$2
failed=0

echo "=== Codex 배포 링크 ==="
for relative in .codex/AGENTS.md .codex/demiurge/communication.md .codex/demiurge/engineering.md; do
    source_file="$repo_root/product/$relative"
    deployed_file="$deploy_root/$relative"
    if [ ! -f "$source_file" ]; then
        echo "  ❌ 원본 없음: $source_file"
        failed=1
    elif [ ! -L "$deployed_file" ]; then
        echo "  ❌ 링크 없음 또는 일반 파일과 충돌: $deployed_file"
        failed=1
    elif [ ! -f "$deployed_file" ]; then
        echo "  ❌ 끊어졌거나 파일을 가리키지 않는 링크: $deployed_file"
        failed=1
    elif [[ ! "$deployed_file" -ef "$source_file" ]]; then
        echo "  ❌ 다른 원본을 가리키는 링크: $deployed_file"
        failed=1
    else
        echo "  ✅ $relative"
    fi
done

if [ -s "$deploy_root/.codex/AGENTS.override.md" ]; then
    echo "  ⚠️ AGENTS.override.md가 존재합니다. Codex는 전역 AGENTS.md보다 이 파일을 우선합니다."
fi

if [ -n "${CODEX_HOME:-}" ] && [[ ! "$CODEX_HOME" -ef "$deploy_root/.codex" ]]; then
    echo "  ⚠️ CODEX_HOME이 배포 위치와 다릅니다. 링크 성공과 실제 지침 로딩은 별도 확인해야 합니다."
fi

echo "  참고: 이 검사는 링크 상태만 확인합니다. 실제 지침 적용은 새 Codex 세션에서 확인하세요."
exit "$failed"
