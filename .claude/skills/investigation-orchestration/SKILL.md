---
name: investigation-orchestration
description: 코드베이스 조사를 위한 다중 조사관 오케스트레이션. 동적 조사관 배정 → 병렬 독립 조사 → 교차 검증 → 반박 → 증거 기반 판정. /investigation-orchestration 으로 실행.
allowed-tools: Read, Grep, Glob, Task, Bash, mcp__sequential-thinking__sequentialthinking
---

# Investigation Orchestration Skill

## Overview

이 스킬은 사용자의 코드베이스 관련 질문/문제를 분석하고, 전문 조사관 에이전트를 **Task tool**로 spawn하여 **독립 조사 → 교차 검증 → 반박 → 증거 기반 판정**의 멀티라운드 구조로 근거 있는 결론을 도출합니다.

**핵심 원리**: 이 스킬은 main conversation context에서 실행되므로 Task tool을 사용하여 subagent를 spawn할 수 있습니다.

**학술적 기반**: Tool-MAD (ICLR 2025), Boris Cherny의 Counter-Reviewer 패턴, CONSENSAGENT (ACL 2025)

---

## IID (Investigator ID) 체계

모든 조사관 리포트에는 IID가 포함되어 출처와 라운드를 추적합니다.

```
형식: "{TYPE}-{PERSPECTIVE}-R{Round}"

TYPE:
  CODE = code-investigator
  LOG  = log-investigator
  HIST = history-investigator
  CR   = counter-reviewer

예시:
  CODE-CALLCHAIN-R1       → 코드 조사관, 호출 체인, Round 1
  LOG-STACKTRACE-R1       → 로그 조사관, 스택트레이스, Round 1
  HIST-RECENT-R1          → 이력 조사관, 최근 변경, Round 1
  CR-AGREED-R3            → 반박자, AGREED 검증, Round 3
  CODE-DATAFLOW-R3-DEEP   → 코드 조사관, 데이터 흐름, Round 3 심화
```

---

## Tiered Report Template (조사관용)

Context 비대화 방지를 위해 3단계 계층 출력을 사용합니다.

| Layer | 용도 | 크기 제한 | 전달 범위 |
|-------|------|-----------|-----------|
| **Layer 1** Executive Summary | IID + 확신도 + 핵심 발견 | 500토큰 | 항상 전달 (context 유지) |
| **Layer 2** Key Findings | 발견 상세 + 증거 + 대안 가설 | 2K토큰 | 교차 검증 시 |
| **Layer 3** Full Report | 전체 분석 + 코드 스니펫 | 제한 없음 | artifact 파일 저장 |

---

## External Artifact 구조

```
investigation/{investigation-id}/
├── investigation-plan.md          # Step 0 결과
├── cross-verification-r2.md       # Step 2 분류 매트릭스
├── counter-review-r3.md           # Step 3 반박 결과 (조건부)
├── final-report.md                # Step 4 최종 보고서
├── execution-log.md               # Step 5 실행 검증 로그
└── artifacts/
    ├── CODE-CALLCHAIN-R1-report.md
    ├── CODE-ERRORHANDLING-R1-report.md
    ├── LOG-STACKTRACE-R1-report.md
    ├── HIST-RECENT-R1-report.md
    └── ...
```

---

## Context Management Protocol

### Context 위생 3원칙

1. **즉시 파일 저장**: 각 조사관 결과는 즉시 artifact 파일로 저장
2. **Layer 1만 유지**: context에는 Executive Summary만 유지, 상세는 파일 참조
3. **마일스톤 compact**: 주요 단계 완료 후 /compact 실행

### Compact 트리거 포인트

| 시점 | 조건 | 이유 |
|------|------|------|
| Step 1 완료 후 | 3+ 조사관 결과 수집 시 | Layer 3 artifact 저장 완료, Layer 1만 필요 |
| Step 3 완료 후 | Counter-review + 심화 조사 결과 수집 시 | 라운드 결과 파일화 완료 |
| Step 4 시작 전 | 항상 | 최종 판정에 깨끗한 context 필요 |

---

## 오케스트레이션 프로토콜 (5 Steps)

