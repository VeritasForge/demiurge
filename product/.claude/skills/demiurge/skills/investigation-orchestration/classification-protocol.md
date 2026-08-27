# Classification Protocol

조사 결과의 교차 검증 분류 규칙 및 최종 판정 알고리즘을 정의합니다.

---

## 분류 매트릭스 (Round 2)

### 분류 카테고리

| 카테고리 | 기호 | 정의 | 조건 |
|----------|------|------|------|
| **AGREED** | ✅ | 합의됨 | 2+ 조사관이 동일/유사 결론 도출 |
| **DISAGREED** | ❌ | 모순 발견 | 조사관 간 상충되는 결론 |
| **UNCERTAIN** | ❓ | 불확실 | 1명만 주장하거나 증거 강도 WEAK |
| **NEEDS_MORE** | 🔍 | 추가 조사 필요 | 조사관이 `needs_further: true` 반환 |

### 분류 알고리즘

```
입력: 모든 조사관의 Layer 1 + Layer 2

for each finding F in all_findings:
    supporting = [조사관 who agree with F]
    opposing = [조사관 who contradict F]

    if len(supporting) >= 2 and len(opposing) == 0:
        classify(F, AGREED)
    elif len(opposing) >= 1:
        classify(F, DISAGREED)
    elif len(supporting) == 1 and evidence_strength(F) in [MODERATE, STRONG]:
        classify(F, UNCERTAIN)
    elif len(supporting) == 1 and evidence_strength(F) == WEAK:
        classify(F, NEEDS_MORE)
    elif any(investigator.needs_further for investigator in related):
        classify(F, NEEDS_MORE)
```

### 유사도 판정 기준

두 발견이 "동일/유사"한지 판단하는 기준:

```
1. 동일 파일/위치를 지목하는가?
2. 동일한 원인을 제시하는가?
3. 동일한 해결 방향을 권고하는가?

→ 3개 중 2개 이상 일치 시 "유사"로 판정
→ 원인만 다르고 위치가 같으면 "DISAGREED" (원인 모순)
→ 위치만 다르고 원인이 같으면 관련된 별개 발견으로 처리
```

---

## Round 3 트리거 조건

### 반드시 실행

다음 중 하나라도 해당하면 Round 3 실행:
1. **DISAGREED** 항목이 1개 이상 존재
2. **UNCERTAIN** 항목 중 HIGH confidence인 것이 존재
3. **NEEDS_MORE** 항목이 존재

### 실행 생략 (조기 종료)

다음을 **모두** 만족하면 Round 3 생략, 바로 Round 4:
1. 모든 항목이 AGREED
2. NEEDS_MORE 없음
3. 모든 evidence_strength가 STRONG 또는 MODERATE

### Track 분배

Round 3 실행 시 두 트랙을 병렬 수행:

| Track | 담당 | 대상 | 목적 |
|-------|------|------|------|
| **Track A** | counter-reviewer | AGREED 항목 | 반박 시도 (false positive 제거) |
| **Track B** | 관련 조사관 재spawn | DISAGREED + UNCERTAIN + NEEDS_MORE | 추가 증거 수집, 모순 해소 |

### Track A: Counter-Reviewer 규칙

```yaml
counter_reviewer_rules:
  # AGREED 항목 반박 (Boris Cherny 패턴)
  mandatory_challenge: true  # 반드시 1개+ challenge 제시

  verdict_options:
    UPHELD: "반박 시도했으나 원래 결론이 견고"
    WEAKENED: "부분적 약점 발견, 결론은 유지하되 주의 필요"
    REFUTED: "심각한 반박 근거 발견, 결론 재검토 필요"

  # UPHELD여도 challenge를 반드시 기록
  output_format:
    challenge: "어떤 반박을 시도했는가"
    evidence: "반박 근거"
    verdict: "UPHELD | WEAKENED | REFUTED"
    impact: "원래 결론에 미치는 영향"
```

### Track B: 심화 조사 규칙

```yaml
deep_dive_rules:
  # DISAGREED 항목
  disagreed_handling:
    action: "모순되는 양측 조사관을 재spawn, 상대 증거 제시하며 재조사"
    focus: "추가 증거 수집으로 모순 해소"
    max_respawn: 2  # 같은 조사관 최대 재spawn 횟수

  # UNCERTAIN 항목
  uncertain_handling:
    action: "원래 조사관 + 다른 type 조사관 1명 추가 배정"
    focus: "다른 관점에서 교차 확인"

  # NEEDS_MORE 항목
  needs_more_handling:
    action: "원래 조사관이 지정한 추가 조사 범위에 따라 재spawn"
    focus: "특정 영역 심화 탐색"
```

---

## 분류 매트릭스 업데이트 (Round 3 후)

Round 3 결과로 분류가 변경될 수 있습니다:

