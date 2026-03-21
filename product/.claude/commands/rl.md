---
description: "Ralph Loop Runner - sequential-thinking MCP 기반 자율 반복 실행"
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch, Edit, Write, Task
---

# Ralph Loop Runner

Ralph Loop (Ralph Wiggum Technique)을 sequential-thinking MCP와 함께 실행합니다.
동일한 프롬프트를 반복 주입하여 작업이 완료될 때까지 자율 반복 실행합니다.

**Usage:**
- `/rl <prompt>` — 기본 20회 반복
- `/rl <prompt> --max-iterations 30` — 최대 반복 횟수 지정
- `/rl --template tdd` — 프롬프트 템플릿 보기

**Available Templates:** `tdd`, `refactoring`, `api`, `investigation`, `batch`

```
Parse the user's input from: $ARGUMENTS

## Step 0: 템플릿 모드 감지

Check if arguments contain `--template` flag.

If `--template` flag is present:
1. Extract the template name (the word after --template)
2. Map the template name to a file:
   - tdd → ~/.claude/ralph-loop-prompts/tdd-development.md
   - refactoring → ~/.claude/ralph-loop-prompts/refactoring.md
   - api → ~/.claude/ralph-loop-prompts/api-development.md
   - investigation → ~/.claude/ralph-loop-prompts/investigation.md
   - batch → ~/.claude/ralph-loop-prompts/batch-migration.md
3. Read the mapped file using the Read tool
4. Display the template content to the user
5. Display this guidance message:

---
**템플릿 사용법:**
1. 위 프롬프트에서 `[작업 설명]` (또는 `[...]`로 표시된 부분)을 실제 내용으로 교체하세요
2. 교체한 전체 프롬프트를 `/rl`에 전달하세요

예시:
```
/rl "교체된 프롬프트 전체 내용" --max-iterations 30
```
---

6. **STOP HERE** — 루프를 시작하지 않고 안내만 표시한 뒤 종료

If the template name is not recognized, display:
"알 수 없는 템플릿: {name}. 사용 가능: tdd, refactoring, api, investigation, batch"
Then STOP.

If `--template` flag is NOT present, continue to Step 1.

## Step 1: 인자 파싱

Extract:
1. The prompt text (everything that is NOT a flag or flag value)
2. The --max-iterations value (number after --max-iterations flag, default: 20)

## Step 2: 안전 장치 경고

Before starting, check and display warnings (but always continue):

- If the prompt does NOT contain any of: "하지 말 것", "하지 마", "DO NOT", "금지", "MUST NOT"
  → Display: "⚠️ '하지 말 것' 섹션 없음 — Claude가 범위를 벗어날 수 있습니다"

- If the prompt does NOT contain any of: "완료 기준", "When complete", "완료되면", "[ ]"
  → Display: "⚠️ 명시적 완료 기준 없음 — 루프 종료 조건이 불명확할 수 있습니다"

- If max-iterations > 50
  → Display: "⚠️ max-iterations > 50 — API 비용이 크게 증가할 수 있습니다"

Display all applicable warnings, then proceed.

## Step 3: 프롬프트 보강

If the prompt does NOT already contain "<promise>COMPLETE</promise>", append this to the prompt:

---
모든 완료 기준이 충족되면 <promise>COMPLETE</promise>를 출력하세요.
완료되지 않았다면 절대 promise를 출력하지 마세요.
---

## Step 4: Ralph Loop 시작

**IMPORTANT**: Do NOT use the Skill tool to invoke ralph-loop:ralph-loop directly.
Multiline prompts with special characters cause bash parsing errors.

Instead, create the Ralph Loop state file directly using these steps:

1. **Create `.claude/ralph-loop.local.md` file** using Write tool:

```markdown
---
active: true
iteration: 1
max_iterations: {max-iterations}
completion_promise: "COMPLETE"
started_at: "{current-timestamp}"
---

{final_prompt}
```

Where:
- {max-iterations} = parsed value or default 20
- {current-timestamp} = current UTC timestamp in ISO format (YYYY-MM-DDTHH:MM:SSZ)
- {final_prompt} = augmented prompt from Step 3

2. **Display startup message** to the user:

```
🔄 Ralph loop activated in this session!

Iteration: 1
Max iterations: {max-iterations}
Completion promise: COMPLETE (ONLY output when TRUE - do not lie!)

The stop hook is now active. When you try to exit, the SAME PROMPT will be
fed back to you. You'll see your previous work in files, creating a
self-referential loop where you iteratively improve on the same task.

To monitor: head -10 .claude/ralph-loop.local.md

⚠️  WARNING: This loop cannot be stopped manually! It will run infinitely
    unless you reach max-iterations or output the completion promise.

🔄

═══════════════════════════════════════════════════════════
CRITICAL - Ralph Loop Completion Promise
═══════════════════════════════════════════════════════════

To complete this loop, output this EXACT text:
  <promise>COMPLETE</promise>

STRICT REQUIREMENTS (DO NOT VIOLATE):
  ✓ Use <promise> XML tags EXACTLY as shown above
  ✓ The statement MUST be completely and unequivocally TRUE
  ✓ Do NOT output false statements to exit the loop
  ✓ Do NOT lie even if you think you should exit

IMPORTANT - Do not circumvent the loop:
  Even if you believe you're stuck, the task is impossible,
  or you've been running too long - you MUST NOT output a
  false promise statement. The loop is designed to continue
  until the promise is GENUINELY TRUE. Trust the process.

  If the loop should stop, the promise statement will become
  true naturally. Do not force it by lying.
═══════════════════════════════════════════════════════════
```

3. **Output the initial prompt** to start the work:

```
{final_prompt}
```

4. **Begin working** on the task immediately.
```
