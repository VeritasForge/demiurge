---
name: architect-orchestration
description: 12개 아키텍트 에이전트를 오케스트레이션하여 합의된 아키텍처 설계를 도출. /architect-orchestration 으로 실행.
allowed-tools: Read, Grep, Glob, Task, WebSearch, WebFetch
---

# Architect Orchestration Skill

## Overview

이 스킬은 사용자의 아키텍처 요구사항을 분석하고, 12개의 전문 아키텍트 에이전트를 **Task tool**로 spawn하여 단계적 검토와 합의를 도출합니다.

**핵심 원리**: 이 스킬은 main conversation context에서 실행되므로 Task tool을 사용하여 subagent를 spawn할 수 있습니다.

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

### Step 1: 요구사항 분석 (Phase 0)

**mcp__sequential-thinking__sequentialthinking**을 사용하여 다음을 분석합니다:

1. **키워드 추출**: 요구사항에서 아키텍처 관련 키워드를 추출
2. **아키텍트 선택**: routing-strategy.md의 키워드 매핑에 따라 관련 아키텍트 결정
3. **실행 계획**: 어떤 아키텍트를 어떤 Phase에서 호출할지 결정

#### 아키텍트 선택 규칙

- **Tier 1 (필수)**: `solution-architect`, `domain-architect` — 항상 포함
- **Tier 2 (조건부)**: 키워드 매칭된 Design 아키텍트만
- **Tier 3 (조건부)**: 키워드 매칭된 Quality 아키텍트만
- **Tier 4 (온디맨드)**: 특수 요구 시에만

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

분석이 끝나면 사용자에게 **선택된 아키텍트 목록과 실행 계획**을 요약하여 보여주고 진행합니다.

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
   - 각 Agent는 자기 도메인에 관련된 발견을 기반으로 Phase 2 (심화 탐색) 수행 가능

4. **최종 문서 생성 시 Phase 3 (지식 합성) 수행**:
   - Step 7에서 Research 결과를 통합하여 출처 인용 및 확신도 태깅 포함

#### 건너뛰기 조건

다음의 경우 Step 1.5를 **건너뛰고** Step 2로 직행합니다:
- 코드 리뷰, 리팩토링 등 기존 코드베이스에 대한 검토
- 잘 정립된 패턴에 대한 적용 검토 (별도 조사 불필요)
- 사용자가 빠른 리뷰를 요청한 경우

---

### Step 2: Phase 1 — Strategic Review (Sequential)

Tier 1 아키텍트를 **순차적으로** 호출합니다. 이전 결과가 다음 입력에 영향을 줍니다.

#### Step 2-1: Solution Architect 호출

1. `.claude/agents/solution-architect.md`를 **Read**로 읽어 페르소나를 확보
2. **Task tool**로 spawn:

```
Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "Solution Architect 리뷰",
  prompt: """
  당신은 Solution Architect입니다.

  [여기에 solution-architect.md에서 읽은 페르소나 전체 삽입]

  ## 검토 요구사항
  [사용자의 원본 요구사항]

  ## 응답 형식
  아래 YAML 형식으로 응답하세요:

  ```yaml
  architect: solution-architect
  timestamp: [현재 시각 ISO8601]
  round: 1

  recommendations:
    - id: R1
      category: DESIGN | SECURITY | PERFORMANCE | OPERATION
      priority: HIGH | MEDIUM | LOW
      description: "권고 내용"
      rationale: "이유"

  concerns:
    - id: C1
      severity: HIGH | MEDIUM | LOW
      description: "우려 내용"
      impact: "영향"
      mitigation: "완화 방안"

  dependencies:
    - type: REQUIRES | CONFLICTS_WITH | ENHANCES
      target: "대상"
      description: "설명"

  vote:
    decision: AGREE | DISAGREE | CONDITIONAL
    confidence: HIGH | MEDIUM | LOW
    rationale: "투표 이유"
    conditions: []   # CONDITIONAL인 경우
    alternatives: [] # DISAGREE인 경우
  ```

  ## 집중 영역
  - 전체 아키텍처 적합성
  - 기술 선택 타당성
  - 품질 속성 영향 (성능, 확장성, 가용성)
  - TOGAF ADM 관점 검토

  ## 코드베이스 참조
  필요시 Read, Grep, Glob 도구로 현재 코드베이스를 조사하여 기존 아키텍처와의 정합성을 확인하세요.
  """
)
```

