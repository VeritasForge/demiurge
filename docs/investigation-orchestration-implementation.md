# Investigation Orchestration System — 설계 과정 및 구현 문서

> **생성일**: 2026-02-04
> **버전**: v4.7 (CLAUDE.md 기준)
> **기반 연구**: [`docs/investigation-orchestration-system.md`](./investigation-orchestration-system.md)

---

## 1. Overview

### 무엇을 만들었는가

코드베이스 조사(버그, 성능, 구조 분석 등)를 위한 **다중 조사관 오케스트레이션 시스템**. 여러 전문 조사관 에이전트가 독립적으로 병렬 조사를 수행한 뒤, 교차 검증 → 반박 → 증거 기반 판정의 단계를 거쳐 근거 있는 결론을 도출합니다.

### 왜 만들었는가

기존 `architect-orchestration`은 **아키텍처 설계 리뷰**에 특화되어 있어, 코드베이스의 구체적인 문제(버그, 장애 원인, 성능 병목 등)를 조사하는 데에는 적합하지 않았습니다. 코드 분석, 로그 분석, Git 이력 분석 등 **서로 다른 관점의 조사관**이 협력하여 하나의 문제를 다각적으로 파고드는 시스템이 필요했습니다.

### 핵심 가치

| 가치 | 설명 |
|------|------|
| **다각적 조사** | 코드, 로그, Git 이력 등 여러 관점에서 동시 분석 |
| **증거 기반 판정** | 다수결이 아닌, 증거 강도 비교를 통한 최종 결론 |
| **Anti-Sycophancy** | 독립 조사 선행 + Counter-Reviewer 반박으로 그룹 동조 방지 |
| **Context 효율성** | Tiered Report + Compact로 세션 안정성 보장 |

---

## 2. 기반 연구

Deep Research 3-Phase Protocol을 통해 15개 출처를 분석한 결과가 [`docs/investigation-orchestration-system.md`](./investigation-orchestration-system.md)에 정리되어 있습니다.

### 핵심 인사이트 8가지

| # | 인사이트 | 출처 | 확신도 |
|---|----------|------|--------|
| 1 | Multi-Agent Debate(MAD)는 에이전트 간 소통 시 더 정확한 합의에 도달 | MIT 2023 (Du et al.) | Confirmed |
| 2 | **단순 MAD(동일 에이전트 × 다수결)는 비효율적** — 전문화 + 증거 기반 필수 | ICLR 2025 | Confirmed |
| 3 | Tool-MAD(2 Debater + 1 Judge)가 기존 MAD 대비 **18.1% 정확도 향상** | arXiv 2601.04742 | Confirmed |
| 4 | Boris Cherny의 Counter-Reviewer 패턴이 false positive 제거에 효과적 | VentureBeat, InfoQ | Confirmed |
| 5 | Claude Code subagent는 1-level only (nesting 불가) | 공식 문서 | Confirmed |
| 6 | CONSENSAGENT의 anti-sycophancy: 독립 조사 선행 → 교차 검증 | ACL 2025 | Likely |
| 7 | Self-Consistency가 단순 MAD보다 효과적인 경우 다수 | ICLR 2025 | Confirmed |
| 8 | 3개 전문 에이전트 + Judge가 비용 대비 최적 | ICLR 2025 + Tool-MAD | Likely |

### 연구에서 발견한 모순과 해결

| 모순 | 해결 |
|------|------|
| MIT 2023: "MAD significantly improves" vs ICLR 2025: "fails to consistently outperform" | **동질적 다수결은 비효율적**이지만, **이질적 에이전트 + 증거 기반은 효과적** |
| "더 많은 에이전트 = 더 나은 성능" vs "increasing agents does not always improve" | **3개 전문 에이전트 + Judge가 최적** |

---

## 3. 설계 결정

### 결정 1: Judge Pattern (majority vote 대신)

```
┌─────────────────────────────────────────────────────┐
│  ❌ Majority Vote (기각)                              │
│                                                       │
│  Agent A: "원인은 X"  ─┐                              │
│  Agent B: "원인은 X"  ─┼─→ X 채택 (2:1)              │
│  Agent C: "원인은 Y"  ─┘                              │
│                                                       │
│  문제: A가 B의 답을 보고 동조했을 수 있음 (sycophancy)│
├─────────────────────────────────────────────────────┤
│  ✅ Judge Pattern (채택)                              │
│                                                       │
│  Agent A: "원인은 X" + 증거 [코드:L42, 로그:err.txt] │
│  Agent B: "원인은 X" + 증거 [git blame, test fail]   │
│  Agent C: "원인은 Y" + 증거 [성능 프로파일]           │
│            ▼                                          │
│  Judge: 증거 강도 비교 → X (증거 4건 vs 1건)          │
└─────────────────────────────────────────────────────┘
```