```
Step 0: 조사 계획 수립 ──────────────────────────────────────────────
  │
Step 1: Round 1 — 독립 병렬 조사 (Task tool × 3-5) ──────────────
  │
Step 2: Round 2 — 교차 검증 + 분류 (Mediator, sequential-thinking)
  │
Step 3: Round 3 — 반박 + 심화 (조건부, max 2회) ─────────────────
  │
Step 4: Round 4 — 최종 판정 (Judge, sequential-thinking) ─────────
  │
Step 5: 실행 검증 ───────────────────────────────────────────────
```

---

### Step 0: 조사 계획 수립

**사용 도구**: `mcp__sequential-thinking__sequentialthinking`

```
실행 내용:

0-1. 참조 문서 로드
  - Read: .claude/skills/investigation-orchestration/investigator-registry.md
  - Read: .claude/skills/investigation-orchestration/classification-protocol.md

0-2. 쿼리 분석 (sequential-thinking)
  - 사용자 질문/문제 분석
  - 핵심 질문 3-5개 도출
  - investigation-id 생성: "inv-{YYMMDD}-{짧은키워드}"

0-3. Quick Mode 판정
  조건 확인:
    - 핵심 질문이 1개인가?
    - 특정 파일/함수에 한정되는가?
    - 추가 맥락 분석이 불필요한가?

  if all(조건):
    Quick Mode → 조사관 1명만 배정 → Step 1 간소화 → Step 2 생략 → Step 4 직행
  else:
    Full Mode → 아래 계속

0-4. 동적 조사관 배정
  investigator-registry.md의 배정 알고리즘에 따라:
  - 각 핵심 질문에 최적의 (type, perspective) 조합 결정
  - IID 할당
  - 최소 2개 이상 서로 다른 type 포함 (다양성 보장)
  - 최소 3개, 최대 5개 조사관

0-5. investigation-plan.md 저장
  investigation/{investigation-id}/investigation-plan.md 파일 생성:
  - investigation-id
  - 원본 쿼리
  - 핵심 질문 목록
  - 배정된 조사관 (IID, type, perspective, 조사 범위)
  - Quick Mode 여부
```

**출력 (사용자에게 표시)**:

```markdown
## 📋 Investigation Plan: {investigation-id}

| # | 핵심 질문 | 조사관 (IID) | 관점 |
|---|----------|-------------|------|
| 1 | ... | CODE-CALLCHAIN-R1 | 호출 체인 추적 |
| 2 | ... | CODE-ERRORHANDLING-R1 | 에러 핸들링 |
| 3 | ... | LOG-STACKTRACE-R1 | 스택트레이스 |
| 4 | ... | HIST-RECENT-R1 | 최근 변경 |

Mode: Full (4 investigators, est. 4 rounds)
```

---

### Step 1: Round 1 — 독립 병렬 조사

**사용 도구**: `Task` tool (병렬 spawn)

```
실행 내용:

1-1. 에이전트 파일 로드
  배정된 각 조사관의 에이전트 .md 파일을 Read

1-2. 병렬 조사 실행
  각 조사관에 대해 Task tool로 병렬 spawn:

  Task({
    subagent_type: "general-purpose",
    prompt: """
    당신은 {agent_name}입니다. 아래 에이전트 정의를 숙지하세요:

    {에이전트 .md 파일 전체 내용}

    ## 조사 임무

    - IID: {IID}
    - Perspective: {perspective}
    - Investigation ID: {investigation-id}
    - 쿼리: {원본 쿼리}
    - 담당 핵심 질문: {할당된 질문}
    - 조사 범위: {범위 설명}

    ## 출력 요구사항

    1. Layer 1 (Executive Summary) — 반드시 yaml 형식으로 출력
    2. Layer 2 (Key Findings) — 반드시 yaml 형식으로 출력
    3. Layer 3 (Full Report) — 마크다운 형식으로 출력

    Layer 1, 2, 3을 순서대로 출력하세요. 각 Layer를 명확히 구분하세요.
    """
  })

1-3. 결과 수집 및 저장
  각 조사관의 결과에서:
  - Layer 1: context에 유지
  - Layer 2: context에 유지 (Step 2 교차 검증용)
  - Layer 3: investigation/{id}/artifacts/{IID}-report.md 파일로 저장

1-4. Context 관리
  - 3개 이상 조사관 결과 수집 후 Layer 3 파일 저장 확인
  - /compact 실행 (3+ 조사관인 경우)
```

