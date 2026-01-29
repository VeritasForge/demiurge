# DDD Patterns Rules

---
description: Domain-Driven Design 패턴 적용 규칙
globs:
  - "**/domain/**/*.py"
  - "**/domain/**/*.kt"
  - "**/domain/**/*.java"
  - "**/domain/**/*.ts"
  - "**/entities/**/*.py"
  - "**/entities/**/*.kt"
  - "**/aggregate/**/*.py"
  - "**/aggregate/**/*.kt"
---

## Entity 규칙

### 정체성 (Identity)
- 모든 Entity는 고유 ID를 가짐
- ID는 불변 (생성 후 변경 불가)
- equals()는 ID 기반 비교

### 예시
```kotlin
// Good
data class OrderId(val value: UUID)

class Order(
    val id: OrderId,  // 불변 ID
    var status: OrderStatus  // 변경 가능한 상태
)

// Bad
class Order(
    var id: String,  // 변경 가능한 ID
    var status: OrderStatus
)
```

## Value Object 규칙

### 불변성 (Immutability)
- Value Object는 불변
- 변경 시 새 인스턴스 반환
- equals()는 모든 속성 기반 비교

### 예시
```kotlin
// Good - Immutable Value Object
data class Money(
    val amount: BigDecimal,
    val currency: Currency
) {
    fun add(other: Money): Money {
        require(currency == other.currency)
        return Money(amount + other.amount, currency)
    }
}

// Bad - Mutable
class Money(
    var amount: BigDecimal,  // 변경 가능
    var currency: Currency
)
```

## Aggregate 규칙

### 트랜잭션 경계
- 하나의 트랜잭션 = 하나의 Aggregate
- 다른 Aggregate 수정은 Domain Event로
- Aggregate 간 eventual consistency

### 참조 규칙
- 외부에서는 Aggregate Root만 참조
- 내부 Entity/VO는 Root를 통해 접근
- 다른 Aggregate는 ID로만 참조

### 예시
```kotlin
// Good
class Order(val id: OrderId) {  // Aggregate Root
    private val items: MutableList<OrderItem> = mutableListOf()

    fun addItem(productId: ProductId, quantity: Int) {  // Root를 통해 접근
        items.add(OrderItem(productId, quantity))
    }
}

// Bad - 내부 Entity 직접 노출
class Order(val id: OrderId) {
    val items: MutableList<OrderItem> = mutableListOf()  // 외부에서 직접 수정 가능
}
```

## Domain Event 규칙

### 네이밍
- 과거 시제 사용 (OrderPlaced, PaymentReceived)
- 도메인 용어 사용

### 구조
- 불변 (Immutable)
- 발생 시점 포함 (occurredAt)
- 필요한 정보만 포함

### 예시
```kotlin
data class OrderPlaced(
    val orderId: OrderId,
    val customerId: CustomerId,
    val totalAmount: Money,
    val occurredAt: Instant = Instant.now()
)
```

## Repository 규칙

### 인터페이스 위치
- Domain Layer에 인터페이스 정의
- Infrastructure Layer에 구현

### Aggregate 단위
- Aggregate당 하나의 Repository
- Aggregate Root만 저장/조회

### 예시
```kotlin
// Domain Layer
interface OrderRepository {
    fun findById(id: OrderId): Order?
    fun save(order: Order)
    fun delete(id: OrderId)
}

// Infrastructure Layer
class JpaOrderRepository : OrderRepository {
    // JPA 구현
}
```

## Ubiquitous Language 규칙

### 네이밍
- 도메인 용어 그대로 사용
- 축약어 사용 자제
- 코드에서도 도메인 용어 유지

### 예시
```kotlin
// Good - 도메인 용어 사용
class Order(...)  // 도메인 용어
class Product(...)  // 도메인 용어

// Bad - 기술 용어나 축약어
class Ord(...)
class Prd(...)
```

## Anti-Corruption Layer (ACL) 규칙

### 목적
- 외부/레거시 시스템의 모델이 도메인 모델을 오염시키지 않도록 보호
- 경계에서 번역 레이어 역할

### 구조
```
┌─────────────────────────────────────────────────────────┐
│                     Our Bounded Context                  │
│  ┌─────────────┐     ┌─────────────────────────────┐   │
│  │   Domain    │◄────│  Anti-Corruption Layer      │   │
│  │   Model     │     │  ┌─────────┐ ┌──────────┐   │   │
│  └─────────────┘     │  │Translator│ │ Facade   │   │   │
│                      │  └─────────┘ └──────────┘   │   │
│                      └──────────────┬──────────────┘   │
└─────────────────────────────────────│──────────────────┘
                                      │
                        ┌─────────────▼─────────────┐
                        │    External/Legacy System  │
                        │    (Different Model)       │
                        └───────────────────────────┘
```

### 예시
```kotlin
// ACL - External 모델을 Domain 모델로 변환
class PatientTranslator {
    fun toDomain(external: ExternalPatientDto): Patient {
        return Patient(
            id = PatientId(external.patientNumber),  // 필드명 다름
            name = Name(external.fullName),
            birthDate = parseBirthDate(external.dob)  // 형식 다름
        )
    }
}

// Facade - 외부 시스템 호출 단순화
class LegacyPatientFacade(
    private val legacyClient: LegacyEmrClient,
    private val translator: PatientTranslator
) {
    fun findPatient(id: PatientId): Patient? {
        val external = legacyClient.getPatient(id.value)
        return external?.let { translator.toDomain(it) }
    }
}
```

## Context Mapping 패턴

### 관계 유형
| 패턴 | 설명 | 사용 시점 |
|------|------|-----------|
| **Shared Kernel** | 일부 모델 공유 | 긴밀한 협력 팀 |
| **Customer-Supplier** | 상류/하류 관계 | 명확한 의존 방향 |
| **Conformist** | 상류 모델 수용 | 협상 불가 시 |
| **ACL** | 번역 레이어 | 모델 오염 방지 |
| **Open Host Service** | 표준 프로토콜 제공 | 다수 소비자 |
| **Published Language** | 공유 언어 정의 | 통합 표준화 |
| **Separate Ways** | 통합 안함 | 비용 > 이익 |

### Context Map 예시
```
┌───────────────────┐   ACL   ┌───────────────────┐
│ External System   │◄────────│    Core Domain    │
│   (Conformist)    │         │                   │
└───────────────────┘         └─────────┬─────────┘
                                        │
                              Customer-Supplier
                                        │
                              ┌─────────▼─────────┐
                              │ Analytics Context │
                              │   (Downstream)    │
                              └───────────────────┘
```

## Specification Pattern

### 목적
- 비즈니스 규칙을 객체로 캡슐화
- 규칙 조합 가능 (AND, OR, NOT)

### 예시
```kotlin
// Specification 인터페이스
interface Specification<T> {
    fun isSatisfiedBy(candidate: T): Boolean

    fun and(other: Specification<T>): Specification<T>
    fun or(other: Specification<T>): Specification<T>
    fun not(): Specification<T>
}

// 구체적인 Specification
class HighRiskPatientSpec : Specification<Patient> {
    override fun isSatisfiedBy(candidate: Patient): Boolean {
        return candidate.ktasLevel <= 2
    }
}

class ElderlyPatientSpec(private val ageThreshold: Int = 65) : Specification<Patient> {
    override fun isSatisfiedBy(candidate: Patient): Boolean {
        return candidate.age >= ageThreshold
    }
}

// 조합 사용
val criticalPatientSpec = HighRiskPatientSpec().and(ElderlyPatientSpec())
val criticalPatients = patients.filter { criticalPatientSpec.isSatisfiedBy(it) }
```