**근거**: Tool-MAD에서 Judge Pattern이 majority vote 대비 18.1% 정확도 향상 (arXiv 2601.04742)

### 결정 2: 이질적(Heterogeneous) 전문 조사관

```
┌──────────────────────────────────────────────────┐
│  ❌ 동일 에이전트 복제 (기각)                      │
│  Agent A (general) ┐                              │
│  Agent B (general) ┼─→ 같은 도구, 같은 관점       │
│  Agent C (general) ┘   → 중복 조사, 정보 없음      │
├──────────────────────────────────────────────────┤
│  ✅ 전문화된 이질적 조사관 (채택)                  │
│  Code Investigator  → 호출 체인, 에러 핸들링       │
│  Log Investigator   → 스택트레이스, 패턴 분석      │
│  History Investigator → git blame, PR 컨텍스트     │
│  Counter-Reviewer   → 발견사항 반박 (Boris 패턴)   │
└──────────────────────────────────────────────────┘
```

**근거**: ICLR 2025 — 이질적 에이전트(heterogeneous)만이 일관된 성능 향상을 보임

### 결정 3: 동적 관점(Perspective) 배정

같은 type의 조사관이라도 **다른 perspective**를 부여하여 다양성을 확보합니다.

```
IID: "{TYPE}-{PERSPECTIVE}-R{Round}"

예시:
  CODE-CALLCHAIN-R1   → 코드 조사관, 호출 체인 관점
  CODE-DATAFLOW-R1    → 코드 조사관, 데이터 흐름 관점
  → 같은 code-investigator지만 다른 조사 범위
```

**근거**: DMAD/Tool-MAD — 동일 에이전트도 다른 관점 부여 시 효과적

### 결정 4: Mediator Pattern (P2P 대신)

```
┌──────────────────────────────────────────────────┐
│  ❌ P2P 교차 검증 (기각)                           │
│                                                    │
│  A ←→ B   A ←→ C   B ←→ C   = O(n²) 통신        │
│  → Context 폭발                                   │
├──────────────────────────────────────────────────┤
│  ✅ Mediator 교차 검증 (채택)                      │
│                                                    │
│  A ──→ ┐                                          │
│  B ──→ ┼──→ Mediator (메인 대화) ──→ 분류 매트릭스│
│  C ──→ ┘                                          │
│  = O(n) 통신                                       │
└──────────────────────────────────────────────────┘
```

**근거**: architect-orchestration v4.0에서 검증된 70% Context 절감 효과

---

## 4. 아키텍처

### 5-Step 오케스트레이션 플로우

```
Step 0: 조사 계획 수립 (sequential-thinking)
  │  쿼리 분석 → 핵심 질문 도출 → Quick/Full 판정 → 조사관 배정
  │
Step 1: Round 1 — 독립 병렬 조사 (Task tool × 3-5)
  │  각 조사관이 서로의 존재를 모른 채 독립 조사 (anti-sycophancy)
  │
Step 2: Round 2 — 교차 검증 + 분류 (Mediator)
  │  ✅ AGREED / ❌ DISAGREED / ❓ UNCERTAIN / 🔍 NEEDS_MORE
  │
Step 3: Round 3 — 반박 + 심화 (조건부, max 2회)
  │  Track A: Counter-Reviewer (AGREED에 "구멍 뚫기")
  │  Track B: 심화 조사 (DISAGREED/UNCERTAIN 추가 증거)
  │
Step 4: Round 4 — 최종 판정 (Judge Pattern)
  │  증거 기반 최종 결론 + 확신도 태깅
  │
Step 5: 실행 검증
     체크리스트 6항목 + execution-log.md
```

### IID (Investigator ID) 체계

모든 조사관 리포트에 출처와 라운드를 추적하는 IID가 포함됩니다.

```
형식: "{TYPE}-{PERSPECTIVE}-R{Round}"

TYPE:                    PERSPECTIVE 예시:
  CODE = code-investigator    CALLCHAIN, DATAFLOW, ERRORHANDLING, CONCURRENCY
  LOG  = log-investigator     STACKTRACE, PATTERN, TIMELINE, METRICS
  HIST = history-investigator RECENT, BLAME, PRCONTEXT, REGRESSION
  CR   = counter-reviewer     AGREED (challenge)
  REL  = release-investigator ARTCOMP, DEPLOY, RISK, INFRA, OPS
```

### Tiered Report Template

| Layer | 용도 | 크기 제한 | 전달 범위 |
|-------|------|-----------|-----------|
| **Layer 1** Executive Summary | IID + 확신도 + 핵심 발견 | 500 tokens | 항상 context에 유지 |
| **Layer 2** Key Findings | 발견 상세 + 증거 + 대안 가설 | 2K tokens | 교차 검증 시 |
| **Layer 3** Full Report | 전체 분석 + 코드 스니펫 | 제한 없음 | artifact 파일 저장 |