---

### Step 2: Round 2 — 교차 검증 + 분류

**사용 도구**: `mcp__sequential-thinking__sequentialthinking`

```
실행 내용:

2-1. 분류 매트릭스 생성 (sequential-thinking)

  classification-protocol.md의 분류 알고리즘에 따라:

  모든 조사관의 Layer 1 + Layer 2를 분석하여 각 발견(finding)을 분류:

  ✅ AGREED     — 2+ 조사관이 동일/유사 결론
  ❌ DISAGREED  — 조사관 간 모순되는 결론
  ❓ UNCERTAIN  — 1명만 주장하거나 증거 강도 WEAK
  🔍 NEEDS_MORE — 조사관이 needs_further: true 반환

  유사도 판정:
  - 동일 파일/위치 지목 + 동일 원인 제시 + 동일 해결 방향 → 3개 중 2개 이상 일치 시 "유사"
  - 원인만 다르고 위치 같으면 → DISAGREED
  - 위치만 다르고 원인 같으면 → 관련된 별개 발견

2-2. 분류 결과 저장
  investigation/{id}/cross-verification-r2.md 파일 생성

2-3. Round 3 트리거 판정

  if DISAGREED >= 1 or (UNCERTAIN with HIGH confidence) >= 1 or NEEDS_MORE >= 1:
    → Step 3 실행
  elif all findings are AGREED and all evidence STRONG|MODERATE:
    → Step 3 생략, Step 4 직행 (조기 종료)
```

**출력 (사용자에게 표시)**:

```markdown
## 🔍 Cross-Verification Results (Round 2)

| # | 발견 | 분류 | 출처 (IID) | 비고 |
|---|------|------|-----------|------|
| 1 | ... | ✅ AGREED | CODE-R1, LOG-R1 | |
| 2 | ... | ❌ DISAGREED | CODE-R1 vs HIST-R1 | 원인 상충 |
| 3 | ... | ❓ UNCERTAIN | LOG-R1 only | 증거 WEAK |

→ DISAGREED 1건, UNCERTAIN 1건 → Round 3 실행
```

---

### Step 3: Round 3 — 반박 + 심화 (조건부)

**트리거**: DISAGREED, UNCERTAIN(HIGH confidence), 또는 NEEDS_MORE 존재 시
**최대 실행**: 2회

```
실행 내용:

3-1. Track 분배

  Track A: Counter-Reviewer
    - 대상: AGREED 항목
    - 에이전트: counter-reviewer.md
    - Perspective: agreed-challenge
    - IID: CR-AGREED-R3

  Track B: 관련 조사관 재spawn
    - 대상: DISAGREED + UNCERTAIN + NEEDS_MORE 항목
    - 에이전트: 원래 조사관 또는 다른 type 추가
    - IID: {TYPE}-{PERSPECTIVE}-R3-DEEP

3-2. 병렬 실행

  Track A와 Track B를 Task tool로 병렬 spawn:

  Counter-Reviewer Task:
    - counter-reviewer.md 에이전트 정의 포함
    - AGREED 항목 목록 전달
    - 원래 조사관의 Layer 2 전달 (증거 포함)
    - "반드시 각 AGREED 항목에 1개+ challenge 제시" 강조

  심화 조사 Task(들):
    - 상대 조사관의 Layer 2 전달 (모순 정보 포함)
    - 추가 조사 범위 명시
    - "기존 발견을 확인하거나 반박하는 추가 증거 수집" 지시

3-3. 결과 수집 및 분류 업데이트

  classification-protocol.md의 "분류 매트릭스 업데이트" 규칙에 따라:

  AGREED + CR UPHELD    → AGREED (확인됨)
  AGREED + CR WEAKENED  → AGREED (주의 필요, caveat 추가)
  AGREED + CR REFUTED   → DISAGREED (재검토)

  DISAGREED + 증거 해소  → AGREED
  DISAGREED + 여전히 모순 → DISAGREED (Judge에게 전달)

  UNCERTAIN + 교차 확인  → AGREED 또는 여전히 UNCERTAIN

3-4. 결과 저장
  investigation/{id}/counter-review-r3.md 파일 생성

3-5. Context 관리
  /compact 실행

3-6. 재실행 판정 (max 2회)
  if round_3_count < 2 and new_DISAGREED exists:
    → Step 3 재실행
  else:
    → Step 4 진행
```

