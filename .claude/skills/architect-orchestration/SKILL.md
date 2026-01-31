---
name: architect-orchestration
description: 12개 아키텍트 에이전트를 오케스트레이션하여 합의된 아키텍처 설계를 도출. /architect-orchestration 으로 실행.
allowed-tools: Read, Grep, Glob, Task, WebSearch, WebFetch
---

# Architect Orchestration Skill

## Overview

이 스킬은 사용자의 아키텍처 요구사항을 분석하고, 12개의 전문 아키텍트 에이전트를 **Task tool**로 spawn하여 **Draft → Specialist Feedback → Cross-Review → Consensus** 의 멀티라운드 구조로 합의된 아키텍처를 도출합니다.

**핵심 원리**: 이 스킬은 main conversation context에서 실행되므로 Task tool을 사용하여 subagent를 spawn할 수 있습니다.

---

## AID (Architect ID) 체계

모든 아키텍트 리포트에는 AID가 포함되어 출처와 라운드를 추적합니다.

```
형식: "{Tier}-{Role}-{Round}"

예시:
  T1-SA-R1    → Tier 1, Solution Architect, Round 1
  T1-DA-R2    → Tier 1, Domain Architect, Round 2
  T2-APP-R1   → Tier 2, Application Architect, Round 1
  T2-DATA-R1  → Tier 2, Data Architect, Round 1
  T2-INT-R1   → Tier 2, Integration Architect, Round 1
  T2-HIA-R1   → Tier 2, Healthcare Informatics Architect, Round 1
  T3-SEC-R1   → Tier 3, Security Architect, Round 1
  T3-SRE-R1   → Tier 3, SRE Architect, Round 1
  T3-CN-R1    → Tier 3, Cloud-Native Architect, Round 1
  T4-EDA-R1   → Tier 4, EDA Specialist, Round 1
  T4-ML-R1    → Tier 4, ML Platform Architect, Round 1
  T4-CON-R1   → Tier 4, Concurrency Architect, Round 1
```

---

## Tiered Report Template

모든 아키텍트는 3단계 계층 출력을 사용합니다. 이를 통해 Context 비대화를 방지합니다.

### Layer 1: Executive Summary (항상 전달, 500토큰 이내)

```yaml
executive_summary:
  aid: "{AID}"
  vote: AGREE | DISAGREE | CONDITIONAL
  confidence: HIGH | MEDIUM | LOW
  one_liner: "핵심 결론 한 줄 요약"
  top_findings:
    - "[권고/우려 1] [priority/severity]"
    - "[권고/우려 2] [priority/severity]"
    - "[권고/우려 3] [priority/severity]"
  changes:   # 기존 아키텍처 변경 시에만
    - target: "변경 대상"
      before: "변경 전"
      after: "변경 후"
      rationale: "변경 이유"
```

### Layer 2: Key Findings (교차 리뷰 시 전달, 2K토큰 이내)

```yaml
key_recommendations:
  - id: R1
    priority: HIGH | MEDIUM | LOW
    category: DESIGN | SECURITY | PERFORMANCE | OPERATION | DATA | INTEGRATION | COMPLIANCE
    description: "권고 내용"
    rationale: "이유"

key_concerns:
  - id: C1
    severity: HIGH | MEDIUM | LOW
    description: "우려 내용"
    impact: "영향"
    mitigation: "완화 방안"

dependencies:
  - type: REQUIRES | CONFLICTS_WITH | ENHANCES
    target: "대상"
    description: "설명"

vote_detail:
  decision: AGREE | DISAGREE | CONDITIONAL
  rationale: "투표 이유"
  conditions: []    # CONDITIONAL인 경우
  alternatives: []  # DISAGREE인 경우
```

### Layer 3: Full Report (artifact 저장, 제한 없음)

Full Report는 `review/{review-id}/artifacts/{AID}-full-report.md`에 저장합니다.
상세 분석, 다이어그램, 코드 예시 등 제한 없이 작성합니다.

---

## External Artifact 경로

```
review/
├── {review-id}/
│   ├── draft-architecture.md              # Step 2 산출물
│   ├── consolidated-findings-r{N}.md      # Step 4 산출물 (라운드별)
│   ├── final-review.md                    # Step 6 최종 문서
│   └── artifacts/
│       ├── T1-SA-R1-full-report.md
│       ├── T1-DA-R1-full-report.md
│       ├── T2-APP-R1-full-report.md
│       └── ...
```

---

## Context Management Protocol

대규모 오케스트레이션 실행 시 컨텍스트 윈도우 초과를 방지하기 위한 **필수** 프로토콜입니다.

> **배경**: Deep Research + 다수 아키텍트 호출 시, 각 결과가 메인 컨텍스트에 누적되어 세션이 멈추는 문제가 발생합니다. Tiered Report와 Mediator 패턴으로 70% 절감했지만, 추가적인 context 위생 관리가 필요합니다.

### 원칙

