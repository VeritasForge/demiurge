---
name: retrospective
description: Use when reviewing an AI collaboration session for lessons learned, when AI keeps repeating mistakes, or when you want to improve your AI harness. '이번 세션에서 뭘 배웠지?', 'AI가 계속 같은 실수를 해', '하니스를 개선하고 싶어' 같은 요청 시 사용.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Skill
argument-hint: "[optional: brief context about the session]"
---

# Retrospective Skill

## Overview

AI와 협업한 세션을 회고하여 교훈(Lessons & Learned)을 체계적으로 추출하고, AI 하니스 전체(Skills, CLAUDE.md, Memory, Hooks, Workarounds, Workflow)에 반영하는 프로토콜입니다.

**철학**: Compound Engineering의 "Each unit of work should make subsequent units easier"를 AI 협업 전체에 적용. 코드 문제뿐 아니라 모든 AI 협업 경험에서 교훈을 추출하여 하니스를 발전시킨다.

```
┌───────────────────────────────────────────────────────────────┐
│              Retrospective Protocol (4-Phase)                  │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Phase 1: 교훈 추출                                           │
│  ┌──────────────────────────────────────────────────┐         │
│  │  세션 컨텍스트 6가지 신호 분석                      │         │
│  │  + git diff 변경 파일 확인                          │         │
│  │  + AskUserQuestion 사용자 인터뷰 (3질문)            │         │
│  │  → L{N} 포맷으로 교훈 구조화                        │         │
│  └────────────────────┬─────────────────────────────┘         │
│                        │                                       │
│  Phase 2: 교훈 분류                                           │
│  ┌────────────────────▼─────────────────────────────┐         │
│  │  6개 반영 대상으로 분류                             │         │
│  │  + 우선순위 판단 (높/중/낮)                         │         │
│  └────────────────────┬─────────────────────────────┘         │
│                        │                                       │
│  Phase 3: 사용자 승인                                         │
│  ┌────────────────────▼─────────────────────────────┐         │
│  │  교훈 테이블 + 변경 제안 제시                       │         │
│  │  → 전체/일부/수정 후 승인                           │         │
│  └────────────────────┬─────────────────────────────┘         │
│                        │                                       │
│  Phase 4: 반영                                                │
│  ┌────────────────────▼─────────────────────────────┐         │
│  │  대상별 순서로 파일 반영                             │         │
│  │  → 반영 결과 요약 테이블 출력                        │         │
│  └──────────────────────────────────────────────────┘         │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

## When to Use

- AI가 같은 유형의 실수를 반복할 때
- 세션에서 많은 교정/거부가 발생했을 때
- 스킬을 실행했는데 결과물이 기대와 달랐을 때
- AI 하니스(Skills, CLAUDE.md, Hooks 등)를 개선하고 싶을 때
- 세션이 길어져서 배운 것을 정리하고 싶을 때

**사용하지 않을 때:**
- 단순 질문/답변 세션 (교훈이 없음)
- 이미 /retrospective를 실행한 직후 (중복)

**필수 도구**: `mcp__sequential-thinking__sequentialthinking` -- 모든 Phase 전환 시 사용
**참조 스킬**: `update-config` -- Phase 4에서 Hooks 반영 시 활용

---

## Sequential Thinking 사용 규칙

모든 Phase 전환 시 `mcp__sequential-thinking__sequentialthinking`을 사용합니다:

| 시점 | 사고 내용 |
|------|----------|
| Phase 시작 | 목표, 수집할 정보, 판단 기준 수립 |
| 핵심 판단 | 신호 분류, 대상 판정, 우선순위 결정 |
| Phase 완료 | Exit Criteria 충족 여부 확인 + 다음 Phase 전환 판단 |

---

## Input Specification

사용자 인자: `$ARGUMENTS`

| 항목 | 필수 | 설명 |
|------|------|------|
| `context` | - | 세션에 대한 간략한 설명 (없으면 현재 대화 컨텍스트에서 자동 추출) |

**예시**: `/retrospective 이력서 최적화 세션에서 AI가 반복적으로 같은 실수를 했음`

---

## Phase 1: 교훈 추출

**mcp__sequential-thinking__sequentialthinking**을 사용하여 분석 계획을 수립한 후 실행.

### Step 1-1: 세션 컨텍스트 자동 분석

현재 대화 컨텍스트에서 다음 **6가지 신호**를 식별:

| 신호 | 설명 | 예시 |
|------|------|------|
| **AI 실행 실패** | AI가 도구 실행 중 에러를 낸 지점 | Write 도구가 "File has not been read yet" 에러 |
| **사용자 교정/거부 (도구)** | 사용자가 도구 호출을 거부하거나 교정한 경우 | AskUserQuestion reject 후 피드백 |
| **사용자 교정/거부 (제안)** | AI의 텍스트/내용 제안을 사용자가 수정한 경우 | "확보 -> 높였습니다"로 대안 제시 |
| **재시도/방향 전환** | AI가 접근 방식을 바꾼 지점 | subagent -> 현재 컨텍스트로 전환 |
| **반복 질문/요청 패턴** | 사용자가 반복적으로 같은 유형의 요청을 한 경우 | "이건 왜 빠졌어?" 반복 = AI가 선제적으로 체크해야 함 |
| **누락 지적** | 사용자가 "이것도 해줘", "왜 안 했어?" 등으로 누락을 지적 | "Experience Summary가 왜 없어?" |

### Step 1-2: 변경 파일 분석

```bash
git diff --name-only HEAD~{N}  # 이 세션에서 변경된 파일 목록
```

변경된 파일 중 하니스 관련 파일(Skills, CLAUDE.md, settings.json, memory/)이 있으면, 어떤 변경이 왜 이루어졌는지를 교훈과 연결.

### Step 1-3: 사용자 인터뷰

AskUserQuestion으로 3가지 질문:

1. "이 세션에서 AI가 잘못하거나 불편했던 점이 있나요?"
2. "다음 세션에서 AI가 기억했으면 하는 것이 있나요?"
3. "이 세션에서 발견한 패턴이나 규칙이 있나요?"

### Step 1-4: 교훈 구조화

각 교훈은 다음 **L{N} 포맷**으로 작성:

```markdown
### L{N}. {짧은 제목}

