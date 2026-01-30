# Consensus Protocol

다중 아키텍트 에이전트 간의 합의를 도출하기 위한 프로토콜입니다.

---

## 합의 프로토콜 개요

### 핵심 원칙

1. **구조화된 의견**: 모든 아키텍트는 표준 형식으로 응답
2. **라운드 기반**: 단계적 합의 수렴
3. **다수결 + 필수 동의**: Tier 1 필수 동의 + 2/3 다수결
4. **투명한 기록**: 모든 의견과 충돌 기록

---

## 투표 시스템

### 투표 옵션

| 투표 | 코드 | 의미 | 처리 |
|------|------|------|------|
| 동의 | `AGREE` | 제안에 동의 | 합의 카운트 +1 |
| 반대 | `DISAGREE` | 제안에 반대 | 사유 필수, 재논의 |
| 조건부 | `CONDITIONAL` | 조건 충족 시 동의 | 조건 해결 후 재투표 |

### 투표 응답 형식

```yaml
vote:
  decision: AGREE | DISAGREE | CONDITIONAL
  confidence: HIGH | MEDIUM | LOW
  rationale: "투표 이유 설명"
  conditions:  # CONDITIONAL인 경우만
    - condition: "조건 1"
      priority: HIGH
    - condition: "조건 2"
      priority: MEDIUM
  alternatives:  # DISAGREE인 경우 제안
    - "대안 1"
    - "대안 2"
```

---

## 라운드 구조

### Round 1: Initial Review

```
┌─────────────────────────────────────────────────────────────┐
│                     Round 1: Initial Review                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 오케스트레이터 → 각 아키텍트에 요구사항 배포            │
│                                                              │
│  2. 각 아키텍트 독립 검토                                   │
│     ├── 요구사항 분석                                       │
│     ├── 권고사항 작성                                       │
│     ├── 우려사항 식별                                       │
│     └── 투표 제출                                           │
│                                                              │
│  3. 오케스트레이터 결과 수집                                │
│     ├── 투표 집계                                           │
│     ├── 합의 지점 식별                                      │
│     └── 충돌 지점 식별                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Synthesis Phase

```
┌─────────────────────────────────────────────────────────────┐
│                     Synthesis Phase                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  오케스트레이터가 수행:                                      │
│                                                              │
│  1. 합의 분석                                               │
│     ├── AGREE 항목 통합                                     │
│     ├── CONDITIONAL 조건 정리                               │
│     └── DISAGREE 사유 분석                                  │
│                                                              │
│  2. 통합 제안 작성                                          │
│     ├── 합의된 결정 정리                                    │
│     ├── 충돌 해결 제안                                      │
│     └── 조건 해결 방안                                      │
│                                                              │
│  3. Broadcast                                               │
│     └── 모든 참여 아키텍트에게 통합 제안 전달              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Round 2+: Feedback

```
┌─────────────────────────────────────────────────────────────┐
│                     Round N: Feedback                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 통합 제안에 대한 피드백                                 │
│     ├── 이전 우려 해결 확인                                 │
│     ├── 새로운 우려 식별                                    │
│     └── 재투표                                              │
│                                                              │
│  2. 조건부 동의자 재검토                                    │
│     ├── 조건 충족 여부 확인                                 │
│     └── AGREE 또는 유지                                     │
│                                                              │
│  3. 반대자 재검토                                           │
│     ├── 대안 반영 여부 확인                                 │
│     └── 입장 변경 또는 유지                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 합의 판정

### 합의 기준

```yaml
consensus_criteria:
  # 기본 기준
  threshold: 0.67  # 2/3 이상 AGREE

  # Tier 1 필수 동의 (veto권)
  tier1_required: true
  tier1_architects:
    - solution-architect
    - domain-architect

  # 최대 라운드 (설정 가능, 기본값: 5)
  max_rounds: 5
