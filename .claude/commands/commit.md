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

### Types
- feat: 새로운 에이전트, 규칙, 스킬, 커맨드 추가
- fix: 기존 정의 오류 수정
- docs: CLAUDE.md, ARCHITECTURE-INDEX.md 등 문서 변경
- refactor: 기존 에이전트/규칙/스킬 구조 개선
- chore: 설정, 빌드, 기타 잡무

### Scopes (this project)
- agents: .claude/agents/ 변경
- rules: .claude/rules/ 변경
- skills: .claude/skills/ 변경
- commands: .claude/commands/ 변경
- orchestration: 오케스트레이션 관련 변경
- docs: CLAUDE.md, ARCHITECTURE-INDEX.md, ADR 등

If changes span multiple scopes, omit the scope or use the most prominent one.

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
