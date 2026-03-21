---
description: Richardson Maturity Model, API Versioning, Contract-First
user-invocable: false
---

# API Design Skill

REST API, GraphQL, API Versioning, Contract-First 설계를 담당합니다.

## 핵심 역량

### Richardson Maturity Model

| Level | 이름 | 특징 |
|-------|------|------|
| 0 | The Swamp of POX | 단일 엔드포인트, RPC |
| 1 | Resources | URI로 리소스 식별 |
| 2 | **HTTP Verbs** | 메서드 활용 (권장 최소) |
| 3 | Hypermedia (HATEOAS) | 링크로 상태 전이 |

### REST API 설계 원칙

#### 리소스 중심
```
# Resource-oriented
GET    /patients/{id}
POST   /patients
PUT    /patients/{id}
DELETE /patients/{id}

# Anti-pattern (RPC style)
POST   /getPatient
POST   /createPatient
```

#### 관계 표현
```
# 중첩 리소스 (belongs-to)
GET /patients/{patientId}/encounters

# 필터링 (has-many, 복잡한 관계)
GET /encounters?patientId={id}&status=active
```

### HTTP 메서드 특성

| Method | 용도 | 멱등 | 안전 | 요청 Body |
|--------|------|------|------|-----------|
| GET | 조회 | ✅ | ✅ | ❌ |
| POST | 생성 | ❌ | ❌ | ✅ |
| PUT | 전체 교체 | ✅ | ❌ | ✅ |
| PATCH | 부분 수정 | ❌ | ❌ | ✅ |
| DELETE | 삭제 | ✅ | ❌ | ❌ |

### API Versioning

| 전략 | 예시 | 권장도 |
|------|------|--------|
| **URL Path** | `/api/v1/users` | ⭐⭐⭐ 명확함 |
| Query Param | `/api/users?v=1` | ⭐⭐ 선택적 |
| Header | `Accept-Version: v1` | ⭐⭐ URL 깔끔 |
| Content-Type | `application/vnd.api.v1+json` | ⭐ 표준적 |

### Contract-First Design

```
1. OpenAPI 스펙 정의 (YAML/JSON)
              │
              ▼
2. 스펙 리뷰 및 합의
              │
              ├──────────┬──────────┐
              ▼          ▼          ▼
3. Server Stub   Client SDK   Mock Server
              │          │          │
              ▼          ▼          ▼
4. 구현        통합 테스트    UI 개발
```

### REST vs GraphQL

| 기준 | REST | GraphQL |
|------|------|---------|
| Over-fetching | 발생 가능 | 해결 |
| Under-fetching | N+1 요청 | 단일 요청 |
| 캐싱 | HTTP 기본 지원 | 별도 구현 |
| 버전 관리 | URL 버전 | 스키마 진화 |
| 학습 곡선 | 낮음 | 중간 |
| **적합** | CRUD, 단순 관계 | 복잡한 관계, 유연한 쿼리 |

### Rate Limiting 패턴

```
고정 윈도우:
│ Window 1 │ Window 2 │ Window 3 │
│ 100 req  │ 100 req  │ 100 req  │
└──────────┴──────────┴──────────┘

슬라이딩 윈도우:
현재 시점에서 과거 1분간 요청 수 계산
(더 정밀하지만 메모리 사용 증가)

토큰 버킷:
초당 10개 토큰 충전, 최대 100개 버킷
버스트 트래픽 허용하면서 평균 제한
```

### Pagination 패턴

| 방식 | 예시 | 장점 | 단점 |
|------|------|------|------|
| **Offset** | `?page=2&size=20` | 단순, 랜덤 접근 | 대용량 성능 저하 |
| **Cursor** | `?cursor=abc123&limit=20` | 일관성, 성능 | 랜덤 접근 불가 |
| **Keyset** | `?after_id=100&limit=20` | 성능 우수 | 정렬 필드 필요 |

### Idempotency 구현

```
POST /payments
Idempotency-Key: req-12345

Server:
1. 키가 존재하는지 확인
2. 존재하면 → 저장된 응답 반환
3. 없으면 → 처리 후 결과 저장 (TTL: 24h)
```

## 평가 체크리스트

- [ ] Richardson Level 2 이상?
- [ ] 리소스 중심 설계?
- [ ] 적절한 HTTP 상태 코드?
- [ ] 버전 관리 전략?
- [ ] Rate Limiting 적용?
- [ ] 멱등성 고려?

## 사용 시점
- 새 API 설계
- API 버전 전략 수립
- REST vs GraphQL 결정
- Rate Limiting 설계
- Contract-First 도입