3. 결과를 `phase1_solution_result` 변수로 저장

#### Step 2-2: Domain Architect 호출

1. `.claude/agents/domain-architect.md`를 **Read**로 읽어 페르소나를 확보
2. **Task tool**로 spawn (Phase 1 결과를 컨텍스트로 전달):

```
Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "Domain Architect 리뷰",
  prompt: """
  당신은 Domain Architect입니다.

  [여기에 domain-architect.md에서 읽은 페르소나 전체 삽입]

  ## 검토 요구사항
  [사용자의 원본 요구사항]

  ## 이전 단계 결과 (Solution Architect)
  [phase1_solution_result 삽입]

  ## 응답 형식
  [위와 동일한 YAML 형식]

  ## 집중 영역
  - Bounded Context 식별
  - Aggregate 경계 설계
  - Ubiquitous Language 일관성
  - Domain Events 모델링
  - Solution Architect의 전략적 방향과의 정합성

  ## 코드베이스 참조
  필요시 Read, Grep, Glob 도구로 현재 코드베이스를 조사하세요.
  """
)
```

3. 결과를 `phase1_domain_result` 변수로 저장

---

### Step 3: Phase 2 — Design Review (Parallel)

Step 1에서 선택된 Tier 2 아키텍트들을 **하나의 메시지에서 동시에 여러 Task를 호출**하여 병렬 실행합니다.

#### 호출 패턴

선택된 각 Tier 2 아키텍트에 대해:

1. 해당 에이전트의 `.claude/agents/{name}.md`를 **Read**로 읽기
2. **단일 메시지에서 여러 Task를 동시 호출**:

```
# 예: application-architect, integration-architect, healthcare-informatics-architect가 선택된 경우
# 하나의 메시지에서 3개의 Task를 동시에 호출

Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "Application Architect 리뷰",
  prompt: """
  당신은 Application Architect입니다.
  [페르소나 삽입]

  ## 검토 요구사항
  [원본 요구사항]

  ## Phase 1 결과
  ### Solution Architect
  [phase1_solution_result]
  ### Domain Architect
  [phase1_domain_result]

  ## 응답 형식
  [표준 YAML 형식]

  ## 집중 영역
  - 레이어 구조 설계
  - 컴포넌트 분리
  - 서비스 분해 전략
  - Clean Architecture / Hexagonal Architecture 적합성
  """
)

Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "Integration Architect 리뷰",
  prompt: """...[동일 패턴, integration-architect 페르소나와 집중 영역]..."""
)

Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "Healthcare Informatics Architect 리뷰",
  prompt: """...[동일 패턴, healthcare-informatics-architect 페르소나와 집중 영역]..."""
)
```

3. 모든 결과를 수집하여 `phase2_results` 변수로 저장

#### Tier 2 아키텍트별 집중 영역

| 아키텍트 | 집중 영역 |
|----------|-----------|
| application-architect | 레이어 구조, 컴포넌트 분리, MSA/SAGA 패턴 |
| data-architect | 데이터 모델, 저장소 선택, CQRS, 쿼리 성능 |
| integration-architect | 외부 시스템 연동, API 설계, 메시징 패턴 |
| healthcare-informatics-architect | FHIR/HL7 표준, HIPAA 준수, PHI 보호 |

---

### Step 4: Phase 3 — Quality Review (Parallel)

