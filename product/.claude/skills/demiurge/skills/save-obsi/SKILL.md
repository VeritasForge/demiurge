---
name: save-obsi
description: 직전 대화 결과를 Obsidian vault의 wiki/ 카테고리에 마크다운 파일로 저장합니다. vault 경로는 환경변수 OBSIDIAN_VAULT(미설정 시 ~/lab/second-brain)에서 읽습니다.
triggers:
  - save-obsi
  - save_obsi
  - obsidian에 저장
  - 옵시디언에 저장
  - wiki에 저장
  - second-brain에 저장
  - 세컨브레인에 저장
user_invocable: true
allowed-tools: Bash, Write, Read, Glob, AskUserQuestion
---

# Save to Obsidian Vault

직전 대화에서 출력된 결과를 wiki/ 해당 카테고리에 마크다운 파일로 저장합니다.

**Usage:**
- `/save-obsi` — 직전 대화 결과를 wiki/에 저장
- `/save-obsi <slug>` — 지정된 slug로 파일명 생성
- `/save-obsi <category>/<slug>` — 카테고리와 slug를 직접 지정

```
Parse the user's input from: $ARGUMENTS

## Step 1: Vault Root 결정 (환경변수 우선, 없으면 기본값)

Vault root는 하드코딩하지 않는다. Bash를 실행하여 환경변수에서 읽고, 없으면 기본값으로 폴백한다:

```bash
VAULT_ROOT="${OBSIDIAN_VAULT:-$HOME/lab/second-brain}"
if [ ! -d "$VAULT_ROOT" ]; then
  echo "ERROR: Obsidian vault를 찾을 수 없음 → $VAULT_ROOT"
  echo "→ ~/.claude/settings.json 의 env 블록에 OBSIDIAN_VAULT 를 설정하거나, 기본 경로에 vault를 두세요."
  exit 1
fi
echo "$VAULT_ROOT"
```

- 환경변수 `OBSIDIAN_VAULT`가 설정돼 있으면 그 값을 vault root로 사용.
- 없으면 기본값 `$HOME/lab/second-brain` 으로 폴백 (설정 없이도 동작).
- 이후 모든 `<vault_root>` 는 이 Bash로 해석한 값으로 치환한다.
- 참고: SKILL.md 본문 텍스트에 `$OBSIDIAN_VAULT`를 그냥 쓰면 확장되지 않으므로, 반드시 위처럼 Bash로 읽어야 한다.

## Step 2: Determine Category & File Name

Look at the conversation history BEFORE this command was invoked.
Analyze the most recent substantive output (the last assistant response before this command).

### Category 결정
- $ARGUMENTS에 category/slug 형태가 주어지면 그것을 사용
- category만 없으면 AskUserQuestion으로 사용자에게 확인:
  - 기존 카테고리: security, gen_ai, develop, develop/fe, develop/git, develop/database, develop/claude-code, develop/os, develop/python, develop/go, develop/k8s, develop/slack, develop/architecture, develop/performance, develop/interview-prep, ai-engineering, algorithm, career, research, mac-os
  - 새 카테고리 입력도 가능

### 파일명 결정
파일명 형식: <slug>.md

- $ARGUMENTS에 slug가 주어지면 그것을 사용
- 없으면 대화 내용에서 자동 생성:
  - Use the main topic or subject as the slug
  - Use lowercase with hyphens for spaces (kebab-case)
  - Keep slug under 50 characters

## Step 3: Prepare Content

Take the most recent substantive assistant output and format it as a clean markdown file.

Add YAML front matter at the top:

---
tags: [tag1, tag2]
created: <current date in YYYY-MM-DD format>
---

- 태그는 내용을 분석하여 3-6개 자동 제안. 사용자에게 확인.

Then include the full content of the last assistant response with the following formatting rules applied:

### 3-1. Table Formatting (CRITICAL)

Tables MUST be valid, well-formed markdown tables for Obsidian to render them correctly:

1. Every table MUST have a header separator row: | --- | --- | immediately after the header row.
2. Column alignment: Pad every cell with spaces so | delimiters are vertically aligned.
3. Pipe escaping: If cell content contains a literal | character, escape it as \|.
4. No trailing/leading whitespace issues: Each row must start and end with |.
5. Empty cells: Use a single space inside empty cells, never leave them completely empty (||).
6. Nested content in cells: If a cell contains inline code, bold, or links, preserve them.
7. Wide tables: Maintain alignment. Do not break a single table row across multiple lines.

### 3-2. Other Markdown Formatting

- Preserve all headings, code blocks, lists, bold, italic, links, and blockquotes as-is.
- Ensure code blocks use triple backticks with language identifiers when available.
- Ensure there is a blank line before and after headings, code blocks, tables, and blockquotes.
- Horizontal rules: use --- on its own line with blank lines before and after.

## Step 4: Ensure Directory Exists

Create the target directory if it doesn't exist:
  mkdir -p <vault_root>/wiki/<category>

## Step 5: Check Duplicate & Save File

저장 경로: <vault_root>/wiki/<category>/<slug>.md

BEFORE writing, check if a file with the same name already exists.

Use Bash to check:
  ls "<vault_root>/wiki/<category>/<slug>.md" 2>/dev/null

- If the file does NOT exist: save as-is.
- If the file ALREADY exists: append an incrementing numeric suffix to the base name.
  - Try -2, then -3, -4, ... until a non-existing name is found.

CRITICAL: NEVER overwrite an existing file. Always verify before writing.

## Step 6: Update index.md & log.md

### index.md 갱신
- <vault_root>/index.md를 읽는다
- 해당 카테고리 섹션에 새 항목 추가: - [[<slug>]] — <한줄 설명>
- 카테고리 섹션이 없으면 새로 생성
- 알파벳순 정렬 유지

### log.md 갱신
- <vault_root>/log.md를 읽는다
- 맨 위에 새 항목 추가 (헤더 다음):
  ## [YYYY-MM-DD] create | <제목>
  - created: [[<slug>]]

## Step 7: Report

Report the result:

**Saved:** <slug>.md
**Path:** wiki/<category>/<slug>.md
**Size:** <file size in human-readable format>
```
