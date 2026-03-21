# Product Stow Distribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** demiurge의 skills/commands/agents를 `product/` 디렉토리로 통합하고 GNU Stow로 `~/.claude/`에 심링크 배포한다.

**Architecture:** `product/.claude/`에 전역 배포 대상 원본을 모으고, `stow -t ~ product`으로 `~/.claude/`에 심링크를 생성. `.claude/`에는 프로젝트 전용 설정만 유지.

**Tech Stack:** GNU Stow, just (task runner), bash

**Spec:** `docs/superpowers/specs/2026-03-21-product-stow-distribution-design.md`

---

## File Map

| 파일 | 작업 | 설명 |
|------|------|------|
| `product/.claude/skills/` | Create | 31개 스킬 원본 디렉토리 |
| `product/.claude/commands/` | Create | 5개 커맨드 원본 |
| `product/.claude/agents/` | Create | 20개 에이전트 원본 |
| `.claude/skills/` | Delete | product로 이동 후 삭제 |
| `.claude/agents/` | Delete | product로 이동 후 삭제 |
| `.claude/commands/commit.md` | Delete | product로 이동 |
| `.claude/commands/rl.md` | Delete | product로 이동 |
| `.claude/commands/save_obsi.md` | Delete | product로 이동 |
| `.claude/commands/wrap.md` | Keep | 프로젝트 전용 |
| `justfile` | Create | 태스크 러너 |
| `bootstrap.sh` | Create | 최초 셋업 스크립트 |
| `.gitignore` | Modify | .DS_Store 제외 추가 |

---

### Task 1: 의존성 설치

**Files:** (없음 — 시스템 도구 설치)

- [ ] **Step 1: stow 설치**

```bash
brew install stow
```

Expected: `stow --version` 출력 확인

- [ ] **Step 2: just 설치**

```bash
brew install just
```

Expected: `just --version` 출력 확인

---

### Task 2: product/ 디렉토리 생성 + demiurge 스킬/에이전트/커맨드 이동

**Files:**
- Create: `product/.claude/skills/`, `product/.claude/commands/`, `product/.claude/agents/`
- Move: `.claude/skills/*` → `product/.claude/skills/`
- Move: `.claude/agents/*` → `product/.claude/agents/`
- Move: `.claude/commands/{commit.md,rl.md,save_obsi.md}` → `product/.claude/commands/`

- [ ] **Step 1: product 디렉토리 구조 생성**

```bash
mkdir -p product/.claude/{skills,commands,agents}
```

- [ ] **Step 2: 25개 스킬을 product로 이동 (git mv로 히스토리 보존)**

```bash
cd ~/lab/demiurge
for skill in .claude/skills/*/; do
    git mv "$skill" "product/.claude/skills/$(basename $skill)"
done
```

- [ ] **Step 3: 20개 에이전트를 product로 이동**

```bash
for agent in .claude/agents/*.md; do
    git mv "$agent" "product/.claude/agents/$(basename $agent)"
done
```

- [ ] **Step 4: 3개 커맨드를 product로 이동 (wrap.md 제외)**

```bash
git mv .claude/commands/commit.md product/.claude/commands/
git mv .claude/commands/rl.md product/.claude/commands/
git mv .claude/commands/save_obsi.md product/.claude/commands/
```

- [ ] **Step 5: 이동 결과 확인**

```bash
ls product/.claude/skills/ | wc -l   # Expected: 25
ls product/.claude/agents/ | wc -l   # Expected: 20
ls product/.claude/commands/          # Expected: commit.md, rl.md, save_obsi.md
ls .claude/commands/                  # Expected: wrap.md만 남음
```

- [ ] **Step 6: 커밋 (git mv가 이미 staging했으므로 add 불필요)**

```bash
git commit -m "refactor: .claude/ skills/agents/commands를 product/.claude/로 이동"
```

---

### Task 3: ~/.claude/ 최신본을 product/로 이전

**Files:**
- Copy: `~/.claude/skills/{concept-explainer,organize,qa,ralph-loop-guide,rl-verify,save-confluence}` → `product/.claude/skills/`
- Overwrite: `product/.claude/skills/deep-research/` (with ~/.claude version)
- Copy: `~/.claude/commands/{new_rl.md,tdd-lfg.md}` → `product/.claude/commands/`
- Overwrite: `product/.claude/commands/{rl.md,save_obsi.md}` (with ~/.claude version)

- [ ] **Step 1: 전역 전용 스킬 6개 복사**

```bash
cd ~/lab/demiurge
for skill in concept-explainer organize qa ralph-loop-guide rl-verify save-confluence; do
    cp -R ~/.claude/skills/$skill product/.claude/skills/
done
```