```

### 판정 알고리즘

```python
def check_consensus(votes, config):
    total = len(votes)
    agree_count = count_agrees(votes)
    conditional_met = count_conditionals_met(votes)       # status=MET
    conditional_partial = count_conditionals_partial(votes) # status=PARTIALLY_MET

    # Tier 1 필수 체크
    if config.tier1_required:
        tier1_votes = get_tier1_votes(votes)
        if any_disagree(tier1_votes):
            return ConsensusResult.BLOCKED_BY_TIER1

    # 비율 체크 (CONDITIONAL 포함)
    effective_agrees = agree_count + conditional_met + (conditional_partial * 0.5)
    ratio = effective_agrees / total

    if ratio >= 1.0:
        return ConsensusResult.UNANIMOUS
    elif ratio >= config.threshold:
        return ConsensusResult.MAJORITY_WITH_MINORITY
    else:
        return ConsensusResult.NO_CONSENSUS


def verify_conditional(vote):
    """CONDITIONAL 투표의 조건 충족 여부를 검증"""
    verification = {
        'architect': vote.aid,
        'conditions': vote.conditions,
        'status': 'UNMET',  # MET | PARTIALLY_MET | UNMET
        'rationale': ''
    }
    for condition in vote.conditions:
        # Consolidated Findings에서 해당 조건이 반영되었는지 확인
        if condition_in_action_items(condition) and action_item_priority_match(condition):
            condition.status = 'MET'
        elif condition_partially_reflected(condition):
            condition.status = 'PARTIALLY_MET'
        else:
            condition.status = 'UNMET'

    met_count = count_status(vote.conditions, 'MET')
    partial_count = count_status(vote.conditions, 'PARTIALLY_MET')
    total_conditions = len(vote.conditions)

    if met_count == total_conditions:
        verification['status'] = 'MET'
    elif met_count + partial_count == total_conditions:
        verification['status'] = 'PARTIALLY_MET'
    else:
        verification['status'] = 'UNMET'

    return verification
```

### 판정 결과

| 결과 | 코드 | 처리 |
|------|------|------|
| 만장일치 | `UNANIMOUS` | 즉시 완료 |
| 다수결 합의 | `MAJORITY_WITH_MINORITY` | 소수의견 기록 후 완료 |
| Tier 1 블록 | `BLOCKED_BY_TIER1` | 필수 동의자와 조율 |
| 합의 실패 | `NO_CONSENSUS` | 다음 라운드 또는 에스컬레이션 |

---

## 충돌 해결

### 충돌 유형

```yaml
conflict_types:
  # 기술 선택 충돌
  technical_choice:
    example: "Redis vs Memcached"
    resolution: "trade-off 분석"

  # 패턴 충돌
  pattern_conflict:
    example: "CQRS vs 단일 모델"
    resolution: "요구사항 재분석"

  # 우선순위 충돌
  priority_conflict:
    example: "성능 vs 보안"
    resolution: "품질 속성 우선순위 결정"

  # 범위 충돌
  scope_conflict:
    example: "최소 구현 vs 확장성"
    resolution: "단계적 접근"
```

### 해결 프로세스

```
충돌 감지
    │
    ▼
┌─────────────────────────────┐
│ Step 1: 충돌 상세화          │
│ • 충돌 당사자 식별           │
│ • 충돌 내용 명확화           │
│ • 영향 범위 분석            │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Step 2: 중재                 │
│ • 양측 입장 정리             │
│ • 공통점 도출               │
│ • 타협점 제안               │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Step 3: 해결                 │
│ • 합의안 도출               │
│ • 또는 에스컬레이션          │
└─────────────────────────────┘
```

---

## 에스컬레이션

### 에스컬레이션 조건

```yaml
escalation_triggers:
  - max_rounds_exceeded: true
  - tier1_persistent_disagree: true
  - critical_unresolved_conflict: true
  - user_requested: true
```

### 에스컬레이션 형식

```markdown
## Escalation Report

### Summary
- 요구사항: [원본]
- 라운드 수: [N]
- 합의 상태: [미합의]

### Agreed Points
- [합의된 사항들]

### Unresolved Conflicts
| 충돌 | 입장 A | 입장 B | 영향 |
|------|--------|--------|------|
| ... | ... | ... | ... |

### Decision Required
[사용자가 결정해야 할 사항]