```
┌─ Context 위생 3원칙 ─────────────────────────────────────────────┐
│                                                                    │
│  1. 📁 즉시 파일 저장: 결과 수신 즉시 artifact 파일에 Write       │
│  2. 📝 Layer 1만 유지: 메인 컨텍스트에는 Executive Summary만 보유  │
│  3. 🔄 마일스톤 compact: /compact 실행으로 누적 context 압축      │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Compact 트리거 포인트

다음 시점에서 **반드시 `/compact`를 실행**하여 컨텍스트를 압축합니다:

| 시점 | 조건 | 이유 |
|------|------|------|
| **Step 1.5 완료 후** | Deep Research가 실행된 경우 | WebSearch/WebFetch 결과가 대량 누적 |
| **Step 3 완료 후** | Specialist 3명 이상 호출된 경우 | 다수 Task 결과가 메인 컨텍스트에 반환됨 |
| **Step 5 재라운드 시** | 재투표 2회 이상 발생 시 | 반복 호출로 context 누적 |

> **중요**: `/compact` 실행 **전에** 모든 중요 결과를 반드시 파일로 저장하세요. compact 후에는 파일에서 Read로 복원합니다.

### Deep Research 결과 파일 저장 규칙

Step 1.5 (Deep Research) 결과는 반드시 파일로 저장하고, 메인 컨텍스트에는 **요약본(research_context)만** 유지합니다:

```
review/{review-id}/
├── research/
│   ├── phase1-broad-findings.md    # Phase 1 전체 결과 (WebSearch 결과 포함)
│   ├── phase2-deep-dive.md         # Phase 2 심화 결과 (WebFetch 결과 포함)
│   └── research-summary.md         # 요약본 (이것만 context에 유지)
```

**research-summary.md** (context에 유지할 요약본, 1K 토큰 이내):
```yaml
research_context:
  topic: "[조사 주제]"
  key_findings:
    - finding: "[핵심 발견 1]"
      confidence: "[Confirmed/Likely/Uncertain]"
    - finding: "[핵심 발견 2]"
      confidence: "[Confirmed/Likely/Uncertain]"
  relevant_to:
    security: "[보안 관련 1줄 요약]"
    data: "[데이터 관련 1줄 요약]"
  full_report: "review/{review-id}/research/"
```

### 단계 간 Context 위생 체크리스트

각 주요 단계 완료 시 다음을 확인합니다:

```yaml
context_hygiene_check:
  after_step_1_5:  # Deep Research 후
    - action: "전체 검색 결과를 research/ 디렉토리에 Write"
    - action: "research_context 요약본만 메인 컨텍스트에 유지"
    - action: "/compact 실행"

  after_step_2:    # Draft Architecture 후
    - action: "draft-architecture.md에 Write 완료 확인"
    - action: "이후 Step에서는 draft-architecture.md를 Read로 참조"

  after_step_3:    # Specialist Review 후
    - action: "각 Full Report를 artifacts/{AID}-full-report.md에 Write"
    - action: "Layer 1 (Executive Summary)만 메인 컨텍스트에 유지"
    - action: "/compact 실행 (3명 이상 호출 시)"

  after_step_4:    # Cross-Review 후
    - action: "consolidated-findings-r{N}.md에 Write 완료 확인"
    - action: "이전 라운드 결과는 파일 참조로 전환"
```

---

## Execution Instructions

아래 단계를 **순서대로** 실행하세요.

---

### Step 0: 참조 문서 로드

다음 3개 파일을 **Read tool**로 읽어 오케스트레이션에 필요한 상세 정보를 확보합니다:

```
.claude/skills/architect-orchestration/architect-registry.md   → 12개 아키텍트 상세 정보
.claude/skills/architect-orchestration/routing-strategy.md      → 키워드 → 아키텍트 매핑 규칙
.claude/skills/architect-orchestration/consensus-protocol.md    → 합의 프로토콜 상세
```

---

### Step 1: 요구사항 분석

**mcp__sequential-thinking__sequentialthinking**을 사용하여 다음을 분석합니다:

1. **키워드 추출**: 요구사항에서 아키텍처 관련 키워드를 추출
2. **review-id 생성**: `{주제}-{YYYY-MM-DD}` 형식 (예: `logistics-design-2026-01-30`)
3. **실행 계획 수립**: 요구사항의 복잡도와 범위 파악

#### 키워드 → 아키텍트 Quick Reference

| 키워드 | 아키텍트 |
|--------|----------|
| API, 레이어, 모듈, 서비스 | application-architect |
| 데이터, DB, 스키마, CQRS | data-architect |
| 통합, 연동, EMR, 메시지, 큐 | integration-architect |
| 환자, 진료, HIPAA, FHIR, HL7 | healthcare-informatics-architect |
| 보안, 인증, 권한, 암호화 | security-architect |
| 모니터링, SLO, 장애, 운영, 배포 | sre-architect |
| 컨테이너, K8s, 클라우드, 스케일 | cloud-native-architect |
| 이벤트, SAGA, 비동기 | eda-specialist |
| ML, AI, 모델, 예측 | ml-platform-architect |
| 동시성, 병렬, 락, 스레드 | concurrency-architect |

> **Note**: 이 단계에서는 키워드를 추출만 하고, 실제 Tier 2/3/4 아키텍트 선정은 Step 2-5 (Draft 기반 라우팅)에서 수행합니다.

분석이 끝나면 사용자에게 **review-id와 실행 계획**을 요약하여 보여주고 진행합니다.

---

### Step 1.5: Deep Research (Optional)

요구사항 분석 결과 다음 조건 중 하나라도 해당하면, **아키텍트 리뷰 전에 심층 조사**를 수행합니다:

| 트리거 조건 | 예시 |
|-------------|------|
| 명시적 조사 요청 | "최신 기술 동향을 반영해서 검토해줘" |
| 최신 기술 검토 필요 | 새로운 프레임워크, 최근 릴리스된 도구 |
| 불확실한 trade-off | 근거 자료 없이 비교가 어려운 기술 선택 |
| 표준/규정 최신 확인 | HIPAA, FHIR, OWASP 등 최신 변경사항 |

#### 실행 방법

1. **오케스트레이터가 Phase 1 (광역 탐색)을 수행**:
   - `deep-research` 스킬의 Phase 1 프로토콜에 따라 WebSearch 3-5회 병렬 실행
   - 쿼리 분해 → 병렬 검색 → 출처 다양성 확인 → 핵심 발견 정리

2. **`research_context` 생성**:
   ```yaml
   research_context:
     topic: "[조사 주제]"
     phase1_summary: "[Phase 1 핵심 발견 요약]"
     key_findings:
       - finding: "[발견]"
         confidence: "[Confirmed/Likely/Uncertain/Unverified]"
         source: "[출처]"
     relevant_to:
       security: "[보안 관련 발견]"
       data: "[데이터 관련 발견]"
       integration: "[통합 관련 발견]"
   ```

3. **각 Agent 프롬프트에 `research_context` 주입**:
   - Step 2 이후의 모든 Agent 호출 시, 프롬프트에 `## Research Context` 섹션 추가

