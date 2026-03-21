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

### Product (전역 배포 — `stow -t ~ product`)

- `product/.claude/skills/` — 31 skills (architecture + AI backend + business + investigation + release + utility)
- `product/.claude/agents/` — 15 architect agents + 5 investigation agents (20 total)
- `product/.claude/commands/` — Slash commands (`commit`, `rl`, `new_rl`, `save_obsi`, `tdd-lfg`)

### Project-local (demiurge 개발 전용)

- `.claude/rules/` — 8 governance rules auto-applied based on file glob patterns
- `.claude/commands/wrap.md` — CLAUDE.md 동기화 커맨드

### Tooling

- `justfile` — 태스크 러너 (`just link`, `just unlink`, `just status`, `just new-skill`, `just new-command`)
- `bootstrap.sh` — 최초 셋업 스크립트 (brew install stow just + just link)

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
| **2 Design** (conditional) | Application, Data, Integration, Healthcare Informatics, LLM, RAG | Specialist Feedback | Parallel |
| **3 Quality** (conditional) | Security, SRE, Cloud-Native, AI Safety | Specialist Feedback | Parallel |
| **4 Enabling** (on-demand) | EDA Specialist, ML Platform, Concurrency | Specialist Feedback | On-demand |

### AID (Architect ID) 체계

모든 아키텍트 리포트에 출처와 라운드를 추적하는 AID가 포함됩니다.

