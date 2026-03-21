---
description: POSA Vol.2, Reactor/Proactor, Active Object, Thread Pool
user-invocable: false
---

# Concurrency Patterns Skill

POSA Volume 2 동시성 패턴과 현대적 비동기 패턴을 담당합니다.

## 핵심 역량

### POSA Vol.2 Event Handling Patterns

| Pattern | 특징 | 사용 사례 |
|---------|------|-----------|
| **Reactor** | 동기적 이벤트 디멀티플렉싱 | Node.js, Nginx, Redis |
| **Proactor** | 비동기 완료 통지 | Windows IOCP, Boost.Asio |

### Reactor vs Proactor

```
Reactor (동기 + 논블로킹):
1. select/poll/epoll로 이벤트 대기
2. 이벤트 발생 시 핸들러 호출
3. 핸들러가 직접 I/O 수행

Proactor (비동기):
1. 비동기 I/O 작업 시작
2. OS가 I/O 완료
3. 완료 통지로 핸들러 호출
```

### Concurrency Patterns

| Pattern | 분리 대상 | 특징 |
|---------|----------|------|
| **Active Object** | 호출 ↔ 실행 | 비동기 메서드 호출 |
| **Half-Sync/Half-Async** | 동기 ↔ 비동기 레이어 | 복잡성 분리 |
| **Leader/Followers** | 이벤트 처리 스레드 | 오버헤드 최소화 |

### Thread Pool Strategies

| 전략 | 설명 | 적합한 경우 |
|------|------|-------------|
| **Fixed Pool** | 고정 크기 | 예측 가능한 부하 |
| **Cached Pool** | 동적 생성/회수 | 짧은 비동기 작업 |
| **Work Stealing** | 유휴 스레드가 작업 훔침 | 불균형 작업 부하 |
| **Fork/Join** | 분할 정복 | 재귀적 병렬 작업 |

### Synchronization Patterns

```
Scoped Locking (RAII):
try (lock) {
    // critical section
}  // auto unlock

Double-Checked Locking:
if (instance == null) {
    synchronized {
        if (instance == null) {
            instance = new Singleton();
        }
    }
}
```

### Lock-Free Patterns

| Pattern | 메커니즘 | 용도 |
|---------|----------|------|
| **CAS Loop** | Compare-And-Swap | 원자적 업데이트 |
| **Lock-Free Queue** | CAS + 포인터 조작 | 고성능 큐 |
| **RCU** | Read-Copy-Update | 읽기 최적화 |

### Modern Async Patterns

```
Structured Concurrency:
- 부모 스코프가 자식 작업 관리
- 모든 자식 완료 후 부모 종료
- 취소 전파

Kotlin: coroutineScope { }
Java: StructuredTaskScope (Project Loom)
```

## 평가 체크리스트

- [ ] I/O 바운드 vs CPU 바운드 식별?
- [ ] 적절한 동시성 모델 선택?
- [ ] 데드락/Race condition 방지?
- [ ] Backpressure 처리?
- [ ] 스레드 풀 크기 최적화?

## 사용 시점
- 고성능 동시성 시스템 설계
- I/O 멀티플렉싱 선택
- 스레드 풀 전략 결정
- 동기화 패턴 적용
