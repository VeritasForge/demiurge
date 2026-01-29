# Healthcare Compliance Rules

---
description: 의료 시스템 규제 준수 규칙 (HIPAA, FDA SaMD)
globs:
  - "**/*.py"
  - "**/*.kt"
  - "**/*.java"
---

## HIPAA Security Rule 준수

### PHI (Protected Health Information) 보호
- 환자 이름, 연락처, 주민번호 등 PHI는 반드시 암호화
- PHI 접근 시 감사 로그 필수 기록
- 최소 필요 원칙 (Minimum Necessary) 준수

### 접근 통제
- 역할 기반 접근 제어 (RBAC) 필수
- 모든 API 엔드포인트에서 권한 검증
- 세션 타임아웃 설정 필수

### 감사 추적
- PHI 접근 로그: who, what, when, where
- 인증 시도 (성공/실패) 기록
- 데이터 변경 (CRUD) 기록
- 로그 보존 기간: 최소 6년

## FDA SaMD 가이드라인

### 소프트웨어 분류
- 프로젝트 분류에 따른 SaMD Class 확인 (Class I/II/III)
- AI 모델 변경 시 영향 분석 필수
- 임상 검증 문서화

### 재현 가능성
- 모델 버전 관리 필수
- 입력/출력 로깅으로 재현 가능
- 알고리즘 변경 이력 추적

## 임상 점수 정확성

### MEWS/NEWS 계산
- 표준 점수표 기준 정확히 구현
- 파라미터 범위 검증 필수
- 단위 변환 주의 (체온: °C, 혈압: mmHg)

### AI 모델
- 앙상블 불확실성(std) 반드시 제공
- 모델별 Window 기간 준수
- 모델 적용 환경(병동/ICU 등) 검증
