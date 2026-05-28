---
name: autopilot
description: Use when an existing plan/task list needs autonomous execution while preserving human-in-the-loop review afterward. Activates only on explicit `/autopilot <plan>` or `/goal "autopilot으로 ..."`. Triggers — '자율주행 시작', 'plan 자율 완주', 'autopilot으로 실행', '판단 프로토콜 적용'.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Skill, Agent, ToolSearch, TaskCreate, TaskUpdate, TaskList, TaskGet, AskUserQuestion
argument-hint: "<plan-path or plain-task-description>"
---

# Autopilot — 자율주행이 필요할 때만 활성되는 판단 품질 보증 프로토콜

명시적 호출 시에만 발동한다. 평소엔 human-in-the-loop 학습 기회를 보존한다.

**판단 지점**에서 학습 데이터 추측 금지 → 1차 출처 확인 → 외부 조사·다관점·수렴 검증 → 합의 기반 결정.

**판단 지점 trigger** (자가 점검 — 3개 중 하나라도 충족하면 발동):
1. ⚠️ `AskUserQuestion`을 띄우려는 직전 — 자율 판단 절차로 우회
2. ⚠️ 결정 옵션이 **2개 이상이고 trade-off 있음**
3. ⚠️ 사실 주장 전 **1차 출처(ADR/spec/코드) 미확인**

**`/goal`과의 관계**: `/goal`은 Claude Code v2.1.139+ 내장 슬래시 커맨드로, **session-scoped prompt-based Stop hook의 wrapper**다 — 각 턴 종료 후 small fast model(기본 Haiku)이 조건 충족 여부를 yes/no 판정하고, 불충족이면 사용자 입력 없이 다음 턴을 시작한다. autopilot skill 자체는 1 turn 단위 — 턴 자동 반복(자율 완주 보장)은 `/goal`의 책임이다. `/goal` 미설정이면 semi-auto degraded(1 turn 만큼 진행 + 안내). 출처: <https://code.claude.com/docs/en/goal>.

**Prerequisites for `/goal`** (미충족 시 자동 반복 불가):
- Claude Code ≥ v2.1.139
- 워크스페이스 trust dialog 수락 완료
- settings에 `disableAllHooks: false` 및 `allowManagedHooksOnly: false`

---

## 진입 방식 (두 가지 모두 지원)

**방식 A — 명시적 2단계 (권고, 진입 명확)**:
```
1. /autopilot <plan-path>
   → autopilot이 plan 읽고 Phase 0~2 진행 후 짧은 /goal 조건 생성·제시
2. (안내된 한 줄을 그대로 복붙) /goal <조건>
   → 이후 turn 자동 반복
```

**방식 B — `/goal` 1회로 통합 (Claude 자율 호출 신뢰)**:
```
/goal autopilot으로 <plan-path> 완주
→ Claude가 goal condition 보고 Skill 도구로 autopilot 자율 호출
```

**공통**: 판단 프로토콜 텍스트를 매번 입력하지 않는다 — 프로토콜은 본 SKILL.md에 캡슐화.

---

## Phase 0 — 진입

1. **Deferred tool 사전 로드** (필수, 누락 시 첫 호출 시 에러):
   ```
   ToolSearch('select:TaskCreate,TaskUpdate,TaskList,TaskGet,AskUserQuestion')
   ```
   `allowed-tools` 명시만으로는 deferred tool schema가 자동 로드되지 않는다 — `compound-engineering:ce-doc-review` SKILL.md도 같은 가드를 명시한다.

2. **`$ARGUMENTS` 파싱**: plan 경로 또는 plain task 설명.

3. **plan 경로 존재 시 `Read`**. 미존재 시 인자 자체를 task 설명으로 단발 모드.

4. **base 디렉토리 결정**: `Bash: git rev-parse --show-toplevel 2>/dev/null || pwd` → 결과를 `<base>`로 사용. 동일 plan의 multi-project 호출 시 로그 분산 방지.

