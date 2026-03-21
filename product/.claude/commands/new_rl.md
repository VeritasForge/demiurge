---
description: "Fresh Context Ralph Loop - subagent 기반 요구사항별 신선한 컨텍스트 실행"
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch, Edit, Write, Task
argument-hint: "PROMPT [--max-iterations N]"
---

# Fresh Context Ralph Loop Runner

subagent(Task tool)를 활용하여 각 요구사항을 신선한 컨텍스트에서 실행합니다.
메인 에이전트는 경량 디스패처 역할만 수행하여 컨텍스트 오염을 방지합니다.

**Usage:**
- `/new_rl <prompt>` — 기본 20회 반복
- `/new_rl <prompt> --max-iterations 30` — 최대 반복 횟수 지정

```
Parse the user's input from: $ARGUMENTS

## Step 0: 인자 파싱

Extract:
1. The prompt text (everything that is NOT a flag or flag value)
2. The --max-iterations value (number after --max-iterations flag, default: 20)

## Step 1: 안전 장치 경고

Before starting, check and display warnings (but always continue):

- If the prompt does NOT contain any of: "하지 말 것", "하지 마", "DO NOT", "금지", "MUST NOT"
  → Display: "⚠️ '하지 말 것' 섹션 없음 — Claude가 범위를 벗어날 수 있습니다"

- If the prompt does NOT contain any of: "완료 기준", "When complete", "완료되면", "[ ]"
  → Display: "⚠️ 명시적 완료 기준 없음 — 루프 종료 조건이 불명확할 수 있습니다"

- If max-iterations > 50
  → Display: "⚠️ max-iterations > 50 — API 비용이 크게 증가할 수 있습니다"

Display all applicable warnings, then proceed.

## Step 2: 요구사항 자동 추출

Analyze the user's prompt and extract discrete, actionable requirements.

### 추출 규칙:
1. 프롬프트에서 독립적으로 실행 가능한 요구사항들을 추출
2. 번호 매기기, 체크리스트, 섹션 헤딩 등 구조가 있으면 그대로 활용
3. 구조가 없으면 논리적 단위로 분해 (구현 → 테스트 → 문서화 등)
4. 요구사항을 추출할 수 없으면 전체 프롬프트를 단일 요구사항으로 처리
5. 각 요구사항은 한 문장으로 요약 (제목 역할)

### 추출 결과:
내부적으로 다음 형식의 리스트를 생성 (파일에 저장하지 않음, Step 3에서 사용):

1. {요구사항 제목 1}
2. {요구사항 제목 2}
3. {요구사항 제목 3}
...

사용자에게 추출 결과를 표시:

📋 추출된 요구사항 ({N}개):
  1. {제목 1}
  2. {제목 2}
  ...

## Step 3: 추적 파일 생성

### 3-1: 충돌 확인

Check if `.claude/ralph-loop.local.md` already exists:
- If exists: Display "⚠️ 기존 ralph-loop가 활성화되어 있습니다. 덮어쓰시겠습니까?" and ask user
- If user declines: STOP

Check if `.claude/new-rl-context.md` or `.claude/new-rl-progress.md` already exists:
- If exists: Display "⚠️ 이전 new_rl 세션 파일이 남아있습니다. 덮어쓰시겠습니까?" and ask user
- If user declines: STOP

### 3-2: context.md 생성

Use **Write** tool to create `.claude/new-rl-context.md`:

Content:
```
# New RL Context

## Original Prompt
{사용자의 원본 프롬프트 전체, 수정 없이 그대로}
```

This file is READ-ONLY after creation. Every subagent receives this as project context.

### 3-3: progress.md 생성

Use **Write** tool to create `.claude/new-rl-progress.md`:

Content:
```
# Progress Tracker

## Status
- total: {N}
- completed: 0
- current: 1
- retries: 0

## Requirements
- [ ] 1. {요구사항 제목 1}
- [ ] 2. {요구사항 제목 2}
- [ ] 3. {요구사항 제목 3}
...

## Log
(subagent 결과가 여기에 기록됩니다)
```

## Step 4: 디스패처 설정 및 Ralph Loop 시작

### 4-1: ralph-loop.local.md 생성

Use **Write** tool to create `.claude/ralph-loop.local.md`:

Content:
```
---
active: true
iteration: 1
max_iterations: {max-iterations}
completion_promise: "COMPLETE"
started_at: "{current-timestamp-ISO}"
---

