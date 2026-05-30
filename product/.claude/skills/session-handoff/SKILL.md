---
name: session-handoff
description: Use when a long or autonomous coding session is about to run out of context and must /clear and resume in a fresh session, or when the user says "handoff", "context-clear 전 정리", "다음 세션 인계", "다음 세션이 이어받게", or invokes /session-handoff. For passing IN-PROGRESS work to the next LLM session. NOT release-handoff (that is release/deploy ops handoff).
argument-hint: "<slug 또는 진행 중 작업 설명>"
allowed-tools: Read, Grep, Glob, Bash, Write, TaskList, TaskGet
---

# Session Handoff

## Overview

진행 중인 작업을 **새 LLM 세션**에 넘기는 인계 문서를 만든다. 핵심 원칙 하나:

> 새 세션의 AI가 **이 문서 한 파일만** 읽고, 첫 turn에 **정확히 멈춘 자리**에서 이어받을 수 있어야 한다. 대화 맥락은 전부 사라진다고 가정한다.

`release-handoff`(릴리즈/배포 운영 인계)와 다르다. 이건 *진행 중 작업의 세션 인계*다.

## When to Use

- context window가 거의 차서 곧 `/clear` 해야 할 때
- autopilot/rl 같은 장기 자율 작업 중간 인계
- 사용자가 "handoff", "다음 세션 인계", "context-clear 전 정리" 요청
- `/session-handoff` 직접 호출

**When NOT:** 릴리즈/배포 이관(→ `release-handoff`), 완료된 chunk의 사람용 1페이지 회고(→ DIGEST, 아래 구분 참조).

## The Iron Rule — 기억으로 쓰지 말고 수집부터 하라

문서를 쓰기 전에 **명령을 실행해 사실을 수집**한다. 기억·대화 맥락에만 의존하면 commit hash·테스트 수·완료 task가 틀린다 (가장 흔한 실패). 단, 아래 순서·구분을 지킨다.

### 0. 기존 HANDOFF 먼저 Read (있으면) — 데이터 손실 방지
`docs/autopilot/<slug>/HANDOFF.md`가 이미 있으면 **Write 전에 반드시 Read**한다. Write는 전체 덮어쓰기다 — 먼저 읽지 않으면 이전 재진입 기록이 날아간다. 이전 본문은 새 문서 하단에 `--- *이하 이전 기록(맥락 참고용)*` 으로 보존하거나 Edit로 갱신한다.

### 1. 싼 수집 — 항상 실행 (빠르고 안전)

**base 브랜치 이름을 하드코딩하지 말 것** (`main`도 `origin/main`도 가정 금지). 이건 전역 스킬이다 — repo에 origin이 없을 수도, 기본 브랜치가 `master`/`develop`일 수도, 진행 plan이 다른 feature 위에 분기했을 수도 있다. 탐지 우선순위:

> ① **plan/이전 HANDOFF에 적힌 base** (다른 feature 위 분기는 이 정보로만 안다 — 최우선) → ② 현재 브랜치 upstream → ③ origin 기본 브랜치 → ④ 로컬 `main`/`master`/`develop`. **모두 실패하거나 모호하면 추측 말고 사용자에게 확인.**

```bash
# 자동 탐지 (②~④). plan이 base를 명시하면 그 값으로 base_ref를 덮어쓸 것.
# 핵심 가드: 후보의 merge-base가 HEAD와 같으면(=완료 커밋 0개) 그 후보는 base가 아니다.
#   (자기 자신의 원격을 추적하는 upstream, base==현재 브랜치, main에서 직접 작업 등 → 빈 history 유발)
head=$(git rev-parse HEAD); base=""; base_ref=""
for c in "$(git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null)" \
         "$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)" \
         main master develop trunk; do
  [ -n "$c" ] || continue
  git rev-parse --verify -q "$c" >/dev/null 2>&1 || continue
  mb=$(git merge-base HEAD "$c" 2>/dev/null) || continue
  [ "$mb" = "$head" ] && continue            # 완료 0개 → 이 후보는 base 아님, 다음으로
  base="$mb"; base_ref="$c"; break
done
git status -sb                               # 브랜치 + 미커밋 변경
# 검증 게이트: base 비었거나(탐지 실패) 완료 커밋 0개면 → 빈/틀린 history로 진행 금지, 사용자에게 base 확인
[ -n "$base" ] && git log --oneline --no-merges "$base"..HEAD   # 완료 커밋 ↔ hash 매핑 출처
```
**완료 커밋이 0개로 나오면 base가 틀린 것이다.** 절대 빈 완료 table을 그대로 쓰지 말고 — plan/이전 HANDOFF의 base를 다시 확인하거나 사용자에게 묻는다. (빈 history = 새 세션이 무엇이 끝났는지 모름 = 인계 실패.)
- **미커밋 변경이 있으면**: hash로 복원 불가능한 in-flight 작업이다. 해당 파일을 #2/#4에 "uncommitted: `<파일>` — `<무엇>`"으로 명시하고, 가능하면 WIP 커밋 후 인계한다. (`/clear`는 대화만 비우고 작업트리는 남지만, 새 세션은 그 맥락을 모른다.)

### 2. 비싼 수집 — 선택 (인계를 절대 막지 말 것)
테스트·커버리지는 **느리거나 hang될 수 있다**. 인계는 context가 찼을 때 쓰는 것이라, 테스트가 인계 작성을 막으면 본말전도다.
- **1순위**: `run.log`·이전 HANDOFF·CI의 **마지막 알려진 베이스라인** 재사용 → `last known: 307 pass/100% (as of <hash>)` 로 기재 + 재검증 명령만 남긴다.
- 최근 결과가 없고 빨리 끝날 때만 실제 실행하되 **프로젝트의 실제 명령**을 쓴다 (justfile/package.json/Makefile/pyproject/README에서 확인 — 아래는 snowball 예시일 뿐, 그대로 복붙 금지):
```bash
# (예시 — 프로젝트마다 다름) timeout으로 hang 차단
timeout 120 bash -c 'cd <repo>/backend && uv run pytest -q' 2>&1 | tail -3
```