5. **slug 생성** (kebab-case, 30자 cap, 충돌 결정성 확보):
   - 우선순위 (1) `basename(plan-path, '.md')`, (2) plan 첫 H1 헤더, (3) task 설명 첫 단어들
   - 정규화: lowercase → non-alnum→hyphen → 연속 hyphen 압축 → 30자 절단 → trailing hyphen 제거

6. **폴더 준비**: `Bash: mkdir -p <base>/docs/autopilot/<slug>/`.

7. **run.log 헤더 append**:
   ```
   Bash: printf -- "-- run %s --\nbase: <base>\nslug: <slug>\nplan: <plan-path or 'inline'>\n" "$(date '+%Y-%m-%d %H:%M')" >> <base>/docs/autopilot/<slug>/run.log
   ```

## Phase 1 — 학습 주입 (ce-learnings-researcher)

1. plan/task 도메인 키워드 추출 — 4-필드: Activity / Concepts / Decisions / Domains.

2. **`Agent` 도구로** `compound-engineering:ce-learnings-researcher` 호출 (skill 아님, agent임). 4-필드를 agent가 명시한 `<work-context>` XML-style 블록 형식 그대로 직렬화 — 필드명 변형 금지(`Decisions to make` 같은 변형은 free-form fallback로 빠져 매칭 품질 저하):
   ```
   Agent(
     subagent_type="compound-engineering:ce-learnings-researcher",
     description="과거 교훈 검색",
     prompt="""
     <work-context>
     Activity: <brief description of what the caller is doing or considering>
     Concepts: <named ideas, abstractions, approaches the work touches>
     Decisions: <specific decisions under consideration, if any>
     Domains: <skill-design | workflow | code-implementation | agent-architecture | ...>
     </work-context>

     Return up to 5 applicable past learnings from docs/solutions/ as prose, prioritized by relevance.
     """
   )
   ```
   ce-learnings-researcher는 standalone 호출을 공식 지원 — agent 본문 `Integration Points` 섹션이 `Standalone invocation before starting work in a documented area`를 명시한다.

3. 반환된 관련 교훈 ID·요약을 `run.log`에 `learning-reference:` 라인으로 기록(telemetry).

4. 컨텍스트 주입은 자연어 인용으로(별도 가공 없이 활용).

## Phase 2 — Task 등록 + `/goal` 안내

1. plan task list 전체를 **모두** `TaskCreate`로 등록(글로벌 CLAUDE.md 강제).

2. plan에서 완료조건 1줄 추출(예: `모든 task 완료 + typecheck/lint/test/build exit 0`).

3. 출력으로 사용자 안내(방식 A 사용 시):
   ```
   🚦 자율 완주 보장: 다음을 그대로 복붙하세요 →
      /goal <추출된 완료조건>
   (이미 /goal active이면 무시)

   ℹ️ 상태 확인: 인자 없이 /goal 만 입력하면 현재 조건·턴 수·토큰 사용 표시
   ℹ️ 중단: /goal clear (또는 stop / off / reset / none / cancel)
   ```

4. **`/goal` active 여부 LLM 자동 감지 불가** — LLM은 `/goal` 직접 호출 못 함. 사용자가 인자 없는 `/goal` 입력으로 상태 조회 가능(공식 사양). 출력 안내에 위 셀프 체크 명령을 포함하는 것이 fail-safe.

## Phase 3 — 실행 루프 (각 task 순차)

각 task에 대해:

1. `TaskUpdate` → `in_progress`.

2. **판단 지점 식별** (자가 점검 — 3 trigger 중 하나 충족 시 발동):
   - ⚠️ `AskUserQuestion`을 띄우려는 순간
   - ⚠️ 결정 옵션이 **2개 이상이고 trade-off** 있음
   - ⚠️ **사실 주장 전 1차 출처 미확인** (Read/Grep/Bash ls -d 의무)