```
형식: "{Tier}-{Role}-R{Round}"
예시: T1-SA-R1, T1-DA-R2, T2-APP-R1, T2-LLM-R1, T2-RAG-R1, T3-SEC-R1, T3-AIS-R1, T4-EDA-R1
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

## Agents (20개)

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
| `security-architect` | 보안 아키텍처 | OWASP, Zero Trust, NIST, AI Safety |
| `sre-architect` | 운영 아키텍처 | SRE, Observability, SLO, LLM Observability |
| `ml-platform-architect` | ML 플랫폼 | MLOps, Feature Store, LLM Fine-tuning, GPU Serving |
| `healthcare-informatics-architect` | 의료 정보 | HL7 FHIR, HIPAA |

### AI Backend Agents

| Agent | 역할 | 핵심 지식 |
|-------|------|-----------|
| `llm-architect` | LLM 시스템 아키텍처 | LLM Gateway, 모델 라우팅, Prompt Management, Caching |
| `rag-architect` | RAG & Agent 아키텍처 | RAG Pipeline, Vector DB, Multi-Agent, MCP |
| `ai-safety-architect` | AI 안전성 아키텍처 | OWASP LLM Top 10, Prompt Injection 방어, EU AI Act |

### Investigation Agents

| Agent | 역할 | 핵심 지식 |
|-------|------|-----------|
| `code-investigator` | 코드베이스 분석 | 호출 체인, 에러 핸들링, 데이터 흐름, 동시성 |
| `log-investigator` | 로그/에러 분석 | 스택트레이스, 패턴, 타임라인, 메트릭 |
| `history-investigator` | Git 이력 분석 | blame, 최근 변경, PR 컨텍스트, 회귀 |
| `counter-reviewer` | 발견사항 반박 | Boris Cherny "poking holes", false positive 제거 |
| `release-investigator` | 릴리즈 핸드오프 검증 | 문서 완전성, 배포 준비, 리스크, 인프라 영향, 운영 준비 |

## Skills (31개)

### Orchestration

| Skill | 내용 |
|-------|------|
| `architect-orchestration` | 다중 아키텍트 오케스트레이션, 라우팅 전략, 합의 프로토콜 |
| `deep-research` | 3단계 심층 조사 프로토콜 (광역 탐색, 심화 탐색, 지식 합성) + Error Resilience + MCP Browser Fallback |

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
| `testing-architecture` | Test Pyramid, Contract Testing, TDD/BDD, LLM Evaluation, LLM-as-Judge |

### Domain-Specific Skills

| Skill | 내용 |
|-------|------|
| `data-architecture` | DAMA-DMBOK, CQRS, Event Sourcing, Data Mesh |
| `integration` | EIP, API Gateway, Event-Driven |
| `security` | OWASP, Zero Trust, Encryption |
| `sre` | SRE Principles, SLO/SLI, Observability, LLM Observability, 토큰/비용 추적 |
| `ml-platform` | MLOps, Model Serving, Feature Store, LLM Fine-tuning, GPU Serving |
| `healthcare-informatics` | HL7 FHIR, HIPAA, Medical Terminology |

### AI Backend Skills

| Skill | 내용 |
|-------|------|
| `llm-gateway` | LLM Gateway 아키텍처, 모델 라우팅, Multi-provider 추상화, Streaming, Caching |
| `rag-architecture` | RAG Pipeline, Chunking, Embedding, Vector DB, Hybrid Search, Re-ranking, Agentic RAG |
| `ai-agent` | AI Agent 패턴 (ReAct, Multi-Agent, Plan-and-Execute), Workflow, MCP, State Management |
| `prompt-engineering` | Prompt Lifecycle, 버저닝, A/B Testing, DSPy, Dynamic Assembly, CI/CD |
| `ai-safety` | OWASP LLM Top 10, Prompt Injection 방어, 할루시네이션 감지, PII 보호, EU AI Act |

### Investigation

| Skill | 내용 |
|-------|------|
| `investigation-orchestration` | 다중 조사관 오케스트레이션 (동적 배정, 병렬 조사, 교차 검증, 반박, 증거 기반 판정) |
| `release-handoff` | 릴리즈 핸드오프 문서 구조, 변경 등급 기준, 섹션별 필수/선택 매트릭스 (참조 스킬) |

### Career Analysis

| Skill | 내용 |
|-------|------|
| `job-analysis` | 이직 분석 4단계 프로토콜 (기업 심층 조사, 직무 분석, 이력서 매칭, 최종 평가 + 면접 예측) |

### Business & Marketing

| Skill | 내용 |
|-------|------|
| `seth-godin-marketing` | Seth Godin 마케팅 철학 (보랏빛 소, 퍼미션 마케팅, 트라이브, 최소 유효 시장, 변화 중심). 전략·카피·이메일·콘텐츠·론칭 생성. |

### Utility Skills

| Skill | 내용 |
|-------|------|
| `concept-explainer` | 기술 개념을 8가지 관점에서 심층 분석, 시각화 리포트 생성 |
| `organize` | 대화 내용을 원문 보존하며 구조화된 문서로 정리 |
| `qa` | 번호 매긴 기술 질문 리스트에 증거 기반 답변 생성 |
| `ralph-loop-guide` | Ralph Loop 사용 가이드 (프롬프트 작성법, 안전 장치, 템플릿) |
| `rl-verify` | 수렴 검증 플랜 생성 + 실행 |
| `save-confluence` | 직전 대화 출력을 Confluence에 업로드 (새 페이지/기존 페이지) |

## Stow Distribution

demiurge의 skills/commands/agents는 `product/.claude/`에 원본이 있으며, GNU Stow를 통해 `~/.claude/`에 심링크로 배포됩니다.

```bash
just link      # 심링크 생성/갱신
just unlink    # 심링크 해제
just status    # 심링크 상태 확인
just new-skill <name>    # 새 스킬 생성 + 자동 link
just new-command <name>  # 새 커맨드 생성 + 자동 link
```

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
| **AI Backend** | LLM Gateway (Routing, Fallback) | ✅ | ✅ | - |
| | RAG Pipeline (Chunking, VectorDB, Rerank) | ✅ | ✅ | - |
| | AI Agent (ReAct, Multi-Agent, MCP) | ✅ | ✅ | - |
| | Prompt Management (Versioning, A/B, DSPy) | ✅ | ✅ | - |
| | AI Safety (OWASP LLM, Injection, PII) | ✅ | ✅ | - |
| | LLM Evaluation (RAGAS, LLM-as-Judge) | - | ✅ | - |
| | LLM Observability (OTel, Token Tracking) | - | ✅ | - |
| | LLM Fine-tuning (SFT, DPO, LoRA) | - | ✅ | - |
| | GPU Serving (vLLM, TGI, Continuous Batching) | - | ✅ | - |
| **Research** | Deep Research Protocol | ✅ (15 agents) | ✅ | - |
| **Investigation** | Multi-Agent Investigation | ✅ (4 agents) | ✅ | - |
| **Release Investigation** | Release Handoff Verification | ✅ (1 agent) | ✅ | - |
| **Career** | Job Analysis Protocol | - | ✅ | - |
| **Business & Marketing** | Purple Cow (Remarkability) | - | ✅ | - |
| | Permission Marketing | - | ✅ | - |
| | Tribes (Community Building) | - | ✅ | - |
| | Smallest Viable Market | - | ✅ | - |
| | Story Framework | - | ✅ | - |
| | Content Strategy (Lighthouse/Gift/Connection) | - | ✅ | - |
| | Launch Framework (Seeding → Ignition → Spread) | - | ✅ | - |
| | Trust Ladder | - | ✅ | - |

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

Use the **investigation skill** for codebase investigation and debugging:
```
/investigation-orchestration 코드베이스 조사 (버그, 성능, 구조 분석 등)
```

Use the **marketing skill** for Seth Godin-style marketing:
```
/seth-godin-marketing strategy "번아웃 직전 스타트업 대표" "AI 업무 자동화 SaaS"
/seth-godin-marketing copywriting "취업준비생" "이력서 작성 도구"
/seth-godin-marketing email "신규 가입자" "웰컴 시퀀스"
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
- Last Updated: 2026-03-21
- Version: 6.0

