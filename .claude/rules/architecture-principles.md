# Architecture Principles Rules

---
description: 아키텍처 설계 시 준수해야 할 일반 원칙
globs:
  - "**/*.py"
  - "**/*.kt"
  - "**/*.java"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.go"
---

## 관심사 분리 (Separation of Concerns)

### 레이어 구조
- 각 레이어는 명확한 책임을 가짐
- 레이어 간 의존성은 한 방향으로만
- 상위 레이어는 하위 레이어에 의존
- 하위 레이어는 상위 레이어를 모름

### Clean Architecture The Dependency Rule
- 소스 코드 의존성은 안쪽으로만 향해야 함
- Domain/Entity 레이어는 외부 프레임워크에 의존하지 않음
- Dependency Inversion으로 의존성 방향 제어

## DDD 원칙

### Aggregate Rules
- 하나의 트랜잭션에서 하나의 Aggregate만 수정
- Aggregate Root만 외부에서 참조 가능
- Aggregate는 가능한 작게 유지
- ID로 다른 Aggregate 참조 (객체 참조 X)

### Repository Pattern
- Aggregate 단위로 Repository 설계
- Repository 인터페이스는 Domain Layer에
- 구현체는 Infrastructure Layer에

## MSA 원칙

### 서비스 경계
- 각 서비스는 명확한 책임(Bounded Context)
- 서비스 간 직접 DB 접근 금지
- API 또는 메시지 큐를 통해서만 통신

### 분산 트랜잭션
- 2PC 대신 SAGA 패턴 사용
- 보상 트랜잭션 설계 필수
- eventual consistency 고려

### 장애 격리
- Circuit Breaker 패턴 적용
- Timeout, Retry 전략 필수
- Bulkhead 패턴으로 리소스 격리

## EDA 원칙

### 메시지 설계
- 메시지 ID (멱등성용) 필수
- Correlation ID (추적용) 필수
- 타임스탬프 및 버전 포함
- 스키마 버전 관리

### 멱등성 보장
- 모든 Consumer는 중복 처리 대비
- 고유 식별자 기반 중복 체크
- At-least-once 전달 가정

### DLQ 전략
- 재시도 정책 정의 (횟수, 백오프)
- 최종 실패 시 Archive
- 에러 분류 (재시도 가능/불가능)

## 보안 원칙

### Defense in Depth
- 다층 보안 적용
- 단일 보안 메커니즘에 의존하지 않음

### Least Privilege
- 최소 권한 원칙
- 필요한 권한만 부여

### Secure by Default
- 기본값은 안전하게
- 명시적으로 허용해야만 접근 가능