Step 1에서 선택된 Tier 3 아키텍트들을 **Phase 2와 동일한 패턴으로 병렬 호출**합니다.

#### 호출 패턴

Phase 2와 동일하되, Phase 1 + Phase 2 결과를 모두 컨텍스트로 전달:

```
Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "Security Architect 리뷰",
  prompt: """
  당신은 Security Architect입니다.
  [페르소나 삽입]

  ## 검토 요구사항
  [원본 요구사항]

  ## Phase 1 결과
  [phase1 결과 요약]

  ## Phase 2 결과
  [phase2 결과 요약]

  ## 응답 형식
  [표준 YAML 형식]

  ## 집중 영역
  - 인증/인가 설계
  - 데이터 암호화 적절성
  - OWASP Top 10 취약점 검토
  - 감사 로그
  """
)
```

#### Tier 3 아키텍트별 집중 영역

| 아키텍트 | 집중 영역 |
|----------|-----------|
| security-architect | 인증/인가, 암호화, OWASP Top 10, 감사 로그 |
| sre-architect | 운영 가능성, 모니터링, SLO 영향, 장애 복구 |
| cloud-native-architect | 12-Factor, 컨테이너, 스케일링, 배포 전략 |

---

### Step 5: Phase 4 — Enabling Review (On-demand, 필요 시)

Step 1에서 Tier 4 아키텍트가 선택된 경우에만 실행합니다. Phase 2/3과 동일한 병렬 호출 패턴을 사용합니다.

#### Tier 4 아키텍트별 집중 영역

| 아키텍트 | 호출 조건 | 집중 영역 |
|----------|-----------|-----------|
| eda-specialist | 이벤트/비동기 처리 요구 | SAGA, Event Sourcing, 멱등성 |
| ml-platform-architect | AI/ML 모델 관련 요구 | MLOps, Model Serving, Feature Store |
| concurrency-architect | 동시성/병렬 처리 요구 | 락 전략, Reactor/Proactor, 경쟁 조건 |

---

### Step 6: Consensus Protocol

모든 Phase의 응답을 수집한 후, **mcp__sequential-thinking__sequentialthinking**을 사용하여 합의를 분석합니다.

#### Step 6-1: 투표 집계

```yaml
# 각 아키텍트의 vote.decision을 집계
status:
  total_architects: N
  agree: [AGREE 수]
  disagree: [DISAGREE 수]
  conditional: [CONDITIONAL 수]
```

#### Step 6-2: Tier 1 Veto 확인

- `solution-architect` 또는 `domain-architect`가 `DISAGREE`이면 → **BLOCKED_BY_TIER1**
- Tier 1 블록 시, 해당 아키텍트의 우려사항과 대안을 정리하여 재논의 진행

#### Step 6-3: 다수결 확인

```
합의 비율 = AGREE 수 / 전체 참여 아키텍트 수

- 비율 >= 1.0  → UNANIMOUS (만장일치, 즉시 완료)
- 비율 >= 0.67 → MAJORITY_WITH_MINORITY (소수의견 기록 후 완료)
- 비율 < 0.67  → NO_CONSENSUS (재투표 필요)
```

#### Step 6-4: 미합의 시 재투표 (최대 5라운드)

합의에 도달하지 못한 경우:

1. **통합 제안 작성**: 합의 지점 + 충돌 해결 제안을 정리
2. **DISAGREE/CONDITIONAL 아키텍트만 재호출**:
   - 통합 제안과 다른 아키텍트의 의견을 컨텍스트로 전달
   - 입장 변경 여부 확인
3. **재집계**: 위 Step 6-1 ~ 6-3 반복
4. **max_rounds(5) 초과 시**: 사용자에게 에스컬레이션

