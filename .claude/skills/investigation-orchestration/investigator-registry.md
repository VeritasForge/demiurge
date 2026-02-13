# Investigator Registry

조사관 타입, 관점(Perspective) 카탈로그, 동적 배정 규칙을 정의합니다.

---

## Investigator Types

| Type | Agent File | 약어 | 핵심 역할 |
|------|-----------|------|-----------|
| **Code Investigator** | `code-investigator.md` | `CODE` | 코드베이스 정적/동적 분석 |
| **Log Investigator** | `log-investigator.md` | `LOG` | 로그, 에러, 런타임 데이터 분석 |
| **History Investigator** | `history-investigator.md` | `HIST` | Git 이력, PR, blame 분석 |
| **Counter-Reviewer** | `counter-reviewer.md` | `CR` | 발견사항 반박, false positive 제거 |
| **Release Investigator** | `release-investigator.md` | `REL` | 릴리즈 핸드오프 문서 검증, 배포 준비 상태 분석 |

---

## Perspective Catalog

### CODE (Code Investigator) Perspectives

| Perspective | 약어 | 설명 | 적합 상황 |
|-------------|------|------|-----------|
| `call-chain` | CALLCHAIN | 함수 호출 경로 추적, 실행 흐름 분석 | 버그 원인 추적, 예상치 못한 동작 |
| `error-handling` | ERRORHANDLING | try/catch, 에러 전파, fallback 분석 | 500 에러, 예외 누락, 에러 삼킴 |
| `data-flow` | DATAFLOW | 데이터 변환, 상태 변이, 입출력 추적 | 잘못된 값, 데이터 손실, 변환 오류 |
| `dependency` | DEPENDENCY | 외부 라이브러리, 서비스 의존성 분석 | 버전 충돌, 호환성, 취약점 |
| `concurrency` | CONCURRENCY | 경합 조건, 스레드 안전성, 락 분석 | 간헐적 버그, 데드락, 레이스 컨디션 |
| `config` | CONFIG | 설정값, 환경 변수, 피처 플래그 분석 | 환경별 동작 차이, 설정 오류 |
| `type-contract` | TYPECONTRACT | 타입 정의, 인터페이스, API 계약 분석 | 타입 불일치, 계약 위반 |
| `resource` | RESOURCE | 메모리, 커넥션, 파일 핸들 관리 분석 | 메모리 릭, 커넥션 풀 고갈 |

### LOG (Log Investigator) Perspectives

| Perspective | 약어 | 설명 | 적합 상황 |
|-------------|------|------|-----------|
| `stacktrace` | STACKTRACE | 에러 스택트레이스 심층 분석 | 특정 예외 원인 파악 |
| `pattern` | PATTERN | 반복 에러 패턴, 주기성 인식 | 간헐적 에러, 반복 장애 |
| `timeline` | TIMELINE | 시간순 이벤트 상관 분석 | 장애 전후 상황 파악 |
| `metrics` | METRICS | 성능 지표 이상 탐지 | 성능 저하, 리소스 사용량 변화 |
| `correlation` | CORRELATION | 여러 서비스 로그 간 상관관계 | 분산 시스템 장애 추적 |

### HIST (History Investigator) Perspectives

| Perspective | 약어 | 설명 | 적합 상황 |
|-------------|------|------|-----------|
| `recent-changes` | RECENT | 최근 N일/커밋 변경 분석 | "갑자기 안 됨" 류의 문제 |
| `blame` | BLAME | 파일별 변경 추적, 책임 분석 | 특정 코드 변경 경위 파악 |
| `pr-context` | PRCONTEXT | PR 설명, 리뷰 코멘트, 의도 분석 | 변경 의도 vs 실제 동작 괴리 |
| `regression` | REGRESSION | 동작 변경점 이진 탐색 | "언제부터 깨졌는지" 추적 |
| `refactor-history` | REFACTORHIST | 리팩토링 이력, 구조 변경 추적 | 아키텍처 변경으로 인한 부작용 |

### REL (Release Investigator) Perspectives