### 3. 그 외
- **TaskList / TaskGet** (있으면) → completed / in_progress / pending 분리. 없으면 plan 단계 ref로 대체.
- `run.log` 있으면 `[judgment #N]` 라인, commit message에서 `Codex`/`stop-hook` 패턴 추출

수집한 값(특히 hash·테스트 수)은 **그대로** 옮긴다. 추정 금지.

## 8-Section Template

순서·번호 고정. #1은 **단 한 줄로 시작**해야 한다.

| # | 섹션 | 핵심 |
|---|------|------|
| 1 | **⚡ 즉시 재진입** | `/autopilot <plan>` 같은 **단일 커맨드 1줄** (또는 자연어 1줄). 새 세션이 첫 turn에 그대로 실행. plan 경로는 `docs/superpowers/plans/`의 최신 mtime 파일에서 추론 — 불확실하면 추측 말고 자연어 1줄로 |
| 2 | **📍 TL;DR — 어디서 멈췄나** | 브랜치 / 마지막 커밋 hash / 테스트 베이스라인 / **다음 task ID** |
| 3 | **✅ 완료 task table** | `task ID │ commit hash │ 한 줄 요약`. **hash 필수** — 새 세션이 `git show <hash>`로 즉시 복원 |
| 4 | **⏳ 남은 task table** | `task ID │ 핵심 액션 │ 예상 turn 수` |
| 5 | **🛡 누적 judgments table** | `결정 │ 적용 위치`. 같은 판단을 새 세션이 되돌리거나 반복하지 않도록 (산문 금지, table) |
| 6 | **🚨 외부 review 패턴** | Codex stop-hook 등 반복 발동 게이트의 history + 다층 안전망 원칙 (해당 시) |
| 7 | **🗂 핵심 파일 위치** | spec / plan / 손댈 code / memory 인덱스. 새 세션이 첫 5분에 읽을 것 |
| 8 | **💡 다음 task 작성 힌트** | import 예시, 패턴 code snippet (있으면) |

## 산출물 경로

- 기본: `docs/autopilot/<slug>/HANDOFF.md` (autopilot/rl 작업과 같은 slug 디렉토리)
- `<slug>`는 인자로 받거나 진행 중 plan 파일명(`docs/superpowers/plans/`의 최신 mtime)에서 추론
- 같은 디렉토리에 이미 HANDOFF가 있으면 **덮어쓰지 말고** 최신 상태로 갱신하되, 이전 재진입 기록은 하단 "맥락 참고용"으로 보존

## DIGEST vs HANDOFF (혼동 금지)

| | 용도 | 독자 |
|---|------|------|
| **HANDOFF.md** | *진행 중* 인계 — 다음 LLM 세션이 한 줄로 재진입 | 다음 세션의 AI |
| **DIGEST.md** | *완료 chunk* 회고 — 어디를 검토할지 1페이지 | 사람 (autopilot Phase 5 DIGEST와 일치) |

둘을 한 문서에 섞지 않는다. 인계가 목적이면 HANDOFF.

## Common Mistakes

| 실패 | 교정 |
|------|------|
| 기억으로 hash·테스트 수 작성 | Iron Rule대로 명령 실행 후 값 복사 |
| 완료 task에 commit hash 없음 | 매 row에 hash — `git show`로 복원 가능해야 함 |
| 기존 HANDOFF를 Read 없이 Write | Write는 전체 덮어쓰기 — 먼저 Read 후 이전 기록 보존 (Iron Rule §0) |
| base를 `main`/`origin/main`으로 하드코딩 | origin 없는 repo·master 기본·다른 feature 위 분기에서 깨짐. 탐지 우선순위(upstream→origin HEAD→로컬 후보)+모호하면 사용자 확인 (Iron Rule §1) |
| 완료 history가 0개인데 그대로 진행 | `merge-base==HEAD`(자기-upstream/base==현재브랜치/main서 작업)면 빈 history. 그 후보 skip + 0개면 base 재확인 (Iron Rule §1 검증 게이트) |
| snowball 예시 명령을 그대로 복붙 | 전역 스킬 — 프로젝트 실제 테스트 명령 확인 후 사용 |
| 테스트 hang으로 인계 못 씀 | 마지막 알려진 베이스라인 재사용 + `timeout` (Iron Rule §2) |
| #1이 `git status`부터 시작 | #1은 **단일 재진입 커맨드 1줄** |
| judgments를 산문으로 | `결정 │ 적용 위치` table |
| DIGEST(회고)와 섞음 | HANDOFF는 인계 전용 |
| release-handoff로 처리 | 그건 배포 운영 인계 — 용도 다름 |

## Quick Reference (실행 순서)

1. `<slug>` 확정 → 산출물 경로 결정 → **기존 HANDOFF 있으면 Read** (Iron Rule §0)
2. 싼 수집 실행(§1: base·log·status) + 비싼 수집은 last-known 재사용 우선(§2)
3. 8-section 템플릿 채우기 (#3 hash 필수, #1 한 줄)
4. `docs/autopilot/<slug>/HANDOFF.md`에 Write (이전 기록 보존)
5. self-check: ① #1 한 줄로 재진입 가능? ② 완료 row마다 hash? ③ base 하드코딩 없이 탐지하고 완료 history가 비지 않았나(0개면 base 재확인)? ④ 이전 기록 안 날렸나?