3. 발동 시 3원칙 적용:

   **(원칙 3) 추측 금지** — 사실 확인:
   - 1차 출처: `Read`(ADR/spec), `Grep`(코드), `Bash ls -d`(경로 실존 = phantom path 방지).

   **(원칙 2) 스킬·agent 활용** — 적합 라우팅 (인라인 매트릭스, 도구 타입 표기):
   | 영역 | 도구 (호출 형식) |
   |------|------|
   | 외부 조사(라이브러리/API/메커니즘) | `Skill('deep-research')`, `mcp__plugin_context7_context7__resolve-library-id` + `__query-docs`, `Agent('claude-code-guide')` |
   | React/Next.js 코드 | `Skill('vercel-react-best-practices')`, `Skill('vercel-composition-patterns')` |
   | 버그/에러/테스트 실패 | `Skill('debug')` (라우터 자동) |
   | 보안 | `Skill('security-review')`, `Agent('compound-engineering:ce-security-reviewer')` |
   | 학습 검색 | `Agent('compound-engineering:ce-learnings-researcher')` |
   | 학습 누적 | `Skill('compound-engineering:ce-compound', args='mode:headless ...')` |
   | 문서 다관점 리뷰 | `Skill('compound-engineering:ce-doc-review', args='mode:headless <path>')` |
   | 적대적 문서 리뷰 | `Agent('compound-engineering:ce-adversarial-document-reviewer')` |

   *Skill vs Agent 구분*: skills/ 하위는 `Skill` 도구, agents/ 하위는 `Agent` 도구. 헷갈리면 `Bash: ls /Users/cjynim/.claude/plugins/cache/.../skills/<name>` 와 `.../agents/<name>` 둘 다 확인.

   **(원칙 1) 다관점** — 결정 중요도별 가중:
   | 중요도 | 절차 |
   |--------|------|
   | 낮음 | 1차 출처 확인만(Read/Grep) |
   | 중간 | + `/code-review` 또는 `/rl-verify` |
   | 높음 | + 외부 조사(deep-research/context7) + 다관점 dispatch(ce-doc-review skill + ce-adversarial-document-reviewer agent 병행) + 합의 + `/rl-verify` 수렴 |

4. **합의·검증 후 결정 명시**: 결정 직전 1줄 이상으로 *어떤 1차 출처/다관점 의견에 근거했는지* 명시. 단순 단정 금지.

5. **결정 로깅** (사용자 학습 사이클의 핵심 — 빠뜨리지 말 것). 판단 지점 발동 시마다 `<base>/docs/autopilot/<slug>/run.log`에 다음 블록 append. **반드시 heredoc로 append** (덮어쓰기·중간 삽입 금지):
   ```
   Bash: cat >> <base>/docs/autopilot/<slug>/run.log <<'EOF'

   [judgment #N] @ <task-id>
     context: <결정이 필요한 상황 1줄>
     importance: 낮음 | 중간 | 높음
     tools-used: <호출한 조사·검증 도구>
     sources:
       - <도구1 결과 요약 + 출처/링크>
       - <도구2 결과 요약>
     multi-agent-opinions:   # 중요도 높음일 때만
       - <persona1>: <의견 1줄>
       - <persona2>: <의견 1줄>
     rl-verify: <수렴 카운터·합의>   # 호출 시
     decision: <최종 결정 1줄>
     rationale: <근거 1-2줄, 어느 출처/의견에 가중치>
   EOF
   ```
   `<...>` 자리표시자는 실제 값으로 치환. heredoc quoting(`'EOF'`)으로 변수 expansion 차단. sensitive 정보(API 키, 비밀번호, 개인정보)는 `[REDACTED]`로 마스킹. 결정 번호 N은 run.log의 기존 `[judgment #` 라인 수 +1 (재실행 시도 단조 증가 보장).

6. 구현: TDD 3 카테고리(`[Happy]/[Boundary]/[Error]` 각 ≥1, 글로벌 룰).

7. `/code-review`(P0/P1 0건까지 반복 — 발견된 P0/P1 수정 후 재실행). React 코드면 호출 프롬프트에 "Vercel best-practices 기준" 명시.

