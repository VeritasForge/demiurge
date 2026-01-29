# Messaging Patterns Rules

---
description: RabbitMQ 메시징 패턴 규칙
globs:
  - "**/messaging/**/*.kt"
  - "**/event-processor/**/*.kt"
  - "**/sync/**/*.py"
  - "**/etl/**/*.py"
  - "**/screening/**/*.py"
  - "**/policy/**/*.py"
  - "**/dlq/**/*.py"
---

## 메시지 헤더 필수 포함

### 추적 헤더
```
x-trace-id: UUID (전체 추적용)
x-correlation-id: UUID (연관 메시지 그룹)
x-origin-published-dt: ISO8601 (최초 발행 시간)
x-retry-count: Integer (재시도 횟수)
```

### 우선순위 (선택)
```
x-priority: HIGH | NORMAL | LOW
```

## 큐 사용 규칙

### Process Queue (HIGH 우선순위)
- 최근 메시지 (TTL 내)
- 즉시 처리 필요
- Worker 수: workerCount × 2

### Deferred Queue (NORMAL 우선순위)
- 오래된 메시지 (TTL 초과)
- 지연 처리 가능
- Worker 수: workerCount × 1

## DLQ 처리 규칙

### 재시도 정책
- 최대 재시도: 3회
- 재시도 초과 시 Archive 큐로 이동
- 재시도 시 x-retry-count 증가

### TTL 기반 라우팅
```python
if (now - x-origin-published-dt) < TTL:
    route_to = "process"  # 최근, 우선 처리
else:
    route_to = "deferred"  # 오래됨, 지연 처리
```

## 멱등성 보장

### Consumer 구현 시
- 동일 메시지 중복 처리 대비
- 고유 식별자(entityId 등) 기반 중복 체크
- DB 또는 캐시를 통한 처리 상태 확인

### 분산 락
- 동일 엔티티 동시 처리 방지
- DB INSERT IGNORE 방식
- 락 획득 실패 시 5초 대기 후 REQUEUE

## 에러 처리

### 재시도 가능 에러
- 네트워크 타임아웃
- 서비스 일시 불가 (5xx)
- 락 획득 실패

### 재시도 불가 에러
- 잘못된 메시지 형식 (4xx)
- 비즈니스 로직 실패
- 검증 실패

## ACK/NACK 규칙

### ACK (정상 처리)
- 처리 완료 후 ACK
- 후속 작업 실패해도 메시지 처리는 완료로 간주

### NACK + Requeue
- 일시적 실패, 재처리 가능
- 락 획득 실패
- 의존 서비스 일시 불가

### NACK + No Requeue (→ DLQ)
- 메시지 형식 오류
- 재처리해도 실패 예상
- 비즈니스 규칙 위반
