# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **multi-agent architecture governance template** for Claude Code. It contains no source code — only agent definitions, rules, and skill references that enable collaborative architectural reviews through orchestrated specialist agents.

## AI 사고 프로세스 (Chain of Thought)

복잡한 문제 해결이나 설계 결정이 필요한 경우, 반드시 `sequentialthinking` MCP 도구를 사용하여
논리적 흐름을 단계별로 구성하고 스스로 검증해야 합니다.

1. **상황 분석**: 현재 요청과 관련된 컨텍스트, 제약 조건, 관련 파일들을 파악
2. **전략 수립**: 가능한 해결책들을 나열하고 장단점을 비교하여 최적의 전략 선택
3. **단계별 계획**: 선택한 전략을 실행하기 위한 구체적인 단계(Step-by-step) 정의
4. **검증 및 회고**: 계획이 요구사항을 충족하는지, 누락된 부분은 없는지 검토

## 응답 가이드라인

AI가 답변 시 준수할 원칙:

1. 항상 맥락을 고려할 것
2. 다양한 관점에서 바라볼 것
3. 개발자로서 알아둬야 할 것들을 정리할 것
4. 단계별로 설명할 것
5. 예를 들어 설명할 것
6. 대안이나 추가로 확인해야 하는 부분도 제시할 것
7. 12살이라고 가정하고, 현실 세계의 사물에 비유해서 설명할 것
8. 답변을 도출해내는 논리와 과정을 보여줄 것 (왜 이러한 답변인지 기준 제시)
9. 이해가 안 되는 부분이 있으면 반드시 물어볼 것
10. 사고 과정에서 사용한 skills, agents 등의 호출/상호작용을 ASCII graph/table로 설명할 것

## Repository Structure

- `.claude/agents/` — 12 architect agent definitions
- `.claude/rules/` — 8 governance rules auto-applied based on file glob patterns
- `.claude/skills/` — 16 quick-reference skill cards for architecture patterns
- `.claude/commands/` — Slash commands (`commit`, `rl`, `wrap`)

## Orchestration Flow

```
[Requirement] → [Analysis] → [Deep Research?] → [Draft Phase] → [Specialist Feedback] → [Cross-Review] → [Consensus] → [Result] → [Verification]
                  Step 1        Step 1.5            Step 2            Step 3                 Step 4          Step 5        Step 6       Step 7
                                (Optional)       (Tier 1 Sequential   (Tier 2/3/4           (Mediator        (Multi-round              (Post-Orch
                                                  + 교차 리뷰)        Parallel)              Pattern)         Loop)                     Verify)
```

### Detailed Step Flow

```
Step 0: 참조 문서 로드
Step 1: 요구사항 분석 (키워드 추출, review-id 생성)
Step 1.5: Deep Research (선택적)

═══ Draft Phase ═══
Step 2-1: Solution Architect → 시스템 아키텍처 초안 생성
Step 2-2: Domain Architect → Draft에 도메인 모델 보강
Step 2-3: Tier 1 교차 리뷰 (SA ↔ DA, max 3 라운드)
Step 2-4: 합의된 Draft Architecture 문서 생성
Step 2-5: Draft 기반 Tier 2/3/4 아키텍트 라우팅 재결정

═══ Specialist Feedback Phase ═══
Step 3: 선정된 아키텍트들에게 Draft 전달 → 병렬 피드백 (Tiered Report)

═══ Cross-Review Phase (Mediator) ═══
Step 4-1: Tier 1 중재자가 모든 리포트 수집·정리 → Consolidated Findings
Step 4-2: Consolidated Findings 기반 재리뷰 + 재투표

═══ Consensus Phase ═══
Step 5: 투표 집계 → 합의 미달 시 Step 4 재진입 (max 5 라운드)

Step 6: 최종 문서 생성

═══ Verification Phase ═══
Step 7: 실행 검증 (Post-Orchestration Verification)
  Step 7-1: 실행 체크리스트 (7개 항목 자동 검증)
  Step 7-2: Execution Log 기록 (review/{review-id}/execution-log.md)
  Step 7-3: 실패 시 보완 실행 or ACKNOWLEDGED_SKIP
```

