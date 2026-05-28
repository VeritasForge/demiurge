---
name: autopilot
description: Use when an existing plan/task list needs autonomous execution with a judgment-quality protocol (deep-research/context7 → multi-agent → rl-verify → consensus). Activated only on explicit `/autopilot <plan>` or `/goal "autopilot으로 ..."` — preserves human-in-the-loop otherwise. Pair with `/goal` for true turn-auto-repeat (skill alone runs one turn = semi-auto degraded). Triggers — '자율주행 시작', 'plan 자율 완주', 'autopilot으로 실행', '판단 프로토콜 적용'.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Skill, TaskCreate, TaskUpdate, TaskList, TaskGet, AskUserQuestion
argument-hint: "<plan-path or plain-task-description>"
---

# Autopilot — 자율주행이 필요할 때만 활성되는 판단 품질 보증 프로토콜

명시적 호출 시에만 발동한다. 평소엔 human-in-the-loop 학습 기회를 보존한다.

**판단 지점**(아래 3가지 trigger 중 하나)에서 학습 데이터 추측 금지 →
`deep-research`/`context7`로 조사 → `Agent` multi-agent 다관점 dispatch →
`rl-verify` 수렴 검증 → 합의 기반 결정.

**판단 지점 trigger** (자가 점검 — 이 3개 중 하나라도 충족하면 발동):
1. ⚠️ `AskUserQuestion`을 띄우려는 직전 — 자율 판단 절차로 우회
2. ⚠️ 결정 옵션이 **2개 이상이고 trade-off 있음**
3. ⚠️ 사실 주장 전 **1차 출처(ADR/spec/코드) 미확인**

**`/goal`과의 관계**: 턴 자동 반복(자율 완주 보장)은 `/goal` Stop hook의 책임. skill 자체는 1 turn 단위. `/goal` 미설정 시 semi-auto degraded(1 turn 만큼 진행 + 안내).

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

1. `$ARGUMENTS` 파싱: plan 경로 또는 plain task 설명.
2. plan 경로 존재 시 `Read`. 미존재 시 인자 자체를 task 설명으로 단발 모드.
3. **slug** 생성(kebab-case, 30자) → `docs/autopilot/<slug>/` 폴더 준비(`mkdir -p`).
4. `docs/autopilot/<slug>/run.log` append 헤더(`-- run YYYY-MM-DD HH:MM --`).

## Phase 1 — 학습 주입 (ce-learnings-researcher)

1. plan/task 도메인 키워드 추출(Activity·Concepts·Decisions·Domains 4-필드).
2. `Skill` 도구로 `compound-engineering:ce-learnings-researcher` 호출, 4-필드 work-context 전달.
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
   ```
4. `/goal` active 여부 감지 불가(공식 API 부재) — 사용자가 출력 보고 판단.

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

   **(원칙 2) 스킬·agent 활용** — 적합 라우팅 (인라인 매트릭스):
   | 영역 | 도구 |
   |------|------|
   | 외부 조사(라이브러리/API/메커니즘) | `deep-research`, `context7` MCP, `claude-code-guide` agent |
   | React/Next.js 코드 | `vercel-react-best-practices`, `vercel-composition-patterns` |
   | 버그/에러/테스트 실패 | `debug` 스킬(라우터 자동) |
   | 보안 | `security-review`, `ce-security-reviewer` |
   | 학습 검색/누적 | `ce-learnings-researcher`, `ce-compound` |

   **(원칙 1) 다관점** — 결정 중요도별 가중:
   | 중요도 | 절차 |
   |--------|------|
   | 낮음 | 1차 출처 확인만(Read/Grep) |
   | 중간 | + `/code-review` 또는 `/rl-verify` |
   | 높음 | + 외부 조사(deep-research/context7) + `Agent` multi-agent dispatch (ce-doc-review/ce-adversarial-document-reviewer) + 합의 + `/rl-verify` 수렴 |

4. **합의·검증 후 결정 명시**: 결정 직전 1줄 이상으로 *어떤 1차 출처/다관점 의견에 근거했는지* 명시. 단순 단정 금지.

5. 구현: TDD 3 카테고리(`[Happy]/[Boundary]/[Error]` 각 ≥1, 글로벌 룰).

6. `/code-review`(P0/P1 0건까지 반복 — 발견된 P0/P1 수정 후 재실행). React 코드면 호출 프롬프트에 "Vercel best-practices 기준" 명시.

7. 커밋:
   ```
   git add <files>
   git commit -m "<conventional message>

   Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
   ```

8. `TaskUpdate` → `completed`.

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
2. `Skill` 도구로 `compound-engineering:ce-compound` 호출(`mode:headless`), 식별된 교훈 전달. `docs/solutions/<topic>.md` 작성/갱신.
3. **Telemetry** 기록(run.log):
   - `learning-impact:` 1줄 — "이번 실행이 N-1 실행 대비 무엇을 우회/단축했는가" 자가 보고.
   - `judgment-points:` N — 이번 실행에서 발동된 판단 지점 수.
   - 누적 실행 횟수 카운터(`run.log`의 총 `-- run` 헤더 수).
4. 누적 10회 도달 또는 마지막 refresh 30일 경과 시 출력:
   ```
   💡 ce-compound-refresh 권고 — stale 학습 정리 시점
   ```

## Phase X — 막힘 처리

결정 불가 / 외부 의존 / spec 모순 시:
- `docs/autopilot/<slug>/blocked-<task-id>-<YYYYMMDD>.md`에:
  - **차단 사유** (분류: 결정-불가 / 외부 의존 / spec 모순)
  - **시도한 방법** (어떤 다관점·조사·확인을 거쳤나)
  - **필요한 결정 / 외부 의존**
- 작성 후 **stop**. `/goal` 미충족이라도 자율 해소 불가 — 사용자 개입 요청.

---

## 3원칙 운영 — 정직 인정

- 3원칙은 **권고적 텍스트**다. enforcement 메커니즘(hook/gate)은 없다. LLM이 본 SKILL.md를 읽고 따른다는 가정.
- 강제력은 (a) Phase 5 retrospective 자가 점검 (b) 결과물 검증 명령(typecheck/lint/test) (c) `/code-review` P0/P1 0 게이트로 보강.
- '자율'은 `/goal`이 활성일 때만 진짜 자율. 미설정이면 semi-auto degraded.

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
