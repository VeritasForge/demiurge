# Demiurge Product Distribution via GNU Stow

> Demiurge AI Harness의 skills, commands, agents를 GNU Stow를 통해 전역(`~/.claude/`)으로 배포하는 설계

## Problem

현재 demiurge에서 만든 스킬/커맨드가 두 곳에 파편화되어 있다:

- `~/lab/demiurge/.claude/` — 프로젝트에서 직접 생성한 25개 스킬, 20개 에이전트, 4개 커맨드
- `~/.claude/` — 전역에서 사용하려고 복사/재생성한 7개 스킬, 4개 커맨드

양쪽에 같은 이름의 스킬이 존재하고(deep-research, rl, save_obsi), 어느 쪽이 최신인지 불명확하다. 수정할 때마다 양쪽을 동기화해야 하는 부담이 있다.

## Decision

**GNU Stow + `product/` 디렉토리 패턴**을 채택한다.

- `product/.claude/`에 전역 배포 대상(skills, commands, agents)의 **원본**을 관리
- `stow -t ~ product`로 `~/.claude/`에 심링크를 생성
- `.claude/`에는 프로젝트 전용 설정만 유지 (CLAUDE.md, rules, wrap 커맨드)

### 선택 근거

| 검토한 방식 | 채택 여부 | 이유 |
|-------------|-----------|------|
| Plugin Marketplace | 불채택 | 네임스페이스(`/demiurge:skill`) 강제, 개인 전용이므로 과잉 |
| 수동 심링크 | 불채택 | 50+ 항목 수동 관리, 새 스킬 추가 시 누락 위험 |
| 셸 스크립트 | 불채택 | Stow가 동일 기능을 더 안전하게 제공 |
| **GNU Stow** | **채택** | dotfiles 업계 표준, 충돌 감지, 깔끔한 해제, 1단 심링크 |
| GNU Stow + `.stow-local-ignore` | 불채택 | `.claude/` 전체를 대상으로 하면 제외 규칙이 복잡 |
| **GNU Stow + `product/` 분리** | **채택** | 전역/프로젝트 전용 경계가 명확, ignore 불필요 |

### 기존 플러그인 참고

superpowers, compound-engineering, ouroboros 모두:
- `skills/`, `commands/`, `agents/` 만 배포 (rules 없음)
- CLAUDE.md는 개발자용 가이드 (전역 배포 대상 아님)

## Architecture

### Directory Structure

```
~/lab/demiurge/
│
├── product/                              # 전역 배포 제품 (stow 대상)
│   └── .claude/
│       ├── skills/                       # 31개 스킬 원본
│       │   ├── ai-agent/                 # from demiurge
│       │   ├── ai-safety/               # from demiurge
│       │   ├── api-design/              # from demiurge
│       │   ├── application-architecture/ # from demiurge
│       │   ├── architect-orchestration/  # from demiurge
│       │   ├── business/                # from demiurge
│       │   ├── cloud-native/            # from demiurge
│       │   ├── concept-explainer/       # from ~/.claude (전역 전용)
│       │   ├── concurrency-patterns/    # from demiurge
│       │   ├── data-architecture/       # from demiurge
│       │   ├── deep-research/           # from ~/.claude (최신본)
│       │   ├── domain-driven-design/    # from demiurge
│       │   ├── eda/                     # from demiurge
│       │   ├── healthcare-informatics/  # from demiurge
│       │   ├── integration/             # from demiurge
│       │   ├── investigation-orchestration/ # from demiurge
│       │   ├── job-analysis/            # from demiurge
│       │   ├── llm-gateway/             # from demiurge
│       │   ├── ml-platform/             # from demiurge
│       │   ├── organize/                # from ~/.claude (전역 전용)
│       │   ├── prompt-engineering/      # from demiurge
│       │   ├── qa/                      # from ~/.claude (전역 전용)
│       │   ├── rag-architecture/        # from demiurge
│       │   ├── ralph-loop-guide/        # from ~/.claude (전역 전용)
│       │   ├── release-handoff/         # from demiurge
│       │   ├── rl-verify/              # from ~/.claude (전역 전용)
│       │   ├── save-confluence/         # from ~/.claude (전역 전용)
│       │   ├── security/               # from demiurge
│       │   ├── solution-architecture/   # from demiurge
│       │   ├── sre/                    # from demiurge
│       │   └── testing-architecture/    # from demiurge
│       ├── commands/                     # 5개 커맨드 원본
│       │   ├── commit.md
│       │   ├── new_rl.md
│       │   ├── rl.md
│       │   ├── save_obsi.md
│       │   └── tdd-lfg.md
│       └── agents/                      # 20개 에이전트 원본
│           ├── ai-safety-architect.md
│           ├── application-architect.md
│           ├── cloud-native-architect.md
│           ├── code-investigator.md
│           ├── concurrency-architect.md
│           ├── counter-reviewer.md
│           ├── data-architect.md
│           ├── domain-architect.md
│           ├── eda-specialist.md
│           ├── healthcare-informatics-architect.md
│           ├── history-investigator.md
│           ├── integration-architect.md
│           ├── llm-architect.md
│           ├── log-investigator.md
│           ├── ml-platform-architect.md
│           ├── rag-architect.md
│           ├── release-investigator.md
│           ├── security-architect.md
│           ├── solution-architect.md
│           └── sre-architect.md
│
├── .claude/                              # demiurge 개발 전용
│   ├── CLAUDE.md                         # 이 repo 개발 가이드
│   ├── rules/                            # 8개 코드 규칙 (프로젝트 전용)
│   │   ├── api-design.md
│   │   ├── architect-review.md
│   │   ├── architecture-principles.md
│   │   ├── cloud-native.md
│   │   ├── ddd-patterns.md
│   │   ├── healthcare-compliance.md
│   │   ├── messaging-patterns.md
│   │   └── security-requirements.md
│   └── commands/
│       └── wrap.md                       # CLAUDE.md 동기화 (프로젝트 전용)
│
├── justfile                              # 태스크 러너
├── bootstrap.sh                          # 최초 셋업 스크립트
└── README.md
```

