# Architect Registry

12개의 전문 아키텍트 에이전트에 대한 상세 정보를 제공합니다.

---

## Tier 구조 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARCHITECT TIERS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tier 1: STRATEGIC (필수, Sequential)                           │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │ Solution Architect   │→│ Domain Architect    │               │
│  │ 전체 방향, 품질 속성  │  │ 도메인 모델, BC     │               │
│  └─────────────────────┘  └─────────────────────┘               │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tier 2: DESIGN (선택, Parallel)                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐│
│  │ Application  │ │ Data         │ │ Integration  │ │Healthcare ││
│  │ 레이어, MSA   │ │ 데이터 모델  │ │ 통합, API    │ │FHIR,HIPAA││
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────┘│
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tier 3: QUALITY (선택, Parallel)                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ Security     │ │ SRE          │ │ Cloud-Native │             │
│  │ 보안, 인증    │ │ 운영, SLO    │ │ K8s, 12-Factor│            │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tier 4: ENABLING (On-demand)                                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ EDA          │ │ ML Platform  │ │ Concurrency  │             │
│  │ 이벤트, SAGA  │ │ ML/AI 플랫폼 │ │ 동시성 패턴   │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tier 1: Strategic Architects

### Solution Architect

```yaml
name: solution-architect
tier: 1
execution: sequential
required: true

role: 전체 시스템 아키텍처 설계
expertise:
  - TOGAF ADM
  - POSA Patterns (Vol.1)
  - 품질 속성 (ISO 25010)
  - 기술 선택 및 Trade-off

focus_areas:
  - 아키텍처 비전 및 방향
  - 시스템 경계 정의
  - 기술 스택 결정
  - 품질 속성 (성능, 확장성, 가용성)

output_types:
  - Architecture Vision
  - ADR (Architecture Decision Record)
  - System Design Document
  - Trade-off Analysis

keywords:
  - 아키텍처, 시스템, 설계, 구조
  - 성능, 확장성, 가용성
  - 기술 선택, 스택
  - TOGAF, POSA

related_architects:
  - domain-architect (도메인과 아키텍처 매핑)
  - application-architect (레이어 설계)
  - cloud-native-architect (배포 아키텍처)
```

### Domain Architect

```yaml
name: domain-architect
tier: 1
execution: sequential
required: true

role: 도메인 중심 설계 (DDD)
expertise:
  - DDD Strategic Design
  - DDD Tactical Design
  - Bounded Context & Context Mapping
  - Aggregate Design

focus_areas:
  - Bounded Context 식별
  - Ubiquitous Language 정의
  - Aggregate 경계 설계
  - Domain Events 모델링

output_types:
  - Context Map
  - Aggregate Design Document
  - Ubiquitous Language Glossary
  - Domain Event Catalog

keywords:
  - 도메인, 모델, DDD
  - Bounded Context, Aggregate
  - Entity, Value Object
  - Domain Event

related_architects:
  - solution-architect (전략적 방향)
  - application-architect (레이어 매핑)
  - data-architect (데이터 모델)
  - eda-specialist (이벤트 설계)
```

---

## Tier 2: Design Architects

### Application Architect

```yaml
name: application-architect
tier: 2
execution: parallel
required: false

role: 애플리케이션 내부 구조 설계
expertise:
  - Clean Architecture
  - Hexagonal Architecture
  - MSA Patterns
  - SAGA Pattern

focus_areas:
  - 레이어 구조 설계
  - 컴포넌트 분리
  - 서비스 분해
  - 내부 API 설계

output_types:
  - Component Diagram
  - Layer Design Document
  - Service Decomposition
  - Internal API Specification

keywords:
  - 레이어, 모듈, 컴포넌트
  - 서비스, API, 컨트롤러
  - Clean Architecture, Hexagonal
  - MSA, SAGA

related_architects:
  - domain-architect (도메인 모델)
  - integration-architect (외부 통합)
  - eda-specialist (SAGA 패턴)
```

### Data Architect

```yaml
name: data-architect
tier: 2
execution: parallel
required: false

role: 데이터 아키텍처 설계
expertise:
  - DAMA-DMBOK
  - CQRS / Event Sourcing
  - Data Mesh
  - 데이터 모델링

focus_areas:
  - 데이터 모델 설계
  - 저장소 선택
  - 읽기/쓰기 분리
  - 데이터 거버넌스

output_types:
  - Data Model (ERD)
  - CQRS Design
  - Data Flow Diagram
  - Storage Strategy

keywords:
  - 데이터, DB, 스키마
  - 마이그레이션, 인덱스
  - CQRS, Event Sourcing
  - 쿼리, 저장소

related_architects:
  - domain-architect (Aggregate 매핑)
  - application-architect (레이어 연동)
  - eda-specialist (이벤트 저장)
```

