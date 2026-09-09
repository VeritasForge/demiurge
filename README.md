# Demiurge

**Demiurge Harness**

> Claude Code·Codex용 개인 하니스 · GNU Stow 기반 공동 배포 · 사용 통계 CLI

---

## 목차

- [이름의 의미](#이름의-의미)
- [철학](#철학)
- [구성 요소 (한눈에)](#구성-요소-한눈에)
- [외부 Plugin 생태계](#외부-plugin-생태계)
- [Quick Start](#quick-start)
- [Codex 전역 지침](#codex-전역-지침)
- [사용법](#사용법)
- [사용 통계 (`demi` CLI)](#사용-통계-demi-cli)
- [구조](#구조)
- [확장](#확장)
- [라이선스](#라이선스)

## 이름의 의미

플라톤의 *티마이오스*에서 **데미우르고스**(δημιουργός)는 영원한 형상(Forms)을 응시하며 혼돈의 질료를 질서 있는 우주로 빚어내는 신적 장인이다. 무에서 창조하는 신이 아니라, 이미 있는 것을 목적에 맞게 *형상화*하는 존재다.

이 프로젝트는 그 이름을 의도적으로 빌려왔다. Claude Code는 강력한 원재료다. **Demiurge**는 이 원재료를 목적에 맞게 형상화하는 메타-설정(meta-configuration)이다. 신화의 데미우르고스가 혼돈에서 코스모스를 빚듯, 이 프로젝트는 빈 캔버스 상태의 Claude Code를 검증·자율실행·문서화 워크플로우가 짜인 작업 환경으로 변환한다.

그러나 오늘날 "원재료"는 Claude Code 하나만으로 끝나지 않는다. 데미우르고스가 형상화하는 질료는 이제 세 층이다. 첫째는 Claude Code 런타임 자체이고, 둘째는 외부 plugin 생태계(`compound-engineering`, `superpowers`, `ouroboros`, `understand-anything` 등)이며, 셋째는 외부 지식(공식 문서와 1차 출처)이다. Demiurge는 이 셋을 하나의 호출 규칙 아래로 끌어와, 자체 구현과 plugin 위임의 경계를 명문화한다.

## 철학

Demiurge는 하나의 확신 위에 세워졌다: **올바른 지식 구조와 거버넌스가 Claude Code를 소프트웨어 엔지니어링에서 전지전능하게 만들 수 있다.**

이 저장소의 핵심은 규칙, 스킬, 외부 plugin 호출 매핑이다. 여기에 배포·검증 스크립트와 사용 통계 CLI가 함께 있다. 올바른 패턴과 원칙을 어떤 plugin·skill에 어떻게 위임할지가 핵심 설계 결정이다.

Claude용 자산은 `product/.claude/`, Codex용 지침은 `product/.codex/`에 독립적으로 관리한다. 아래 스킬·플러그인 구성은 Claude용이며, Codex는 [전역 지침](#codex-전역-지침)과 현재 설치된 Codex 스킬을 사용한다.

이 확신은 네 가지 운영 원칙으로 구현된다:

- **수렴할 때까지 검증** — `rl-verify`가 여러 관점의 검증자를 붙여 발견마다 판정 라벨을 매기고, 같은 판정이 연속으로 나올 때까지 반복한다. 확정 직전 발견은 별도 반박 검증자가 근거를 다시 읽어 뒤집을 수 있는지 확인한다.
- **자동 거버넌스** — `paths` frontmatter rule이 파일 경로별 작성 규칙을 자동 적용한다 (`skills.md`, `agents.md`, 프로젝트 로컬 `stow-deployment.md`). 스킬 파일을 열면 그 규칙이 함께 로드된다.
- **Plugin 생태계 wrapping** — 검증된 외부 plugin을 자체 구현으로 대체하지 않고, `CLAUDE.md` 호출 매핑과 skill chain으로 통합한다. 자체 구현과 위임의 경계는 [외부 Plugin 생태계](#외부-plugin-생태계)에 명문화되어 있다.
- **사용 데이터 자가 진단** — `demi` CLI가 자산을 `active`/`live`/`dead` 3등급으로 추적하고, 의존성 그래프로 false positive를 걸러낸다. 메타-설정이 자기 사용을 측정하고, 그 측정으로 자기를 정리한다.

## 구성 요소 (한눈에)

| 컴포넌트 | 개수 | 위치 / 설명 |
|---------|------|------------|
| **Skills** | 20 | Workflow · Utility · Career · Business (`product/.claude/skills/demiurge/skills/`) |
| **Rules** | 3 | 전역 2 (`skills.md`, `agents.md`, `paths` frontmatter 지원) + 프로젝트 로컬 1 (`stow-deployment.md`) |
| **Commands** | 1 | 프로젝트 로컬 `wrap.md` (전역 `/commit`은 `skills/`로 마이그레이션됨) |
| **Codex 지침** | 3 | `AGENTS.md` + 설명·질문·문서 참조 + 계획·검증·배포 참조 (`product/.codex/`) |
| **CLI Tools** | 1 | `git cleanup-worktrees` (`bin/.local/bin/` → `~/.local/bin/`) |
| **Stats CLI** | `demi` | `scripts/demi/` — 플러그인·스킬·에이전트 사용 통계 (uv packaged Python) |
| **External Plugins** | 30 활성 | `~/.claude/plugins/installed_plugins.json`이 관리하고 `settings.json`의 `enabledPlugins`가 켜고 끈다. `CLAUDE.md` 호출 매핑으로 통합하며, demiurge가 실제로 chain하는 것은 그중 일부다. [외부 Plugin 생태계](#외부-plugin-생태계) 참조. |

> 카운트 출처: `ls product/.claude/skills/demiurge/skills`, `ls product/.claude/rules` 직접 측정 + `~/.claude/plugins/installed_plugins.json`. 자동 검증은 `/wrap --check` 또는 `just stats`로 확인.

## 외부 Plugin 생태계

Demiurge는 자체 구현보다 **검증된 외부 plugin을 wrapping**한다. `~/.claude/plugins/installed_plugins.json`에 설치된 plugin을 `CLAUDE.md` "Skills/Agents 호출 매핑" 절·skill chain으로 통합한다.

> 아래 목록은 *현재 사용자 머신 기준*(시간이 지나면 변동). 정확한 인벤토리는 `demi plugin-stats inventory`로 조회.

### 카테고리별 plugin

| 카테고리 | Plugin | demiurge에서의 역할 |
|---------|--------|-------------------|
| 반론·단순화 관점 | `ouroboros` | `rl-verify`가 `ouroboros_lateral_think` 도구로 contrarian·simplifier 페르소나 호출 |
| 문서·코드 리뷰 | `compound-engineering` | `ce-doc-review` · `ce-code-review` · `ce-debug` · `ce-compound` |
| 협업·계획 | `superpowers` | `brainstorming` · `writing-plans` · `subagent-driven-development` · `test-driven-development` |
| 코드베이스 이해 | `understand-anything` | 지식그래프 생성·질의 (`.ua/` 있는 레포에서 탐색 우선 경로) |
| 보조 코딩 | `codex` | 다른 모델 계열로 재검토·구조 위임 (`/codex:rescue`) |
| 워크스페이스 | `notion` · `atlassian` | 문서·이슈 추적 |
| UI 설계 | `frontend-design` · `vercel` | 비주얼 디자인 품질, React/Next.js 기준 |

### 통합 패턴 — 단계별 수렴

외부 plugin 호출은 `CLAUDE.md` "Skills/Agents 호출 매핑" 절에서 *언제 어떤 plugin을 호출할지* 명문화돼 있다 (호출 매핑 = 거버넌스).

```
[판단 지점] → deep-research → rl-verify ──┬─ contrarian/simplifier (ouroboros)
              (1차 출처 조사)  (수렴 검증)  ├─ 도메인 검증 관점 (compound 리뷰어 페르소나)
                                           └─ 판정자 → 안정 카운터 → 수렴 시 종료
```

### 자체 구현 vs Plugin 위임 경계

| 항목 | demiurge 자체 | plugin 위임 |
|------|-------------|------------|
| 수렴 검증 오케스트레이션 | `rl-verify` (판정자·반박 검증자 페르소나 내장) | 검증 관점 일부를 `ouroboros`·`compound-engineering`에 위임 |
| 리뷰 엔진 합성 | `review-ensemble` (여러 리뷰 엔진 병렬 실행 후 병합) | 각 엔진이 `code-review`·`compound-engineering`·`codex` |
| 자율 완주 | `autopilot` (모드 판별 + 결정 로그 + DIGEST) | — |
| 심층 조사 | `deep-research` (3단계 프로토콜) | 웹 조사 도구는 런타임 기본 제공 |
| 개별 리뷰·계획·디버깅 | — | `compound-engineering` · `superpowers` |
| 교훈 누적 | — | `compound-engineering:ce-compound` |

근거: `product/.claude/CLAUDE.md` "Skills/Agents 호출 규칙" 절.

## Quick Start

```bash
git clone <repo> ~/lab/demiurge
cd ~/lab/demiurge
./bootstrap.sh          # stow/just/jq 설치, ~/.claude/·~/.codex/·~/.local/bin/ 공동 배포 + Claude 상태줄 설정
```

> **전제 조건:** macOS + Homebrew. fish 사용자는 `bootstrap.sh`가 `fish_add_path -U`로 `~/.local/bin`을 자동 등록.

기존 `~/.codex/AGENTS.md`가 있으면 먼저 [Codex 최초 전환](#codex-최초-전환)을 수행한다. 설치기는 기존 지침을 자동 병합·이동·덮어쓰지 않는다. Codex CLI·플러그인의 설치와 로그인은 이 배포에 포함하지 않는다.

설치 후 Claude Code에서:

```text
/demiurge:deep-research <주제>     # 3단계 심층 조사
/demiurge:rl-verify <대상>         # 수렴할 때까지 다관점 검증
/demiurge:autopilot <plan.md>      # 자율주행 (사람 검토 사이클 포함)
```

> 스킬은 `demiurge` 플러그인 네임스페이스로 로드되므로 접두어가 붙는다. 목록 확인은 `/plugin` 또는 `just stats`.

## Codex 전역 지침

`product/.codex/AGENTS.md`는 새 Codex 세션에서 읽을 개인 전역 지침이다. 한국어 응답·리뷰,
근거 확인, 최소 변경, 완료조건과 검증, 설치된 스킬의 선택 기준을 담는다.
`demiurge/communication.md`와 `engineering.md`는 작업 종류에 맞춰 읽는 상세 참조다.
조직·프로젝트 전용 규칙이나 개인 절대 경로는 포함하지 않는다. 코드 탐색은 각 저장소의
지침을 따르며, 제공되는 인덱스의 최신성을 확인하고 실제 소스와 대조한다.

이 배포는 Claude 스킬을 Codex에 설치하지 않는다. Superpowers·Vercel 관련 스킬·OpenAI
도구는 현재 Codex에 실제로 제공되는 목록에서 찾아 사용한다. 캐시의 존재만으로 활성화나
호출 성공을 판단하지 않는다. `config.toml`, 인증 파일, 플러그인 캐시, 모델·권한·MCP 설정은
관리하지 않는다. Codex용 자체 스킬·에이전트와 통계 수집도 첫 버전의 범위 밖이다.

### Codex 최초 전환

기존 전역 지침이 일반 파일이면 Stow가 충돌로 중단한다. 먼저 내용을 다시 읽고
`product/.codex/AGENTS.md`와 상세 참조에 필요한 일반 원칙·예외가 반영됐는지 대조한다.
조직·프로젝트 전용 규칙과 개인 절대 경로는 배포 원본에 합치지 않는다. 유지해야 하는
저장소 전용 규칙은 사용자가 승인한 범위에서 해당 저장소의 `AGENTS.md`로 분리하고,
이관하지 않는 항목도 전환 전에 확인한다. 다른 곳을 가리키는 심볼릭 링크나 디렉터리는 자동 이관하지 않는다.

반영·분리·제외할 항목을 검토한 사용자만 다음을 실행한다. 기존 원문은 고유 디렉터리에
백업해 보존하고 이름 충돌을 피한다.

```bash
# Demiurge 저장소 루트에서 실행. 원문 보존을 먼저 검토할 것.
if [ -f "$HOME/.codex/AGENTS.md" ] && [ ! -L "$HOME/.codex/AGENTS.md" ]; then
    codex_backup_dir=$(mktemp -d "$HOME/.codex/agents-before-demiurge-$(date +%Y%m%d-%H%M%S).XXXXXX") &&
    mv "$HOME/.codex/AGENTS.md" "$codex_backup_dir/AGENTS.md" &&
    printf '기존 지침 백업: %s/AGENTS.md\n' "$codex_backup_dir"
fi
stow -n -v -R --no-folding -t "$HOME" product bin &&
just link &&
just status
```

`AGENTS.override.md`에 내용이 있으면 Codex는 그 파일을 전역 `AGENTS.md`보다 먼저 선택한다.
`CODEX_HOME`을 별도로 설정한 경우에도 기본 배포 위치와 실제 로딩 위치가 다를 수 있다.
`just status`는 이 조건들을 경고하지만 임의로 수정하지 않는다.
백업 이후 배포가 실패하면 출력한 백업 위치를 보존하고 아래 복구 절차를 따른다.

### 검증과 복구

`just status`는 Codex 원본 3개를 가리키는 링크가 정확한지 검사한다. 누락·일반 파일·
다른 대상·끊어진 링크는 실패 종료 코드로 알린다. override 경고는 링크 실패와 구분한다.
이 명령은 실제 모델에 지침이 전달됐는지를 검사하지 않는다.

배포 후 새 Codex 세션에서 '현재 로드한 전역 지침의 경로와 핵심 규칙을 설명해줘'라고
요청한다. 문서 작성·코드 검토 요청에서도 해당 상세 참조를 읽고 가용 스킬을 선택하는지
확인한다. 지원되는 CLI에서는 `codex debug prompt-input`으로 프롬프트 입력을 점검할 수도
있지만 출력에는 다른 개인 지침이 포함될 수 있으므로 원본을 외부에 공유하지 않는다.
권한 오류로 검사하지 못하면 **링크 검증 성공 / 실제 로딩 미검증**으로 구분한다.

전환을 되돌릴 때는 **Codex 원본이 존재하는 동안 `just unlink` → Codex 원본을 별도
보관 위치로 이동 → 백업한 기존 AGENTS.md 복원 → `just link`로 Claude·공용 CLI 재배포**
순서를 지킨다. `just unlink`는 두 하니스와 공용 CLI를 모두 해제한다.
Codex 원본이 여전히 product 안에 있으면 복원한 일반 AGENTS.md와 다시 충돌하므로,
원본을 배포 대상에서 제외한 후 나머지를 재배포해야 한다. 원본·기존 지침은 삭제하지 않는다.
Codex 배포를 되돌린 상태에서는 현재 `just status`의 Codex 검사가 실패하는 것이 예상 동작이다.

사용자 홈을 건드리지 않는 자동 검증:

```bash
python3 -m unittest discover -s scripts/tests -v
bash -n bootstrap.sh scripts/check-codex-links.sh
```

테스트는 실제 just·Stow를 사용하며 최초 배포·재배포·충돌·잘못된 링크·해제를 검증한다.
`link`·`unlink`·`status`는 `just deploy_target=/존재하는/절대경로 link`처럼 대상만 바꿀 수
있다. 기본은 사용자 홈이며 HOME을 재지정하지 않는다. 이 옵션은 세 명령에만 적용된다.
`bootstrap.sh`와 `setup-statusline`은 실제 사용자 홈에 적용되므로 임시 검증에 사용하지 않는다.

Codex 지침의 기준: [전역 지침과 우선순위](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[스킬 발견·실행](https://learn.chatgpt.com/docs/build-skills),
[공식 모범 사례](https://learn.chatgpt.com/guides/best-practices).

## 사용법

### 자율주행 (autopilot, MVP)

```text
/demiurge:autopilot <plan.md>   # 명시 호출 시에만 발동 — 평소엔 사람이 개입하는 흐름 유지
```

> autopilot은 자율 완주 후 `DIGEST.md`(사람용 1페이지 요약)를 자동 생성한다. 자세한 절차는 `product/.claude/skills/demiurge/skills/autopilot/README.md` 참조.

### 문서 동기화

```text
/wrap          # CLAUDE.md 분석 + 드리프트 감지 + 업데이트
/wrap --check  # 분석 + 드리프트 감지만 (변경 없음)
```

### Stow 관리

```bash
just status    # 심링크 상태 확인
just link      # ~/.claude·~/.codex·~/.local/bin 심링크 공동 생성/갱신
just unlink    # 두 하니스와 공용 CLI 심링크 공동 해제
```

> ⚠️ 파일 삭제·이동 시 순서: `just unlink → 소스 변경 → just link`. 역순으로 하면 `~/.claude/` 하위에 dangling symlink가 남는다. 자세한 근거는 `.claude/rules/stow-deployment.md` 참조.

### 상태줄 (Status Line)

`product/.claude/statusline.sh`가 Claude Code 하단 상태줄을 4줄로 렌더링한다:

1. 모델명 / Claude Code 버전 / reasoning effort / extended thinking 여부 / 실행 중인 agent 이름
2. 세션 누적 비용(USD) / 경과 시간
3. context window 사용률 progress bar (200K/1M 확장 컨텍스트 모델 모두 대응) + 남은 비율
4. Prompt Caching(KV Cache) 히트율

`./bootstrap.sh` 실행 시 `~/.claude/settings.json`의 `statusLine` 키에 자동 등록된다. 이미 설정되어 있으면 덮어쓸지 확인(`[y/N]`)하고, 비대화형 실행에서는 자동으로 건너뛴다. 수동으로 다시 적용하려면:

```bash
just setup-statusline
```

### CLI Tools

`bin/.local/bin/`이 `~/.local/bin/`으로 stow 배포되어, PATH 등록 후 어디서나 호출 가능.

| 명령 | 설명 |
|------|------|
| `git cleanup-worktrees [base-branch]` | git worktree 상태 분석 + interactive 정리 (`-h` 도움말, `-f` 강제 삭제) |

> `--help`는 git이 `man` 페이지로 가로채므로 `-h` 사용.

## 사용 통계 (`demi` CLI)

`scripts/demi/`는 Claude Code 개발환경(plugins / skills / agents / MCP / commands)의 **사용 통계 CLI**다. 순수 Python(stdlib + typer), 토큰 0원, 외부 네트워크 없음.

```bash
cd scripts/demi
uv sync
uv run demi plugin-stats report             # 전체 리포트 + 스냅샷 저장
uv run demi plugin-stats unused --grade dead  # dead 자산만 (정리 후보)
```

레포 루트 단축: `just stats` / `just stats-unused`.

### 3등급 분류

| 등급 | 조건 | 의미 |
|------|------|------|
| 🟢 **active** | 직접 호출 횟수 > 0 | 유지 |
| 🟡 **live** | 호출 0회 + 다른 자산 frontmatter에서 참조됨 | **제거 금지** (의존성 그래프) |
| 🔴 **dead** | 호출 0회 + 참조 없음 (고립) | 정리 후보 |

리포트는 `scripts/demi/reports/plugin-stats/latest.md`에 마크다운으로, 스냅샷은 `snapshots/YYYY-MM-DD.json`에 누적된다. 자세한 사용은 `scripts/demi/README.md` 참조.

## 구조

```
demiurge/
├── product/.claude/              # 전역 배포 (GNU Stow 경유 → ~/.claude/)
│   ├── skills/demiurge/          # skills-directory plugin (네임스페이스: demiurge)
│   │   ├── .claude-plugin/       # plugin.json — 마켓플레이스 등록 없이 로드
│   │   └── skills/      (20)     # /demiurge:<name>으로 호출
│   ├── rules/       (2)          # 전역 룰: skills.md, agents.md (paths frontmatter)
│   ├── statusline.sh             # Claude Code 상태줄(statusLine) 스크립트
│   └── CLAUDE.md                 # 응답 가이드라인 · TDD · 스킬 호출 규칙
├── product/.codex/               # 전역 배포 (GNU Stow 경유 → ~/.codex/)
│   ├── AGENTS.md                 # Codex 핵심 지침과 참조 읽기 조건
│   └── demiurge/                 # communication.md · engineering.md
├── bin/.local/bin/               # 전역 CLI 배포 (GNU Stow 경유 → ~/.local/bin/)
│   └── git-cleanup-worktrees
├── scripts/demi/                 # 사용 통계 CLI (uv packaged Python)
│   ├── src/demi/plugin_stats/    # collector · analyzer · reporter · commands
│   ├── reports/plugin-stats/     # latest.md + snapshots/*.json (git 추적)
│   └── tests/                    # pytest (Happy/Boundary/Error 카테고리)
├── scripts/check-codex-links.sh  # Codex 링크의 정확한 원본·끊어짐 검사
├── scripts/tests/               # 실제 just·Stow를 사용하는 배포 테스트
├── .claude/                      # 프로젝트 로컬 (demiurge 한정, stow 미경유)
│   ├── rules/stow-deployment.md
│   └── commands/wrap.md
├── justfile                      # Task runner: link/unlink/status/setup-statusline/new-*/stats
├── bootstrap.sh                  # 최초 설정 (stow/just/jq 설치 + fish PATH + statusLine 자동 설정)
└── README.md                     # 이 문서
```

개별 스킬·규칙 인벤토리는 `just stats` 출력 참조. 문서와 실제 파일이 어긋났는지는 `/wrap --check`로 확인한다.

## 확장

```bash
just new-skill <name>       # Claude 스킬 템플릿 생성 + 공동 재배포
just new-command <name>     # Claude 커맨드 템플릿 생성 + 공동 재배포
```

전역 vs 프로젝트 로컬 선택 기준:

- **전역** (`product/.claude/skills/demiurge/skills/<name>/`) — 여러 프로젝트에서 재사용. 파일 생성 후 `just link` 필수. 배포되면 `/demiurge:<name>`으로 호출된다.
- **프로젝트 로컬** (`<repo>/.claude/skills/<name>/`) — 특정 레포 도메인 지식·워크플로우와 결합. stow 불필요, 레포와 함께 버전 관리.

> 서브에이전트가 필요하면 `product/.claude/skills/demiurge/agents/<name>.md`에 만든다. 다만 현재 demiurge는 자체 에이전트를 두지 않는다 — 정의 파일이 프롬프트에 실리는지 확인하기 어려워, 페르소나가 필요한 스킬은 자기 폴더 안에 참조 파일을 두고 직접 주입한다 (`rl-verify/convergence-evaluator.md`, `review-ensemble/counter-reviewer.md`).

## 라이선스

이 프로젝트는 설정 템플릿입니다. 자유롭게 사용하세요.