4. **최종 문서 생성 시 Phase 3 (지식 합성) 수행**:
   - Step 6에서 Research 결과를 통합하여 출처 인용 및 확신도 태깅 포함

#### Context 관리 (필수)

Deep Research 실행 후 반드시 다음을 수행합니다:

1. **Phase 1 전체 결과** → `review/{review-id}/research/phase1-broad-findings.md`에 Write
2. **Phase 2 심화 결과** (실행 시) → `review/{review-id}/research/phase2-deep-dive.md`에 Write
3. **요약본 생성** → `review/{review-id}/research/research-summary.md`에 Write
4. 메인 컨텍스트에는 **research_context 요약본(1K 토큰 이내)만** 유지
5. **`/compact` 실행** — WebSearch/WebFetch 결과로 비대해진 컨텍스트를 압축

> 이후 Step에서 Research 상세 내용이 필요하면 `research/` 디렉토리에서 Read로 참조합니다.

#### 건너뛰기 조건

- 코드 리뷰, 리팩토링 등 기존 코드베이스에 대한 검토
- 잘 정립된 패턴에 대한 적용 검토
- 사용자가 빠른 리뷰를 요청한 경우

---

### Step 2: Draft Architecture (Tier 1 Sequential)

Tier 1 아키텍트가 **아키텍처 초안(Draft)**을 생성합니다. 이전 "리뷰"가 아닌 **설계** 역할입니다.

#### Step 2-1: Solution Architect — 시스템 아키텍처 초안 생성

1. `.claude/agents/solution-architect.md`를 **Read**로 읽어 페르소나를 확보
2. **Task tool**로 spawn:

```
Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "Solution Architect Draft",
  prompt: """
  당신은 Solution Architect입니다.

  [solution-architect.md 페르소나 전체 삽입]

  ## 임무: 시스템 아키텍처 초안(Draft) 생성

  아래 요구사항을 바탕으로 **시스템 아키텍처 초안**을 생성하세요.
  이것은 리뷰가 아닌 **설계**입니다. 전체 시스템의 큰 그림을 잡아주세요.

  ## 요구사항
  [사용자의 원본 요구사항]

  ## Draft 포함 사항
  1. 아키텍처 스타일 선택 및 근거
  2. 주요 컴포넌트/서비스 식별
  3. 컴포넌트 간 통신 방식
  4. 기술 선택 및 trade-off
  5. 품질 속성 목표 (성능, 확장성, 가용성, 보안)
  6. 주요 리스크 및 완화 방안

  ## 응답 형식

  ### Part 1: Executive Summary (Layer 1)
  ```yaml
  executive_summary:
    aid: "T1-SA-R1"
    vote: AGREE
    confidence: HIGH | MEDIUM | LOW
    one_liner: "핵심 설계 방향 한 줄"
    top_findings:
      - "[핵심 설계 결정 1]"
      - "[핵심 설계 결정 2]"
      - "[핵심 설계 결정 3]"
  ```

  ### Part 2: Draft Architecture (본문)
  위 Draft 포함 사항을 상세히 작성하세요.
  다이어그램(ASCII), 컴포넌트 정의, 데이터 흐름 등을 포함합니다.

  ## 코드베이스 참조
  필요시 Read, Grep, Glob 도구로 현재 코드베이스를 조사하여 기존 아키텍처와의 정합성을 확인하세요.
  """
)
```

3. 결과를 `draft_solution` 변수로 저장

#### Step 2-2: Domain Architect — Draft에 도메인 모델 보강

1. `.claude/agents/domain-architect.md`를 **Read**로 읽어 페르소나를 확보
2. **Task tool**로 spawn:

