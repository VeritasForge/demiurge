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
4. 빈 디렉터리 정리       # 삭제한 스킬의 껍데기 폴더 제거 (아래 검증 명령 참조)
5. 검증                   # broken symlink 0건 + 스킬 개수 일치 확인
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
# 1. 빈 디렉터리 정리 — 스킬을 삭제·이동한 뒤 반드시 실행
find ~/.claude/skills/demiurge -depth -type d -empty -delete

# 2. dangling symlink 스캔
find ~/.claude/ -maxdepth 5 -type l ! -exec test -e {} \; -print
# 위 출력이 없으면 0건

# 3. 배포된 스킬 개수가 소스와 같은지 확인
ls ~/.claude/skills/demiurge/skills | wc -l
ls product/.claude/skills/demiurge/skills | wc -l
```

### 왜 빈 디렉터리 정리가 필요한가

`--no-folding`이라 배포 산출물은 **파일 단위 심링크**다. `just unlink`는 그 심링크 파일만 지우고 **디렉터리는 남긴다.** 그래서 스킬을 삭제하면 `~/.claude/skills/demiurge/skills/<name>/`이 빈 껍데기로 남아, `ls`로 센 스킬 개수가 실제보다 많게 나온다. 하위 폴더(`assets/`, `references/`)를 가진 스킬은 껍데기가 여러 겹이라 `rmdir` 한 번으로는 지워지지 않으니 위 `find -depth -empty -delete`를 쓴다.

실측 확인 사항 (2026-09-06):
- 이 명령은 **완전히 빈** 디렉터리만 아래에서부터 지운다. 파일이 하나라도 있으면 남는다.
- **깨진 심링크가 든 디렉터리는 "비어 있지 않음"으로 판정되어 살아남는다** — 즉 이 정리가 dangling 스캔 결과를 가리지 않는다. 두 명령의 실행 순서는 무관하다.
- `-type d`는 심링크를 따라가지 않으므로, `~/.claude/skills/` 아래 다른 곳을 가리키는 심링크 스킬(`vercel-*` 등)은 대상이 되지 않는다.
- 범위를 `~/.claude/skills/demiurge`로 좁혀 쓴다. `~/.claude/` 전체에 걸면 Claude Code가 쓰는 다른 빈 디렉터리까지 지운다.

## 사전 점검 (선택)

대규모 변경 전 dry-run으로 충돌 사전 확인:

```bash
stow -n -v -R --no-folding -t ~ product 2>&1 | head -30
```

`--no-folding` 동작 특성: 하위 디렉터리는 폴딩되지 않고 **파일 단위 심링크**가 만들어진다. 즉 `~/.claude/skills/demiurge/skills/<name>/SKILL.md`이 개별 심링크다 (스킬은 `demiurge` 플러그인 네임스페이스 아래에 배포된다).

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

`commands/` → `skills/` 마이그레이션 시 위 순서로 진행하면 git이 rename으로 깔끔하게 인식하고 (`R` 상태), `~/.claude/commands/`에 dangling 0건 달성 가능. 실측 commit: `42ae242`.

미사용 자산 정리(스킬 26개·에이전트 21개 삭제, 스킬 2개 이동) 시에도 같은 순서로 dangling 0건을 유지했다. 다만 삭제한 스킬 자리마다 빈 디렉터리가 남아 배포 스킬 수가 실제보다 많게 집계됐고, 위 정리 명령을 추가해 해결했다. 실측 commit: `96821cc`.