```
Round 3 결과 반영:

AGREED + CR verdict UPHELD    → AGREED (확인됨, confidence 상승)
AGREED + CR verdict WEAKENED  → AGREED (주의 필요, caveat 추가)
AGREED + CR verdict REFUTED   → DISAGREED (재검토 필요)

DISAGREED + 추가 증거로 해소  → AGREED
DISAGREED + 여전히 모순       → DISAGREED (기록 후 Judge에게 전달)

UNCERTAIN + 교차 확인 성공    → AGREED
UNCERTAIN + 교차 확인 실패    → UNCERTAIN (최종 보고서에 명시)

NEEDS_MORE + 추가 조사 완료   → 새 분류 부여
NEEDS_MORE + 추가 조사 불가   → UNCERTAIN
```

---

## 최종 판정 알고리즘 (Round 4 — Judge Pattern)

### 증거 강도 기반 판정

Round 4에서는 majority vote가 아닌 **증거 강도 기반 판정**을 수행합니다.
(Tool-MAD 연구: Judge 패턴이 majority vote 대비 18.1% 개선)

```
판정 입력:
  - 최종 분류 매트릭스 (Round 2 or Round 3 후)
  - 모든 조사관의 Layer 1 + Layer 2
  - Counter-Reviewer의 verdict (있는 경우)

판정 프로세스 (sequential-thinking 사용):

1. AGREED 항목 처리:
   for each AGREED finding:
     if CR_verdict == UPHELD or no_CR:
       tag = [Confirmed]
     elif CR_verdict == WEAKENED:
       tag = [Likely] + caveat 기록
     elif CR_verdict == REFUTED:
       재분석 후 [Confirmed] | [Likely] | [Uncertain] 결정

2. DISAGREED 항목 처리:
   for each DISAGREED finding:
     evidence_A = 지지 측 증거 총량
     evidence_B = 반대 측 증거 총량

     if evidence_A >> evidence_B:
       tag = [Likely] (A 측 결론 채택)
       record minority_opinion(B)
     elif evidence_B >> evidence_A:
       tag = [Likely] (B 측 결론 채택)
       record minority_opinion(A)
     else:
       tag = [Uncertain]
       record both_opinions()

3. UNCERTAIN 항목 처리:
   tag = [Uncertain]
   record available_evidence()
   suggest follow_up_investigation()

4. 확신도 태깅:
   [Confirmed] — 2+ 조사관 합의 + 강한 증거 + CR 미반박
   [Likely]    — 증거 우세하나 완전한 확인은 아님
   [Uncertain] — 증거 부족 또는 모순 미해소
```

### 최종 보고서 구조

```markdown
# Investigation Report: {investigation-id}

## Executive Summary
- **결론**: [한 줄 요약]
- **확신도**: [Confirmed] | [Likely] | [Uncertain]
- **조사관 수**: N명, Round 수: M

## Findings

### [Confirmed] 발견사항
| # | 발견 | 증거 | 출처 (IID) |
|---|------|------|-----------|
| 1 | ... | ... | CODE-CALLCHAIN-R1, LOG-STACKTRACE-R1 |

### [Likely] 발견사항
| # | 발견 | 증거 | 출처 (IID) | 주의사항 |
|---|------|------|-----------|---------|
| 1 | ... | ... | ... | ... |

### [Uncertain] 발견사항
| # | 발견 | 가용 증거 | 추가 조사 권고 |
|---|------|----------|--------------|
| 1 | ... | ... | ... |

## Disagreements (미해결 모순)
- [모순 1]: 조사관 A vs 조사관 B — 근거 요약

## Counter-Review Summary
| AGREED 항목 | Challenge | Verdict |
|------------|-----------|---------|
| ... | ... | UPHELD / WEAKENED / REFUTED |

## Recommendations
1. [즉시 조치 필요 항목]
2. [추가 조사 권고 항목]
3. [모니터링 권고 항목]

## Investigation Metadata
- investigation-id: {id}
- 조사관 배정: [IID 리스트]
- 총 라운드 수: N
- Quick Mode: true | false
```

---

## 에러 처리

### 조사관 응답 실패
- Task 실패 시 1회 재시도
- 재시도 실패 시 해당 조사관 제외, 사유를 최종 보고서에 기록
- 최소 2명 이상의 조사관 결과가 있어야 Round 2 진행 가능
  - 2명 미만이면 사용자에게 알리고 단일 결과로 간이 보고

### Layer 형식 미준수
- 조사관 응답이 Tiered Report 형식을 따르지 않을 경우
- Orchestrator가 수동으로 Layer 1을 추출/요약

### Round 3 무한 루프 방지
- Round 3은 최대 2회까지만 실행
- 2회 후에도 DISAGREED가 남으면 Judge에게 그대로 전달

### Context 관리
- 3+ 조사관 결과 수집 후 반드시 /compact 실행
- Layer 1만 context에 유지, Layer 2/3은 파일에서 Read로 참조