### Recommendations
[오케스트레이터의 권고]
```

---

## 소수 의견 처리

### 소수 의견 기록

합의가 이루어져도 소수 의견은 반드시 기록됩니다.

```yaml
minority_opinion:
  architect: "security-architect"
  vote: DISAGREE
  concern: "JWT 만료 시간이 너무 길어 보안 위험"
  severity: HIGH
  rationale: "15분 권고, 현재 제안은 1시간"
  mitigation_suggested: "토큰 회전 메커니즘 추가"
```

### 소수 의견 활용

```yaml
minority_opinion_usage:
  # 문서화
  - 최종 문서에 "Minority Opinions" 섹션 포함

  # 향후 참조
  - 리스크 레지스터에 등록
  - 추후 검토 항목으로 표시

  # 알림
  - 관련 이슈 발생 시 참조
```

---

## 표준 응답 형식

### 아키텍트 리뷰 응답

```yaml
# Architect Review Response v1.0

architect: <architect-name>
timestamp: <ISO8601>
round: <round-number>

# 권고사항
recommendations:
  - id: R1
    category: DESIGN | SECURITY | PERFORMANCE | OPERATION
    priority: HIGH | MEDIUM | LOW
    description: "권고 내용"
    rationale: "이유"
    implementation_hint: "구현 힌트"

# 우려사항
concerns:
  - id: C1
    severity: HIGH | MEDIUM | LOW
    description: "우려 내용"
    impact: "영향"
    mitigation: "완화 방안"

# 의존성
dependencies:
  - type: REQUIRES | CONFLICTS_WITH | ENHANCES
    target: "다른 아키텍트 또는 결정"
    description: "설명"

# 투표
vote:
  decision: AGREE | DISAGREE | CONDITIONAL
  confidence: HIGH | MEDIUM | LOW
  rationale: "투표 이유"
  conditions:  # CONDITIONAL인 경우
    - condition: "조건"
      priority: HIGH | MEDIUM | LOW
  alternatives:  # DISAGREE인 경우
    - "대안 제안"
```

### 통합 제안 형식

```yaml
# Synthesis Proposal v1.0

round: <round-number>
timestamp: <ISO8601>

# 현황
status:
  total_architects: <N>
  agree: <count>
  disagree: <count>
  conditional: <count>

# 합의 사항
agreed_items:
  - id: A1
    description: "합의 내용"
    supporters: [architect1, architect2]

# 미해결 사항
unresolved_items:
  - id: U1
    type: CONFLICT | CONDITIONAL | DISAGREE
    description: "미해결 내용"
    parties: [architect1, architect2]
    proposed_resolution: "해결 제안"

# 조건 해결
condition_resolutions:
  - original_condition: "원래 조건"
    architect: "architect-name"
    resolution: "해결 방안"
    status: RESOLVED | PENDING

# 다음 액션
next_actions:
  - action: "필요한 행동"
    responsible: "담당자"
```

---

## 설정 옵션

### 기본 설정

```yaml
consensus_config:
  # 투표 설정
  threshold: 0.67           # 2/3 다수결
  tier1_required: true      # Tier 1 필수 동의 (veto권)

  # 라운드 설정
  max_rounds: 5             # 기본값: 5라운드 (설정 가능)
  round_timeout: 300s

  # 에스컬레이션 설정
  auto_escalate: true       # 미합의 시 사용자에게 결정 위임
  escalate_on_tier1_block: true

  # 기록 설정
  include_minority_opinion: true
  record_all_votes: true

  # 충돌 해결
  auto_mediation: true
  mediation_timeout: 120s
```

### 커스텀 프로필

```yaml
# 빠른 리뷰
fast_review:
  threshold: 0.5
  max_rounds: 1
  auto_escalate: true

# 표준 리뷰 (기본값)
standard_review:
  threshold: 0.67
  max_rounds: 5
  tier1_required: true
  auto_escalate: true  # 사용자 결정 위임

# 철저한 리뷰
thorough_review:
  threshold: 0.8
  max_rounds: 10
  tier1_required: true
  include_minority_opinion: true

# 중요 결정
critical_decision:
  threshold: 1.0  # 만장일치
  max_rounds: 15
  auto_escalate: false
```
