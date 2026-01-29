# Routing Strategy

요구사항을 분석하여 적절한 아키텍트 에이전트를 선택하고 실행 순서를 결정합니다.

---

## 라우팅 원칙

### 1. Tier 기반 우선순위

```
Tier 1 (Strategic) → 항상 먼저, 순차 실행
Tier 2 (Design)    → 관련 시 병렬 실행
Tier 3 (Quality)   → 관련 시 병렬 실행
Tier 4 (Enabling)  → 특정 요구 시에만
```

### 2. Hybrid Routing

- **Phase 1**: Sequential (이전 결과가 다음에 영향)
- **Phase 2, 3**: Parallel (독립적 검토)
- **Conflict**: Sequential 전환 (충돌 시)

---

## 키워드 매핑 규칙

### Tier 1: Strategic (항상 포함)

모든 요구사항에 대해 `solution-architect`와 `domain-architect`가 참여합니다.

### Tier 2: Design

| 아키텍트 | 트리거 키워드 | 예시 요구사항 |
|----------|---------------|---------------|
| `application-architect` | API, 레이어, 모듈, 서비스, 컨트롤러, 컴포넌트, Clean Architecture, Hexagonal | "새 API 엔드포인트 추가", "서비스 레이어 리팩토링" |
| `data-architect` | 데이터, DB, 스키마, 마이그레이션, CQRS, Event Sourcing, 쿼리, 인덱스 | "데이터베이스 스키마 설계", "읽기/쓰기 분리" |
| `integration-architect` | 통합, 연동, EMR, 외부 시스템, 메시지, 큐, Kafka, RabbitMQ, API Gateway | "EMR 연동", "서비스 간 통신" |
| `healthcare-informatics-architect` | 환자, 진료, 임상, HIPAA, FHIR, HL7, PHI, 의료, 처방, 진단 | "환자 데이터 처리", "FHIR 리소스 설계" |

### Tier 3: Quality

| 아키텍트 | 트리거 키워드 | 예시 요구사항 |
|----------|---------------|---------------|
| `security-architect` | 보안, 인증, 권한, 암호화, 취약점, OAuth, JWT, RBAC, 감사 로그 | "인증 시스템 개선", "데이터 암호화" |
| `sre-architect` | 모니터링, SLO, SLI, 장애, 운영, 배포, 롤백, 알림, 메트릭, 로그 | "모니터링 체계 구축", "장애 대응 개선" |
| `cloud-native-architect` | 컨테이너, 쿠버네티스, K8s, 클라우드, 스케일, Pod, Helm, 12-Factor | "K8s 배포 구성", "오토스케일링" |

### Tier 4: Enabling

| 아키텍트 | 트리거 키워드 | 예시 요구사항 |
|----------|---------------|---------------|
| `eda-specialist` | 이벤트, SAGA, 비동기, 큐, 이벤트 소싱, Choreography, Orchestration | "이벤트 기반 처리", "SAGA 패턴 적용" |
| `ml-platform-architect` | ML, AI, 모델, 예측, 추론, 학습, Feature Store, MLOps | "예측 모델 서빙", "ML 파이프라인" |
| `concurrency-architect` | 동시성, 병렬, 락, 스레드, 비동기, Reactor, 경쟁 조건 | "동시성 이슈 해결", "락 전략 설계" |

---

## 요구사항 분석 알고리즘

### Step 1: 키워드 추출

```
요구사항 텍스트
    │
    ▼
┌─────────────────────────────┐
│ 키워드 매칭                   │
│ • 명사 추출                   │
│ • 기술 용어 식별               │
│ • 도메인 용어 인식             │
└─────────────────────────────┘
    │
    ▼
매칭된 키워드 목록
```

### Step 2: 아키텍트 선택

```python
def select_architects(keywords):
    architects = set()

    # Tier 1: 항상 포함
    architects.add("solution-architect")
    architects.add("domain-architect")

    # Tier 2-4: 키워드 기반 선택
    for keyword in keywords:
        for rule in routing_rules:
            if keyword in rule.keywords:
                architects.add(rule.architect)

    return architects
```

### Step 3: 실행 순서 결정

```
Selected Architects
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 1 (Sequential)                                     │
│ [solution-architect] → [domain-architect]               │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 2 (Parallel)                                       │
│ [application] [data] [integration] [healthcare]          │
│ (선택된 것만)                                            │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 3 (Parallel)                                       │
│ [security] [sre] [cloud-native]                          │
│ (선택된 것만)                                            │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 4 (On-demand, Parallel)                            │
│ [eda] [ml-platform] [concurrency]                        │
│ (필요한 경우만)                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 컨텍스트 전달

### Phase 간 컨텍스트

```yaml
# Phase 1 → Phase 2 전달
phase1_context:
  strategic_direction: "solution-architect 권고 요약"
  domain_model: "domain-architect 권고 요약"
  key_decisions: ["결정 1", "결정 2"]
  constraints: ["제약 1", "제약 2"]