```
Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "Domain Architect Draft 보강",
  prompt: """
  당신은 Domain Architect입니다.

  [domain-architect.md 페르소나 전체 삽입]

  ## 임무: Draft Architecture에 도메인 모델 보강

  Solution Architect가 작성한 시스템 아키텍처 초안을 바탕으로
  **도메인 모델을 보강**하세요.

  ## 요구사항
  [사용자의 원본 요구사항]

  ## Solution Architect의 Draft Architecture
  [draft_solution 삽입]

  ## 보강 사항
  1. Bounded Context 식별 및 정의
  2. Context Map (관계 설정)
  3. 핵심 Aggregate 설계
  4. Domain Events 모델링
  5. Ubiquitous Language 정의
  6. Draft에 대한 도메인 관점 피드백

  ## 응답 형식

  ### Part 1: Executive Summary (Layer 1)
  ```yaml
  executive_summary:
    aid: "T1-DA-R1"
    vote: AGREE | DISAGREE | CONDITIONAL
    confidence: HIGH | MEDIUM | LOW
    one_liner: "도메인 모델 핵심 결론"
    top_findings:
      - "[핵심 도메인 결정 1]"
      - "[핵심 도메인 결정 2]"
      - "[핵심 도메인 결정 3]"
    changes:
      - target: "변경 대상"
        before: "Solution Architect의 원안"
        after: "도메인 관점 보강/수정"
        rationale: "변경 이유"
  ```

  ### Part 2: Domain Model Augmentation (본문)
  위 보강 사항을 상세히 작성하세요.

  ## 코드베이스 참조
  필요시 Read, Grep, Glob 도구로 현재 코드베이스를 조사하세요.
  """
)
```

3. 결과를 `draft_domain` 변수로 저장

#### Step 2-3: Tier 1 교차 리뷰 라운드

Tier 1 아키텍트 간 Draft를 교차 리뷰하여 합의된 Draft Architecture를 생성합니다.

**프로세스**:

```yaml
tier1_cross_review:
  participants: [solution-architect, domain-architect]
  max_rounds: 3
  process:
    round_1:
      # Step 2-1, 2-2에서 이미 완료
      - solution-architect: Draft 시스템 아키텍처 생성
      - domain-architect: Draft에 도메인 모델 보강
    round_2_onwards:
      # 양쪽 모두 상대방의 결과물을 리뷰하고 피드백
      - solution-architect에게 전달: domain-architect의 보강안 + 변경사항
      - domain-architect에게 전달: solution-architect의 피드백 + 수정안
      - 각자 피드백 + 수정안 제출 (Layer 1 형식)
    consensus_check:
      - 양쪽 모두 AGREE → 합의 완료
      - 한쪽이라도 DISAGREE/CONDITIONAL → 다음 라운드
      - max_rounds 초과 → 현재 상태로 확정 + 미합의 사항 기록
```

**Round 2 이후 호출 패턴** (합의 필요 시):

```
# Solution Architect에게 Domain Architect의 보강안 리뷰 요청
Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "T1-SA 교차 리뷰 R{N}",
  prompt: """
  당신은 Solution Architect입니다.
  [페르소나 삽입]

  ## 임무: Domain Architect 보강안 리뷰

  당신의 Draft Architecture에 대해 Domain Architect가 다음과 같이 보강했습니다.

  ## Domain Architect의 보강안
  [draft_domain 삽입]

  ## 검토 요청
  1. 도메인 모델 보강이 시스템 아키텍처와 정합적인가?
  2. 수용할 부분과 수정이 필요한 부분은?
  3. 추가 보강이 필요한 부분은?

  ## 응답 형식
  ```yaml
  executive_summary:
    aid: "T1-SA-R{N}"
    vote: AGREE | DISAGREE | CONDITIONAL
    one_liner: "..."
    top_findings: [...]
    changes:
      - target: "..."
        before: "..."
        after: "..."
        rationale: "..."
  ```
  """
)

# Domain Architect에게도 동일 패턴으로 역방향 리뷰 요청
```

**합의 판정**: 양쪽 모두 `AGREE`이면 교차 리뷰 종료.

#### Step 2-4: 합의된 Draft Architecture 문서 생성

Tier 1 교차 리뷰가 완료되면, **mcp__sequential-thinking__sequentialthinking**을 사용하여 양쪽 결과를 통합한 **Agreed Draft Architecture** 문서를 생성합니다.

```markdown
# Draft Architecture: {review-id}

## System Architecture (Solution Architect)
[Solution Architect의 최종 합의안]

## Domain Model (Domain Architect)
[Domain Architect의 최종 합의안]

## Agreed Decisions
- [합의된 결정 사항 목록]

## Open Items
- [남은 논의 사항 — 있을 경우]
```

이 문서를 `review/{review-id}/draft-architecture.md`에 **Write tool**로 저장합니다.

#### Step 2-5: Draft 기반 아키텍트 라우팅 재결정

Draft Architecture 내용을 분석하여 **필요한 Tier 2/3/4 아키텍트를 선정**합니다.

Step 1의 키워드 기반 선정과 달리, **Draft 내용 기반**으로 정확한 선정이 가능합니다.

```yaml
routing_decision:
  tier2_design:
    - architect: "application-architect"
      reason: "Draft에서 MSA/레이어 구조 설계가 필요하므로"
    - architect: "data-architect"
      reason: "Draft에서 데이터 모델이 정의되었으므로"
  tier3_quality:
    - architect: "security-architect"
      reason: "인증/암호화 요구사항이 포함되어 있으므로"
    - architect: "sre-architect"
      reason: "SLO 및 모니터링 요구사항이 있으므로"
  tier4_enabling:
    - architect: "eda-specialist"
      reason: "이벤트 기반 통신이 설계에 포함되므로"
```

사용자에게 **선정된 아키텍트 목록과 이유**를 보여주고 진행합니다.

---

### Step 3: Specialist Review (Tier 2/3/4 병렬)

Step 2-5에서 선정된 아키텍트들에게 **Draft Architecture를 전달**하고 독립적으로 피드백을 받습니다.

