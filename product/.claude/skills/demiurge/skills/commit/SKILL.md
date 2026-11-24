---
name: commit
description: 변경사항을 git에 커밋하고 원격으로 푸시할 때 사용. /commit으로 직접 호출하거나 메시지 인자(/commit "msg")를 받음. Conventional Commits 형식으로 메시지 자동 생성.
allowed-tools: Bash, Read, Grep, Glob
argument-hint: "[commit message]"
model: claude-haiku-4-5
---

# Commit & Push Changes

변경사항을 커밋하고 원격 저장소로 푸시합니다.

**Usage:** `/commit` 또는 `/commit <message>`

```
Parse the user's input from: $ARGUMENTS

If the user provided a custom commit message, use it as the commit subject line.
Otherwise, analyze the changes and generate an appropriate message.

Follow these steps in order:

## Step 1: Check Status

Run the following commands in parallel:
- `git status` (never use -uall flag)
- `git diff HEAD` (or `git diff --cached` if no commits exist yet)
- `git log --oneline -5` (to follow existing commit style, skip if no commits yet)

If there are no changes (working tree clean, nothing staged), report:
  "변경사항이 없습니다. Working tree is clean."
and stop.

## Step 2: Generate Commit Message

Follow Conventional Commits format:

<type>(<scope>): <subject>

[optional body]

Co-Authored-By: Claude <noreply@anthropic.com>

### Types and scope
- type: feat | fix | docs | refactor | chore
- scope: the module, directory, or skill name where the change is concentrated. Follow the scopes this repo already uses in `git log --oneline -20` first. If changes span multiple areas, omit the scope.

## Step 3: Stage & Commit

Stage specific changed files by name (avoid `git add .` or `git add -A`).
Do NOT stage files that may contain secrets (.env, credentials, keys).

Use HEREDOC format for the commit message:

git commit -m "$(cat <<'EOF'
<type>(<scope>): <subject>

<body if needed>

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

## Step 4: Push

Push to remote:
- If the branch has an upstream: `git push`
- If no upstream yet: `git push -u origin <current-branch>`

If push fails due to conflict, report the error and suggest:
  git pull --rebase && git push

## Step 5: Report

Report the result:

**Commit:** <commit message subject>
**Branch:** <branch name>
**Files Changed:** <count> files (+<additions>, -<deletions>)
**Remote:** pushed to origin/<branch>
```