8. 커밋:
   ```
   git add <files>
   git commit -m "<conventional message>

   Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
   ```

9. `TaskUpdate` → `completed`.

`/goal` 미설정 상태(semi-auto degraded)에서는 1 turn 한도 내 최대 진행 후 출력:
```
⏸ semi-auto degraded — 다음 task 진행하려면:
   /goal <조건>  (turn 자동) 또는
   '계속' / 'go' 입력 (수동 ack 1회)
```

## Phase 4 — 전체 검증

1. 프로젝트 검증 명령 실행(예: `pnpm typecheck && pnpm lint && pnpm test && pnpm build` 또는 `pytest && ruff && mypy` 등 프로젝트별).
2. 모든 명령 exit 0 확인.
3. **조건부** `/ce-code-review` 1회 — plan 규모 ≥50 changed lines, 또는 auth/payments/migration 같은 high-risk 도메인 (글로벌 CLAUDE.md 명시).
4. 플랜 완료조건 재확인. 미충족 시 보완 task `TaskCreate` 등록 → Phase 3 재진입.

## Phase 5 — 교훈 누적 (ce-compound)

1. 이번 실행의 핵심 교훈을 **4 카테고리**(실패·발견·반복실수·좋은패턴)로 식별. 적용 가능한 모든 카테고리 시도, 최소 1개 누적.

2. **`Skill` 도구로** `compound-engineering:ce-compound` 호출, args에 `mode:headless` 토큰을 반드시 포함(interactive AskUserQuestion 차단):
   ```
   Skill(
     skill="compound-engineering:ce-compound",
     args="mode:headless autopilot run <slug> — <1줄 컨텍스트>"
   )
   ```
   ce-compound가 `$ARGUMENTS`의 `mode:headless` 토큰을 파싱해 비대화형 모드로 진입한다(ce-compound SKILL.md L35: *"intended for automations and skill-to-skill invocation"*).

   **⚠️ headless 모드 side effect — 사용자 사전 고지 필수**:
   - **Discoverability Check 자동 적용**: ce-compound는 headless에서 사용자 confirm 없이 프로젝트 `CLAUDE.md` 또는 `AGENTS.md`에 `docs/solutions/` 안내 라인을 직접 편집 추가한다 (ce-compound SKILL.md L330). disable 옵션 없음 — 사후 `git status` / `git diff CLAUDE.md AGENTS.md`로 확인.
   - **Phase 3 specialized review 자동 skip**: 토큰 절약 목적 (ce-compound SKILL.md L336). 보안/성능 자동 리뷰 필요하면 사용자가 별도 호출.
   - **ce-compound-refresh 자동 호출 안 함**: 권고 텍스트만 출력 (ce-compound SKILL.md L276). autopilot이 stale trigger 도달 시 권고 출력하는 것과 동일 정책.
   - autopilot DIGEST.md의 `## 📊 통계` 마지막에 "ce-compound side effects" 1줄 추가: "instruction-file 편집 여부(있음/없음 — git diff 확인 권장)".

3. **Telemetry 요약** 기록(run.log 마지막에):
   - `learning-impact:` 1줄 — "이번 실행이 N-1 실행 대비 무엇을 우회/단축했는가" 자가 보고.
   - `judgment-points:` N (이번 실행에서 발동된 판단 지점 수).
   - 누적 실행 횟수 카운터(`run.log`의 총 `-- run` 헤더 수).

