---
paths:
  - "**/justfile"
  - "**/bootstrap.sh"
  - "**/.claude/CLAUDE.md"
---

# Stow 배포 규칙

demiurge는 `product/.claude/`와 `bin/.local/bin/`을 GNU Stow로 `~/.claude/`, `~/.local/bin/`에 심링크 배포한다. justfile 명령: `just link`, `just unlink`.

## 핵심 규칙: cleanup 순서

소스 파일을 삭제하거나 이동(rename)할 때 **반드시 다음 순서를 지켜라**:

```
1. just unlink            # 소스가 살아있는 상태에서 모든 심링크 제거
2. 소스 파일 변경/삭제    # rm/mv/edit
3. just link              # 정리된 상태로 다시 배포
4. 검증                   # broken symlink 0건 확인
```

### 왜 이 순서인가?

stow `-D` (unlink)는 "**stow source에 현재 존재하는 파일**"의 심링크만 추적해서 제거한다. 따라서:

- ❌ **잘못된 순서**: 소스 삭제 → unlink → link
  - unlink 시 stow가 source에 파일이 없어 인식 못 함
  - dangling symlink가 `~/.claude/` 하위에 그대로 남음
  - 예: `~/.claude/commands/new_rl.md` → (broken target)

- ✅ **올바른 순서**: unlink → 소스 삭제 → link
  - unlink가 모든 심링크를 깔끔히 제거
  - 소스 삭제 후 link 재실행 시 살아있는 파일만 새로 배포

## 검증 명령

```bash
# dangling symlink 스캔
find ~/.claude/ -maxdepth 3 -type l ! -exec test -e {} \; -print
# 위 출력이 없으면 0건

# 또는 ls로 깨진 심링크 확인 (ls가 빨간색으로 표시)
ls -la ~/.claude/commands/ ~/.claude/skills/ ~/.claude/agents/
```

## 사전 점검 (선택)

대규모 변경 전 dry-run으로 충돌 사전 확인:

```bash
stow -n -v -R --no-folding -t ~ product 2>&1 | head -30
```

`--no-folding` 동작 특성: skills/agents 하위는 **파일 단위 심링크**가 만들어진다 (디렉토리 폴딩 안 함). 즉 `~/.claude/skills/<name>/SKILL.md`이 개별 심링크.

## 직접 정리 옵션 (응급)

`just unlink && just link` 사이클이 무거우면 dangling만 직접 제거 가능:

```bash
rm ~/.claude/commands/{name1,name2,...}.md
```

단, 누락 위험이 있어 권장은 위 4단계 사이클.

## 롤백 절차

skill 배포가 실패했거나 의도와 다르게 동작하면:

```bash
git checkout product/.claude/   # 소스 원복
just unlink && just link        # 심링크도 원복
```

## 마이그레이션 사례

`commands/` → `skills/` 마이그레이션(`/new_rl`→`/rl-fresh` 등) 시 위 순서로 진행하면 git이 rename으로 깔끔하게 인식하고 (`R` 상태), `~/.claude/commands/`에 dangling 0건 달성 가능. 실측 commit: `42ae242`.