---

### Step 4: Round 4 — 최종 판정 (Judge Pattern)

**사용 도구**: `mcp__sequential-thinking__sequentialthinking`

```
실행 내용:

4-1. Context 정리
  /compact 실행 (Step 4 시작 전 깨끗한 context 확보)

4-2. 판정 입력 수집
  - 최종 분류 매트릭스 (Step 2 또는 Step 3 후)
  - 모든 조사관의 Layer 1 (context에 있음)
  - Counter-Reviewer verdict (있는 경우)
  - 필요시 Layer 2를 파일에서 Read

4-3. 증거 기반 최종 판정 (sequential-thinking)

  classification-protocol.md의 "최종 판정 알고리즘"에 따라:

  AGREED 항목:
    CR UPHELD or no CR → [Confirmed]
    CR WEAKENED → [Likely] + caveat
    CR REFUTED → 재분석 후 태깅

  DISAGREED 항목:
    증거 강도 비교 → 우세한 측 채택 [Likely]
    균형 → [Uncertain] + both opinions

  UNCERTAIN 항목:
    → [Uncertain] + follow-up suggestion

4-4. Investigation Report 생성

  investigation/{id}/final-report.md 파일 생성:

  # Investigation Report: {investigation-id}

  ## Executive Summary
  - 결론 (한 줄)
  - 확신도 태깅
  - 조사관 수, 라운드 수

  ## Findings
  ### [Confirmed] 발견사항
  ### [Likely] 발견사항
  ### [Uncertain] 발견사항

  ## Disagreements (미해결 모순)
  ## Counter-Review Summary
  ## Recommendations
  ## Investigation Metadata

4-5. 사용자에게 결과 출력
```

**출력 (사용자에게 표시)**:

```markdown
## 📊 Investigation Report: {investigation-id}

### Executive Summary
{결론 요약}

### Findings

#### ✅ [Confirmed]
| # | 발견 | 증거 | 출처 |
|---|------|------|------|
| 1 | ... | ... | CODE-R1, LOG-R1 |

#### 🟡 [Likely]
| # | 발견 | 증거 | 출처 | 주의사항 |
|---|------|------|------|---------|
| 1 | ... | ... | ... | ... |

#### ❓ [Uncertain]
| # | 발견 | 가용 증거 | 추가 조사 권고 |
|---|------|----------|--------------|
| 1 | ... | ... | ... |

### Recommendations
1. ...
2. ...
```

---

### Step 5: 실행 검증

```
실행 내용:

5-1. 실행 체크리스트 검증

  | # | 항목 | 검증 방법 | 결과 |
  |---|------|----------|------|
  | 1 | investigation-plan.md 존재 | file exists | PASS/FAIL |
  | 2 | 모든 조사관 artifact 존재 | file exists per IID | PASS/FAIL |
  | 3 | cross-verification-r2.md 존재 | file exists | PASS/FAIL |
  | 4 | final-report.md 존재 | file exists | PASS/FAIL |
  | 5 | 모든 IID가 보고서에 반영 | grep IID in final-report | PASS/FAIL |
  | 6 | 확신도 태깅 완료 | [Confirmed]/[Likely]/[Uncertain] 존재 | PASS/FAIL |

5-2. Execution Log 기록

  investigation/{id}/execution-log.md 파일 생성:

  ```yaml
  investigation_id: "{id}"
  timestamp: "{ISO8601}"
  mode: "quick | full"
  investigators_planned: [IID 리스트]
  investigators_completed: [IID 리스트]
  rounds_executed: N
  round_3_triggered: true | false
  round_3_count: N
  early_termination: true | false
  early_termination_reason: "..."

  checklist:
    investigation_plan: PASS | FAIL
    all_artifacts: PASS | FAIL
    cross_verification: PASS | FAIL | SKIPPED
    final_report: PASS | FAIL
    iid_coverage: PASS | FAIL
    confidence_tagging: PASS | FAIL

  context_management:
    compact_points: ["Step 1 후", "Step 3 후", "Step 4 전"]
    layer3_artifacts_saved: N
    context_peak_estimate: "~{N}K tokens"

  errors:
    - investigator: "{IID}"
      error: "Task 실패"
      action: "1회 재시도 후 성공 | 제외"
  ```

5-3. 실패 항목 처리
  FAIL 항목이 있으면:
  - 보완 가능 → 즉시 보완 실행
  - 보완 불가 → ACKNOWLEDGED_SKIP 기록 + 사유 명시
```

