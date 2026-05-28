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