#### 호출 패턴

선정된 모든 아키텍트를 **하나의 메시지에서 동시에 여러 Task를 호출**하여 병렬 실행합니다.

```
# 예: application-architect, data-architect, security-architect, sre-architect, eda-specialist가 선정된 경우
# 하나의 메시지에서 5개의 Task를 동시에 호출

Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "Application Architect 리뷰",
  prompt: """
  당신은 Application Architect입니다.

  [application-architect.md 페르소나 전체 삽입]

  ## 임무: Draft Architecture에 대한 전문 피드백

  Tier 1 아키텍트(Solution + Domain)가 합의한 Draft Architecture에 대해
  당신의 전문 영역 관점에서 **피드백과 권고사항**을 제시하세요.

  ## Draft Architecture
  [review/{review-id}/draft-architecture.md 내용 삽입]

  ## 집중 영역
  - 레이어 구조 설계 / Clean Architecture 적합성
  - 컴포넌트 분리 및 서비스 분해 전략
  - MSA/SAGA 패턴 적용 적절성
  - 내부 API 설계 및 의존성 방향

  ## 응답 형식 (Tiered Report — 반드시 3개 파트 모두 작성)

  ### Part 1: Executive Summary (Layer 1 — 500토큰 이내)
  ```yaml
  executive_summary:
    aid: "T2-APP-R1"
    vote: AGREE | DISAGREE | CONDITIONAL
    confidence: HIGH | MEDIUM | LOW
    one_liner: "핵심 결론 한 줄"
    top_findings:
      - "[권고/우려 1] [priority/severity]"
      - "[권고/우려 2] [priority/severity]"
      - "[권고/우려 3] [priority/severity]"
    changes:
      - target: "변경 대상"
        before: "Draft 원안"
        after: "제안하는 변경"
        rationale: "변경 이유"
  ```

  ### Part 2: Key Findings (Layer 2 — 2K토큰 이내)
  ```yaml
  key_recommendations:
    - id: R1
      priority: HIGH | MEDIUM | LOW
      category: DESIGN | SECURITY | PERFORMANCE | OPERATION | DATA | INTEGRATION | COMPLIANCE
      description: "권고 내용"
      rationale: "이유"

  key_concerns:
    - id: C1
      severity: HIGH | MEDIUM | LOW
      description: "우려 내용"
      impact: "영향"
      mitigation: "완화 방안"

  vote_detail:
    decision: AGREE | DISAGREE | CONDITIONAL
    rationale: "투표 이유"
    conditions: []
    alternatives: []
  ```

  ### Part 3: Full Report (Layer 3 — 제한 없음)
  상세 분석, 다이어그램, 코드 예시 등을 포함한 전체 리포트를 작성하세요.

  ## 코드베이스 참조
  필요시 Read, Grep, Glob 도구로 현재 코드베이스를 조사하세요.
  """
)

# 나머지 선정된 아키텍트들도 동일 패턴으로 동시 호출
# (각각의 페르소나, AID, 집중 영역만 변경)
```

#### 아키텍트별 AID 및 집중 영역

| 아키텍트 | AID | 집중 영역 |
|----------|-----|-----------|
| application-architect | T2-APP | 레이어 구조, 컴포넌트 분리, MSA/SAGA |
| data-architect | T2-DATA | 데이터 모델, 저장소 선택, CQRS, 쿼리 성능 |
| integration-architect | T2-INT | 외부 시스템 연동, API 설계, 메시징 패턴 |
| healthcare-informatics-architect | T2-HIA | FHIR/HL7 표준, HIPAA 준수, PHI 보호 |
| security-architect | T3-SEC | 인증/인가, 암호화, OWASP Top 10, 감사 로그 |
| sre-architect | T3-SRE | 운영 가능성, 모니터링, SLO 영향, 장애 복구 |
| cloud-native-architect | T3-CN | 12-Factor, 컨테이너, 스케일링, 배포 전략 |
| eda-specialist | T4-EDA | SAGA, Event Sourcing, 멱등성, DLQ |
| ml-platform-architect | T4-ML | MLOps, Model Serving, Feature Store |
| concurrency-architect | T4-CON | 락 전략, Reactor/Proactor, 경쟁 조건 |

#### 결과 수집

1. 각 아키텍트의 **Layer 1 (Executive Summary)** 을 `specialist_summaries` 변수로 수집
2. 각 아키텍트의 **Layer 2 (Key Findings)** 를 `specialist_findings` 변수로 수집
3. 각 아키텍트의 **Layer 3 (Full Report)** 를 `review/{review-id}/artifacts/{AID}-full-report.md`에 **Write tool**로 저장

#### Context 관리 (필수)

Specialist Review 완료 후 반드시 다음을 수행합니다:

1. **모든 Full Report가 파일에 Write되었는지 확인**
2. 메인 컨텍스트에는 **Layer 1 (Executive Summary)만 유지** — Layer 2/3은 파일 참조
3. **3명 이상 호출된 경우 `/compact` 실행** — 다수 Task 결과로 비대해진 컨텍스트 압축

> `/compact` 실행 후에도 `specialist_summaries` (Layer 1)는 compact 요약에 포함되므로 Step 4에서 활용 가능합니다. Layer 2가 필요한 경우 `artifacts/{AID}-full-report.md`에서 Read로 참조합니다.

---

### Step 4: Cross-Review — Mediator 방식