### Agent Tiers

| Tier | Agents | Role | Execution |
|------|--------|------|-----------|
| **1 Strategic** (required) | Solution Architect, Domain Architect | Draft 생성 + 교차 리뷰 + 중재자 | Sequential |
| **2 Design** (conditional) | Application, Data, Integration, Healthcare Informatics | Specialist Feedback | Parallel |
| **3 Quality** (conditional) | Security, SRE, Cloud-Native | Specialist Feedback | Parallel |
| **4 Enabling** (on-demand) | EDA Specialist, ML Platform, Concurrency | Specialist Feedback | On-demand |

### AID (Architect ID) 체계

모든 아키텍트 리포트에 출처와 라운드를 추적하는 AID가 포함됩니다.

```
형식: "{Tier}-{Role}-R{Round}"
예시: T1-SA-R1, T1-DA-R2, T2-APP-R1, T3-SEC-R1, T4-EDA-R1
```

### Tiered Report Template

Context 비대화 방지를 위해 3단계 계층 출력을 사용합니다.

| Layer | 용도 | 크기 제한 | 전달 범위 |
|-------|------|-----------|-----------|
| **Layer 1** Executive Summary | 투표 + 핵심 발견 + 변경이력 | 500토큰 | 항상 전달 |
| **Layer 2** Key Findings | 권고·우려·투표상세 | 2K토큰 | 교차 리뷰 시 |
| **Layer 3** Full Report | 상세 분석·다이어그램·코드 | 제한 없음 | artifact 파일 저장 |

### Cross-Review: Mediator 패턴

- P2P 방식(O(n²)) 대신 Mediator 방식(O(n)) 채택 — 70% Context 절감
- Tier 1 아키텍트가 중재자로서 모든 리포트를 수집·정리
- Consolidated Findings 생성 (Concern 집계, Recommendation 클러스터링, 충돌 명시, 소수 의견 기록)

### Consensus Protocol

- Threshold: 2/3 agreement (67%)
- Tier 1 architects hold veto power
- Maximum 5 consensus rounds (Step 4-5 loop)
- Maximum 3 Tier 1 cross-review rounds (Step 2-3)
- Minority opinions are recorded
- DISAGREE 또는 CONDITIONAL 아키텍트만 재호출 (1명 이상 존재 시 반드시 실행)
- Step 5-0: CONDITIONAL 조건 충족 검증 (MET/PARTIALLY_MET/UNMET) — Pre-Consensus Gate

## Agents (12개)

### Core Architecture Agents

| Agent | 역할 | 핵심 지식 |
|-------|------|-----------|
| `solution-architect` | 전체 시스템 아키텍처 | TOGAF ADM, POSA, 품질 속성 |
| `domain-architect` | 도메인 중심 설계 | DDD Strategic/Tactical Design |
| `application-architect` | 애플리케이션 구조 | Clean Architecture, Hexagonal, MSA |
| `eda-specialist` | 이벤트 기반 아키텍처 | SAGA, Event Sourcing, CQRS |
| `concurrency-architect` | 동시성 패턴 | POSA Vol.2, Reactor/Proactor |
| `cloud-native-architect` | 클라우드 네이티브 | 12-Factor, Kubernetes, Service Mesh |

### Domain-Specific Agents

| Agent | 역할 | 핵심 지식 |
|-------|------|-----------|
| `data-architect` | 데이터 아키텍처 | DAMA-DMBOK, CQRS, Data Mesh |
| `integration-architect` | 시스템 통합 | EIP, API Gateway, Message Broker |
| `security-architect` | 보안 아키텍처 | OWASP, Zero Trust, NIST |
| `sre-architect` | 운영 아키텍처 | SRE, Observability, SLO |
| `ml-platform-architect` | ML 플랫폼 | MLOps, Feature Store |
| `healthcare-informatics-architect` | 의료 정보 | HL7 FHIR, HIPAA |

