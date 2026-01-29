# Solution Architecture Skill

전체 시스템 아키텍처, TOGAF, POSA 패턴을 담당합니다.

## 핵심 역량

### TOGAF ADM Phases
| Phase | 이름 | 목적 |
|-------|------|------|
| Preliminary | 준비 | 아키텍처 프레임워크 수립 |
| A | Vision | 비전 및 범위 정의 |
| B | Business | 비즈니스 아키텍처 |
| C | Information | 데이터/애플리케이션 아키텍처 |
| D | Technology | 기술 인프라 |
| E | Opportunities | 구현 전략 |
| F | Migration | 마이그레이션 계획 |
| G | Governance | 구현 거버넌스 |
| H | Change Mgmt | 변경 관리 |

### POSA Architectural Patterns

| Pattern | 문제 | 해결책 | 사용 시점 |
|---------|------|--------|-----------|
| **Layers** | 관심사 분리 | 계층 구조 | 대부분의 앱 |
| **Pipes & Filters** | 데이터 처리 | 연속 변환 | ETL, 파이프라인 |
| **Blackboard** | 복잡한 문제 | 공유 저장소 | AI, 음성인식 |
| **Broker** | 분산 통신 | 중개자 | MSA, 분산 시스템 |
| **MVC** | UI 분리 | Model-View-Controller | 웹 앱 |
| **Microkernel** | 확장성 | 코어 + 플러그인 | IDE, 브라우저 |
| **Reflection** | 런타임 변경 | 메타 레벨 | 프레임워크 |

### 품질 속성 (ISO 25010)

| 속성 | 정의 | 측정 예시 |
|------|------|-----------|
| 성능 | 응답 시간, 처리량 | p95 latency, TPS |
| 호환성 | 상호 운용성 | API 버전 호환 |
| 신뢰성 | 가용성, 복구성 | MTBF, MTTR |
| 보안성 | 기밀성, 무결성 | 취약점 수 |
| 유지보수성 | 수정 용이성 | 순환 복잡도 |
| 이식성 | 환경 적응성 | 배포 시간 |

### Architecture Decision Record (ADR)

```markdown
# ADR-[번호]: [제목]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[의사결정 배경]

## Decision
[결정 내용]

## Rationale
| Option | Pros | Cons |
|--------|------|------|
| A | ... | ... |
| B | ... | ... |

## Consequences
- Positive: [긍정적 결과]
- Negative: [부정적 결과]
- Risks: [위험 요소]
```

### 아키텍처 평가

#### 구조적 평가
- [ ] 관심사 분리가 적절한가?
- [ ] 의존성이 명확한가?
- [ ] 컴포넌트 경계가 잘 정의되어 있는가?
- [ ] 확장 포인트가 설계되어 있는가?

#### 품질 평가
- [ ] 성능 요구사항 충족?
- [ ] 확장 가능한 구조?
- [ ] 장애 격리 가능?
- [ ] 보안 요구사항 충족?

## 사용 시점
- 새 시스템 아키텍처 설계
- 아키텍처 스타일 선택
- 기술 의사결정 (ADR)
- 품질 속성 분석
- 마이그레이션 계획