**Tier 1 아키텍트(중재자)**가 모든 Specialist 리포트를 수집·정리하여 Consolidated Findings를 생성하고, 이를 전 아키텍트에게 배포합니다.

> **왜 Mediator 방식인가?**
> - P2P 방식(각 아키텍트가 다른 모든 리포트를 직접 리뷰)은 O(n²) 토큰 폭증
> - Mediator 방식은 O(n) — 70% Context 절감
> - ATAM, CrewAI Hierarchical Process 등 실무에서도 검증된 패턴
> - Tier 1의 Strategic 판단력이 정리 품질을 보장

#### Step 4-1: Tier 1이 Consolidated Findings 생성

**mcp__sequential-thinking__sequentialthinking**을 사용하여 모든 Specialist 리포트를 분석하고 다음을 정리합니다:

```yaml
consolidated_findings:
  review_id: "{review-id}"
  round: {N}
  participants: ["T2-APP", "T2-DATA", ...]

  # 심각도별 Concern 집계
  concerns_by_severity:
    HIGH:
      - id: "CC-1"
        description: "우려 내용"
        raised_by: ["T2-DATA", "T3-SRE"]
        agreement: "2/5"
      - id: "CC-2"
        description: "..."
        raised_by: [...]
        agreement: "..."
    MEDIUM: [...]
    LOW: [...]

  # 카테고리별 Recommendation 클러스터링
  recommendations_by_category:
    DESIGN:
      - id: "CR-1"
        description: "권고 내용"
        proposed_by: ["T2-APP"]
        supported_by: ["T1-SA", "T2-DATA"]
    SECURITY: [...]
    PERFORMANCE: [...]

  # 충돌 지점
  conflicts:
    - id: "CF-1"
      topic: "충돌 주제"
      position_a:
        view: "A 입장"
        supporters: ["T2-APP", "T3-CN"]
      position_b:
        view: "B 입장"
        supporters: ["T2-INT"]
      proposed_resolution: "중재자 제안"

  # 합의된 사항
  agreed_points:
    - "합의 사항 1 (전원 동의)"
    - "합의 사항 2 (다수 동의)"

  # 소수 의견
  minority_opinions:
    - architect: "T2-INT"
      concern: "핵심 우려"
      severity: HIGH
      rationale: "반대 이유"

  # 투표 현황
  votes:
    AGREE: {N}
    CONDITIONAL: {N}
    DISAGREE: {N}
```

이 문서를 `review/{review-id}/consolidated-findings-r{N}.md`에 저장합니다.

#### Step 4-2: Consolidated Findings 기반 재리뷰 요청

Consolidated Findings 기반으로 **DISAGREE 또는 CONDITIONAL** 투표한 아키텍트를 재호출합니다.
AGREE 아키텍트는 입장 변경 사유가 없으므로 기존 투표를 유지합니다.

**재호출 조건**: DISAGREE 또는 CONDITIONAL 아키텍트가 1명 이상 존재하면 반드시 실행
**건너뛰기 조건**: 모든 아키텍트가 AGREE인 경우에만 건너뜀 (= UNANIMOUS)

```
# DISAGREE 또는 CONDITIONAL 아키텍트만 재호출 (효율성)
# AGREE 아키텍트는 입장 변경 사유가 없으므로 유지

Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "{architect-name} 재리뷰 R{N}",
  prompt: """
  당신은 {architect-name}입니다.
  [페르소나 삽입]

  ## 이전 라운드 투표
  [이 아키텍트의 이전 Layer 1 + Layer 2 삽입]

  ## Consolidated Findings
  [consolidated_findings 삽입]

  ## 요청
  1. Consolidated Findings를 검토하세요
  2. 당신의 우려사항이 적절히 반영되었는지 확인하세요
  3. 충돌 지점에 대한 중재자 제안에 동의하는지 판단하세요
  4. 입장을 유지하거나 변경하세요

  ## 응답 형식 (Layer 1만 — 500토큰 이내)
  ```yaml
  executive_summary:
    aid: "{AID}-R{N}"
    vote: AGREE | DISAGREE | CONDITIONAL
    confidence: HIGH | MEDIUM | LOW
    one_liner: "..."
    top_findings: [...]
    changes:
      - target: "..."
        before: "이전 라운드 입장"
        after: "변경된 입장 (있을 경우)"
        rationale: "변경 이유"
  ```
  """
)
```

---

### Step 5: Consensus Protocol

모든 리뷰 결과를 수집한 후, **mcp__sequential-thinking__sequentialthinking**을 사용하여 합의를 분석합니다.

#### Step 5-1: 투표 집계

```yaml
consensus_status:
  round: {N}
  total_architects: {N}
  votes:
    agree: {N}
    disagree: {N}
    conditional: {N}
  tier1_status:
    solution_architect: AGREE | DISAGREE | CONDITIONAL
    domain_architect: AGREE | DISAGREE | CONDITIONAL
```

#### Step 5-2: Tier 1 Veto 확인

- `solution-architect` 또는 `domain-architect`가 `DISAGREE`이면 → **BLOCKED_BY_TIER1**
- Tier 1 블록 시, 해당 아키텍트의 우려사항과 대안을 정리하여 재논의 진행

#### Step 5-0: CONDITIONAL 조건 충족 검증 (Pre-Consensus Gate)

Step 5 진입 전, CONDITIONAL 투표의 조건 충족 여부를 검증합니다.