4. **🔥 `DIGEST.md` 자동 생성** (사람용 1페이지 요약 — 가장 중요):
   - 경로: `<base>/docs/autopilot/<slug>/DIGEST.md`
   - **재실행 정책**: `run.log`는 append(누적), `DIGEST.md`는 `Write`로 덮어쓰기(최신 1페이지만). 이전 DIGEST를 보존할 필요 있으면 사용자가 직접 archive.
   - 자고 일어나 `cat run.log` 대신 **이 파일만 보면 어디 검토할지 즉시 파악**.
   - 형식 (이대로 채워 쓸 것):
     ```markdown
     # 📒 Autopilot Run Digest — <slug>
     *<YYYY-MM-DD HH:MM> · 소요 ~<분> · plan: <경로>*

     ## TL;DR
     - ✅ <X>개 task 완주 / 검증 명령 exit <0|N>
     - 🤔 검토 권고 결정 <K>개 (아래 섹션)
     - 🚧 차단 <M>건

     ## 🤔 한 번 더 봐주세요 (다관점 의견 분기·낮은 confidence)
     순서: importance 높음 → 낮음. 비어있으면 "없음".

     ### #<N>. <짧은 제목>
     - **위치**: <task-id>, <파일:라인>
     - **컨텍스트**: 1줄
     - **분기점**: 다관점에서 어떤 의견 차이가 있었는지 1~2줄
     - **내 결정**: <decision>
     - **근거**: <rationale 요약>
     - 👉 잘못됐으면: `<수정 위치 힌트>` 수정 + 하니스 후보(`<CLAUDE.md/rules/skill>`)

     ## ✅ 자신 있게 한 결정 (간략 리스트)
     - [#<N>] <decision 1줄> — <rationale 핵심 5단어>
     - ...

     ## 🚧 차단 (사용자 결정 필요)
     없음 / 또는 각 `<task-id>.blocked.md` 링크 + 사유 한 줄.

     ## 📊 통계
     - 판단 지점: 총 <N> (높음 <a> / 중간 <b> / 낮음 <c>)
     - 다관점 호출: <ce-doc-review N회 / code-review M회 / rl-verify K회>
     - 외부 조사: <deep-research N / context7 M>
     - 토큰: `/goal` session info(인자 없이 `/goal` 입력) 값 인용 / 미측정

     ## 📚 학습
     - 추가: `docs/solutions/<topic>.md` (Phase 5에서 자동)
     - 참조: <Phase 1 learning-reference 목록>

     ## 🔗 상세 / 다음 액션
     - raw: `run.log`
     - 차단: (없음) 또는 `<task-id>.blocked.md`
     - 검토 후 잘못된 결정 있으면: 직접 수정 + 하니스 업데이트
     - 더 봐주고 싶으면: `/md-to-html` 호출해 공유용 HTML 변환 가능
     ```

5. **사용자 학습 사이클 안내** 출력(skill 종료 직전):
   ```
   📒 한 페이지 요약: <base>/docs/autopilot/<slug>/DIGEST.md
      → 🤔 섹션 먼저 검토 (다관점 분기가 있었던 결정)
      → 잘못된 결정 발견: 코드 수정 + 하니스 업데이트(CLAUDE.md/rules/skill)
      → 좋은 패턴: ce-compound (이미 자동, 추가 다듬기 옵션)
      → 반복 실수: /retrospective
   📜 raw 로그: <base>/docs/autopilot/<slug>/run.log
   ```

6. **누적 10회 도달 또는 마지막 refresh 30일 경과** 시 출력:
   ```
   💡 ce-compound-refresh 권고 — stale 학습 정리 시점
   ```

## Phase X — 막힘 처리

결정 불가 / 외부 의존 / spec 모순 시:
- `<base>/docs/autopilot/<slug>/<task-id>.blocked.md` 작성 (글로벌 CLAUDE.md Section 8 표준 형식):
  - 첫 줄: `# Blocked: <task-id> · <YYYY-MM-DD>`
  - **차단 사유** (분류: 결정-불가 / 외부 의존 / spec 모순)
  - **시도한 방법** (어떤 다관점·조사·확인을 거쳤나)
  - **필요한 결정 / 외부 의존**
- **Task 상태 처리**: TaskCreate/Update는 `blocked` 상태가 없으므로 `in_progress` 유지 + description prefix에 `🚧 BLOCKED: see <task-id>.blocked.md` 추가(`TaskUpdate(taskId, description=...)`). 사용자 해소 후 다음 autopilot 호출 시 재진입.
- 작성 후 **stop**. `/goal` 미충족이라도 자율 해소 불가 — 사용자 개입 요청.