### Context 절감 효과

```
Layer 관리 없는 단순 병렬 조사:
  4 조사관 × 5K (Full Report) = 20K tokens + CR 5K = 25K tokens
  → Context 폭발 → 세션 불안정

Investigation Orchestration (Tiered + Compact):
  Step 1: 4 × 500 (L1) + 4 × 2K (L2) = 10K → compact 후 ~3K
  Step 3: CR 500 + 심화 1K = 1.5K → compact 후 ~1K
  Step 4: 최종 판정 ~2K
  ────
  피크 Context ≈ 6K tokens (compact 후 기준)
  Layer 3는 파일 참조 (0 context cost)
```

---

## 5. 생성된 파일 목록

### 신규 생성 (9개)

| # | 파일 경로 | 역할 | 버전 |
|---|-----------|------|------|
| 1 | `.claude/skills/investigation-orchestration/SKILL.md` | 5-Step 오케스트레이션 프로토콜 | v4.6 |
| 2 | `.claude/skills/investigation-orchestration/investigator-registry.md` | 조사관 타입/관점 카탈로그, 배정 알고리즘 | v4.6 |
| 3 | `.claude/skills/investigation-orchestration/classification-protocol.md` | 분류 규칙, 판정 알고리즘, 보고서 구조 | v4.6 |
| 4 | `.claude/agents/code-investigator.md` | 코드 분석 전문 조사관 에이전트 | v4.6 |
| 5 | `.claude/agents/log-investigator.md` | 로그/에러 분석 전문 조사관 에이전트 | v4.6 |
| 6 | `.claude/agents/history-investigator.md` | Git 이력 분석 전문 조사관 에이전트 | v4.6 |
| 7 | `.claude/agents/counter-reviewer.md` | 발견사항 반박 (Boris Cherny 패턴) | v4.6 |
| 8 | `.claude/agents/release-investigator.md` | 릴리즈 분석 전문 조사관 에이전트 | v4.7 |
| 9 | `.claude/skills/release-handoff/SKILL.md` | 릴리즈 핸드오프 참조 지식 스킬 카드 | v4.7 |

### 수정 (5개)

| 파일 | 변경 내용 | 버전 |
|------|-----------|------|
| `CLAUDE.md` | v4.6: Investigation agents/skill 추가 (12→16 agents, 17→18 skills); v4.7: Release Investigator 추가 (16→17 agents, 18→19 skills) | v4.6, v4.7 |
| `investigator-registry.md` | v4.7: REL type + 5 perspectives + IID + 권장 조합 3건 추가 | v4.7 |
| `investigation-orchestration/SKILL.md` | v4.7: description에 릴리즈 조사 범위 추가, IID에 REL 추가 | v4.7 |
| `docs/investigation-orchestration-implementation.md` | v4.7: 신규 파일 2개 + 수정 4개 반영, 매트릭스/시나리오 추가 | v4.7 |

---

## 6. 사용 방법

### 슬래시 커맨드

```
/investigation-orchestration 코드베이스 조사 (버그, 성능, 구조 분석 등)
```

### 시나리오별 사용 예시

#### 시나리오 1: 버그 조사

```
/investigation-orchestration 주문 생성 API에서 간헐적으로 500 에러가 발생합니다.
최근 2주간 3건 보고되었고, 특정 시간대(새벽 2-4시)에 집중됩니다.
```

예상 배정:
| IID | 조사관 | 조사 범위 |
|-----|--------|----------|
| CODE-CALLCHAIN-R1 | code-investigator | 주문 생성 API 호출 체인 |
| CODE-ERRORHANDLING-R1 | code-investigator | 에러 핸들링/예외 처리 경로 |
| LOG-STACKTRACE-R1 | log-investigator | 500 에러 스택트레이스 분석 |
| HIST-RECENT-R1 | history-investigator | 최근 2주 관련 코드 변경 |

#### 시나리오 2: 성능 분석

```
/investigation-orchestration 환자 목록 조회 API 응답 시간이 3초 이상으로 느립니다.
데이터가 10만건 이상일 때 발생하며, DB 쿼리가 의심됩니다.
```

예상 배정:
| IID | 조사관 | 조사 범위 |
|-----|--------|----------|
| CODE-DATAFLOW-R1 | code-investigator | 데이터 흐름 + 쿼리 분석 |
| CODE-CONCURRENCY-R1 | code-investigator | 동시성/커넥션 풀 |
| HIST-BLAME-R1 | history-investigator | 쿼리 변경 이력 |

#### 시나리오 3: 릴리즈 핸드오프 문서 검증