- [ ] **Step 2: deep-research를 전역 최신본으로 덮어쓰기**

```bash
rm -rf product/.claude/skills/deep-research
cp -R ~/.claude/skills/deep-research product/.claude/skills/
```

- [ ] **Step 3: 전역 전용 커맨드 2개 복사**

```bash
cp ~/.claude/commands/new_rl.md product/.claude/commands/
cp ~/.claude/commands/tdd-lfg.md product/.claude/commands/
```

- [ ] **Step 4: rl.md, save_obsi.md를 전역 최신본으로 덮어쓰기**

```bash
cp ~/.claude/commands/rl.md product/.claude/commands/rl.md
cp ~/.claude/commands/save_obsi.md product/.claude/commands/save_obsi.md
```

- [ ] **Step 5: 최종 카운트 확인**

```bash
ls product/.claude/skills/ | wc -l    # Expected: 31
ls product/.claude/commands/ | wc -l  # Expected: 5
ls product/.claude/agents/ | wc -l    # Expected: 20
```

- [ ] **Step 6: 커밋**

```bash
git add product/
git commit -m "feat: ~/.claude/ 전역 스킬/커맨드를 product/로 통합"
```

---

### Task 4: ~/.claude/ 정리 (stow 충돌 방지)

**Files:**
- Delete: `~/.claude/skills/{concept-explainer,deep-research,organize,qa,ralph-loop-guide,rl-verify,save-confluence}`
- Delete: `~/.claude/commands/{new_rl.md,rl.md,save_obsi.md,tdd-lfg.md}`
- Delete: `~/.claude/commands/.rl.md.swp`
- Keep: `~/.claude/skills/{vercel-*,web-design-guidelines}` (기존 심링크)

- [ ] **Step 1: 정리 전 백업 (안전망)**

```bash
mkdir -p /tmp/claude-backup
cp -R ~/.claude/skills/concept-explainer /tmp/claude-backup/
cp -R ~/.claude/skills/deep-research /tmp/claude-backup/
cp -R ~/.claude/skills/organize /tmp/claude-backup/
cp -R ~/.claude/skills/qa /tmp/claude-backup/
cp -R ~/.claude/skills/ralph-loop-guide /tmp/claude-backup/
cp -R ~/.claude/skills/rl-verify /tmp/claude-backup/
cp -R ~/.claude/skills/save-confluence /tmp/claude-backup/
cp ~/.claude/commands/new_rl.md /tmp/claude-backup/
cp ~/.claude/commands/rl.md /tmp/claude-backup/
cp ~/.claude/commands/save_obsi.md /tmp/claude-backup/
cp ~/.claude/commands/tdd-lfg.md /tmp/claude-backup/
echo "Backup at /tmp/claude-backup/"
```

- [ ] **Step 2: 스킬 디렉토리 7개 삭제**

```bash
rm -rf ~/.claude/skills/concept-explainer
rm -rf ~/.claude/skills/deep-research
rm -rf ~/.claude/skills/organize
rm -rf ~/.claude/skills/qa
rm -rf ~/.claude/skills/ralph-loop-guide
rm -rf ~/.claude/skills/rl-verify
rm -rf ~/.claude/skills/save-confluence
```

- [ ] **Step 3: 커맨드 파일 4개 + swap 파일 삭제**

```bash
rm ~/.claude/commands/new_rl.md
rm ~/.claude/commands/rl.md
rm ~/.claude/commands/save_obsi.md
rm ~/.claude/commands/tdd-lfg.md
rm -f ~/.claude/commands/.rl.md.swp
```

- [ ] **Step 4: 정리 결과 확인**

```bash
echo "=== ~/.claude/skills/ (심링크만 남아야 함) ==="
ls -la ~/.claude/skills/
# Expected: vercel-composition-patterns, vercel-react-best-practices,
#           vercel-react-native-skills, web-design-guidelines (모두 심링크)

echo "=== ~/.claude/commands/ (비어 있어야 함) ==="
ls -la ~/.claude/commands/
# Expected: 빈 디렉토리
```

---

### Task 5: stow 실행 + 검증

**Files:** (없음 — stow 심링크 생성)

- [ ] **Step 1: stow dry-run (충돌 사전 감지)**

```bash
cd ~/lab/demiurge
stow -n -v -t ~ product
```

Expected: `LINK: .claude/skills/ai-agent => ...` 같은 메시지 출력, `WARNING` 또는 `ERROR` 없음. 충돌 발견 시 Task 4로 돌아가 정리.

- [ ] **Step 2: stow 실행**

```bash
stow -v -t ~ product
```

Expected: dry-run과 동일한 메시지, 에러 없음

- [ ] **Step 3: 심링크 검증 — skills**