---

## Quick Mode 프로토콜

단순 문의에 대한 간소화된 프로토콜:

```
Step 0: 조사 계획 (Quick Mode 판정)
  │
Step 1: 조사관 1명 실행
  │
Step 4: 직접 결론 도출 (교차 검증 생략)
  │
Step 5: 간소화된 실행 검증
```

Quick Mode에서는:
- Round 2 (교차 검증) 생략
- Round 3 (반박) 생략
- 최종 보고서에 "Quick Mode — 교차 검증 미실행" 명시

---

## 설정 옵션

```yaml
# 기본 프로필
default:
  max_investigators: 4
  max_round3_iterations: 2
  quick_mode_enabled: true
  auto_compact: true

# 심층 조사 프로필
thorough:
  max_investigators: 5
  max_round3_iterations: 2
  quick_mode_enabled: false
  auto_compact: true

# 빠른 조사 프로필
fast:
  max_investigators: 3
  max_round3_iterations: 1
  quick_mode_enabled: true
  auto_compact: true
```

---

## 에러 처리

### 조사관 응답 실패
- Task 실패 시 1회 재시도
- 재시도 실패 시 해당 조사관 제외, 사유를 최종 보고서에 기록
- 최소 2명 이상의 결과가 있어야 Round 2 진행 가능

### Layer 형식 미준수
- 조사관 응답이 Tiered Report 형식을 따르지 않을 경우
- Orchestrator가 수동으로 Layer 1을 추출/요약

### Context 폭발 방지
- 각 조사관 Layer 1은 500토큰 이내
- 4 조사관 × 500 = 2K 토큰 (context 안전)
- Layer 3는 반드시 파일로 저장

---

## Context 절감 효과

```
단순 병렬 조사 (Layer 관리 없음):
  4 조사관 × 5K (Full Report) = 20K 토큰
  + Counter-Review 5K = 25K 토큰
  → Context 폭발 → 세션 불안정

Investigation Orchestration (Tiered + Compact):
  Step 1: 4 × 500 (Layer 1) + 4 × 2K (Layer 2) = 10K → compact 후 ~3K
  Step 3: CR 500 + 심화 1K = 1.5K → compact 후 ~1K
  Step 4: 최종 판정 ~2K
  ────────────
  피크 Context ≈ 6K 토큰 (compact 후 기준)
  Layer 3는 파일 참조 (0 context cost)
```

---

## 관련 문서

- `investigator-registry.md` — 조사관 타입, 관점 카탈로그, IID 체계, 배정 알고리즘
- `classification-protocol.md` — 분류 규칙, 판정 알고리즘, 보고서 구조

---

## 학술적 근거

| 패턴 | 출처 | 적용 |
|------|------|------|
| **Tool-MAD** | arXiv 2601.04742 | 전문화된 에이전트 + 도구 기반 증거 수집 |
| **Judge Pattern** | Tool-MAD (18.1% 개선) | Round 4 증거 기반 판정 (majority vote 대신) |
| **Boris Cherny Counter-Reviewer** | VentureBeat, InfoQ | Round 3 반박 (poking holes) |
| **CONSENSAGENT** | ACL 2025 | Anti-Sycophancy: 독립 조사 → 교차 검증 순서 |
| **ICLR 2025 MAD Analysis** | ICLR 2025 Blog | 이질적 에이전트 + 증거 기반 > 동질적 다수결 |
| **Dynamic Perspective Assignment** | DMAD/Tool-MAD | 동일 에이전트도 다른 관점 부여 시 효과적 |
