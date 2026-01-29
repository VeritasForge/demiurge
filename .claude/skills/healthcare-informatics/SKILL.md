---
description: HL7 FHIR, HIPAA, Medical Terminology
user-invocable: false
---

# Healthcare Informatics Skill

의료 도메인 지식, 표준, 규제 준수를 담당합니다.

## 핵심 역량

### HL7 FHIR R4 리소스
| Domain Entity | FHIR Resource | Profile |
|---------------|---------------|---------|
| Patient | Patient | us-core-patient |
| Encounter | Encounter | us-core-encounter |
| Observation | Observation | vital-signs |
| Score | RiskAssessment | - |

### LOINC 코드 매핑
| 관측값 | LOINC | Display |
|--------|-------|---------|
| PR (맥박) | 8867-4 | Heart rate |
| RR (호흡) | 9279-1 | Respiratory rate |
| BT (체온) | 8310-5 | Body temperature |
| SBP (수축기혈압) | 8480-6 | Systolic BP |
| DBP (이완기혈압) | 8462-4 | Diastolic BP |
| SpO2 (산소포화도) | 2708-6 | Oxygen saturation |

### ICD-10 카테고리
- A00-B99: 감염성 질환
- I00-I99: 순환계 질환
- J00-J99: 호흡계 질환
- R00-R99: 증상/징후

## 규제 준수

### HIPAA Security Rule
- **Administrative**: 정책, 절차, 교육
- **Physical**: 시설 접근 통제
- **Technical**: 접근 통제, 감사, 암호화

### FDA SaMD 분류
| Class | Risk | 예시 |
|-------|------|------|
| I | Low | 건강 정보 앱 |
| II | Medium | 진단 보조 |
| III | High | 생명 유지 장치 제어 |

## 임상 워크플로우

### KTAS (Korean Triage and Acuity Scale)
| Level | 이름 | 대기시간 | 색상 |
|-------|------|----------|------|
| 1 | Resuscitation | 즉시 | 빨강 |
| 2 | Emergent | 10분 | 주황 |
| 3 | Urgent | 30분 | 노랑 |
| 4 | Less Urgent | 60분 | 초록 |
| 5 | Non-Urgent | 120분 | 파랑 |

## 사용 시점
- 새 임상 점수 도입 검토
- FHIR 연동 설계
- 규제 준수 검토
- 임상 워크플로우 변경