```bash
echo "=== Skills symlink check ==="
for d in ~/.claude/skills/*/; do
    name=$(basename "$d")
    if [ -L "${d%/}" ]; then
        target=$(readlink "${d%/}")
        echo "✅ $name → $target"
    else
        echo "❌ $name (NOT a symlink!)"
    fi
done
```

Expected: 31개 demiurge 심링크 + 4개 vercel 심링크, 모두 ✅

- [ ] **Step 4: 심링크 검증 — commands**

```bash
echo "=== Commands symlink check ==="
for f in ~/.claude/commands/*; do
    name=$(basename "$f")
    if [ -L "$f" ]; then
        target=$(readlink "$f")
        echo "✅ $name → $target"
    else
        echo "❌ $name (NOT a symlink!)"
    fi
done
```

Expected: 5개 모두 심링크

- [ ] **Step 5: 심링크 검증 — agents**

```bash
echo "=== Agents symlink check ==="
for f in ~/.claude/agents/*; do
    name=$(basename "$f")
    if [ -L "$f" ]; then
        echo "✅ $name"
    else
        echo "❌ $name (NOT a symlink!)"
    fi
done
```

Expected: 20개 모두 심링크

- [ ] **Step 6: broken symlink 검증**

```bash
find ~/.claude/skills ~/.claude/commands ~/.claude/agents -type l ! -exec test -e {} \; -print
```

Expected: 출력 없음 (broken symlink 없음)

---

### Task 6: justfile 작성

**Files:**
- Create: `justfile`

- [ ] **Step 1: justfile 작성**

```just
# Demiurge AI Harness — Task Runner

# 사용 가능한 명령 목록
default:
    @just --list

# 전역 심링크 생성/갱신
link:
    stow -v -R -t ~ product
    @echo "✅ product → ~/.claude linked"

# 전역 심링크 해제
unlink:
    stow -v -D -t ~ product
    @echo "🔓 symlinks removed"

# 심링크 상태 확인
status:
    @echo "=== Skills (symlinked) ==="
    @for d in ~/.claude/skills/*/; do \
        name=$$(basename "$$d"); \
        if [ -L "$${d%/}" ]; then \
            echo "  ✅ $$name"; \
        else \
            echo "  ⚠️  $$name (not from product)"; \
        fi; \
    done
    @echo ""
    @echo "=== Commands (symlinked) ==="
    @for f in ~/.claude/commands/*; do \
        name=$$(basename "$$f"); \
        if [ -L "$$f" ]; then \
            echo "  ✅ $$name"; \
        else \
            echo "  ⚠️  $$name (not from product)"; \
        fi; \
    done
    @echo ""
    @echo "=== Agents (symlinked) ==="
    @for f in ~/.claude/agents/*; do \
        name=$$(basename "$$f"); \
        if [ -L "$$f" ]; then \
            echo "  ✅ $$name"; \
        else \
            echo "  ⚠️  $$name (not from product)"; \
        fi; \
    done

# 새 스킬 생성 + 심링크
new-skill name:
    mkdir -p product/.claude/skills/{{name}}
    @printf '%s\n' '---' 'name: {{name}}' 'description: "TODO: 설명을 작성하세요"' '---' '' '# {{name}}' '' 'TODO: 스킬 내용을 작성하세요.' > product/.claude/skills/{{name}}/SKILL.md
    just link
    @echo "🆕 product/.claude/skills/{{name}}/SKILL.md created"

# 새 커맨드 생성 + 심링크
new-command name:
    @printf '%s\n' '---' 'description: "TODO: 설명을 작성하세요"' 'allowed-tools: Read, Grep, Glob, Bash' '---' '' 'TODO: 커맨드 내용을 작성하세요.' > product/.claude/commands/{{name}}.md
    just link
    @echo "🆕 product/.claude/commands/{{name}}.md created"
```

- [ ] **Step 2: just 동작 확인**

```bash
cd ~/lab/demiurge
just
```

Expected: 6개 커맨드 목록 출력 (default, link, unlink, status, new-skill, new-command)

- [ ] **Step 3: just status 확인**

```bash
just status
```

Expected: skills 35개 (31 product + 4 vercel), commands 5개, agents 20개 모두 ✅

- [ ] **Step 4: 커밋**

```bash
git add justfile
git commit -m "feat: justfile 태스크 러너 추가 (link, unlink, status, new-skill, new-command)"
```

---

### Task 7: bootstrap.sh 작성

**Files:**
- Create: `bootstrap.sh`

- [ ] **Step 1: bootstrap.sh 작성**

