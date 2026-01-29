---
description: Clean Architecture, Hexagonal, MSA/SAGA 패턴
user-invocable: false
---

# Application Architecture Skill

Clean Architecture, Hexagonal Architecture, MSA 패턴을 담당합니다.

## 핵심 역량

### Clean Architecture

#### The Dependency Rule
```
"소스 코드 의존성은 반드시 안쪽을 향해야 한다"

          ┌───────────────────────────┐
          │     Frameworks &          │
          │       Drivers             │
          │  ┌───────────────────┐    │
          │  │ Interface Adapters│    │
          │  │  ┌─────────────┐  │    │
          │  │  │  Use Cases  │  │    │
          │  │  │  ┌───────┐  │  │    │
          │  │  │  │Entity │  │  │    │
          │  │  │  └───────┘  │  │    │
          │  │  └─────────────┘  │    │
          │  └───────────────────┘    │
          └───────────────────────────┘

안쪽 원은 바깥쪽 원에 대해 아무것도 알지 못한다
```

#### Layers
| Layer | 책임 | 변경 빈도 |
|-------|------|-----------|
| **Entities** | 핵심 비즈니스 규칙 | 낮음 (가장 안정) |
| **Use Cases** | 애플리케이션 비즈니스 규칙 | 중간 |
| **Interface Adapters** | 데이터 변환 | 중간 |
| **Frameworks** | 외부 인터페이스 | 높음 (가장 불안정) |

#### Crossing Boundaries
```
Dependency Inversion으로 의존성 방향 제어:

Use Case Layer          Interface Adapter Layer
┌─────────────────┐    ┌─────────────────────┐
│   Use Case      │    │    Presenter        │
│       │         │    │        ▲            │
│       ▼         │    │        │            │
│  <<interface>>  │────│────implements       │
│  Output Port    │    │                     │
└─────────────────┘    └─────────────────────┘
```

### Hexagonal Architecture (Ports & Adapters)

```
        Driving Side                    Driven Side
       (Primary/Left)                  (Secondary/Right)

 ┌─────────────┐                           ┌─────────────┐
 │  REST API   │                           │  Database   │
 │  Adapter    │                           │  Adapter    │
 └──────┬──────┘                           └──────┬──────┘
        │                                         │
        ▼                                         ▼
 ┌─────────────┐     ┌─────────────┐      ┌─────────────┐
 │   Input     │────>│ Application │<─────│   Output    │
 │   Port      │     │    Core     │      │   Port      │
 └─────────────┘     └─────────────┘      └─────────────┘
        ▲                                         ▲
        │                                         │
 ┌──────┴──────┐                           ┌──────┴──────┐
 │  CLI        │                           │  Message    │
 │  Adapter    │                           │  Adapter    │
 └─────────────┘                           └─────────────┘

Primary Ports: 애플리케이션을 구동
Secondary Ports: 애플리케이션이 사용
```

### MSA Patterns

#### SAGA Pattern
| 스타일 | 특징 | 적합한 경우 |
|--------|------|-------------|
| **Choreography** | 이벤트 기반, 분산 | 2-4개 서비스, 단순 흐름 |
| **Orchestration** | 중앙 조율자 | 4+ 서비스, 복잡한 로직 |

#### Orchestration SAGA
```
         ┌──────────────┐
         │ Orchestrator │
         └──────┬───────┘
       ┌────────┼────────┐
       ▼        ▼        ▼
    ┌─────┐  ┌─────┐  ┌─────┐
    │ Svc │  │ Svc │  │ Svc │
    │  A  │  │  B  │  │  C  │
    └─────┘  └─────┘  └─────┘

장점: 흐름 명확, 중앙 제어, 복잡한 보상 로직 처리
단점: 조율자에 로직 집중, 단일 장애점 가능성
```

#### Other MSA Patterns
| Pattern | 문제 | 해결책 |
|---------|------|--------|
| **API Gateway** | 여러 서비스 직접 호출 | 단일 진입점 |
| **Service Discovery** | 동적 IP/포트 | 서비스 레지스트리 |
| **Circuit Breaker** | 연쇄 장애 | 빠른 실패로 보호 |
| **Sidecar** | 공통 기능 중복 | 프록시로 추출 |
| **Database per Service** | 데이터 독립성 | 서비스별 DB |
| **Strangler Fig** | 레거시 마이그레이션 | 점진적 교체 |

### 디렉토리 구조 예시

```
src/
├── domain/                    # Entities
│   ├── entities/
│   ├── value-objects/
│   └── domain-services/
├── application/               # Use Cases
│   ├── use-cases/
│   ├── ports/
│   │   ├── input/            # Driving Ports
│   │   └── output/           # Driven Ports
│   └── dto/
├── infrastructure/            # Frameworks & Drivers
│   ├── persistence/
│   ├── messaging/
│   └── external/
└── interfaces/               # Interface Adapters
    ├── api/
    ├── cli/
    └── presenters/
```

## 평가 체크리스트

### Clean Architecture
- [ ] 의존성이 안쪽으로만 향하는가?
- [ ] Domain이 프레임워크 독립적인가?
- [ ] 테스트가 외부 의존성 없이 가능한가?

### MSA
- [ ] 서비스 간 동기 호출 최소화?
- [ ] 분산 트랜잭션이 SAGA로 처리?
- [ ] Circuit Breaker 적용?
- [ ] 서비스 장애 격리 가능?

## 사용 시점
- 새 애플리케이션 구조 설계
- 레이어 분리 검토
- 분산 트랜잭션 설계
- 서비스 간 통신 설계
- 레거시 마이그레이션 계획