---

## 3원칙 운영 — 정직 인정

- 3원칙은 **권고적 텍스트**다. enforcement 메커니즘(hook/gate)은 없다. LLM이 본 SKILL.md를 읽고 따른다는 가정.
- 강제력은 (a) Phase 5 retrospective 자가 점검 (b) 결과물 검증 명령(typecheck/lint/test) (c) `/code-review` P0/P1 0 게이트로 보강.
- '자율'은 `/goal`이 활성일 때만 진짜 자율. 미설정이면 semi-auto degraded.

---

## Common Rationalizations (자율주행 압박 시 trigger bypass)

writing-skills의 Iron Law: 압박 상황에서 LLM이 trigger를 우회하려고 만들 핑계를 미리 박아둔다.

| 핑계 | 현실 |
|------|------|
| "이건 너무 명백해서 1차 출처 확인 불필요" | 명백함 ≠ 검증됨. 추측 단정의 99%가 이 핑계. **출처 1줄이라도 확인**. |
| "외부 조사는 토큰 낭비" | 잘못된 결정 1건의 수정 비용 > deep-research 1회 비용. 중요도 '높음'이면 **무조건 호출**. |
| "AskUserQuestion 띄우면 사용자가 더 빨라" | autopilot은 *발동된 순간부터* HITL을 뒤로 미루는 게 가치. 띄우는 순간 자율 종료. |
| "rl-verify까지는 과하다" | 중요도 '높음' 결정에서 rl-verify 누락 = 다관점이 갈렸을 때 합의 검증 0. **수렴 검증 의무**. |
| "결정 로깅은 다음 turn에 몰아서" | run.log에 누락된 결정은 DIGEST에서 사라짐 = 사용자 학습 사이클 끊김. **결정 직후 append**. |
| "Skill vs Agent 도구는 알아서 잡힐 것" | 잘못 호출 시 즉시 에러. **Phase 3 라우팅 매트릭스의 호출 형식 그대로 사용**. |
| "ToolSearch 사전 로드 생략 OK" | deferred tool은 schema 없이 호출 시 InputValidationError. **Phase 0 step 1 의무**. |

## Red Flags — 즉시 STOP

이 생각이 들면 trigger 충족이다. 발동하지 않으려는 자신을 의심하라.

- "그냥 학습 데이터 기반으로 답해도 충분해" → 1차 출처 확인 trigger
- "옵션이 2개지만 거의 같은 답이야" → 다관점 trigger
- "사용자한테 물어보면 되니까" → AskUserQuestion 차단 trigger
- "이번엔 토큰 아끼자" → 비용은 결정 품질의 2차 함수
- "어차피 사용자가 DIGEST에서 잡아줄 거" → 자율주행 책임 포기 신호

**모두: trigger 발동. 절차 적용.**

---

## Self-improving — Stale trigger

`ce-compound-refresh` 자동 권고 trigger:
1. **누적 10회 실행** 후
2. **30일 경과** 후 첫 호출
3. **충돌 발견** (ce-compound 감지)
4. **교훈 누적 50건 초과**

skill은 trigger 도달 시 출력으로 권고만 — 실제 실행은 사용자 호출.

---

## ROI 검증 (N=5 동작 품질 게이트)

본 skill은 v1 MVP다. 가치 자체보다 **동작 품질 미입증 상태**. 사용자가 N=5회 실사용 후 retrospective로:
- (a) **판단 지점 자각 빈도** — autopilot이 발동해야 할 때 실제 발동했나? (자가 누락률)
- (b) **결정 품질 향상** — 외부 조사·다관점·rl-verify가 결정을 실제로 더 정확하게 만들었나?
- (c) **토큰 비용 vs 품질 trade-off** — 비용 대비 가치 있나?
- 평가 결과 → **유지 / 축소(snippet화) / 폐기** 결정. 매몰비용 차단 안전망.
- 가치 입증 시 references/ 분리(principles/routing/workflow/learning) 후속 작업.

평가 결과는 `README.md`에 기록.
