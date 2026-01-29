# Data Architecture Skill

데이터 모델링, ETL 파이프라인, CQRS/Event Sourcing, Data Mesh를 담당합니다.

## 핵심 역량

### DAMA-DMBOK 지식 영역
1. **Data Governance**: 데이터 관리 정책
2. **Data Architecture**: 데이터 구조 설계
3. **Data Modeling**: 논리적/물리적 모델링
4. **Data Storage**: 저장소 운영
5. **Data Security**: 데이터 보호
6. **Data Integration**: 통합 및 상호운용
7. **Document Management**: 비구조화 데이터
8. **Master Data**: 참조/마스터 데이터
9. **Data Warehousing**: 분석 및 BI
10. **Metadata**: 메타데이터 관리
11. **Data Quality**: 품질 관리

## CQRS (Command Query Responsibility Segregation)

### 기본 구조
```
                    ┌─────────────────┐
                    │    Commands     │
                    │  (Write Model)  │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────>│   Command    │─────>│  Write DB   │
│             │      │   Handler    │      │ (Normalized)│
└─────────────┘      └──────────────┘      └──────┬──────┘
      │                                           │
      │                                    Events/Sync
      │                                           │
      │              ┌──────────────┐      ┌──────▼──────┐
      └─────────────>│   Query      │<─────│  Read DB    │
                     │   Handler    │      │(Denormalized│
                     └──────────────┘      └─────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Queries      │
                    │  (Read Model)   │
                    └─────────────────┘
```

### CQRS 적용 시점
| 시나리오 | CQRS 적용 |
|----------|-----------|
| 읽기/쓰기 비율이 크게 다름 | ✅ 적합 |
| 복잡한 도메인 로직 | ✅ 적합 |
| 단순 CRUD | ❌ 오버엔지니어링 |
| 팀 규모 작음 | ❌ 복잡성 부담 |

## Event Sourcing

### 기본 개념
```
전통적 방식:
┌──────────────────────────────────────┐
│ Account: balance = 100               │  ← 현재 상태만 저장
└──────────────────────────────────────┘

Event Sourcing:
┌──────────────────────────────────────┐
│ 1. AccountCreated(id=A, amount=0)    │
│ 2. MoneyDeposited(id=A, amount=150)  │
│ 3. MoneyWithdrawn(id=A, amount=50)   │  ← 모든 이벤트 저장
└──────────────────────────────────────┘
    replay → balance = 0 + 150 - 50 = 100
```

### Event Store 구조
```
┌────────┬───────────────────┬─────────────┬────────────────┐
│ seq_no │ aggregate_id      │ event_type  │ event_data     │
├────────┼───────────────────┼─────────────┼────────────────┤
│ 1      │ account-123       │ Created     │ { "amount": 0 }│
│ 2      │ account-123       │ Deposited   │ { "amount": 150}│
│ 3      │ account-123       │ Withdrawn   │ { "amount": 50} │
└────────┴───────────────────┴─────────────┴────────────────┘
```

### Snapshot 전략
```
Events: [1] [2] [3] ... [99] [Snapshot@100] [101] [102]
                              │
Rebuild: Snapshot + events after snapshot
         (훨씬 빠름)
```

## Data Mesh

### 4가지 원칙
| 원칙 | 설명 |
|------|------|
| **Domain Ownership** | 도메인 팀이 데이터 소유 |
| **Data as a Product** | 데이터를 제품으로 취급 |
| **Self-Serve Platform** | 셀프 서비스 인프라 |
| **Federated Governance** | 연합 거버넌스 |

### Data Mesh vs Data Lake
```
Data Lake (중앙집중식):
┌───────────┐
│  Team A   │──┐
├───────────┤  │     ┌─────────────┐
│  Team B   │──┼────>│  Data Lake  │
├───────────┤  │     │  (Central)  │
│  Team C   │──┘     └─────────────┘
└───────────┘

Data Mesh (분산):
┌───────────────────┐   ┌───────────────────┐
│ Domain A          │   │ Domain B          │
│ ┌───────────────┐ │   │ ┌───────────────┐ │
│ │ Data Product  │◄├───┤►│ Data Product  │ │
│ └───────────────┘ │   │ └───────────────┘ │
└───────────────────┘   └───────────────────┘
```

### 데이터 모델링 레벨
| 레벨 | 이름 | 목적 |
|------|------|------|
| Conceptual | 개념 모델 | 비즈니스 엔티티 정의 |
| Logical | 논리 모델 | 속성, 관계, 정규화 |
| Physical | 물리 모델 | 테이블, 인덱스, 파티션 |

## 사용 시점
- 새 데이터 소스 연동
- 스키마 변경 검토
- ETL 파이프라인 설계
- 데이터 품질 이슈 분석