```bash
#!/bin/bash
set -e

echo "🚀 Demiurge AI Harness Setup"
echo ""

# Homebrew 확인
if ! command -v brew &>/dev/null; then
    echo "❌ Homebrew required: https://brew.sh"
    exit 1
fi

# 의존성 설치
for tool in stow just; do
    if ! command -v $tool &>/dev/null; then
        echo "📦 Installing $tool..."
        brew install $tool
    else
        echo "✅ $tool already installed ($(which $tool))"
    fi
done

echo ""

# 심링크 생성
echo "🔗 Linking product → ~/.claude..."
cd "$(dirname "$0")"
just link

echo ""
echo "🎉 Done! Run 'just' for available commands."
```

- [ ] **Step 2: 실행 권한 부여**

```bash
chmod +x bootstrap.sh
```

- [ ] **Step 3: 커밋**

```bash
git add bootstrap.sh
git commit -m "feat: bootstrap.sh 최초 셋업 스크립트 추가"
```

---

### Task 8: .gitignore 업데이트

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: .gitignore에 .DS_Store 추가**

`.gitignore`에 다음 추가 (없을 경우 파일 생성):

```
.DS_Store
**/.DS_Store
```

- [ ] **Step 2: 기존 .DS_Store 추적 제거 (있을 경우)**

```bash
git rm -r --cached '*.DS_Store' 2>/dev/null || true
```

- [ ] **Step 3: 커밋**

```bash
git add .gitignore
git commit -m "chore: .gitignore에 .DS_Store 제외 규칙 추가"
```

---

### Task 9: CLAUDE.md 업데이트

**Files:**
- Modify: `.claude/CLAUDE.md`

- [ ] **Step 1: Repository Structure 섹션 업데이트**

CLAUDE.md의 Repository Structure를 새 구조에 맞게 수정:

```markdown
## Repository Structure

- `product/.claude/skills/` — 31 skills (전역 배포, stow 대상)
- `product/.claude/agents/` — 20 architect + investigation agents (전역 배포, stow 대상)
- `product/.claude/commands/` — 5 commands (전역 배포, stow 대상)
- `.claude/rules/` — 8 governance rules (프로젝트 전용)
- `.claude/commands/wrap.md` — CLAUDE.md 동기화 (프로젝트 전용)
- `justfile` — 태스크 러너 (link, unlink, status, new-skill, new-command)
- `bootstrap.sh` — 최초 셋업 스크립트
```

- [ ] **Step 2: Skills 카운트 업데이트**

스킬 수를 25 → 31로, 전역 배포 경로를 `product/.claude/skills/`로 업데이트.

- [ ] **Step 3: Usage 섹션에 stow 사용법 추가**

```markdown
## Stow Distribution

demiurge의 skills/commands/agents는 GNU Stow를 통해 `~/.claude/`에 심링크로 배포됩니다.

\```bash
just link      # 심링크 생성/갱신
just unlink    # 심링크 해제
just status    # 심링크 상태 확인
\```
```

- [ ] **Step 4: 커밋**

```bash
git add .claude/CLAUDE.md
git commit -m "docs: CLAUDE.md를 product/ stow 구조에 맞게 업데이트"
```

---

### Task 10: 최종 통합 검증

**Files:** (없음 — 검증만)

- [ ] **Step 1: just link 재실행 (idempotent 확인)**

```bash
cd ~/lab/demiurge
just link
```

Expected: 에러 없이 완료

- [ ] **Step 2: just status 전체 확인**

```bash
just status
```

Expected: 모든 항목 ✅

- [ ] **Step 3: broken symlink 검사**

```bash
find ~/.claude/skills ~/.claude/commands ~/.claude/agents -type l ! -exec test -e {} \; -print
```

Expected: 출력 없음

- [ ] **Step 4: 전역 설정 무결성 확인**

```bash
# 이 파일들이 심링크가 아닌 실제 파일인지 확인
test -f ~/.claude/settings.json && ! test -L ~/.claude/settings.json && echo "✅ settings.json OK"
test -f ~/.claude/CLAUDE.md && ! test -L ~/.claude/CLAUDE.md && echo "✅ CLAUDE.md OK"
test -d ~/.claude/plugins && ! test -L ~/.claude/plugins && echo "✅ plugins/ OK"
```

Expected: 모두 ✅ (stow가 건드리지 않았음)

- [ ] **Step 5: unlink + relink 사이클 테스트**

```bash
just unlink
ls ~/.claude/skills/ | wc -l   # Expected: 4 (vercel만 남음)
just link
ls ~/.claude/skills/ | wc -l   # Expected: 35 (31 + 4 vercel)
```

- [ ] **Step 6: /tmp/claude-backup 정리**

```bash
rm -rf /tmp/claude-backup
echo "✅ Backup cleaned up"
```