```yaml
conditional_verification:
  for_each_conditional_vote:
    - architect: "{AID}"
      conditions: [이 아키텍트가 제시한 조건 목록]
      consolidated_response: "Consolidated Findings에서 해당 조건이 어떻게 반영되었는지"
      status: MET | PARTIALLY_MET | UNMET
      rationale: "판단 근거"
```

- **MET**: 조건이 합의에 명시적으로 반영되고 Action Item으로 추적 가능
- **PARTIALLY_MET**: 조건의 일부만 반영되었거나 우선순위가 기대보다 낮음
- **UNMET**: 조건이 반영되지 않았거나 거부됨

#### Step 5-3: 다수결 확인

```
합의 비율 = (AGREE + CONDITIONAL 중 status=MET) / 전체 참여 아키텍트 수
- PARTIALLY_MET → 0.5로 계산
- UNMET → 0으로 계산

- 비율 >= 1.0  → UNANIMOUS (만장일치, 즉시 완료)
- 비율 >= 0.67 → MAJORITY_WITH_MINORITY (소수의견 기록 후 완료)
- 비율 < 0.67  → NO_CONSENSUS (Step 4로 돌아가 재라운드)
```

#### Step 5-4: 미합의 시 재라운드 (최대 5라운드)

합의에 도달하지 못한 경우:
1. **Step 4로 돌아감** — 새로운 Consolidated Findings 생성
2. 충돌 해결 제안을 보강하여 재배포
3. **max_rounds(5) 초과 시**: 사용자에게 에스컬레이션

```
Consensus Loop:
  Step 3 → Step 4 → Step 5 → (미합의 시) → Step 4 → Step 5 → ...
                                                     (max 5 라운드)
```

---

### Step 6: 최종 문서 생성

합의가 완료되면 다음 형식으로 최종 아키텍처 문서를 생성합니다.

```markdown
# Architecture Review: {review-id}

## Overview
- **요청**: [원본 요구사항]
- **참여 아키텍트**: [목록 with AID]
- **합의 상태**: [UNANIMOUS / MAJORITY_WITH_MINORITY / ESCALATED]
- **총 라운드**: [N]

## Draft Architecture (Tier 1 합의)

### System Architecture
[Solution Architect의 최종 합의안]

### Domain Model
[Domain Architect의 최종 합의안]

## Specialist Feedback Summary

### Design Decisions (Tier 2)
[각 Design 아키텍트의 핵심 권고사항 요약 — AID 포함]

### Quality Assurance (Tier 3)
[각 Quality 아키텍트의 핵심 권고사항 요약 — AID 포함]

### Enabling (Tier 4)
[해당 아키텍트 핵심 권고사항 요약 — AID 포함]

## Consensus Summary

### Agreed Points
- [합의된 사항 목록]

### Resolved Conflicts
- [해결된 충돌 사항 — 어떤 입장이 채택되었는지]

### Minority Opinions
[소수 의견 기록 — 해당 시]
- architect: [AID]
- concern: [핵심 우려]
- severity: [HIGH/MEDIUM/LOW]
- rationale: [반대 이유]
- mitigation_suggested: [권고 완화 방안]
- follow_up: [향후 재검토 시점/조건]

## Action Items
| # | 항목 | 담당 | 우선순위 | 상태 |
|---|------|------|----------|------|
| 1 | ... | ... | HIGH | OPEN |

## Risks & Mitigations
| Risk | Impact | Likelihood | Mitigation | Raised By |
|------|--------|------------|------------|-----------|
| ... | ... | ... | ... | [AID] |

## Change Log
| Round | Architect | Change | Rationale |
|-------|-----------|--------|-----------|
| R1 | T1-SA | 초안 생성 | - |
| R1 | T1-DA | 도메인 모델 보강 | - |
| R1 | T2-APP | Hexagonal 적용 권고 | Clean Architecture 준수 |
| ... | ... | ... | ... |

## Artifacts
- Draft Architecture: `review/{review-id}/draft-architecture.md`
- Consolidated Findings: `review/{review-id}/consolidated-findings-r{N}.md`
- Full Reports: `review/{review-id}/artifacts/`
```

이 문서를 `review/{review-id}/final-review.md`에 **Write tool**로 저장합니다.

---

### Step 7: 실행 검증 (Post-Orchestration Verification)

오케스트레이션 완료 후, 모든 단계가 설계대로 실행되었는지 자동 검증합니다.

#### Step 7-1: 실행 체크리스트

**mcp__sequential-thinking__sequentialthinking**으로 다음 항목을 검증:

| # | 검증 항목 | 확인 방법 | PASS 기준 |
|---|----------|-----------|-----------|
| 1 | Draft Architecture 생성 | `draft-architecture.md` 존재 | 파일 존재 + SA/DA 섹션 포함 |
| 2 | Tier 1 교차 리뷰 실행 | Draft 내 교차 리뷰 결과 기록 | 합의 상태 명시 |
| 3 | Specialist 피드백 수집 | `artifacts/` 내 Full Report 파일 수 | 선정 아키텍트 수와 일치 |
| 4 | Consolidated Findings 생성 | `consolidated-findings-r{N}.md` 존재 | Vote Summary + Concern Clusters 포함 |
| 5 | Step 4-2 재호출 실행 여부 | CONDITIONAL/DISAGREE 존재 시 R2 산출물 확인 | 재호출 대상이 있었으면 R2 투표 결과 존재 |
| 6 | Consensus Protocol 실행 | final-review.md 내 Consensus Status | 합의 비율 + 판정 결과 명시 |
| 7 | 최종 문서 완성 | final-review.md 필수 섹션 | Agreed Points, Action Items, Risks 포함 |
| 8 | Context 관리 실행 | /compact 실행 횟수 확인 | Deep Research 후 + Step 3 후 (해당 시) |