| Perspective | 약어 | 설명 | 적합 상황 |
|-------------|------|------|-----------|
| `artifact-completeness` | ARTCOMP | 핸드오프 문서 각 섹션 완전성 검증 | 문서 누락 체크, 변경 등급별 필수 섹션 |
| `deployment-readiness` | DEPLOY | 배포 절차/인프라 준비 상태 분석 | 배포 전 검증, 사전 조건 충족 |
| `risk-assessment` | RISK | 변경 리스크, 롤백 계획 적절성 | Breaking changes, 마이그레이션 |
| `infra-impact` | INFRA | 인프라 요구사항 변경 영향 | 리소스, 네트워크, 방화벽, 신규 모듈 인프라 |
| `ops-readiness` | OPS | 운영 준비 상태 (모니터링, 장애 대응) | 스모크 테스트, 헬스체크, 관찰 기간 |

### CR (Counter-Reviewer) Perspectives

| Perspective | 약어 | 설명 | 적합 상황 |
|-------------|------|------|-----------|
| `agreed-challenge` | AGREED | AGREED 항목에 대한 반박 시도 | Round 3 기본 |
| `alternative-hypothesis` | ALTHYPO | 대안 가설 제시 및 검증 | UNCERTAIN 항목 재분석 |
| `evidence-quality` | EVQUALITY | 증거 강도 및 신뢰도 평가 | 전체 발견사항 메타 분석 |

---

## IID (Investigator ID) 체계

```
형식: "{TYPE}-{PERSPECTIVE_ABBR}-R{Round}"

TYPE:
  CODE = code-investigator
  LOG  = log-investigator
  HIST = history-investigator
  CR   = counter-reviewer
  REL  = release-investigator

예시:
  CODE-CALLCHAIN-R1       → 코드 조사관, 호출 체인, Round 1
  LOG-PATTERN-R1          → 로그 조사관, 패턴 분석, Round 1
  HIST-BLAME-R1           → 이력 조사관, blame 분석, Round 1
  CR-AGREED-R3            → 반박자, AGREED 검증, Round 3
  CODE-DATAFLOW-R3-DEEP   → 코드 조사관, 데이터 흐름, Round 3 심화
  REL-ARTCOMP-R1          → 릴리즈 조사관, 문서 완전성, Round 1
  REL-DEPLOY-R1           → 릴리즈 조사관, 배포 준비, Round 1
  REL-RISK-R1             → 릴리즈 조사관, 리스크 분석, Round 1
```

### Round Suffix 규칙

| Suffix | 의미 |
|--------|------|
| `R1` | Round 1 독립 조사 |
| `R3` | Round 3 심화 조사 |
| `R3-DEEP` | Round 3 심화 + 추가 탐색 |

---

## 동적 배정 규칙

### Step 0 배정 알고리즘

```
입력: 사용자 쿼리 + 코드베이스 컨텍스트
출력: [(type, perspective, rationale)] 리스트 (3-5개)

1. 쿼리 분석 → 핵심 질문 3-5개 도출
2. 각 질문에 대해:
   a. 가장 적합한 investigator type 선택
   b. type 내에서 가장 적합한 perspective 선택
   c. 동일 type이 2개 이상이면 허용 (perspective가 다르면 OK)
3. 최소 2개 이상 서로 다른 type 포함 (다양성 보장)
4. Quick Mode 판정: 질문이 1개이고 명확하면 1 에이전트만 배정
```

### 쿼리 유형별 권장 조합

| 쿼리 유형 | 권장 조사관 조합 | 근거 |
|-----------|-----------------|------|
| **버그/에러 조사** | CODE-CALLCHAIN + CODE-ERRORHANDLING + LOG-STACKTRACE + HIST-RECENT | 코드 + 로그 + 변경이력 교차 검증 |
| **성능 저하** | CODE-CALLCHAIN + CODE-DATAFLOW + CODE-CONCURRENCY | 다중 코드 관점이 효과적 |
| **"갑자기 안 됨"** | HIST-RECENT + HIST-BLAME + CODE-CALLCHAIN | 최근 변경이 원인일 가능성 높음 |
| **설계/구조 질문** | CODE-CALLCHAIN + CODE-DEPENDENCY + HIST-REFACTORHIST | 현재 구조 + 의존성 + 변천사 |
| **간헐적 버그** | CODE-CONCURRENCY + LOG-PATTERN + LOG-TIMELINE | 타이밍 관련 원인 탐색 |
| **설정 관련** | CODE-CONFIG + LOG-PATTERN + HIST-RECENT | 설정 변경 영향 추적 |
| **보안 취약점** | CODE-CALLCHAIN + CODE-TYPECONTRACT + CODE-DEPENDENCY | 입력 흐름 + 계약 + 의존성 |
| **릴리즈 핸드오프 문서 검증** | REL-ARTCOMP + REL-RISK + REL-DEPLOY + CODE-DEPENDENCY | 문서 완전성 + 리스크 + 배포 준비 + 의존성 교차 검증 |
| **배포 준비 상태 확인** | REL-DEPLOY + REL-INFRA + CODE-CONFIG | 배포 절차 + 인프라 + 설정 변경 |
| **신규 모듈 전달 검증** | REL-ARTCOMP + REL-OPS + REL-INFRA + CODE-CALLCHAIN | 문서 + 운영 준비 + 인프라 + 코드 구조 |