# Phase 2 → Phase 3 전달
phase2_context:
  design_decisions:
    application: "레이어 구조, 패턴"
    data: "데이터 모델, 저장소"
    integration: "통합 전략"
  dependencies: ["의존성 1", "의존성 2"]
```

### 아키텍트 간 컨텍스트

```yaml
# 개별 아키텍트에 전달
architect_context:
  original_requirement: "원본 요구사항"
  previous_reviews: [
    { architect: "solution-architect", summary: "..." },
    { architect: "domain-architect", summary: "..." }
  ]
  focus_areas: ["이 아키텍트가 집중할 영역"]
  constraints: ["다른 아키텍트가 제시한 제약"]
```

---

## 시나리오별 라우팅 예시

### 시나리오 1: "환자 알림 시스템 추가"

```yaml
keywords: [환자, 알림, 시스템]

selected_architects:
  tier1: [solution-architect, domain-architect]
  tier2: [application-architect, integration-architect, healthcare-informatics-architect]
  tier3: [security-architect, sre-architect]
  tier4: []

execution:
  phase1: solution-architect → domain-architect
  phase2: [application, integration, healthcare] # parallel
  phase3: [security, sre] # parallel
```

### 시나리오 2: "KTAS 점수 API v2 설계"

```yaml
keywords: [KTAS, 점수, API, v2, 설계]

selected_architects:
  tier1: [solution-architect, domain-architect]
  tier2: [application-architect, integration-architect, healthcare-informatics-architect]
  tier3: [security-architect]
  tier4: []

execution:
  phase1: solution-architect → domain-architect
  phase2: [application, integration, healthcare] # parallel
  phase3: [security] # parallel
```

### 시나리오 3: "데이터 암호화 강화"

```yaml
keywords: [데이터, 암호화, 강화]

selected_architects:
  tier1: [solution-architect, domain-architect]
  tier2: [data-architect, healthcare-informatics-architect]
  tier3: [security-architect]
  tier4: []

execution:
  phase1: solution-architect → domain-architect
  phase2: [data, healthcare] # parallel
  phase3: [security] # parallel
```

### 시나리오 4: "실시간 이벤트 처리 파이프라인"

```yaml
keywords: [실시간, 이벤트, 처리, 파이프라인]

selected_architects:
  tier1: [solution-architect, domain-architect]
  tier2: [application-architect, data-architect, integration-architect]
  tier3: [sre-architect, cloud-native-architect]
  tier4: [eda-specialist, concurrency-architect]

execution:
  phase1: solution-architect → domain-architect
  phase2: [application, data, integration] # parallel
  phase3: [sre, cloud-native] # parallel
  phase4: [eda, concurrency] # parallel
```

---

## 충돌 처리

### 병렬 실행 중 충돌 감지

```yaml
conflict_detection:
  # 동일 컴포넌트에 대한 상충 권고
  - type: "conflicting_recommendations"
    example: "A는 Redis 권고, B는 Memcached 권고"
    action: "순차 해결 모드 전환"

  # 상호 배타적 패턴 선택
  - type: "exclusive_patterns"
    example: "A는 CQRS 권고, B는 단일 DB 권고"
    action: "trade-off 분석 요청"

  # 리소스 경합
  - type: "resource_conflict"
    example: "둘 다 동일 서비스 변경 필요"
    action: "우선순위 결정"
```

### 충돌 해결 프로세스

```
충돌 감지
    │
    ▼
┌─────────────────────────────┐
│ 충돌 유형 분류               │
│ • 기술 선택                  │
│ • 패턴 선택                  │
│ • 우선순위                   │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 관련 아키텍트 순차 호출       │
│ • 충돌 상황 설명             │
│ • 상대 의견 전달             │
│ • 조율 요청                  │
└─────────────────────────────┘
    │
    ▼
합의 또는 에스컬레이션
```

---

## 최적화 전략

### 병렬 실행 효율화

```yaml
optimization:
  # 의존성 없는 작업 병렬화
  parallel_threshold: 3  # 3개 이상이면 병렬

  # 빠른 응답자 우선 처리
  early_return: true

  # 타임아웃 관리
  timeout_per_architect: 60s
  total_phase_timeout: 180s
```

### 캐싱

```yaml
caching:
  # 동일 요구사항 캐시
  requirement_cache: true
  cache_ttl: 3600s

  # 아키텍트 응답 캐시
  response_cache: false  # 항상 새로운 검토
```