```
/investigation-orchestration vc-backend v2.3.0 릴리즈 핸드오프 문서를 검증해주세요.
신규 모듈(vc-screening-service)이 포함되어 있고, DB 마이그레이션이 있습니다.
```

예상 배정:
| IID | 조사관 | 조사 범위 |
|-----|--------|----------|
| REL-ARTCOMP-R1 | release-investigator | 문서 Section 1-7 완전성 검증 |
| REL-RISK-R1 | release-investigator | 변경 리스크 + 롤백 계획 적절성 |
| REL-DEPLOY-R1 | release-investigator | 배포 절차 + 마이그레이션 검증 |
| CODE-DEPENDENCY-R1 | code-investigator | 의존성 변경 교차 검증 |

#### 시나리오 4: 단순 문의 (Quick Mode)

```
/investigation-orchestration OrderService.createOrder() 메서드에서
validateStock() 호출이 어디서 이루어지는지 확인
```

Quick Mode 판정 → 조사관 1명(CODE-CALLCHAIN-R1)만 배정 → 교차 검증 생략

### Architect Orchestration과의 차이

| 구분 | Architect Orchestration | Investigation Orchestration |
|------|------------------------|----------------------------|
| **목적** | 아키텍처 설계 리뷰/합의 | 코드베이스 문제 조사/분석 |
| **에이전트** | 12 Architect agents | 5 Investigator agents |
| **합의** | 2/3 투표 + Veto | Judge Pattern (증거 기반) |
| **결과물** | ADR, Architecture Decision | Investigation Report, Findings |
| **적합한 질문** | "이 설계가 적절한가?" | "왜 이 버그가 발생하는가?" |

---

## 7. 검증 결과

### 구현 후 체크리스트

| # | 항목 | 결과 |
|---|------|------|
| 1 | SKILL.md 5-Step 프로토콜 정의 | PASS |
| 2 | investigator-registry.md 조사관 카탈로그 | PASS |
| 3 | classification-protocol.md 분류/판정 알고리즘 | PASS |
| 4 | code-investigator.md 에이전트 정의 | PASS |
| 5 | log-investigator.md 에이전트 정의 | PASS |
| 6 | history-investigator.md 에이전트 정의 | PASS |
| 7 | counter-reviewer.md 에이전트 정의 | PASS |
| 8 | release-investigator.md 에이전트 정의 | PASS |
| 9 | release-handoff/SKILL.md 참조 스킬 정의 | PASS |
| 10 | CLAUDE.md v4.7 반영 (17 agents, 19 skills) | PASS |
| 11 | IID 체계 정의 및 일관성 (REL 포함) | PASS |
| 10 | Tiered Report Template 정의 | PASS |
| 11 | Quick Mode 분기 로직 | PASS |
| 12 | Context Management Protocol 포함 | PASS |
| 13 | 학술적 근거 6개 패턴 참조 | PASS |

### 학술적 근거 커버리지

| 학술 패턴 | 적용 위치 |
|-----------|----------|
| Tool-MAD (arXiv 2601.04742) | 전문화된 에이전트 + 도구 기반 증거 수집 |
| Judge Pattern | Step 4 증거 기반 판정 |
| Boris Cherny Counter-Reviewer | Step 3 반박 (counter-reviewer agent) |
| CONSENSAGENT (ACL 2025) | Step 1 독립 조사 → Step 2 교차 검증 순서 |
| ICLR 2025 MAD Analysis | 이질적 에이전트 설계 근거 |
| Dynamic Perspective Assignment | IID의 PERSPECTIVE 동적 배정 |

---

## 부록: 조사관-관점 매트릭스

```
           ┌─────────────┬───────────────┬──────────────┬─────────────┬──────────────┐
           │ Code Inv.   │ Log Inv.      │ History Inv. │ Counter-Rev │ Release Inv. │
           │ (CODE)      │ (LOG)         │ (HIST)       │ (CR)        │ (REL)        │
  ─────────┼─────────────┼───────────────┼──────────────┼─────────────┼──────────────┤
  Persp. 1 │ CALLCHAIN   │ STACKTRACE    │ RECENT       │ AGREED      │ ARTCOMP      │
  Persp. 2 │ DATAFLOW    │ PATTERN       │ BLAME        │             │ DEPLOY       │
  Persp. 3 │ ERRORHANDL. │ TIMELINE      │ PRCONTEXT    │             │ RISK         │
  Persp. 4 │ CONCURRENCY │ METRICS       │ REGRESSION   │             │ INFRA        │
  Persp. 5 │             │               │              │             │ OPS          │
           └─────────────┴───────────────┴──────────────┴─────────────┴──────────────┘

  조합 예: CODE-CALLCHAIN-R1, LOG-STACKTRACE-R1, HIST-BLAME-R1, REL-ARTCOMP-R1
  → 쿼리에 따라 동적으로 최적 조합 결정
```