### Changelog

- v6.0: Product Stow Distribution — 전역 배포 아키텍처 전환
  - `product/.claude/` 디렉토리 신설: 전역 배포 대상(skills, commands, agents) 원본 관리
  - GNU Stow 기반 심링크 배포: `stow -t ~ product`로 `~/.claude/`에 자동 심링크
  - `~/.claude/` 전역 스킬 7개 통합: concept-explainer, organize, qa, ralph-loop-guide, rl-verify, save-confluence + deep-research 최신본
  - `~/.claude/` 전역 커맨드 4개 통합: new_rl, rl, save_obsi, tdd-lfg
  - justfile 태스크 러너 추가: link, unlink, status, new-skill, new-command
  - bootstrap.sh 최초 셋업 스크립트 추가
  - `.claude/`는 프로젝트 전용으로 축소: CLAUDE.md, rules/, commands/wrap.md만 유지
  - Skills 수: 25 → 31, Commands 수: 4 → 5 (전역) + 1 (프로젝트 전용)
- v5.1: Deep Research Anti-Hallucination 강화 — Prevention-First 설계
  - Phase 1 Authority Discovery 추가: Semantic Scholar API로 인용 수 기반 권위 논문/저자 사전 식별 (Step 1-2)
  - Phase 2 Iterative Retrieval 강화: Step 2-0 (지식 갭 분석 + 쿼리 재생성), Step 2-1 (원문 직접 확인 강화 + source_verification 기록), Step 2-4 (근거 충분성 검증)
  - Phase 3 Anti-Hallucination Gate 신설 (Evidence-First, Attribution Specificity, Synthesis Necessity Check)
  - 확신도 태깅에 [Synthesized] 태그 추가 + [Confirmed] 부여 조건 강화 (원문 확인 필수)
  - 교차 검증에 서술/규범 구분 + 독립 출처 검증 규칙 추가
  - 품질 기준 "최소 N개" → 조건부 유연화 + "N/A" 허용
  - Quick Research 결과에 [QuickResearch] 접두어 + Full Research 오염 방지 경고 추가
  - Playwright fallback 한계 문서화: Cloudflare/Google Scholar 수준 보안은 headless도 차단됨
  - 차용 패턴: superpowers (Evidence-First), compound-engineering (Source Attribution), spec-kit ([NEEDS CLARIFICATION])
  - 연구 근거: IM-RAG, Auto-RAG, Self-Refine 등 Iterative Retrieval이 Post-hoc Detection보다 효과적
  - 검증 완료: Semantic Scholar API (WebFetch) 정상 동작 확인 (2026-02-24 테스트)
