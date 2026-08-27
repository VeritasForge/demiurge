---
description: DDD Strategic/Tactical Design, Bounded Context, Aggregate 패턴
user-invocable: false
---

# Domain-Driven Design Skill

도메인 중심 설계, Bounded Context, Aggregate, 전략적/전술적 패턴을 담당합니다.

## 핵심 역량

### 전략적 설계 (Strategic Design)

#### Bounded Context
```
Bounded Context = 특정 도메인 모델이 적용되는 명시적 경계

특징:
• 하나의 Ubiquitous Language가 일관되게 사용되는 범위
• 팀 조직과 일치하는 것이 이상적 (Conway's Law)
• 서로 다른 Context는 같은 용어가 다른 의미를 가질 수 있음
```

#### Context Mapping Patterns
| 패턴 | 설명 | 사용 시점 |
|------|------|-----------|
| **Shared Kernel** | 공유 도메인 모델 | 긴밀한 협력 |
| **Customer/Supplier** | 상류-하류 관계 | 명확한 의존 |
| **Conformist** | 하류가 상류 모델 수용 | 협상력 없음 |
| **ACL** | 번역 계층 | 레거시/외부 연동 |
| **Open Host** | 표준 프로토콜 | 다수 소비자 |
| **Published Language** | 공유 언어 | 데이터 교환 |
| **Separate Ways** | 통합 안 함 | 비용 > 이점 |
| **Partnership** | 공동 운명 | 상호 의존 |

#### Subdomain Types
| 유형 | 설명 | 투자 전략 |
|------|------|-----------|
| **Core** | 경쟁 우위의 핵심 | 최고의 인력, 맞춤 개발 |
| **Supporting** | Core를 지원 | 적절한 품질 |
| **Generic** | 일반적 기능 | 외부 솔루션 활용 |

### 전술적 설계 (Tactical Design)

#### Building Blocks
```
┌─────────────────────────────────────────────────────────────┐
│                     Aggregate                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Aggregate Root (Entity)                             │   │
│  │  ├── Entity (내부)                                  │   │
│  │  ├── Value Object                                   │   │
│  │  └── Value Object                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  불변조건 (Invariants): Aggregate 내에서 일관성 보장        │
│  경계: 하나의 트랜잭션에서 하나의 Aggregate만 수정          │
└─────────────────────────────────────────────────────────────┘
```

#### Entity vs Value Object
| 구분 | Entity | Value Object |
|------|--------|--------------|
| 정체성 | 고유 ID | 속성 값 |
| 변경 | Mutable | Immutable |
| 동등성 | ID 기반 | 값 기반 |
| 예시 | User, Order | Money, Address |

#### Aggregate Design Rules
1. 하나의 트랜잭션에서 하나의 Aggregate만 수정
2. Aggregate Root만 외부에서 참조 가능
3. Aggregate는 가능한 작게 유지
4. ID로 다른 Aggregate 참조 (객체 참조 X)

### Domain Events

```
Domain Event 특징:
├── 과거 시제 명명 (OrderPlaced, PaymentReceived)
├── 불변 (Immutable)
├── 발생 시점 포함 (occurredAt)
└── Aggregate 간 통신 수단

사용 패턴:
├── Event Notification: 최소 데이터
├── Event-Carried State Transfer: 충분한 데이터
└── Event Sourcing: 이벤트가 곧 상태
```

### Repository Pattern
```
Repository = Aggregate의 Collection-like Interface

목적:
• Domain Layer와 Infrastructure Layer 분리
• Aggregate 단위의 저장/조회
• 도메인 모델 중심의 인터페이스

규칙:
• Aggregate당 하나의 Repository
• Repository 인터페이스는 Domain Layer에
• 구현체는 Infrastructure Layer에
```

## Ubiquitous Language

### 용어집 템플릿
```markdown
### Term: [용어]
- **Definition**: 정확한 정의
- **Context**: 적용되는 Bounded Context
- **Examples**: 사용 예시
- **Related Terms**: 관련 용어
- **Anti-patterns**: 잘못된 사용
```