```
Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "[architect-name] 재투표",
  prompt: """
  당신은 [architect-name]입니다.
  [페르소나]

  ## 이전 라운드 투표
  [이 아키텍트의 이전 투표 내용]

  ## 통합 제안
  [합의 지점 + 충돌 해결 제안]

  ## 다른 아키텍트 의견
  [관련 아키텍트들의 의견 요약]

  ## 요청
  통합 제안을 검토하고 재투표해주세요.
  이전 우려가 해결되었는지 확인하고, 입장을 유지하거나 변경하세요.

  ## 응답 형식
  [표준 YAML 형식, round: N]
  """
)
```

---

### Step 7: 최종 문서 생성

합의가 완료되면 다음 형식으로 최종 아키텍처 문서를 생성합니다:

```markdown
# Architecture Review: [요구사항 제목]

## Overview
- **요청**: [원본 요구사항]
- **참여 아키텍트**: [목록]
- **합의 상태**: [UNANIMOUS / MAJORITY_WITH_MINORITY / ESCALATED]
- **총 라운드**: [N]

## Strategic Direction (Tier 1)

### Solution Architecture
[solution-architect의 권고사항 요약]

### Domain Model
[domain-architect의 권고사항 요약]

## Design Decisions (Tier 2)

### Application Architecture
[application-architect 권고사항 - 참여 시]

### Data Architecture
[data-architect 권고사항 - 참여 시]

### Integration Architecture
[integration-architect 권고사항 - 참여 시]

### Healthcare Compliance
[healthcare-informatics-architect 권고사항 - 참여 시]

## Quality Assurance (Tier 3)

### Security
[security-architect 권고사항 - 참여 시]

### Operations (SRE)
[sre-architect 권고사항 - 참여 시]

### Cloud Native
[cloud-native-architect 권고사항 - 참여 시]

## Enabling (Tier 4)
[해당 아키텍트 권고사항 - 참여 시]

## Consensus Summary

### Agreed Points
- [합의된 사항 목록]

### Resolved Conflicts
- [해결된 충돌 사항]

### Minority Opinions
[소수 의견 기록 - 해당 시]
- architect: [name]
- concern: [핵심 우려]
- severity: [HIGH/MEDIUM/LOW]
- mitigation_suggested: [권고 완화 방안]

## Action Items
| # | 항목 | 담당 | 우선순위 | 상태 |
|---|------|------|----------|------|
| 1 | ... | ... | HIGH | OPEN |

## Risks & Mitigations
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| ... | ... | ... | ... |
```

---

## 설정 옵션

사용자가 요구사항과 함께 설정을 지정할 수 있습니다:

```yaml
# 기본 설정 (별도 지정 없으면 이 값 사용)
orchestration:
  max_rounds: 5              # 최대 투표 라운드
  consensus_threshold: 0.67  # 합의 기준 (2/3)
  tier1_required: true       # Tier 1 필수 동의 (veto권)
  auto_escalate: true        # 미합의 시 사용자 에스컬레이션

# 빠른 리뷰 프로필
fast_review:
  max_rounds: 1
  consensus_threshold: 0.5

# 철저한 리뷰 프로필
thorough_review:
  max_rounds: 10
  consensus_threshold: 0.8

# 중요 결정 프로필
critical_decision:
  max_rounds: 15
  consensus_threshold: 1.0  # 만장일치
```

---

## 에러 처리

### 아키텍트 응답 실패
- Task 실패 시 1회 재시도
- 재시도 실패 시 해당 아키텍트 제외, 사유를 최종 문서에 기록

### 합의 실패 (max_rounds 초과)
- 현재까지 결과를 에스컬레이션 보고서로 정리
- 충돌 지점을 명시하고 사용자에게 결정 요청

---

## 관련 문서

- `architect-registry.md` — 12개 아키텍트 상세 정보, 역량, 키워드
- `routing-strategy.md` — 라우팅 전략, 키워드 매핑, 시나리오 예시
- `consensus-protocol.md` — 합의 프로토콜, 투표 시스템, 충돌 해결