### Integration Architect

```yaml
name: integration-architect
tier: 2
execution: parallel
required: false

role: 시스템 통합 설계
expertise:
  - EIP (Enterprise Integration Patterns)
  - API Gateway
  - Message Broker
  - Service Mesh

focus_areas:
  - 외부 시스템 연동
  - API 설계 (외부)
  - 메시징 아키텍처
  - 프로토콜 선택

output_types:
  - Integration Architecture
  - API Contract
  - Message Flow Diagram
  - Protocol Specification

keywords:
  - 통합, 연동, 외부 시스템
  - EMR, API Gateway
  - 메시지, 큐, Kafka, RabbitMQ
  - REST, gRPC, GraphQL

related_architects:
  - application-architect (내부 API)
  - security-architect (API 보안)
  - eda-specialist (메시징)
```

### Healthcare Informatics Architect

```yaml
name: healthcare-informatics-architect
tier: 2
execution: parallel
required: false

role: 의료 정보 표준 및 규정 준수
expertise:
  - HL7 FHIR
  - HIPAA Security Rule
  - Medical Terminology (ICD, SNOMED CT)
  - Clinical Data Models

focus_areas:
  - 의료 데이터 표준
  - 규정 준수 (HIPAA, GDPR)
  - PHI 보호
  - 임상 용어 표준화

output_types:
  - FHIR Resource Design
  - Compliance Checklist
  - PHI Handling Policy
  - Clinical Data Model

keywords:
  - 환자, 진료, 임상
  - HIPAA, FHIR, HL7
  - PHI, 개인정보
  - 의료, 처방, 진단

related_architects:
  - data-architect (의료 데이터 모델)
  - security-architect (PHI 보안)
  - integration-architect (EMR 연동)
```

---

## Tier 3: Quality Architects

### Security Architect

```yaml
name: security-architect
tier: 3
execution: parallel
required: false

role: 보안 아키텍처 설계
expertise:
  - OWASP Top 10
  - Zero Trust Architecture
  - Encryption Standards
  - Identity & Access Management

focus_areas:
  - 인증/인가 설계
  - 데이터 암호화
  - 취약점 방지
  - 감사 로그

output_types:
  - Security Architecture
  - Threat Model
  - Authentication Design
  - Encryption Strategy

keywords:
  - 보안, 인증, 권한
  - 암호화, 취약점
  - OAuth, JWT, RBAC
  - 감사 로그, Zero Trust

related_architects:
  - healthcare-informatics-architect (PHI 보안)
  - integration-architect (API 보안)
  - cloud-native-architect (인프라 보안)
```

### SRE Architect

```yaml
name: sre-architect
tier: 3
execution: parallel
required: false

role: 운영 아키텍처 및 안정성 설계
expertise:
  - SRE Principles
  - SLO/SLI/SLA
  - Observability (Metrics, Logs, Traces)
  - Incident Management

focus_areas:
  - 모니터링 체계
  - SLO 정의
  - 장애 대응 설계
  - 배포 전략

output_types:
  - SLO Document
  - Monitoring Strategy
  - Runbook
  - Incident Response Plan

keywords:
  - 모니터링, SLO, SLI
  - 장애, 운영, 배포
  - 롤백, 알림
  - 메트릭, 로그, 트레이스

related_architects:
  - cloud-native-architect (배포)
  - application-architect (Health Check)
  - security-architect (보안 모니터링)
```

### Cloud-Native Architect

```yaml
name: cloud-native-architect
tier: 3
execution: parallel
required: false

role: 클라우드 네이티브 아키텍처 설계
expertise:
  - 12-Factor App
  - Kubernetes Patterns
  - Service Mesh
  - Deployment Strategies

focus_areas:
  - 컨테이너 설계
  - K8s 배포 구성
  - 오토스케일링
  - 서비스 메시

output_types:
  - K8s Manifest Design
  - Container Strategy
  - Deployment Pipeline
  - Scaling Strategy

keywords:
  - 컨테이너, 쿠버네티스, K8s
  - 클라우드, 스케일, Pod
  - Helm, 12-Factor
  - Service Mesh, Istio

related_architects:
  - sre-architect (배포, 운영)
  - application-architect (컨테이너화)
  - security-architect (인프라 보안)
```

---

## Tier 4: Enabling Architects

### EDA Specialist

