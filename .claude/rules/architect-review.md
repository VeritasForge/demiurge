# Architect Review Rules

---
description: 아키텍처 리뷰 시 준수해야 할 규칙 및 표준
globs:
  - "**/*.py"
  - "**/*.kt"
  - "**/*.java"
  - "**/*.ts"
  - "**/*.tsx"
---

## 리뷰 응답 표준

### 필수 응답 형식

모든 아키텍트 에이전트는 리뷰 시 다음 형식을 준수해야 합니다:

```yaml
architect: <architect-name>
timestamp: <ISO8601>
round: <round-number>

## Recommendations
- [권고사항 목록]

## Concerns
- [우려사항 목록 with severity]

## Dependencies
- [의존성/선행조건]

## Vote
decision: AGREE | DISAGREE | CONDITIONAL
rationale: [투표 이유]
```

---

## 권고사항 작성 규칙

### 우선순위 정의

| 우선순위 | 정의 | 처리 |
|----------|------|------|
| **HIGH** | 반드시 적용 필요, 미적용 시 심각한 문제 | 필수 반영 |
| **MEDIUM** | 적용 권장, 품질 향상에 기여 | 검토 후 반영 |
| **LOW** | 선택적 적용, nice-to-have | 시간 여유 시 반영 |

### 카테고리 정의

| 카테고리 | 설명 | 담당 아키텍트 |
|----------|------|---------------|
| **DESIGN** | 설계, 구조, 패턴 | Solution, Domain, Application |
| **SECURITY** | 보안, 인증, 암호화 | Security, Healthcare |
| **PERFORMANCE** | 성능, 확장성 | SRE, Cloud-Native, Concurrency |
| **OPERATION** | 운영, 배포, 모니터링 | SRE, Cloud-Native |
| **DATA** | 데이터 모델, 저장소 | Data, Domain |
| **INTEGRATION** | 통합, API, 메시징 | Integration, EDA |
| **COMPLIANCE** | 규정 준수, 표준 | Healthcare, Security |

---

## 우려사항 작성 규칙

### Severity 정의

| Severity | 정의 | 예시 |
|----------|------|------|
| **HIGH** | 시스템 장애, 보안 위협, 규정 위반 가능 | PHI 암호화 누락, SQL Injection 취약점 |
| **MEDIUM** | 성능 저하, 유지보수 어려움 예상 | N+1 쿼리, 하드코딩된 설정값 |
| **LOW** | 개선 가능하지만 큰 영향 없음 | 명명 규칙 불일치, 주석 부족 |

### 우려사항 필수 요소

```yaml
concern:
  id: C1
  severity: HIGH | MEDIUM | LOW
  description: "무엇이 문제인가"
  impact: "문제가 발생하면 어떤 영향이 있는가"
  mitigation: "어떻게 해결할 수 있는가"
  evidence: "문제의 근거 (코드 위치, 문서 참조 등)"
```

---

## 투표 규칙

### 투표 결정 기준

| 투표 | 기준 | 필수 요소 |
|------|------|-----------|
| **AGREE** | 제안에 동의, 주요 우려 없음 | rationale |
| **DISAGREE** | 심각한 우려 존재, 수정 필요 | rationale, alternatives |
| **CONDITIONAL** | 특정 조건 충족 시 동의 | rationale, conditions |

### DISAGREE 시 필수 제공 사항

```yaml
vote:
  decision: DISAGREE
  rationale: "반대 이유 상세 설명"
  blocking_concerns:
    - "해결되어야 할 우려 1"
    - "해결되어야 할 우려 2"
  alternatives:
    - description: "대안 1"
      pros: ["장점"]
      cons: ["단점"]
    - description: "대안 2"
      pros: ["장점"]
      cons: ["단점"]
```

### CONDITIONAL 시 필수 제공 사항

```yaml
vote:
  decision: CONDITIONAL
  rationale: "조건부 동의 이유"
  conditions:
    - condition: "해결되어야 할 조건 1"
      priority: HIGH
      verification: "조건 충족 확인 방법"
    - condition: "해결되어야 할 조건 2"
      priority: MEDIUM
      verification: "조건 충족 확인 방법"
```

---

## Tier별 검토 범위

### Tier 1: Strategic (필수)

```yaml
solution_architect:
  must_review:
    - 전체 아키텍처 적합성
    - 기술 선택 타당성
    - 품질 속성 영향
    - 확장성/유지보수성
  output: ADR, System Design

domain_architect:
  must_review:
    - 도메인 모델 적합성
    - Bounded Context 영향
    - Aggregate 경계
    - Ubiquitous Language 일관성
  output: Context Map, Aggregate Design
```

### Tier 2: Design (조건부)