### Stow Mapping

```
stow -t ~ product 실행 시:

product/.claude/skills/X/     →  ~/.claude/skills/X       (symlink)
product/.claude/commands/X.md →  ~/.claude/commands/X.md   (symlink)
product/.claude/agents/X.md   →  ~/.claude/agents/X.md     (symlink)
```

### Scope Boundary

| 항목 | 위치 | 배포 범위 |
|------|------|-----------|
| Skills (31) | `product/.claude/skills/` | 전역 (stow) |
| Commands (5) | `product/.claude/commands/` | 전역 (stow) |
| Agents (20) | `product/.claude/agents/` | 전역 (stow) |
| Rules (8) | `.claude/rules/` | 프로젝트 전용 |
| CLAUDE.md | `.claude/CLAUDE.md` | 프로젝트 전용 |
| wrap 커맨드 | `.claude/commands/wrap.md` | 프로젝트 전용 |

## Migration Plan

### Phase 1: product/ 디렉토리 생성

```bash
mkdir -p product/.claude/{skills,commands,agents}
```

### Phase 2: demiurge/.claude/ → product/ 이동

프로젝트에서 만든 원본을 product/로 이동 (git mv로 히스토리 보존):

- 25개 스킬: `.claude/skills/*` → `product/.claude/skills/`
- 20개 에이전트: `.claude/agents/*` → `product/.claude/agents/`
- 3개 커맨드 (commit, rl, save_obsi): `.claude/commands/` → `product/.claude/commands/`

### Phase 3: ~/.claude/ → product/ 이전 (최신본 우선)

전역에만 있거나 전역이 최신인 파일을 product/로 복사:

**스킬 (전역에만 있는 6개):**
- concept-explainer, organize, qa, ralph-loop-guide, rl-verify, save-confluence

**스킬 (양쪽 존재, ~/.claude 최신 1개):**
- deep-research — ~/.claude 버전으로 덮어쓰기

**커맨드 (전역에만 있는 2개):**
- new_rl.md, tdd-lfg.md

**커맨드 (양쪽 존재, ~/.claude 최신 2개):**
- rl.md, save_obsi.md — ~/.claude 버전으로 덮어쓰기

### Phase 4: ~/.claude/ 정리

stow 충돌 방지를 위해 기존 실제 파일 삭제:

**스킬 디렉토리 삭제 (7개 — product에 이전 완료):**
- concept-explainer, deep-research, organize, qa, ralph-loop-guide, rl-verify, save-confluence