### Quick Mode 기준

다음 조건을 **모두** 만족하면 Quick Mode (조사관 1명):
1. 핵심 질문이 1개
2. 질문이 특정 파일/함수에 한정
3. 추가 맥락 분석이 불필요

Quick Mode 예시:
- "이 함수가 뭘 하는지 설명해줘" → CODE-CALLCHAIN-R1 단독
- "이 에러 메시지가 어디서 나오는지 찾아줘" → CODE-ERRORHANDLING-R1 단독

---

## Tiered Report Template (조사관용)

모든 조사관은 아래 형식으로 결과를 반환합니다.

### Layer 1: Executive Summary (500토큰, context 유지)

```yaml
executive_summary:
  iid: "{IID}"
  confidence: HIGH | MEDIUM | LOW
  one_liner: "핵심 발견 한 줄 요약"
  findings:
    - "[발견 1] [evidence_strength: STRONG|MODERATE|WEAK]"
    - "[발견 2] [evidence_strength: STRONG|MODERATE|WEAK]"
    - "[발견 3] [evidence_strength: STRONG|MODERATE|WEAK]"
  needs_further: true | false
  needs_further_reason: "추가 조사 필요 시 사유"
```

### Layer 2: Key Findings (2K토큰, 교차 검증용)

```yaml
key_findings:
  - id: F1
    description: "발견 상세 설명"
    evidence:
      - type: code | log | commit | config
        location: "file:line 또는 commit hash"
        snippet: "관련 코드/로그 발췌 (5줄 이내)"
    confidence: HIGH | MEDIUM | LOW
    alternative_explanations:
      - "대안 가설 1"
      - "대안 가설 2"
  - id: F2
    description: "..."
    evidence: [...]
    confidence: "..."
    alternative_explanations: []
```

### Layer 3: Full Report (무제한, artifact 파일 저장)

```
investigation/{investigation-id}/artifacts/{IID}-report.md

내용:
- 조사 방법론 설명
- 전체 증거 목록 (코드 스니펫, 로그 발췌 등)
- 분석 과정 상세
- 배제한 가설과 배제 근거
- 관련 파일 목록
- 추가 조사 권고
```

---

## 조사관 간 관계

```
┌─────────────────────────────────────────────────────────┐
│                   Investigation Round Flow                │
│                                                           │
│  Round 1: 독립 조사 (서로의 결과를 모름)                  │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐         │
│  │ CODE   │  │ CODE   │  │ LOG    │  │ HIST   │         │
│  │ (관점A)│  │ (관점B)│  │ (관점C)│  │ (관점D)│         │
│  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘         │
│      └───────────┼───────────┼───────────┘               │
│                  ▼                                        │
│  Round 2: Orchestrator가 분류 (Mediator)                 │
│                  │                                        │
│                  ▼                                        │
│  Round 3: Counter-Reviewer + 심화 (조건부)               │
│  ┌────────────────┐  ┌────────────────┐                  │
│  │ CR             │  │ 관련 조사관     │                  │
│  │ (AGREED 반박)  │  │ (UNCERTAIN 심화)│                  │
│  └────────┬───────┘  └────────┬───────┘                  │
│           └──────────┬────────┘                           │
│                      ▼                                    │
│  Round 4: Orchestrator가 최종 판정 (Judge)               │
└─────────────────────────────────────────────────────────┘
```