- v5.0: Deep Research 스킬 고도화 — Error Resilience + Playwright MCP Fallback
  - `deep-research` SKILL.md에 Error Resilience Protocol 섹션 추가 (Fallback Tool Chain, 403 대응표, Graceful Degradation)
  - 병렬 호출 안전 전략 추가: WebSearch 최대 3개 배치, WebFetch 최대 2개 배치, cascade 실패 방지
  - Playwright MCP 설정 가이드 추가 + Tool Selection Matrix (상황별 도구 선택)
  - `.mcp.json` 생성: Playwright MCP headless 설정
  - SKILL.md allowed-tools 확장: `mcp__playwright__*` 추가
  - 해결 대상: WebFetch 403 봇 차단, Sibling tool call cascade 버그 (Claude Code Issue #22264)
- v4.9: Seth Godin Marketing Skill 추가 — 비즈니스/마케팅 도메인 확장
  - `.claude/skills/business/seth-godin-marketing/` 신규 생성 (1 SKILL.md + 5 reference docs)
  - NEW PATTERN: business/ 카테고리 폴더 도입 (향후 마케팅/세일즈 스킬 확장 기반)
  - User-invocable skill: `/seth-godin-marketing <request_type> <target_audience> [context]`
  - 5 Core Principles: Purple Cow, Permission Marketing, Tribes, The Dip, This Is Marketing
  - 5 Supporting Docs: strategy.md (5단계), copywriting.md (4단계), email.md (Trust Ladder), content.md (3타입), launch.md (3단계)
  - 5-Step Process: Empathy Map → SVM → Story Framework → Output → Purple Cow Check
  - Coverage Matrix에 Business & Marketing 영역 추가 (8개 패턴)
  - First business/marketing skill (project expansion from pure technical to business domain)
  - Skills 수: 24 → 25
- v4.8: AI Backend 아키텍처 확장 — LLM/RAG/Agent/Safety 스킬 및 에이전트 추가
  - 10개 카테고리 심층 조사 수행 (`research/ai-backend/` 디렉토리, ~845KB 산출물)
  - 5개 신규 스킬 생성: `llm-gateway`, `rag-architecture`, `ai-agent`, `prompt-engineering`, `ai-safety`
  - 3개 기존 스킬 확장: `ml-platform` (+LLM Fine-tuning, GPU Serving), `sre` (+LLM Observability), `testing-architecture` (+LLM Evaluation)
  - 3개 신규 에이전트 생성: `llm-architect` (Tier 2), `rag-architect` (Tier 2), `ai-safety-architect` (Tier 3)
  - 3개 기존 에이전트 업데이트: `security-architect` (+ai-safety 스킬), `sre-architect` (+llm-gateway 스킬), `ml-platform-architect` (+llm-gateway 스킬, 설명 업데이트)
  - Agent Tiers 업데이트: Tier 2에 LLM/RAG 추가, Tier 3에 AI Safety 추가
  - Coverage Matrix에 AI Backend 영역 9개 패턴 추가
  - AID 체계 확장: T2-LLM, T2-RAG, T3-AIS 추가
  - Agents 수: 17 → 20, Skills 수: 19 → 24
- v4.7: Release Investigator 확장 — 릴리즈 핸드오프 검증 시스템
  - `.claude/agents/release-investigator.md` 신규 생성 (릴리즈 분석 전문 조사관)
  - `.claude/skills/release-handoff/SKILL.md` 신규 생성 (릴리즈 핸드오프 참조 지식)
  - `investigator-registry.md`에 REL type + 5개 perspectives + 권장 조합 3건 추가
  - `investigation-orchestration/SKILL.md`에 릴리즈 조사 범위 + REL IID 추가
  - 5개 Perspectives: artifact-completeness, deployment-readiness, risk-assessment, infra-impact, ops-readiness
  - 증거 소스 확장: 릴리즈 문서, CHANGELOG, 배포 스크립트, 설정 파일, 마이그레이션, IaC, diff
  - Agents 수: 16 → 17, Skills 수: 18 → 19
- v4.6: Investigation Orchestration System 추가 — 코드베이스 다중 조사관 오케스트레이션
  - `.claude/skills/investigation-orchestration/SKILL.md` 신규 생성 (5-Step 프로토콜)
  - `.claude/skills/investigation-orchestration/investigator-registry.md` 신규 생성 (조사관 타입/관점 카탈로그)
  - `.claude/skills/investigation-orchestration/classification-protocol.md` 신규 생성 (분류 규칙 + 판정 알고리즘)
  - `.claude/agents/code-investigator.md` 신규 생성 (코드 분석 전문 조사관)
  - `.claude/agents/log-investigator.md` 신규 생성 (로그/에러 분석 전문 조사관)
  - `.claude/agents/history-investigator.md` 신규 생성 (Git 이력 분석 전문 조사관)
  - `.claude/agents/counter-reviewer.md` 신규 생성 (Boris Cherny 반박 패턴)
  - 동적 조사관 배정: 타입 x 관점(perspective) 조합을 쿼리에 따라 동적 결정
  - IID (Investigator ID) 체계: `{TYPE}-{PERSPECTIVE}-R{Round}` 형식
  - 증거 기반 판정: majority vote 대신 Judge 패턴 (Tool-MAD 18.1% 개선)
  - Anti-Sycophancy: Counter-Reviewer 필수 반박 + 독립 조사 선행
  - Quick Mode: 단순 문의는 1 조사관으로 간소화
  - Agents 수: 12 → 16, Skills 수: 17 → 18
- v4.5: `/wrap` 동기화 — `save_obsi` 커맨드 누락 반영
  - Repository Structure의 commands 목록에 `save_obsi` 추가
- v4.4: `job-analysis` 스킬 개선 — Executive Summary 섹션 추가
  - Step 4-5 `📌 Executive Summary` 단계 신설 (기존 저장은 Step 4-6으로 이동)
  - 분석 파일 마지막에 Executive Summary 포함 (콘솔 출력과 동일)
  - 필수 포함: Verdict Box, 차원별 Bar Chart, 핵심 요약 테이블, 종합 코멘트
  - Output Template에 Executive Summary 섹션 추가
  - Quality Checklist에 Executive Summary 검증 항목 추가
- v4.3: `job-analysis` 스킬 추가 — 이직 준비 4단계 분석 프로토콜
  - `.claude/skills/job-analysis/SKILL.md` 신규 생성
  - Phase 1: 기업 심층 조사 (deep-research 프로토콜 적용, 재무 안전성, 레드플래그)
  - Phase 2: 직무 역할 분석 (JD 파싱, 기술 스택, 채용 프로세스 조사)
  - Phase 3: 이력서 매칭 분석 (6차원 매칭률, 강점/약점/성장 기회)
  - Phase 4: 최종 평가 (종합 판정, Radar Chart, 예상 과제/면접 질문, 전략적 권고)
  - 모든 Phase에서 sequential-thinking MCP 필수 사용
  - 이모지 활용 리포팅 (가독성 강화)
  - 이력서 자동 감지 (resume.md / RESUME.md / career/resume.md)
  - 결과 저장: `career/{company-slug}-{role-slug}-analysis.md`
  - Skills 수: 16 → 17
- v4.2: Context Management Protocol 추가 — 오케스트레이션 세션 안정성 개선
  - `architect-orchestration` 스킬에 Context Management Protocol 섹션 추가
  - Context 위생 3원칙: 즉시 파일 저장 / Layer 1만 유지 / 마일스톤 compact
  - Compact 트리거 포인트 3곳 정의: Step 1.5 후, Step 3 후, Step 5 재라운드 시
  - Deep Research 결과 파일 저장 규칙 추가 (`research/` 디렉토리)
  - 단계 간 Context 위생 체크리스트 추가
  - Step 3 결과 수집에 Context 관리 지침 삽입
  - Step 7 실행 검증에 Context 관리 검증 항목 추가 (#8)
  - execution-log에 `context_management` 섹션 추가
  - Context 절감 효과 수치 업데이트 (compact 포함)
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
