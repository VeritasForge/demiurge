# Security Requirements Rules

---
description: 보안 요구사항 규칙
globs:
  - "**/*.py"
  - "**/*.kt"
  - "**/*.java"
  - "**/*.ts"
---

## 인증/인가

### JWT 토큰
- Access Token: 15분 만료
- Refresh Token: 7일 만료
- 토큰 갱신 메커니즘 구현

### 비밀번호
- Argon2 해싱 사용
- 최소 8자, 대소문자+숫자+특수문자 조합
- 계정 잠금: 5회 실패 시 30분 잠금

### 세션
- 서버 사이드 세션 검증
- 동시 로그인 제한 고려
- 비활성 세션 타임아웃

## 입력 검증

### SQL Injection 방지
- Parameterized Query 또는 ORM 사용 필수
- 동적 쿼리 생성 시 화이트리스트 검증
- 사용자 입력 직접 쿼리 포함 금지

### XSS 방지
- 출력 인코딩 (HTML, JavaScript, URL)
- Content-Type 헤더 명시
- CSP (Content Security Policy) 적용

### 기타 입력 검증
- 모든 사용자 입력 검증
- 파일 업로드 시 확장자/MIME 타입 검증
- 경로 조작 방지 (Path Traversal)

## 암호화

### 저장 데이터
- PHI: AES-128-CBC 또는 AES-256
- ID 필드(정렬 필요): OPE
- 비밀번호: Argon2 (단방향)

### 전송 데이터
- 모든 API: HTTPS/TLS 1.2+
- RabbitMQ: AMQPS (TLS)
- Database: SSL Connection

### 키 관리
- 환경 변수로 키 관리
- 하드코딩된 키/비밀번호 금지
- 키 로테이션 정책 준수

## API 보안

### Rate Limiting
- 엔드포인트별 요청 제한
- IP 기반 또는 사용자 기반

### CORS
- 허용된 Origin만 명시
- 와일드카드(*) 사용 자제

### 에러 처리
- 상세 에러 정보 노출 금지
- 스택 트레이스 숨김 (프로덕션)
- 일관된 에러 응답 형식