### 언어 일관성 규칙
- 코드에서 도메인 용어 그대로 사용
- 축약어 사용 자제
- 도메인 전문가와 같은 용어 사용
- 기술 용어와 도메인 용어 구분

## 모델링 기법

### Event Storming
```
1. Domain Events (오렌지): 과거형으로 중요 사건
2. Commands (파랑): 이벤트를 유발하는 행위
3. Aggregates (노랑): 커맨드 처리, 이벤트 발생
4. Policies (보라): "~할 때 ~한다" 자동 반응
5. Read Models (초록): 의사결정에 필요한 정보
6. External Systems (분홍): 외부 시스템
7. Hotspots (빨강): 질문, 리스크, 불확실성
```

### Domain Model 평가
- [ ] Ubiquitous Language가 코드에 반영되는가?
- [ ] Aggregate 경계가 불변조건을 보호하는가?
- [ ] Entity/VO 구분이 적절한가?
- [ ] Bounded Context가 명확한가?
- [ ] Context Map이 문서화되어 있는가?

## Anti-Corruption Layer (ACL)

### 목적
```
외부/레거시 시스템의 모델이 도메인 모델을 오염시키지 않도록 보호

┌─────────────────────────────────────────────────┐
│              Our Bounded Context                 │
│  ┌─────────┐     ┌──────────────────────────┐  │
│  │ Domain  │◄────│  Anti-Corruption Layer   │  │
│  │ Model   │     │  (Translator + Facade)   │  │
│  └─────────┘     └─────────────┬────────────┘  │
└────────────────────────────────│───────────────┘
                                 │
               ┌─────────────────▼─────────────────┐
               │      External/Legacy System        │
               └───────────────────────────────────┘
```

### 구성 요소
| 구성 요소 | 역할 |
|-----------|------|
| **Translator** | 외부 모델 ↔ 도메인 모델 변환 |
| **Facade** | 외부 시스템 호출 단순화 |
| **Adapter** | 인터페이스 변환 |

## Specification Pattern

### 목적
- 비즈니스 규칙을 객체로 캡슐화
- 규칙 조합 가능 (AND, OR, NOT)
- 재사용 및 테스트 용이

### 기본 구조
```
interface Specification<T> {
    isSatisfiedBy(candidate: T): boolean
    and(other: Specification<T>): Specification<T>
    or(other: Specification<T>): Specification<T>
    not(): Specification<T>
}

// 사용
val highRiskSpec = HighRiskPatientSpec()
val elderlySpec = ElderlyPatientSpec(65)
val criticalSpec = highRiskSpec.and(elderlySpec)

patients.filter { criticalSpec.isSatisfiedBy(it) }
```

### 적용 사례
| 사례 | Specification |
|------|---------------|
| 할인 적용 조건 | VipCustomerSpec, BulkOrderSpec |
| 검색 필터 | ActiveUserSpec, VerifiedSpec |
| 유효성 검증 | ValidAddressSpec |

## Factory Pattern (DDD)

### Aggregate Factory
```
Factory 사용 시점:
• Aggregate 생성이 복잡할 때
• 불변조건 검증이 필요할 때
• 생성 로직이 도메인 지식을 포함할 때

interface OrderFactory {
    fun createOrder(customer: Customer, items: List<OrderItem>): Order
}

class OrderFactoryImpl : OrderFactory {
    override fun createOrder(...): Order {
        // 불변조건 검증
        require(items.isNotEmpty()) { "Order must have items" }
        // 복잡한 생성 로직
        return Order(...)
    }
}
```

## 사용 시점
- 새 도메인 모델링
- Bounded Context 식별
- Aggregate 설계
- Context 간 통합 설계
- 레거시 시스템 분석
- 외부 시스템 연동 (ACL)
- 비즈니스 규칙 캡슐화 (Specification)