**커맨드 파일 삭제 (4개 — product에 이전 완료):**
- new_rl.md, rl.md, save_obsi.md, tdd-lfg.md

**기타:**
- `.rl.md.swp` 삭제 (vim swap 파일)

**유지 (건드리지 않음):**
- vercel-composition-patterns, vercel-react-best-practices, vercel-react-native-skills, web-design-guidelines (기존 심링크 4개, demiurge 제품 아님)
- `~/.claude/CLAUDE.md` (사용자 전역 설정, stow 범위 밖)
- `~/.claude/settings.json`, `plugins/`, `mcp.json` 등 기존 설정

**참고:** `~/.claude/agents/` 디렉토리는 현재 존재하지 않음. stow가 Phase 5에서 자동 생성함.

### Phase 5: stow 실행

```bash
cd ~/lab/demiurge
stow -v -t ~ product
```

### Phase 6: 검증

- 모든 심링크가 정상 대상을 가리키는지 확인
- Claude Code에서 `/deep-research`, `/commit`, `/save_obsi` 호출 테스트
- `just status`로 심링크 상태 확인

## Tooling

### Dependencies

| 도구 | 용도 | 설치 |
|------|------|------|
| GNU Stow | 심링크 관리 | `brew install stow` |
| just | 태스크 러너 | `brew install just` |

### bootstrap.sh

최초 클론 시 1회 실행하는 셋업 스크립트:

1. Homebrew 존재 확인
2. stow, just 설치 (없을 때만)
3. `just link` 실행
4. 완료 메시지 출력

### justfile

| 커맨드 | 설명 |
|--------|------|
| `just` | 사용 가능한 명령 목록 |
| `just link` | `stow -v -R -t ~ product` 실행 |
| `just unlink` | `stow -v -D -t ~ product` 실행 |
| `just status` | 심링크 상태 확인 (skills, commands, agents) |
| `just new-skill <name>` | 스킬 디렉토리 + SKILL.md 템플릿 생성 + 자동 link |
| `just new-command <name>` | 커맨드 파일 템플릿 생성 + 자동 link |

## Daily Workflows

### 스킬 수정

```bash
# product/.claude/skills/deep-research/SKILL.md 편집
# → ~/.claude/skills/deep-research 는 심링크이므로 즉시 반영
# → git commit (demiurge repo에서 버전 관리)
```

### 새 스킬 추가

```bash
just new-skill my-new-skill
# → product/.claude/skills/my-new-skill/SKILL.md 생성
# → stow -R 자동 실행
# → git commit
```

### 스킬 삭제

```bash
just unlink
rm -rf product/.claude/skills/old-skill/
just link
git commit
```

### 다른 머신에서 클론

```bash
git clone <repo-url> ~/lab/demiurge
cd ~/lab/demiurge
./bootstrap.sh    # stow + just 설치 + 심링크 생성
```

## Constraints

- macOS 전용 (Homebrew 의존)
- 개인 사용만 고려 (다중 사용자 배포 불필요)
- `~/.claude/` 내 기존 vercel-* 심링크와 공존해야 함
- `~/.claude/settings.json`, `plugins/`, `mcp.json`, `CLAUDE.md` 등은 절대 건드리지 않음
- `product/` 하위에 `.DS_Store` 파일이 포함되지 않도록 `.gitignore`에 추가 필요
- 롤백 방법: `just unlink`로 모든 심링크를 즉시 제거 가능

## Testing

- [ ] stow 실행 후 `~/.claude/skills/` 내 모든 항목이 심링크인지 확인
- [ ] stow 실행 후 `~/.claude/commands/` 내 모든 항목이 심링크인지 확인
- [ ] stow 실행 후 `~/.claude/agents/` 내 모든 항목이 심링크인지 확인
- [ ] 심링크 대상이 실제 존재하는 파일을 가리키는지 확인
- [ ] Claude Code 새 세션에서 `/deep-research` 호출 가능한지 확인
- [ ] Claude Code 새 세션에서 `/commit` 호출 가능한지 확인
- [ ] `just unlink` 후 심링크가 모두 제거되는지 확인
- [ ] `just link` 재실행 후 심링크가 복원되는지 확인
- [ ] vercel-* 심링크가 stow 작업에 영향 받지 않는지 확인