## Skills (16개)

### Orchestration

| Skill | 내용 |
|-------|------|
| `architect-orchestration` | 다중 아키텍트 오케스트레이션, 라우팅 전략, 합의 프로토콜 |
| `deep-research` | 3단계 심층 조사 프로토콜 (광역 탐색, 심화 탐색, 지식 합성) |

### Architecture Patterns

| Skill | 내용 |
|-------|------|
| `solution-architecture` | TOGAF, POSA, ADR, 품질 속성 |
| `domain-driven-design` | Bounded Context, Aggregate, ACL, Specification |
| `application-architecture` | Clean Architecture, Hexagonal, MSA/SAGA |
| `eda` | Event Patterns, SAGA, Idempotency, DLQ |
| `concurrency-patterns` | Reactor, Proactor, Active Object, Thread Pool |
| `cloud-native` | 12-Factor, K8s Patterns, Deployment Strategies |
| `api-design` | Richardson Model, Versioning, Contract-First |
| `testing-architecture` | Test Pyramid, Contract Testing, TDD/BDD |

### Domain-Specific Skills

| Skill | 내용 |
|-------|------|
| `data-architecture` | DAMA-DMBOK, CQRS, Event Sourcing, Data Mesh |
| `integration` | EIP, API Gateway, Event-Driven |
| `security` | OWASP, Zero Trust, Encryption |
| `sre` | SRE Principles, SLO/SLI, Observability |
| `ml-platform` | MLOps, Model Serving, Feature Store |
| `healthcare-informatics` | HL7 FHIR, HIPAA, Medical Terminology |

## Rules Auto-Application (8개)

Rules in `.claude/rules/` are automatically loaded based on file path globs:

| Rule | Trigger Paths | Content |
|------|---------------|---------|
| `architecture-principles` | `**/*.py`, `**/*.kt`, `**/*.java`, `**/*.ts`, `**/*.tsx`, `**/*.go` | SoC, DDD, MSA, EDA, security principles |
| `security-requirements` | `**/*.py`, `**/*.kt`, `**/*.java`, `**/*.ts` | JWT, encryption, input validation, API security |
| `ddd-patterns` | `**/domain/**`, `**/entities/**`, `**/aggregate/**` | Entity, VO, Aggregate, Repository, ACL |
| `api-design` | `**/controller/**`, `**/router/**`, `**/api/**` | Richardson Model, versioning, rate limiting |
| `cloud-native` | `**/Dockerfile`, `**/k8s/**`, `**/helm/**` | 12-Factor, containers, resilience |
| `messaging-patterns` | messaging/event-related service paths | Idempotency, DLQ, event schema |
| `healthcare-compliance` | `**/*.py`, `**/*.kt`, `**/*.java` | HIPAA, FDA SaMD, PHI protection |
| `architect-review` | all code files | Review standards, voting, conflict resolution |

## Coverage Matrix

### 아키텍처 패턴 커버리지