```yaml
application_architect:
  must_review:
    - 레이어 구조 준수
    - 컴포넌트 분리
    - 내부 API 설계
    - 의존성 방향
  output: Component Diagram, Layer Design

data_architect:
  must_review:
    - 데이터 모델 정합성
    - 저장소 선택 적절성
    - 쿼리 성능
    - 데이터 일관성
  output: ERD, Data Flow

integration_architect:
  must_review:
    - 외부 시스템 영향
    - API 계약
    - 메시징 패턴
    - 프로토콜 적절성
  output: Integration Architecture, API Contract

healthcare_informatics_architect:
  must_review:
    - 의료 표준 준수 (FHIR, HL7)
    - HIPAA 규정 준수
    - PHI 처리 적절성
    - 임상 데이터 정확성
  output: Compliance Checklist, FHIR Design
```

### Tier 3: Quality (조건부)

```yaml
security_architect:
  must_review:
    - 인증/인가 설계
    - 암호화 적절성
    - OWASP Top 10 취약점
    - 감사 로그
  output: Security Assessment, Threat Model

sre_architect:
  must_review:
    - 운영 가능성
    - 모니터링 가능성
    - SLO 영향
    - 장애 복구 가능성
  output: Operational Assessment, SLO Impact

cloud_native_architect:
  must_review:
    - 12-Factor 준수
    - 컨테이너 적합성
    - 스케일링 전략
    - 배포 전략
  output: Cloud-Native Assessment, Deployment Strategy
```

---

## 충돌 처리 규칙

### 충돌 유형 및 해결

| 충돌 유형 | 예시 | 해결 방법 |
|-----------|------|-----------|
| **기술 선택** | Redis vs Memcached | Trade-off 분석, Solution Architect 중재 |
| **패턴 선택** | CQRS vs 단일 모델 | 요구사항 기반 평가, 팀 합의 |
| **우선순위** | 성능 vs 보안 | 비즈니스 요구사항 기반 결정 |
| **범위** | 최소 구현 vs 확장성 | 단계적 접근, 로드맵 수립 |

### 충돌 에스컬레이션

```yaml
escalation_rules:
  # Tier 1 간 충돌
  tier1_conflict:
    mediator: "오케스트레이터"
    max_rounds: 3

  # Tier 2/3 충돌
  tier2_3_conflict:
    mediator: "Tier 1 아키텍트"
    reference: "Strategic Direction"

  # 미해결 충돌
  unresolved:
    action: "사용자 에스컬레이션"
    format: "Escalation Report"
```

---

## 소수 의견 기록

### 소수 의견 필수 기록 조건

- 다수결로 합의되었으나 반대 의견이 있는 경우
- HIGH severity 우려가 해결되지 않은 경우
- Tier 1 아키텍트가 조건부 동의한 경우

### 소수 의견 형식

```yaml
minority_opinion:
  architect: <name>
  original_vote: DISAGREE | CONDITIONAL
  concern: "핵심 우려사항"
  severity: HIGH | MEDIUM
  rationale: "반대/조건부 이유"
  risk: "무시할 경우 발생 가능한 리스크"
  mitigation_suggested: "권고하는 완화 방안"
  follow_up: "향후 재검토 시점/조건"
```

---

## 합의 후 액션

### 합의 완료 시 필수 산출물

```yaml
required_outputs:
  # 결정 기록
  - type: "Architecture Decision"
    format: ADR
    owner: solution-architect

  # 리스크 기록
  - type: "Risk Register Entry"
    condition: "HIGH severity 우려 존재 시"
    owner: 해당 아키텍트

  # 소수 의견 기록
  - type: "Minority Opinion Record"
    condition: "소수 의견 존재 시"
    owner: 오케스트레이터

  # 액션 아이템
  - type: "Action Items"
    format: 표
    owner: 오케스트레이터
```

### 액션 아이템 형식

```markdown
## Action Items

| # | 항목 | 담당 | 우선순위 | 기한 | 상태 |
|---|------|------|----------|------|------|
| 1 | ... | ... | HIGH | ... | OPEN |
| 2 | ... | ... | MEDIUM | ... | OPEN |
```

---

## 리뷰 품질 기준

### 충분한 리뷰의 조건

- [ ] 모든 권고사항에 rationale 포함
- [ ] HIGH severity 우려에 mitigation 제시
- [ ] 다른 아키텍트 의견 충돌 시 해결책 제안
- [ ] 투표 시 명확한 이유 제시
- [ ] 관련 문서/코드 참조 포함

### 리뷰 품질 체크리스트

```yaml
review_quality:
  completeness:
    - "요구사항의 모든 측면 검토"
    - "관련 기존 시스템 영향 검토"

  actionability:
    - "권고사항이 실행 가능"
    - "구체적인 구현 방향 제시"

  consistency:
    - "기존 아키텍처 원칙과 일관"
    - "다른 아키텍트 의견과 조화"

  traceability:
    - "결정의 근거 명확"
    - "관련 문서/표준 참조"
```
