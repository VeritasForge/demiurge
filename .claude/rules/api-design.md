# API Design Rules

---
description: REST API 설계 규칙 (Richardson Maturity Model, API First Design)
globs:
  - "**/controller/**/*.kt"
  - "**/controller/**/*.java"
  - "**/router/**/*.py"
  - "**/routes/**/*.ts"
  - "**/api/**/*.kt"
  - "**/api/**/*.py"
---

## Richardson Maturity Model

### Level 0: The Swamp of POX
```
단일 엔드포인트, RPC 스타일
POST /api → { "action": "getPatient", "id": 123 }
(사용하지 않음)
```

### Level 1: Resources
```
리소스별 URI, 하지만 HTTP 메서드 미활용
POST /patients/123 → { "action": "get" }
POST /patients/123 → { "action": "delete" }
```

### Level 2: HTTP Verbs (권장 최소 수준)
```
HTTP 메서드를 활용한 리소스 조작
GET    /patients/123    → 조회
POST   /patients        → 생성
PUT    /patients/123    → 수정
DELETE /patients/123    → 삭제
```

### Level 3: Hypermedia Controls (HATEOAS)
```json
{
  "id": 123,
  "name": "John Doe",
  "_links": {
    "self": { "href": "/patients/123" },
    "encounters": { "href": "/patients/123/encounters" },
    "update": { "href": "/patients/123", "method": "PUT" }
  }
}
```

## API First Design

### OpenAPI 우선 원칙
1. **Contract First**: 코드 전에 스펙 정의
2. **스펙 리뷰**: 구현 전 API 스펙 합의
3. **코드 생성**: 스펙에서 클라이언트/서버 코드 생성
4. **테스트 자동화**: 스펙 기반 계약 테스트

## URL 네이밍 규칙

### 리소스 기반 URL
```
# Good
GET  /api/v1/patients/{id}
POST /api/v1/patients
GET  /api/v1/patients/{id}/encounters

# Bad
GET  /api/v1/getPatient?id=123
POST /api/v1/createPatient
```

### 복수형 사용
```
# Good
/api/v1/patients
/api/v1/encounters

# Bad
/api/v1/patient
/api/v1/encounter
```

### 소문자 + 하이픈
```
# Good
/api/v1/chief-complaints

# Bad
/api/v1/chiefComplaints
/api/v1/chief_complaints
```

## HTTP 메서드

| Method | 용도 | 멱등성 |
|--------|------|--------|
| GET | 조회 | Yes |
| POST | 생성 | No |
| PUT | 전체 수정 | Yes |
| PATCH | 부분 수정 | No |
| DELETE | 삭제 | Yes |

## 응답 형식

### 성공 응답
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    // 실제 데이터
  }
}
```

### 에러 응답
```json
{
  "code": "404001",
  "message": "Patient not found",
  "details": {
    "patientId": "123"
  }
}
```

### 에러 코드 형식
```
{HTTP_STATUS}{3자리_일련번호}

예시:
400001: 필수 필드 누락
401001: 토큰 만료
404001: 환자 없음
409001: 중복 데이터
500001: 서버 오류
```

## HTTP 상태 코드

### 성공
- 200: 조회/수정 성공
- 201: 생성 성공
- 204: 삭제 성공 (본문 없음)
- 207: Multi-Status (부분 성공)

### 클라이언트 에러
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 422: Unprocessable Entity

### 서버 에러
- 500: Internal Server Error
- 502: Bad Gateway
- 503: Service Unavailable
- 504: Gateway Timeout

## 페이징

### 요청
```
GET /api/v1/patients?page=0&size=20&sort=createdAt,desc
```

### 응답
```json
{
  "data": {
    "content": [...],
    "page": 0,
    "size": 20,
    "totalElements": 100,
    "totalPages": 5
  }
}
```

## 버전 관리

### URL Path 방식 (현재 사용)
```
/api/v1/patients
/api/v2/patients
```

### 버전 전환 정책
1. 새 버전 배포 (v1, v2 공존)
2. Deprecation 공지 (6개월)
3. 기존 버전 종료

## API Versioning Strategies

| 전략 | 예시 | 장점 | 단점 |
|------|------|------|------|
| **URL Path** | /api/v1/users | 명확, 캐싱 용이 | URL 변경 |
| **Query Param** | /api/users?v=1 | 선택적 | 기본값 혼란 |
| **Header** | Accept-Version: v1 | URL 깔끔 | 테스트 어려움 |
| **Content-Type** | Accept: application/vnd.api.v1+json | 표준적 | 복잡 |

## Rate Limiting

### 헤더 표준
```
X-RateLimit-Limit: 1000        # 윈도우당 최대 요청
X-RateLimit-Remaining: 999     # 남은 요청
X-RateLimit-Reset: 1640000000  # 리셋 시각 (Unix timestamp)
Retry-After: 60                # 429 응답 시 재시도 대기 (초)
```

### 응답 (429 Too Many Requests)
```json
{
  "code": "429001",
  "message": "Rate limit exceeded",
  "details": {
    "retryAfter": 60
  }
}
```

## GraphQL 고려사항

### REST vs GraphQL 선택
| 기준 | REST | GraphQL |
|------|------|---------|
| **Over-fetching** | 발생 가능 | 해결 |
| **Under-fetching** | N+1 요청 | 단일 요청 |
| **캐싱** | HTTP 캐싱 용이 | 별도 구현 필요 |
| **버전 관리** | URL 버전 | 스키마 진화 |
| **적합** | CRUD, 단순 관계 | 복잡한 관계, 유연한 쿼리 |

## Idempotency

### 멱등성 키 헤더
```
POST /api/v1/payments
Idempotency-Key: unique-request-id-123

# 동일 키로 재요청 시 동일 결과 반환 (중복 처리 방지)
```

### 멱등성 보장 메서드
| Method | 멱등 | 안전 |
|--------|------|------|
| GET | Yes | Yes |
| HEAD | Yes | Yes |
| OPTIONS | Yes | Yes |
| PUT | Yes | No |
| DELETE | Yes | No |
| POST | **No** | No |
| PATCH | **No** | No |