| 영역 | 패턴/프레임워크 | Agent | Skill | Rule |
|------|-----------------|-------|-------|------|
| **Enterprise** | TOGAF ADM | ✅ | ✅ | - |
| | POSA Vol.1 | ✅ | ✅ | - |
| | POSA Vol.2 (Concurrency) | ✅ | ✅ | - |
| **Domain** | DDD Strategic Design | ✅ | ✅ | - |
| | DDD Tactical Design | ✅ | ✅ | ✅ |
| | Anti-Corruption Layer | ✅ | ✅ | ✅ |
| | Specification Pattern | - | ✅ | ✅ |
| **Application** | Clean Architecture | ✅ | ✅ | ✅ |
| | Hexagonal Architecture | ✅ | ✅ | - |
| | CQRS | ✅ | ✅ | - |
| | Event Sourcing | ✅ | ✅ | - |
| **MSA** | SAGA (Choreography) | ✅ | ✅ | - |
| | SAGA (Orchestration) | ✅ | ✅ | - |
| | Circuit Breaker | ✅ | ✅ | ✅ |
| | API Gateway | ✅ | ✅ | - |
| **EDA** | Event Notification | ✅ | ✅ | ✅ |
| | Event-Carried State | ✅ | ✅ | - |
| | Event Sourcing | ✅ | ✅ | - |
| **Cloud-Native** | 12-Factor App | ✅ | ✅ | ✅ |
| | K8s Patterns (Sidecar, etc.) | ✅ | ✅ | - |
| | Service Mesh | ✅ | ✅ | - |
| | Deployment (Blue-Green, Canary) | ✅ | ✅ | - |
| **API** | Richardson Maturity Model | - | ✅ | ✅ |
| | Contract-First Design | - | ✅ | ✅ |
| | Rate Limiting | - | ✅ | ✅ |
| **Testing** | Test Pyramid | - | ✅ | - |
| | Contract Testing | - | ✅ | - |
| | TDD/BDD | - | ✅ | - |
| **Concurrency** | Reactor/Proactor | ✅ | ✅ | - |
| | Active Object | ✅ | ✅ | - |
| | Half-Sync/Half-Async | ✅ | ✅ | - |
| **Data** | DAMA-DMBOK | ✅ | ✅ | - |
| | Data Mesh | ✅ | ✅ | - |
| **Research** | Deep Research Protocol | ✅ (12 agents) | ✅ | - |

## Usage

Use the **orchestrator skill** for complex, cross-cutting architecture decisions:
```
/architect-orchestration 스킬을 실행하여 요구사항 분석 및 다중 아키텍트 리뷰 수행
```

Use **individual agents** for focused reviews:
```
domain-architect: 도메인 모델 및 Bounded Context 검토
security-architect: 보안 위협 분석 및 암호화 검증
solution-architect: 전체 시스템 아키텍처 설계
```

Reference **skills** for quick pattern lookups:
```
.claude/skills/domain-driven-design/SKILL.md
.claude/skills/eda/SKILL.md
.claude/skills/cloud-native/SKILL.md
```

Use **`/wrap`** to validate and sync documentation:
```
/wrap          # 분석 + 불일치 감지 + CLAUDE.md 업데이트
/wrap --check  # 분석 + 불일치 감지만 (수정 없음)
```

## Version & Changelog

- Created: 2026-01-27
- Last Updated: 2026-01-30
- Version: 4.1

### Changelog

- v4.1: Step 4-2 버그 수정 + Step 5-0 Pre-Consensus Gate + Step 7 자기검증 메커니즘
  - Step 4-2 재호출 조건 명확화: "DISAGREE/CONDITIONAL" → "DISAGREE 또는 CONDITIONAL" (1명 이상 존재 시 반드시 실행)
  - Step 5-0 (Pre-Consensus Gate) 추가: CONDITIONAL 조건 충족 검증 (MET/PARTIALLY_MET/UNMET)
  - consensus-protocol.md 판정 알고리즘에 CONDITIONAL 처리 추가 (effective_agrees 계산)
  - Step 7 (Post-Orchestration Verification) 추가: 7개 항목 실행 체크리스트 + execution-log.md + 실패 시 보완
  - 설정 옵션에 `auto_verify`, `execution_log` 추가
  - Orchestration Flow 다이어그램에 Step 7 반영
  - `/wrap` 동기화
