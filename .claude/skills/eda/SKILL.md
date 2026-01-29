---
description: Event-Driven Architecture, SAGA, Event Sourcing, 멱등성
user-invocable: false
---

# Event-Driven Architecture Skill

이벤트 기반 아키텍처, 메시징 패턴, SAGA, CQRS를 담당합니다.

## 핵심 역량

### Martin Fowler의 이벤트 패턴

| 패턴 | 설명 | 특징 |
|------|------|------|
| **Event Notification** | 최소 데이터만 전달 | 느슨한 결합, 추가 쿼리 필요 |
| **Event-Carried State** | 충분한 데이터 포함 | 쿼리 불필요, 데이터 중복 |
| **Event Sourcing** | 이벤트가 상태 | 완전한 감사 추적, 복잡 |
| **CQRS** | 읽기/쓰기 분리 | 독립 최적화, eventual consistency |

### SAGA Pattern

#### Choreography
```
각 서비스가 이벤트 발행/구독 (중앙 조율자 없음)

Service A → Event → Service B → Event → Service C

장점: 느슨한 결합, 확장성
단점: 흐름 파악 어려움, 순환 의존 가능
적합: 2-4개 서비스, 단순한 흐름
```

#### Orchestration
```
중앙 조율자가 각 서비스에 지시

        Orchestrator
       /     |     \
    Svc A  Svc B  Svc C

장점: 흐름 명확, 복잡한 보상 로직
단점: 조율자에 로직 집중
적합: 4+ 서비스, 복잡한 로직
```

### 메시지 전달 보장

| 보장 | 설명 | 구현 |
|------|------|------|
| At-most-once | 최대 1번 | Fire and forget |
| At-least-once | 최소 1번 | ACK + Retry |
| Exactly-once | 정확히 1번 | 멱등성 + 트랜잭션 |

### 멱등성 패턴

1. **Message ID 기반**: 처리된 메시지 ID 저장
2. **Business Key 기반**: 자연 키로 중복 체크
3. **Optimistic Locking**: version으로 동시 수정 방지

### DLQ (Dead Letter Queue)

```
Original Queue
    │
    ├── reject/expire/maxlen
    │
    ▼
Dead Letter Exchange
    │
    ▼
DLQ
    │
    ├── retry_count < max → Republish (backoff)
    └── retry_count >= max → Archive
```

### 메시지 스키마

```json
{
  "header": {
    "messageId": "uuid (idempotency)",
    "correlationId": "uuid (trace)",
    "timestamp": "ISO8601",
    "version": "1.0",
    "source": "service-name"
  },
  "payload": { }
}
```

## 평가 체크리스트

- [ ] 이벤트 스키마 버전 관리?
- [ ] 멱등성 보장?
- [ ] DLQ 전략 정의?
- [ ] 보상 트랜잭션 설계?
- [ ] 메시지 추적 가능? (correlation ID)

## 사용 시점
- 메시징 아키텍처 설계
- SAGA 설계 (Choreography/Orchestration)
- Event Sourcing/CQRS 도입
- DLQ 전략 수립
- 멱등성 설계