- **발견 소스**: 실행 실패 / 사용자 교정(도구) / 사용자 교정(제안) / 방향 전환 / 반복 패턴 / 누락 지적 / 사용자 인터뷰
- **문제**: 무엇이 잘못되었는가 (구체적 사례)
- **반영 대상**: Skills / CLAUDE.md / Memory / Hooks / Workarounds / Workflow
- **우선순위**: 높음 / 중간 / 낮음
- **개선**: 구체적 변경 제안
- **영향 파일**: 반영 대상 파일 경로
```

**Exit Criteria**: 교훈이 1개 이상 추출됨.

---

## Phase 2: 교훈 분류

**mcp__sequential-thinking__sequentialthinking**을 사용하여 분류 판단을 수행.

### 6개 반영 대상

| 대상 | 분류 기준 | 반영 방식 |
|------|----------|----------|
| **Skills** | 특정 스킬 실행 중 발생한 문제 | SKILL.md 수정 |
| **CLAUDE.md** | 모든 세션에 적용되는 범용 규칙 | CLAUDE.md에 규칙 추가 |
| **Memory** | 사용자 선호도, 프로젝트 맥락, 피드백 | memory/ 파일 생성/수정 |
| **Hooks** | 반복적으로 실패하는 패턴을 자동 방지 | settings.json 수정 |
| **Workarounds** | Claude Code 자체의 한계/버그 | Memory에 reference 타입으로 저장 |
| **Workflow** | 작업 방식/프로세스 개선 | CLAUDE.md 또는 Memory에 반영 |

### 분류 판단 로직

교훈 하나에 대해 (복수 대상 가능):

```
1. 특정 스킬에서만 발생? → Skills
2. 모든 세션에 적용? → CLAUDE.md
3. 사용자 개인 선호/맥락? → Memory
4. 자동 강제가 필요? (규칙으로는 안 지켜짐) → Hooks
5. Claude Code 도구 한계? → Workarounds
6. 작업 방식 변경? → Workflow
```

### CLAUDE.md vs Memory 판별 기준

핵심 질문: **"이것을 제거하면 팀 누구라도 실수할까?"**
- Yes → CLAUDE.md (프로젝트 규칙)
- No, 나만 해당 → Memory (개인 학습)

| 기준 | CLAUDE.md | Memory |
|------|-----------|--------|
| 성격 | 지시사항 (해야 할 것/하면 안 되는 것) | 학습 기록 (발견한 것/교정된 것) |
| 공유 | git 체크인, 팀 공유 | 로컬, 개인용 |
| 예시 | "`:bd` 대신 mini.bufremove 사용" | "lazy.nvim config는 lazy-load 후 실행됨" |

**CLAUDE.md에 넣으면 안 되는 것**: 코드에서 유추 가능한 것, 도구 워크어라운드, 개인 선호
**Memory에 넣으면 안 되는 것**: 팀 공유 규칙, 빌드 명령어, 위험 행동 금지 규칙

### 우선순위 판단

- **높음**: 같은 실수가 반복될 가능성이 높고, 반영하면 즉시 효과가 있는 것
- **중간**: 개선하면 좋지만 급하지 않은 것
- **낮음**: 특수한 상황에서만 발생하는 것

**Exit Criteria**: 모든 교훈에 반영 대상과 우선순위가 할당됨.

---

## Phase 3: 사용자 승인

**mcp__sequential-thinking__sequentialthinking**을 사용하여 승인 요청 내용을 정리.

### 교훈 테이블 제시

AskUserQuestion으로 전체 교훈 목록을 테이블 형태로 제시:

```markdown
| # | 교훈 | 대상 | 우선순위 | 변경 제안 |
|---|------|------|---------|----------|
| 1 | ... | Skills | 높음 | ... |
| 2 | ... | Memory | 높음 | ... |
| 3 | ... | Workarounds | 중간 | ... |
```

### 승인 선택지 (3가지)

1. **"전체 승인"** -- 모든 교훈을 반영
2. **"일부만 승인"** -- 반영할 번호 선택 (예: "1, 3만 반영")
3. **"수정 후 승인"** -- 특정 교훈의 내용/대상/변경 제안을 수정

**Exit Criteria**: 사용자가 반영할 교훈 목록을 확정함.

---

## Phase 4: 반영

**mcp__sequential-thinking__sequentialthinking**을 사용하여 반영 계획을 수립한 후 실행.

### 대상별 반영 순서

반드시 아래 순서로 반영 (의존성 고려):

```
1. Memory   → Write로 memory/ 파일 생성/수정 (feedback/user/project/reference 타입)
              ⚠️ MEMORY.md 인덱스도 함께 업데이트할 것