- v4.0: Architect-Orchestration 재설계 — Draft → Cross-Review → Consensus 멀티라운드 구조
  - SKILL.md 전면 재작성: Draft Phase (Step 2), Specialist Feedback (Step 3), Cross-Review (Step 4), Consensus Loop (Step 5)
  - Draft Phase: Tier 1이 "리뷰"가 아닌 "설계" 역할 — Solution Architect 초안 + Domain Architect 보강
  - Tier 1 교차 리뷰: SA ↔ DA 합의 라운드 (max 3회)
  - Draft 기반 라우팅: 키워드 기반이 아닌 Draft 내용 분석으로 Tier 2/3/4 선정
  - Cross-Review Mediator 패턴: Tier 1이 중재자로 Consolidated Findings 생성 (70% Context 절감)
  - AID (Architect ID) 체계: `{Tier}-{Role}-R{Round}` 형식으로 출처·라운드 추적
  - Tiered Report Template: Layer 1 (500토큰) / Layer 2 (2K토큰) / Layer 3 (무제한, artifact 저장)
  - Changes 섹션: structured changelog (before/after/rationale) — 변경 이력 추적
  - External Artifact 패턴: `review/{review-id}/` 경로에 Draft, Findings, Full Reports 저장
  - 12개 에이전트 파일에 Tiered Report Template + AID 할당 규칙 추가
  - CLAUDE.md Orchestration Flow 다이어그램 업데이트
- v3.5: Deep Research 스킬에 SNS 조회 기능 추가 + `/wrap` 동기화
  - `deep-research` 스킬에 SNS 검색 전략 추가 (WebSearch `site:` 연산자 기반)
  - SNS 플랫폼별 적합도 테이블 추가 (Reddit > X > Instagram > Facebook)
  - SNS 심화 조사 서브섹션 및 신뢰도 판정 규칙 추가
  - Research Metadata에 SNS 출처 필드 추가
  - 품질 기준 체크리스트에 SNS 항목 2건 추가
  - SNS 조사 가이드 독립 섹션 추가 (MCP 향후 대응 포함)
  - `architecture-principles` rule의 Trigger Paths에 `**/*.tsx`, `**/*.go` 누락 수정
- v3.4: Skills/Commands YAML front matter 표준화
  - 14개 참조 스킬에 `description`, `user-invocable: false` front matter 추가
  - `deep-research` 스킬에 `allowed-tools` 추가
  - `architect-orchestration` 스킬에 `allowed-tools` 추가
  - 3개 슬래시 커맨드(`commit`, `wrap`, `rl`)에 `description`, `allowed-tools` front matter 추가
- v3.3: Deep Research 스킬 추가
  - `deep-research` 스킬 신규 생성 (3단계 심층 조사 프로토콜)
  - 12개 아키텍트 에이전트에 `deep-research` 스킬 연결
  - `cloud-native-architect`, `concurrency-architect` 에이전트에 YAML front matter 추가
  - `architect-orchestration` 스킬에 Step 1.5 (Deep Research) 삽입
  - Skills 수: 15 → 16
- v3.2: `/wrap` 동기화 - `commit` 커맨드 누락 반영
  - Repository Structure의 commands 목록에 `commit` 추가
- v3.1: AI 사고 프로세스 및 응답 가이드라인 추가
  - `sequentialthinking` MCP 도구 사용 필수 지침 추가
  - 응답 시 준수할 10가지 원칙 추가
- v3.0: CLAUDE.md + ARCHITECTURE-INDEX.md 통합, `/wrap` 커맨드 추가
  - ARCHITECTURE-INDEX.md 내용을 CLAUDE.md에 흡수 (단일 진실 소스)
  - ARCHITECTURE-INDEX.md 삭제
  - `/wrap` 슬래시 커맨드 생성 (문서 동기화 검증)
  - Repository Structure에서 9 rules → 8 rules 수정
- v2.1: Orchestrator를 Agent에서 Skill로 전환
  - architect-orchestrator 에이전트 삭제 (subagent는 Task tool 사용 불가)
  - architect-orchestration 스킬을 실행 가능한 오케스트레이션 스킬로 전면 재작성
  - 12개 architect agent에서 Task tool 제거
- v2.0: Architect Orchestration System 추가
  - architect-orchestrator 에이전트
  - architect-orchestration 스킬 (라우팅, 합의 프로토콜)
  - architect-review 규칙
- v1.0: 초기 버전 (12개 아키텍트, 14개 스킬, 8개 규칙)
