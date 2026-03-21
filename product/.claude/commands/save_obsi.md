---
description: 직전 대화 결과를 Obsidian vault에 마크다운 파일로 저장합니다.
allowed-tools: Bash, Write, Read, Glob
---

# Save to Obsidian Vault

직전 대화에서 출력된 결과를 관련된 파일명의 `.md` 파일로 Obsidian vault에 저장합니다.

**Usage:**
- `/save_obsi <child_path>` — default vault root(`~/den/Den`)에 저장
- `/save_obsi <vault_root>, <child_path>` — 지정된 vault root에 저장

```
Parse the user's input from: $ARGUMENTS

## Step 1: Parse Parameters

Arguments are comma-separated.

- If there is exactly 1 argument (no comma): treat it as <child_path>, use default vault root "~/den/Den"
- If there are 2 arguments (comma-separated): first = <vault_root>, second = <child_path>
- Trim whitespace from both values.
- Expand `~` to the user's home directory.

Construct the full save directory: <vault_root>/<child_path>

## Step 2: Determine File Name

Look at the conversation history BEFORE this command was invoked.
Analyze the most recent substantive output (the last assistant response before this command).

Generate a descriptive, concise file name based on the content:
- Use the main topic or subject as the file name
- Use lowercase with hyphens for spaces (kebab-case)
- Keep it under 60 characters
- Add `.md` extension
- Examples: `clean-architecture-overview.md`, `jwt-authentication-flow.md`, `order-aggregate-design.md`

## Step 3: Prepare Content

Take the most recent substantive assistant output and format it as a clean markdown file.

Add YAML front matter at the top (tags will be filled in after Step 4):

---
created: <current date in YYYY-MM-DD format>
source: claude-code
tags: []
---

Then include the full content of the last assistant response with the following formatting rules applied:

### 3-1. Table Formatting (CRITICAL)

Tables MUST be valid, well-formed markdown tables for Obsidian to render them correctly. Apply these rules:

1. **Every table MUST have a header separator row**: `| --- | --- |` immediately after the header row. If missing, add it.
2. **Column alignment**: Pad every cell with spaces so that `|` delimiters in each column are vertically aligned. This ensures Obsidian's live preview renders correctly.
3. **Pipe escaping**: If cell content contains a literal `|` character, escape it as `\|`.
4. **No trailing/leading whitespace issues**: Each row must start and end with `|`.
5. **Empty cells**: Use a single space ` ` inside empty cells, never leave them completely empty (`||`).

Example of a well-formed table:

| Name    | Status  | Count |
| ------- | ------- | ----- |
| Alpha   | Active  | 10    |
| Beta    | Pending | 5     |

6. **Nested content in cells**: If a cell contains inline code, bold, or links, preserve them but ensure the pipe alignment still holds.
7. **Wide tables**: If a table has many columns, still maintain alignment. Do not break a single table row across multiple lines.

### 3-2. Other Markdown Formatting

- Preserve all headings, code blocks, lists, bold, italic, links, and blockquotes as-is.
- Ensure code blocks use triple backticks with language identifiers when available.
- Ensure there is a blank line before and after headings, code blocks, tables, and blockquotes for proper Obsidian rendering.
- Horizontal rules: use `---` on its own line with blank lines before and after.

## Step 4: Suggest Save Location & Tags

Scan the vault root (from Step 1) for directories up to 2 levels deep:
  find <vault_root> -maxdepth 2 -type d

Compare the content topic against existing directory names to identify the best matching path.
Also analyze the content and suggest 3–6 relevant tags.

Present both suggestions in a **single AskUserQuestion**:

```
📁 저장 위치 제안
  추천: <vault_root>/<추천_경로> (이유: ...)
  후보: <다른_후보들> (없으면 생략)
  (새 경로 입력 가능)

🏷️ 태그 제안
  추천: tag1, tag2, tag3, ...
  (수정하려면 원하는 태그 입력)

[Enter] — 제안 그대로 사용
또는 아래 형식으로 수정:
  경로: <수정할_경로>
  태그: <수정할_태그_목록>
```

- If user presses Enter (no input): use the suggested path and tags as-is.
- If user provides input: parse `경로:` and `태그:` lines and apply them.
- Override the <full_save_directory> with the confirmed path.
- Replace `tags: []` in the prepared front matter with the confirmed tag list, formatted as a YAML list:
  tags: [tag1, tag2, tag3]

## Step 5: Ensure Directory Exists

Create the target directory if it doesn't exist:
  mkdir -p <full_save_directory>

## Step 6: Check Duplicate & Save File

BEFORE writing, check if a file with the same name already exists in the target directory.

Use Bash to check:
  ls "<full_save_directory>/<generated_filename>.md" 2>/dev/null

- If the file does NOT exist: save as-is.
- If the file ALREADY exists: append an incrementing numeric suffix to the base name.
  - Try `-2`, then `-3`, `-4`, ... until a non-existing name is found.
  - Example: `clean-architecture-overview.md` exists
    → try `clean-architecture-overview-2.md`
    → if that also exists, try `clean-architecture-overview-3.md`
    → and so on.

CRITICAL: NEVER overwrite an existing file. Always verify before writing.

## Step 7: Report

Report the result:

**Saved:** <filename>
**Path:** <full_file_path>
**Size:** <file size in human-readable format>
```
