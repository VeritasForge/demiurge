# autopilot — 자율주행 판단 품질 보증 프로토콜 (MVP v1)

자율주행이 **필요할 때만 활성**되는 판단 품질 보증 프로토콜. 명시적 호출 시에만 발동 — 평소엔 human-in-the-loop 학습 기회를 보존한다.

> ⚠️ **MVP 상태**: 동작 품질 미입증. N=5 실사용 후 유지/축소/폐기 결정 (아래 트래커).

## 사용법 (두 진입 방식)

### 방식 A — 명시적 2단계 (권고)

```
1. /autopilot docs/superpowers/plans/foo.md
   → autopilot이 plan 읽고 짧은 /goal 조건 생성·제시

2. (안내된 한 줄 그대로 복붙) /goal <조건>
   → 이후 turn 자동 반복 + 자율 완주
```

### 방식 B — `/goal` 1회로 통합

```
/goal autopilot으로 docs/superpowers/plans/foo.md 완주
→ Claude가 goal condition 보고 Skill 도구로 autopilot 자율 호출
```

### 단발 작업 (semi-auto degraded)

```
/autopilot "<plain task 설명>"   # plan 없는 단발 — 1 turn 만큼 진행 + 안내
```

## 작동 원리 (요약)

1. **판단 지점 자동 식별** — `AskUserQuestion` 직전 / 옵션 2+개 trade-off / 1차 출처 미확인 사실 주장 시 발동.
2. **학습 데이터 추측 금지** → `deep-research`/`context7` 외부 조사 → `Agent` multi-agent 다관점 → 합의 → `/rl-verify` 수렴 → 결정.
3. **학습 자동 연계** — 시작 시 `ce-learnings-researcher`로 과거 교훈 주입, 종료 시 `ce-compound`로 누적.

자세한 절차는 `SKILL.md`의 Phase 0~5 참조.

## spec / plan

- spec: `zombie_pang/docs/superpowers/specs/2026-05-28-autopilot-skill-design.md` (v2.1)
- plan: `zombie_pang/docs/superpowers/plans/2026-05-28-autopilot-skill.md`

---

## 🔄 자율 완주 후 학습 사이클 (HITL 보존의 핵심)

autopilot은 평소 HITL 학습 기회를 보존하기 위해 *명시 호출 시만 발동*한다. 그러나 한번 발동해 자율 완주하고 나면, **사용자가 깨어나 결정 로그를 검토하고 하니스를 학습시키는 사이클**이 가장 중요한 가치다.

### 단계

1. **`DIGEST.md` 먼저 열기** (사람용 1페이지 요약):
   ```bash
   cat <project>/docs/autopilot/<slug>/DIGEST.md
   # 또는 더 보기 좋게:
   # /md-to-html docs/autopilot/<slug>/DIGEST.md  → 공유용 HTML
   ```
   - 🤔 **"한 번 더 봐주세요"** 섹션을 먼저 읽는다 — 다관점 의견이 갈렸거나 confidence가 낮았던 결정. 잘못 판단됐을 가능성이 가장 큰 곳.
   - ✅ 자신 있게 한 결정은 간략 리스트로 — 의심 없으면 skip.
   - 🚧 차단이 있으면 그 결정부터 처리.

   `run.log`(raw 디테일)는 DIGEST의 특정 결정을 깊이 파볼 때만 열면 된다.

2. **잘못된 결정 발견 시** (가장 흔한 케이스):
   - 해당 코드 직접 수정 + 커밋
   - **패턴화** — 같은 실수가 반복될 만한 결정이면 하니스 업데이트:
     - 글로벌 룰: `~/.claude/CLAUDE.md` 또는 `~/.claude/rules/*.md` 추가/수정
     - 도메인 룰: 해당 프로젝트 `.claude/rules/` 또는 `CLAUDE.md`
     - 라우팅 룰: autopilot SKILL.md의 routing 매트릭스 수정 (이 파일에 직접 Edit)
     - 새 패턴: 새 skill 작성 (`/superpowers:writing-skills` 사용)

3. **좋은 패턴 발견 시**:
   - 이미 Phase 5가 `ce-compound`로 `docs/solutions/` 누적 — 추가 작업 보통 불요
   - 더 일반화할 가치 있으면 직접 `docs/solutions/<topic>.md` 다듬기

4. **반복 실수 발견 시**:
   - `/retrospective` 호출 → 하니스 전체 점검 + Skills/CLAUDE.md/Memory/Hooks 업데이트
   - autopilot의 판단 지점 trigger를 조정해야 할 수도 — SKILL.md Phase 3의 trigger 3종에 케이스 추가

5. **`blocked-*.md` 발견 시**:
   - autopilot이 자율로 못 푼 막힘 — 사용자가 결정 → autopilot 재호출 가능
   - blocked 패턴이 반복되면 라우팅/trigger 보강 후보

### 학습 사이클의 가치

> 자율주행은 **빠른 완주**를 주고, **결정 로그**는 **느린 학습**을 준다. 두 속도가 함께 가야 매 실행이 다음 실행을 더 똑똑하게 만든다 (compound engineering).
>
> HITL을 *모든 결정마다* 강요하면 빠른 완주를 잃고, *전혀 안 보면* 느린 학습을 잃는다. autopilot은 **완주 시점에 한 번** HITL 사이클을 모아두는 절충안이다.

---

## N=5 실사용 검증 트래커

| # | 날짜 | plan/task | 진입 방식 | `/goal` pair | 판단 지점 발동 N | 결과 | 평가 |
|---|------|----------|----------|-------------|----------------|------|------|
| 1 | — | — | A / B | — | — | — | — |
| 2 | — | — | A / B | — | — | — | — |
| 3 | — | — | A / B | — | — | — | — |
| 4 | — | — | A / B | — | — | — | — |
| 5 | — | — | A / B | — | — | — | — |

### N=5 도달 후 평가 (작성 가이드 — v2.1 동작 품질 중심)

1. **판단 지점 자각 빈도**: autopilot이 발동해야 할 때 실제 발동했나? 자가 누락률은?
   - 측정: 누락된 판단 지점 = 사후 retrospective에서 "여기선 다관점 했어야"라고 발견된 케이스 수.
2. **결정 품질 향상**: 외부 조사(deep-research/context7) + 다관점 + rl-verify가 결정을 실제로 더 정확하게 만들었나?
   - 측정: 다관점이 잡은 오류 / 학습 데이터로 단정했으면 놓쳤을 것.
3. **토큰 비용 vs 품질 trade-off**: 비용 대비 가치 있나?
   - 측정: autopilot 사용 세션 token 평균 vs 비사용 세션.
4. **결정**: 유지 / 축소(`~/.claude/goal-templates/3-principles.md` snippet화) / 폐기.

### 평가 결과 기록란

```
[N=5 도달 후 작성]
- 자각 빈도:
- 결정 품질:
- 비용 vs 품질:
- 최종 결정:
```
