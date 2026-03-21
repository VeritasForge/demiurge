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

Add YAML front matter at the top:

---
created: <current date in YYYY-MM-DD format>
source: claude-code
tags: []
---

Then include the full content of the last assistant response, preserving all markdown formatting.

## Step 4: Ensure Directory Exists

Create the target directory if it doesn't exist:
  mkdir -p <full_save_directory>

## Step 5: Check Duplicate & Save File

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

## Step 6: Report

Report the result:

**Saved:** <filename>
**Path:** <full_file_path>
**Size:** <file size in human-readable format>
```