```yaml
name: eda-specialist
tier: 4
execution: on-demand
required: false

role: 이벤트 기반 아키텍처 전문가
expertise:
  - Event-Driven Architecture
  - SAGA Patterns (Choreography/Orchestration)
  - Event Sourcing
  - Message Broker

focus_areas:
  - 이벤트 설계
  - SAGA 패턴 적용
  - 이벤트 스토어
  - 멱등성 보장

output_types:
  - Event Catalog
  - SAGA Design
  - Event Flow Diagram
  - Idempotency Strategy

keywords:
  - 이벤트, SAGA, 비동기
  - 큐, 메시지
  - Event Sourcing
  - Choreography, Orchestration

trigger_conditions:
  - 비동기 처리 요구
  - 분산 트랜잭션
  - 이벤트 기반 통신

related_architects:
  - domain-architect (Domain Events)
  - integration-architect (메시징)
  - application-architect (SAGA)
```

### ML Platform Architect

```yaml
name: ml-platform-architect
tier: 4
execution: on-demand
required: false

role: ML/AI 플랫폼 아키텍처
expertise:
  - MLOps
  - Model Serving
  - Feature Store
  - ML Pipeline

focus_areas:
  - 모델 서빙 아키텍처
  - 피처 관리
  - 학습 파이프라인
  - 모델 버전 관리

output_types:
  - ML Architecture
  - Model Serving Design
  - Feature Store Design
  - MLOps Pipeline

keywords:
  - ML, AI, 모델
  - 예측, 추론, 학습
  - Feature Store, MLOps
  - 파이프라인

trigger_conditions:
  - ML/AI 모델 서빙
  - 예측 시스템 구축
  - 피처 엔지니어링

related_architects:
  - data-architect (데이터 파이프라인)
  - application-architect (서빙 레이어)
  - sre-architect (모니터링)
```

### Concurrency Architect

```yaml
name: concurrency-architect
tier: 4
execution: on-demand
required: false

role: 동시성 및 병렬 처리 패턴
expertise:
  - POSA Volume 2
  - Reactor / Proactor
  - Active Object
  - Lock Strategies

focus_areas:
  - 동시성 모델
  - 락 전략
  - 병렬 처리
  - 경쟁 조건 방지

output_types:
  - Concurrency Model
  - Lock Strategy Document
  - Thread Model
  - Race Condition Analysis

keywords:
  - 동시성, 병렬
  - 락, 스레드
  - 비동기, Reactor
  - 경쟁 조건

trigger_conditions:
  - 동시성 이슈 해결
  - 고성능 처리 요구
  - 락 전략 필요

related_architects:
  - application-architect (비동기 설계)
  - data-architect (트랜잭션)
  - sre-architect (성능)
```

---

## 아키텍트 선택 매트릭스

### 요구사항 유형별 권장 아키텍트

| 요구사항 유형 | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---------------|--------|--------|--------|--------|
| **새 기능 개발** | Solution, Domain | Application, Data | Security, SRE | - |
| **API 설계** | Solution, Domain | Application, Integration | Security | - |
| **데이터 모델** | Solution, Domain | Data, Healthcare* | Security | - |
| **보안 강화** | Solution, Domain | Healthcare* | Security | - |
| **성능 최적화** | Solution, Domain | Application, Data | SRE, Cloud-Native | Concurrency |
| **시스템 통합** | Solution, Domain | Integration, Healthcare* | Security | EDA* |
| **클라우드 마이그레이션** | Solution, Domain | Application | Cloud-Native, SRE | - |
| **이벤트 처리** | Solution, Domain | Application, Integration | SRE | EDA |
| **ML 시스템** | Solution, Domain | Application, Data | SRE | ML Platform |

*조건부: 의료 도메인인 경우

---

## 협력 인터페이스

### 표준 입력 (아키텍트가 받는 정보)

```yaml
architect_input:
  # 기본 정보
  requirement: "원본 요구사항"
  context: "추가 컨텍스트"

  # 이전 단계 결과
  previous_reviews:
    - architect: "solution-architect"
      summary: "전략적 방향 요약"
      key_decisions: ["결정 1", "결정 2"]
    - architect: "domain-architect"
      summary: "도메인 모델 요약"
      key_decisions: ["결정 1", "결정 2"]

  # 집중 영역
  focus_areas:
    - "이 아키텍트가 집중할 영역 1"
    - "이 아키텍트가 집중할 영역 2"

  # 제약 조건
  constraints:
    - "다른 아키텍트가 제시한 제약 1"
    - "다른 아키텍트가 제시한 제약 2"
```

### 표준 출력 (아키텍트가 제공하는 정보)

```yaml
architect_output:
  architect: "<name>"
  timestamp: "<ISO8601>"

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

  vote:
    decision: AGREE | DISAGREE | CONDITIONAL
    confidence: HIGH | MEDIUM | LOW
    rationale: "투표 이유"
```
