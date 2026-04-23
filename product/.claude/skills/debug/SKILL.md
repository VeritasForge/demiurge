---
name: debug
description: 디버깅 라우터. 문제 상황을 판별하여 ce-debug 또는 systematic-debugging 중 적절한 스킬을 선택하여 호출한다. 버그, 에러, 테스트 실패, 예상치 못한 동작 시 사용.
---

# Debug Router

문제 상황을 판별하여 최적의 디버깅 스킬을 선택하고 호출하는 라우터.

## 라우팅 로직

```
사용자 입력 분석
    │
    ├─ 보조 기법 트리거 감지?
    │   - "콜스택", "역추적", "어디서 호출", "data flow"
    │     → root-cause-tracing 필요
    │   - "레이어", "middleware", "다중 검증", "각 단계마다"
    │     → defense-in-depth 필요
    │   - "flaky", "가끔 실패", "타이밍", "race condition",
    │     "setTimeout", "sleep", "비동기 대기"
    │     → condition-based-waiting 필요
    │
    │   YES → systematic-debugging 호출
    │
    └─ 그 외 모든 경우
        → ce-debug 호출 (기본값)
```

## 실행 절차

### Step 1: 판별

사용자 입력에서 위 트리거 키워드를 확인한다.

### Step 2: 사용자 알림 (한 줄)

선택한 스킬과 이유를 한 줄로 알린다.

예시:
- "비동기 타이밍 문제이므로 systematic-debugging(condition-based-waiting)을 사용합니다."
- "ce-debug로 디버깅을 시작합니다."

### Step 3: 스킬 호출

Skill 도구로 해당 스킬을 호출한다.

```
트리거 매칭됨 → Skill("superpowers:systematic-debugging")
트리거 없음   → Skill("compound-engineering:ce-debug")
```

사용자의 원래 문제 설명을 args로 그대로 전달한다.

## 선택 근거 (참고용)

| 스킬 | 강점 | 고유 기능 |
|------|------|----------|
| ce-debug (기본값) | 이슈 트래커 통합, 패턴 진단 테이블, 학습 기록, 설계 결함 감지 | Phase 0 Triage, /ce-compound, /ce-brainstorm 연동 |
| systematic-debugging | 보조 기법 문서 3개, 엄격한 Iron Law | root-cause-tracing, defense-in-depth, condition-based-waiting |

## 하지 말 것

- 두 스킬을 순차로 호출하지 마라 (핵심 프로세스가 동일하므로 중복)
- 판별이 애매하면 기본값(ce-debug)을 사용하라
- 라우터가 직접 디버깅하지 마라 — 반드시 스킬에 위임
