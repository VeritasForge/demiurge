# demi

Claude Code 개발환경(plugins / skills / agents / MCP / commands) **사용 통계 CLI**.
호출 빈도를 집계하고 `active` / `live` / `dead` 3등급으로 분류해 정리(추천)를 돕는다.

- **결정적(deterministic)**: 순수 Python(stdlib + typer), 토큰 0원, 외부 네트워크 없음
- **로컬 실행 전용**: `~/.claude/projects/**/*.jsonl` 로그와 `~/.claude/`·플러그인 인벤토리를 직접 읽는다
- **typer command group** 확장형: 새 통계 주제(예: `mcp-stats`)는 `add_typer` 한 줄로 추가

## 설치 / 실행

```bash
cd scripts/demi
uv sync
uv run demi plugin-stats report             # 전체 리포트 + 스냅샷 저장
uv run demi plugin-stats usage              # 호출 빈도 상위 출력
uv run demi plugin-stats unused --grade dead  # dead 자산만 (정리 후보)
uv run demi plugin-stats inventory          # 유형별 자산 개수
uv run demi plugin-stats diff A.json B.json # 두 스냅샷 추세 비교
```

편의: 레포 루트에서 `just stats` (또는 `just stats-unused`).

## 등급 (3-grade)

| 등급 | 조건 | 의미 |
|---|---|---|
| 🟢 **active** | 직접 호출 횟수 > 0 (지난 N개월) | 유지 |
| 🟡 **live** | 호출 0회 + 다른 자산의 frontmatter(`skills`/`tools`/`agents`)에서 참조됨 | **제거 금지** (의존성 그래프) |
| 🔴 **dead** | 호출 0회 + 참조 없음 (고립) | 정리 후보 |

> 단순 "호출 0회 = 미사용"이 아니라 **의존성 그래프**(inline `[a, b]` 및 block `- a` YAML 모두 파싱)를 반영해 false positive를 줄인다.

## 호출 카운트 (v1.1)

두 종류의 호출 신호를 **합산**한다:

1. **`tool_use` Skill / Task / `mcp__*`** — assistant 메시지에서 모델이 호출한 도구. `tool_use.id`로 dedup.
2. **`<command-name>/cmd</command-name>` wrapper** — user 메시지에 기록되는 *사용자 직접 입력* slash command. user message uuid로 dedup.

> ⚠️ 같은 명령이 양쪽에 모두 기록되면(예: `/rl-verify`는 wrapper 32 + tool_use 34 → 카운트 66) **이중 카운트**가 발생한다. 이는 `/save_obsi`처럼 wrapper로만 호출되는 명령이 false-dead로 잘못 분류되는 위험을 막기 위한 의도적 선택이다. 절대 카운트는 부풀려질 수 있으나 *비례 비교*(어떤 자산을 더 자주 쓰는가)는 유지된다.

## 리포트 (latest.md)

`render_markdown`이 만드는 섹션:

1. **요약** — 유형별 등급 표 (total/active/live/dead)
2. **사용 빈도 그래프** (Top 15, ASCII bar) — `█`/`░` 막대로 4개 차트
   - **통합** (skill + agent + command)
   - **skills** 단독
   - **agents** 단독
   - **commands** 단독
3. **활성 자산 (active)** — 호출된 자산 목록
4. **정리 후보 (dead)** — 제거 후보
5. **추세** — 이전 스냅샷 대비 신규 dead

## 추적 대상 (5종)

- **plugins** — `~/.claude/plugins/installed_plugins.json`
- **skills** — `~/.claude/skills/` (전역) + 플러그인 `installPath/**/SKILL.md` + `product/.claude/skills/` (프로젝트 로컬)
- **agents** — `~/.claude/agents/` + 플러그인 `**/agents/*.md` + 빌트인 하드코딩 목록
- **MCP servers** — `~/.claude.json` (top + projects) + 레포 루트 `.mcp.json` + 각 플러그인 번들 `.mcp.json`
  - MCP 호출 키(`mcp__server__tool` / `mcp__plugin_X_Y__tool`)는 서버 토큰으로 정규화되어 인벤토리와 매칭