#### Step 7-2: Execution Log

검증 결과를 `review/{review-id}/execution-log.md`에 기록:

```yaml
execution_log:
  review_id: "{review-id}"
  timestamp: "ISO8601"
  steps_executed:
    - step: "2-1"
      status: EXECUTED
      output: "draft-architecture.md"
    - step: "2-2"
      status: EXECUTED
      output: "draft-architecture.md (DA 보강)"
    - step: "2-3"
      status: EXECUTED
      rounds: 1
      result: "SA/DA AGREE"
    - step: "3"
      status: EXECUTED
      architects: ["APP", "DATA", "INT", "SRE", "CN", "EDA"]
      output: "artifacts/*.md (6 files)"
    - step: "4-1"
      status: EXECUTED
      output: "consolidated-findings-r1.md"
    - step: "4-2"
      status: EXECUTED | SKIPPED
      reason: "CONDITIONAL 6명 재호출" | "모든 아키텍트 AGREE (UNANIMOUS)"
      output: "consolidated-findings-r2.md" | null
    - step: "5"
      status: EXECUTED
      rounds: 1
      result: "UNANIMOUS | MAJORITY_WITH_MINORITY"
    - step: "6"
      status: EXECUTED
      output: "final-review.md"
  context_management:
    compact_executed:
      - after: "step-1.5"
        reason: "Deep Research 완료"
      - after: "step-3"
        reason: "Specialist 6명 호출 완료"
    files_saved: 12
    layer1_only_in_context: true
  verification:
    total_checks: 8
    passed: 7
    failed: 0
    result: PASS | FAIL
    failures: []
```

#### Step 7-3: 실패 시 처리

- FAIL 항목 발견 시 → 누락된 단계를 명시하고 보완 실행 여부를 사용자에게 확인
- 사용자 승인 시 → 누락 단계만 보완 실행
- 사용자 거부 시 → execution-log.md에 "ACKNOWLEDGED_SKIP" 기록

---

## 설정 옵션

사용자가 요구사항과 함께 설정을 지정할 수 있습니다:

```yaml
# 기본 설정 (별도 지정 없으면 이 값 사용)
orchestration:
  max_consensus_rounds: 5       # 최대 합의 라운드 (Step 4-5 루프)
  max_tier1_rounds: 3           # 최대 Tier 1 교차 리뷰 라운드
  consensus_threshold: 0.67     # 합의 기준 (2/3)
  tier1_required: true          # Tier 1 필수 동의 (veto권)
  auto_escalate: true           # 미합의 시 사용자 에스컬레이션
  auto_verify: true             # 자동 검증 실행 (Step 7)
  execution_log: true           # 실행 로그 기록

# 빠른 리뷰 프로필
fast_review:
  max_consensus_rounds: 1
  max_tier1_rounds: 1
  consensus_threshold: 0.5

# 철저한 리뷰 프로필
thorough_review:
  max_consensus_rounds: 10
  max_tier1_rounds: 5
  consensus_threshold: 0.8

# 중요 결정 프로필
critical_decision:
  max_consensus_rounds: 15
  max_tier1_rounds: 5
  consensus_threshold: 1.0   # 만장일치
```

---

## 에러 처리

### 아키텍트 응답 실패
- Task 실패 시 1회 재시도
- 재시도 실패 시 해당 아키텍트 제외, 사유를 최종 문서에 기록

### 합의 실패 (max_rounds 초과)
- 현재까지 결과를 에스컬레이션 보고서로 정리
- 충돌 지점을 명시하고 사용자에게 결정 요청

### Layer 형식 미준수
- 아키텍트 응답이 Tiered Report 형식을 따르지 않을 경우, Layer 1을 수동으로 추출/요약

---

## Context 절감 효과

```
이전 방식 (교차 리뷰 없음, 1라운드):
  오케스트레이터 Context ≈ 8 × 5K = 40K 토큰
  → Context 폭발 → 세션 초기화

개선 후 (Mediator + Tiered Output + Context Management Protocol):
  Step 1.5 Deep Research: 결과 파일 저장 + /compact → context 초기화
  Step 2 Draft: draft-architecture.md 파일 참조 ≈ 0 (Read 시에만)
  Step 3 리포트 수집: 8 × 500 (Layer 1만) = 4K 토큰
  Step 3 완료 후: Full Report 파일 저장 + /compact → context 압축
  Step 4 중재 정리: Consolidated Findings ≈ 3K 토큰
  Step 4 재배포: 각 에이전트에 3K + Draft 참조 = 5K 토큰
  Step 5 합의: 재투표 결과 ≈ 1K 토큰
  ────────────
  오케스트레이터 피크 Context ≈ 8K 토큰 (compact 후 기준)
  Deep Research 포함 시에도 안정적 실행 가능

  필요 시 Layer 2/3는 파일에서 Read로 참조
```

---

## 관련 문서

- `architect-registry.md` — 12개 아키텍트 상세 정보, 역량, 키워드
- `routing-strategy.md` — 라우팅 전략, 키워드 매핑, 시나리오 예시
- `consensus-protocol.md` — 합의 프로토콜, 투표 시스템, 충돌 해결
