# Integration Skill

시스템 통합, API 설계, REST/gRPC 패턴을 담당합니다.

## 핵심 역량

### Google API Design Guide 원칙
1. **Resource-Oriented Design**: 리소스 중심 설계
2. **Standard Methods**: GET, POST, PUT, PATCH, DELETE
3. **Custom Methods**: POST /resource:customMethod
4. **Naming Conventions**: 일관된 네이밍

### REST vs gRPC
| 기준 | REST | gRPC |
|------|------|------|
| 프로토콜 | HTTP/1.1, HTTP/2 | HTTP/2 only |
| 페이로드 | JSON (텍스트) | Protobuf (바이너리) |
| 스트리밍 | 제한적 | 양방향 지원 |
| 브라우저 지원 | 네이티브 | grpc-web 필요 |
| 사용 시나리오 | 외부 API, 웹 | 내부 서비스 간 |

### HTTP 메서드 사용
| Method | 용도 | 멱등성 | 안전 |
|--------|------|--------|------|
| GET | 조회 | Yes | Yes |
| POST | 생성 | No | No |
| PUT | 전체 수정 | Yes | No |
| PATCH | 부분 수정 | No | No |
| DELETE | 삭제 | Yes | No |

## URL 네이밍 규칙

### 올바른 예시
```
GET  /api/v1/patients/{id}
POST /api/v1/patients
GET  /api/v1/patients/{id}/encounters
POST /api/v1/patients/{id}/encounters/{encounterId}/notes
```

### 잘못된 예시
```
GET  /api/v1/getPatient?id=123
POST /api/v1/createPatient
GET  /api/v1/patientEncounters
```

## API 버전 관리

### 전략
- **URL Path**: /api/v1/, /api/v2/ (현재 사용)
- **Header**: Accept: application/vnd.myservice.v1+json

### 버전 전환 정책
1. 새 버전 배포 (v2 alongside v1)
2. Deprecation 공지 (6개월)
3. 기존 버전 종료

## 사용 시점
- 새 API 엔드포인트 설계
- 외부 시스템 연동
- API 버전 관리
- 서비스 간 통신 최적화