- **commands** — `product/.claude/commands/` + `~/.claude/commands/` (전역)

## 산출물

- `reports/plugin-stats/latest.md` — 사람용 마크다운 리포트 (git 추적)
- `reports/plugin-stats/snapshots/YYYY-MM-DD.json` — 기계용 누적 스냅샷 (git 추적, 추세 분석용)

세션 로그가 약 4개월치만 보존되므로 **장기 추세는 스냅샷 누적**에 의존한다.

## 주기 실행 (cron — 매월 첫째 주 월요일 정오)

> ⚠️ macOS `crontab(5)`:
> - `%`는 newline으로 변환되므로 `\%`로 escape 필수
> - day-of-month(`1-7`)와 day-of-week(`*`)가 둘 다 제한되면 **OR** 결합. 여기서는 dow=`*`로 두고 셸 가드(`date +%u = 1`)가 월요일만 발동시킨다 (ISO 요일: 월=1)

```cron
0 12 1-7 * * [ "$(date +\%u)" = "1" ] && cd /Users/cjynim/lab/demiurge/scripts/demi && /Users/cjynim/.local/bin/uv run demi plugin-stats report >> /tmp/demi-stats.log 2>&1
```

등록:
```bash
crontab -e   # 위 라인 추가
crontab -l   # 확인
```

cron이 cloud(/schedule)가 아닌 **로컬**에서 도는 이유: 로그(`~/.claude/projects`)와 인벤토리가 로컬 파일시스템에 있어 `/schedule`(Anthropic 클라우드)에서는 접근 불가.

## 개발 / 테스트

```bash
uv run pytest -v                    # 전체 (현재 46 passed)
uv run pytest tests/plugin-stats/test_analyzer.py -v  # 모듈별
```

TDD 규칙: 각 모듈 테스트는 `[Happy]` / `[Boundary]` / `[Error]` 카테고리를 모두 포함 (외부 호출 부재 모듈은 `[Error]` 면제 + 사유 명시).

## 구조

```
scripts/demi/
├── pyproject.toml                # uv packaged app
├── src/demi/
│   ├── cli.py                    # 루트 typer app + add_typer
│   └── plugin_stats/
│       ├── models.py             # Asset · CallStat · GradedAsset
│       ├── collector.py          # frontmatter + 인벤토리(5종) + jsonl 집계
│       ├── analyzer.py           # 3등급 판정 (alias-resolved refs)
│       ├── reporter.py           # 스냅샷 + 마크다운
│       └── commands.py           # plugin-stats 5 commands
├── reports/plugin-stats/         # 산출물 (git 추적)
└── tests/plugin-stats/           # pytest, 카테고리별
```

## 확장 (새 통계 주제 추가)

```python
# src/demi/<topic>/commands.py 와 같은 패턴 복제
new_app = typer.Typer(help="...")
app.add_typer(new_app, name="<topic>")
@new_app.command()
def report(): ...
```
실행: `uv run demi <topic> report`. 산출물은 `reports/<topic>/`, 테스트는 `tests/<topic>/`.

## 알려진 제약 (v1)

- **MCP 도구 단위 전체 목록 대비 미사용** 판정은 v2 (서버 연결 필요). 현재는 호출된 도구만 서버 단위로 집계.
- **타 레포 commands** 미수집 — 현재는 demiurge `product/.claude` + 전역 `~/.claude/commands/`만. 다른 레포(`vc-monorepo/.claude/skills/security-patch` 등)에서 호출된 명령은 ghost로 표기됨.
- **전이적 dead 전파** (dead가 참조하는 자산도 dead로) 미구현 (v2).
- **빌트인 슬래시 명령** (`/clear`, `/exit` 등 Claude Code 내장)은 SKILL.md 파일이 없어 인벤토리에 안 잡힘 → ghost로 표기되지만 호출 카운트는 정확히 집계됨. 정상 동작.

## 라이선스

demiurge 레포 라이선스를 따른다.