# New RL Dispatcher

You are a LIGHTWEIGHT DISPATCHER. Do NOT implement requirements yourself.
Your ONLY job is to read progress, spawn subagents, and update progress.

## Dispatcher Protocol

### 1. Read Progress
Read `.claude/new-rl-progress.md` and find the first `- [ ]` item (not completed).
If no `- [ ]` items remain, ALL requirements are done → output <promise>COMPLETE</promise> and exit.

### 2. Read Context
Read `.claude/new-rl-context.md` to get the full original prompt.

### 3. Spawn Subagent
Use the **Task** tool with `subagent_type: "general-purpose"` to spawn a subagent.

Construct the subagent prompt as follows:

---BEGIN SUBAGENT PROMPT---
# Task: Requirement {N}

## Full Project Context
{contents of new-rl-context.md, verbatim}

## Current Task
From the requirements above, implement ONLY **#{N}: {title}**.

## Rules
- Focus on this requirement only. Do not touch other requirements.
- Run tests/verification after implementation.
- At the end, provide a clear summary:
  - Files modified/created
  - Test results (pass/fail)
  - Any issues or notes
  - Final verdict: SUCCESS or FAILURE
---END SUBAGENT PROMPT---

### 4. Process Result
After the subagent returns:

**If SUCCESS:**
- Update `.claude/new-rl-progress.md`:
  - Change `- [ ] {N}. {title}` to `- [x] {N}. {title}`
  - Increment `completed` count
  - Set `current` to next incomplete item number
  - Reset `retries` to 0
  - Append to Log: `### Req {N}: ✅ {summary}`

**If FAILURE:**
- Increment `retries` in progress.md
- If retries < 3: Keep `current` same (retry on next iteration)
  - Append to Log: `### Req {N} (retry {retries}): ❌ {reason}`
- If retries >= 3: Mark as skipped
  - Change `- [ ] {N}. {title}` to `- [!] {N}. {title} (SKIPPED: {reason})`
  - Set `current` to next incomplete item
  - Reset `retries` to 0
  - Append to Log: `### Req {N}: ⏭️ SKIPPED after 3 retries — {reason}`

### 5. Exit (triggers stop hook)
After processing ONE requirement, attempt to exit.
The stop hook will re-inject this dispatcher prompt if work remains.

IMPORTANT: Process only ONE requirement per iteration to keep context lean.
IMPORTANT: Do NOT accumulate subagent results in your own context. Write them to progress.md only.
```

### 4-2: 시작 메시지 출력

Display to user:

🔄 Fresh Context Ralph Loop activated!

Mode: Subagent Dispatcher (fresh context per requirement)
Requirements: {N}개
Max iterations: {max-iterations}
Completion promise: COMPLETE

📋 Requirements:
  1. {제목 1}
  2. {제목 2}
  ...

Each requirement will be executed by a fresh subagent.
The dispatcher (main agent) only tracks progress.

To monitor: cat .claude/new-rl-progress.md

═══════════════════════════════════════════════════════════
CRITICAL - Fresh Context Ralph Loop Completion
═══════════════════════════════════════════════════════════

The dispatcher will output <promise>COMPLETE</promise>
ONLY when ALL requirements in progress.md are marked [x] or [!].

Do NOT output the promise if any [ ] items remain.
The loop will continue automatically via the stop hook.
═══════════════════════════════════════════════════════════

### 4-3: 첫 번째 디스패치 실행

Immediately begin the dispatcher protocol above:
1. Read progress.md → find first `- [ ]` item
2. Read context.md → get full prompt
3. Spawn subagent for requirement #1
4. Process result → update progress.md
5. Attempt to exit (stop hook will re-inject if not done)

## Edge Cases

### No requirements extracted
If Step 2 could not extract discrete requirements:
- Treat the entire prompt as a single requirement: `1. {first 80 chars of prompt}...`
- progress.md will have exactly 1 item

### All requirements skipped
If all requirements end up as `[!]` (all failed 3 times):
- Output <promise>COMPLETE</promise> to exit the loop
- The user can review progress.md to see what failed and why

### Subagent timeout or error
If the Task tool itself returns an error (not a logical failure):
- Treat as a failure → increment retries → retry or skip logic applies
```
