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
[Requirement] → [Analysis & Routing] → [Tier 1: Strategic] → [Tier 2: Design] → [Tier 3: Quality] → [Consensus] → [Result]
                                         (Sequential)          (Parallel)         (Parallel)          (Round-based voting)
```

### Agent Tiers

| Tier | Agents | Execution |
|------|--------|-----------|
| **1 Strategic** (required) | Solution Architect, Domain Architect | Sequential |
| **2 Design** (conditional) | Application, Data, Integration, Healthcare Informatics | Parallel |
| **3 Quality** (conditional) | Security, SRE, Cloud-Native | Parallel |
| **4 Enabling** (on-demand) | EDA Specialist, ML Platform, Concurrency | On-demand |

### Consensus Protocol

- Threshold: 2/3 agreement (67%)
- Tier 1 architects hold veto power
- Maximum 5 voting rounds
- Minority opinions are recorded

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
- Last Updated: 2026-01-29
- Version: 3.5

### Changelog

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
