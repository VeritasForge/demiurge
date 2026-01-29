---
description: OWASP Top 10, Zero Trust, 암호화, 인증/인가
user-invocable: false
---

# Security Skill

보안 아키텍처, 취약점 분석, 암호화 전략을 담당합니다.

## 핵심 역량

### OWASP Top 10 (2021)
| 순위 | 취약점 | 대응 |
|------|--------|------|
| A01 | Broken Access Control | RBAC, 최소 권한 |
| A02 | Cryptographic Failures | 강력한 암호화 |
| A03 | Injection | 입력 검증, Prepared Statement |
| A04 | Insecure Design | 위협 모델링 |
| A05 | Security Misconfiguration | 보안 기준선 |
| A06 | Vulnerable Components | 의존성 스캔 |
| A07 | Authentication Failures | MFA, 강력한 세션 |
| A08 | Software Integrity | 서명 검증 |
| A09 | Logging Failures | 중앙 로깅, SIEM |
| A10 | SSRF | 화이트리스트 |

### Zero Trust 5 Pillars (NIST)
1. **Identity**: 강력한 신원 확인
2. **Device**: 디바이스 상태 검증
3. **Network**: 마이크로 세그멘테이션
4. **Application**: 앱 레벨 접근 제어
5. **Data**: 데이터 중심 보안

### HIPAA Security Rule
- **Administrative**: 정책, 절차, 교육
- **Physical**: 시설 접근 통제
- **Technical**: 접근 통제, 감사, 암호화

## 보안 체크리스트

### API 보안
- [ ] 입력 검증 (모든 사용자 입력)
- [ ] SQL Injection 방지
- [ ] XSS 방지 (Output Encoding)
- [ ] CSRF 토큰
- [ ] Rate Limiting
- [ ] CORS 정책

### 인증/인가
- [ ] 강력한 비밀번호 정책
- [ ] 계정 잠금 정책
- [ ] 세션 타임아웃
- [ ] 토큰 갱신 메커니즘
- [ ] 권한 검증 (모든 엔드포인트)

### 데이터 보호
- [ ] 민감 데이터 암호화 (저장/전송)
- [ ] 키 관리 정책
- [ ] 백업 암호화
- [ ] 안전한 삭제

### 감사 (Audit)
- [ ] PHI 접근 로깅
- [ ] 인증 시도 (성공/실패)
- [ ] 데이터 변경 (CRUD)
- [ ] 시스템 이벤트

## 취약점 심각도

| Severity | CVSS | 대응 시간 |
|----------|------|-----------|
| Critical | 9.0-10.0 | 24시간 내 |
| High | 7.0-8.9 | 7일 내 |
| Medium | 4.0-6.9 | 30일 내 |
| Low | 0.1-3.9 | 90일 내 |

## 키 관리

### 환경 변수
```
ENCRYPTION_KEY     # 암호화 키
JWT_SECRET_KEY     # JWT 서명 키
DB_PASSWORD        # DB 접속 정보
MQ_PASSWORD        # MQ 접속 정보
```

### 키 로테이션
- JWT 키: 분기별
- 암호화 키: 연간 (데이터 재암호화 필요)
- 서비스 계정: 분기별

## 사용 시점
- 보안 설계 검토
- 취약점 분석 요청
- 암호화 전략 변경
- 인증/인가 설계
- HIPAA 준수 검토