2. CLAUDE.md → Edit으로 규칙 추가
              ⚠️ 기존 규칙과 중복되지 않는지 반드시 체크
3. Skills    → Edit으로 해당 SKILL.md 수정
4. Hooks     → Skill 도구로 update-config 스킬을 호출하여 settings.json 수정
5. Workarounds → Memory에 reference 타입으로 저장
6. Workflow  → CLAUDE.md 또는 Memory에 반영 (범용 규칙이면 CLAUDE.md, 개인 맥락이면 Memory)
```

### 반영 시 주의사항

- **Memory 반영**: memory/ 하위에 파일 생성/수정 후, MEMORY.md의 인덱스 섹션에 링크를 추가
- **CLAUDE.md 반영**: 반영 전 기존 CLAUDE.md를 Read하여 중복 규칙이 없는지 확인. CLAUDE.md가 너무 길어지면 Claude가 무시하므로 간결하게 유지
- **Hooks 반영**: 직접 settings.json을 수정하지 말고, `update-config` 스킬을 Skill 도구로 호출하여 안전하게 수행
- **교훈 간 충돌**: 교훈 간 충돌이 있으면 사용자에게 AskUserQuestion으로 알리고 결정을 요청

### 반영 결과 요약

모든 반영 완료 후 결과 테이블을 출력:

```markdown
## Retrospective 결과

| # | 교훈 | 대상 | 반영 상태 |
|---|------|------|----------|
| 1 | ... | Skills | 반영됨 (SKILL.md:L45) |
| 2 | ... | Memory | 반영됨 (memory/feedback_xxx.md) |
| 3 | ... | CLAUDE.md | 반영됨 |

총 N개 교훈 중 M개 반영 완료.
```

**Exit Criteria**: 승인된 모든 교훈이 대상 파일에 반영됨 + 반영 결과 요약 테이블 출력.

---

## 제약사항

- CLAUDE.md가 너무 길어지면 Claude가 무시하므로, CLAUDE.md 반영 시 기존 규칙과 중복되지 않는지 반드시 체크
- Memory 파일 생성/수정 시 MEMORY.md 인덱스도 함께 업데이트
- Hooks 반영은 직접 settings.json을 수정하지 말고, update-config 스킬을 통해 안전하게 수행
- 교훈 간 충돌이 있으면 사용자에게 알리고 결정을 요청
- 한 세션에서 추출하는 교훈은 실행 가능한 수준으로 제한 (너무 추상적인 교훈은 구체화하거나 제외)

---

## Common Mistakes

- 교훈이 너무 추상적 ("더 잘해야 한다") → 구체적 사례와 변경 제안이 있어야 함
- 반영 대상을 잘못 분류 (사용자 선호를 CLAUDE.md에 넣기) → Memory(feedback)가 맞음
- CLAUDE.md에 너무 많은 규칙 추가 → Claude가 무시함. 정말 범용적인 것만
- 교훈 간 충돌을 무시하고 반영 → 사용자에게 먼저 확인
