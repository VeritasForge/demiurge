---
name: deep-research
description: 3단계 심층 조사 프로토콜. 광역 탐색 → 심화 탐색 → 지식 합성을 통해 근거 기반 아키텍처 의사결정을 지원.
allowed-tools: WebSearch, WebFetch, Read, Grep, Glob, mcp__playwright__*
---

# Deep Research Skill

## Overview

이 스킬은 아키텍처 의사결정에 필요한 **심층 조사(Deep Research)**를 3단계 프로토콜로 수행합니다.
최신 기술 동향, 패턴 비교, trade-off 분석 등에서 **출처 기반의 근거 있는 정보**를 제공합니다.

```
┌─────────────────────────────────────────────────────────┐
│              Deep Research Protocol (3-Phase)             │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Phase 1: 광역 탐색 (Broad Exploration)                  │
│  ┌─────────────────────────────────────────────────┐     │
│  │  Query Decomposition → Authority Discovery      │     │
│  │  → Parallel WebSearch (4-7, 일반+SNS)           │     │
│  │  → Source Diversity Check → Key Findings        │     │
│  └─────────────────────┬───────────────────────────┘     │
│                         │                                 │
│  Phase 2: 심화 탐색 (Deep Dive)                          │
│  ┌─────────────────────▼───────────────────────────┐     │
│  │  Knowledge Gap → Query Refinement               │     │
│  │  → WebSearch + WebFetch (source_verification)   │     │
│  │  → Cross-Validation → Evidence Sufficiency      │     │
│  └─────────────────────┬───────────────────────────┘     │
│                         │                                 │
│  Phase 3: 지식 합성 (Knowledge Synthesis)                │
│  ┌─────────────────────▼───────────────────────────┐     │
│  │  Anti-Hallucination Gate → Confidence Tagging   │     │
│  │  → Edge Cases → Structured Output               │     │
│  └─────────────────────────────────────────────────┘     │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 실행 트리거 조건

다음 조건 중 하나 이상에 해당하면 이 프로토콜을 실행합니다:

| 조건 | 예시 |
|------|------|
| **명시적 조사 요청** | "~에 대해 조사해줘", "최신 동향을 알려줘" |
| **기술 비교/선택** | "A vs B 어떤 것이 나은가?", "기술 스택 추천" |
| **최신 정보 필요** | "2025년 이후 변경사항", "최근 릴리스" |
| **불확실한 trade-off** | "성능과 일관성 중 어떤 것을 우선?", 근거 부족 시 |
| **표준/규정 확인** | "HIPAA 최신 요구사항", "FHIR R5 변경사항" |
| **패턴 적용 사례** | "실제 운영 환경에서 CQRS 적용 사례" |

### 트리거 제외 조건

다음의 경우 Deep Research를 **건너뛰고** 기존 지식으로 응답합니다:

- 이미 잘 알려진 패턴에 대한 단순 설명 요청
- 코드 리뷰/버그 수정 등 조사가 불필요한 작업
- 사용자가 명시적으로 빠른 응답을 요청한 경우

---

## Execution Instructions

### Phase 1: 광역 탐색 (Broad Exploration)

**목적**: 주제의 전체 지형(landscape)을 파악하고 핵심 키워드를 수집

#### Step 1-1: 쿼리 분해 (Query Decomposition)

**mcp__sequential-thinking__sequentialthinking**을 사용하여:

1. 사용자의 요구사항에서 **핵심 질문 3-5개**를 도출
2. 각 질문에 대한 **검색 쿼리**를 영어와 한국어로 각각 작성
3. 검색 전략 수립 (어떤 출처에서 어떤 정보를 얻을지)

```yaml
query_decomposition:
  original_question: "[사용자의 원본 질문]"
  sub_questions:
    - q1: "핵심 질문 1"
      search_queries:
        - en: "English search query"
        - ko: "한국어 검색 쿼리"
    - q2: "핵심 질문 2"
      search_queries:
        - en: "English search query"
        - ko: "한국어 검색 쿼리"
    # ... (3-5개)
```

#### Step 1-2: Authority Discovery

Phase 1의 WebSearch 광역 탐색 후, 주제의 권위 있는 출처를 사전 식별합니다:

1. **Semantic Scholar API로 핵심 논문 탐색**
   - WebFetch로 API 호출:
     `https://api.semanticscholar.org/graph/v1/paper/search?query={주제}&fields=title,citationCount,authors,year&limit=10`
   - citationCount 기준 상위 논문 3-5개 식별
   - 해당 논문의 저자(핵심 연구자) 기록

2. **Survey/Meta 논문 탐색** (Semantic Scholar API 실패 시 fallback)
   - WebSearch로 `"survey" OR "systematic review" {주제}` 검색
   - Survey 논문의 참고문헌에서 반복 인용되는 논문 식별

3. **실무/비학술 주제의 경우**
   - WebSearch로 `"awesome" OR "curated list" {주제}` 검색
   - 공식 문서, RFC, 표준 스펙을 우선 권위 출처로 설정

4. **Authority Anchor 기록**
   ```yaml
   authority_anchors:
     - type: paper | standard | official_doc
       title: "[제목]"
       authors: ["[저자]"]
       citation_count: N  # Semantic Scholar에서 확인한 수치
       url: "[URL]"
       relevance: "[이 주제에서 왜 권위 있는지]"
   ```

5. **Phase 2 연계**: authority_anchors의 논문/문서를 Phase 2 심화 탐색의 우선 WebFetch 대상으로 설정

#### Step 1-3: 병렬 WebSearch (4-7회)

도출된 검색 쿼리로 **WebSearch**를 **병렬로** 실행합니다:

> **병렬 호출 안전 전략**: Claude Code의 sibling tool call cascade 버그로 인해
> 병렬 호출 중 하나가 실패하면 나머지도 연쇄 취소됩니다.
> 이를 방지하기 위해 **WebSearch는 최대 3개씩 배치**로 나누어 실행합니다.
> 배치 내 실패 발생 시, 실패한 쿼리만 다음 배치에서 순차 재시도합니다.
>
> ```
> 배치 1: WebSearch x3 (병렬) → 결과 수집
> 배치 2: WebSearch x3 (병렬) → 결과 수집
> 실패 건: WebSearch x1 (순차) → 개별 재시도
> ```

##### 일반 검색 (3-5회)

- 각 검색은 서로 다른 관점/키워드를 사용
- 출처 다양성 확보: 공식 문서, 기술 블로그, 학술 자료, 커뮤니티 등

##### SNS 검색 (1-2회)

일반 검색과 병렬로 **SNS 전용 검색**을 수행합니다:

```yaml
sns_search_strategy:
  # WebSearch site: 연산자 기반 (기본)
  method: "WebSearch site: operator"

  search_patterns:
    reddit: "site:reddit.com {keyword} {year}"      # 우선순위 1
    twitter: "site:twitter.com {keyword}"            # 우선순위 2
    instagram: "site:instagram.com {keyword}"        # 우선순위 3
    facebook: "site:facebook.com {keyword}"          # 우선순위 4

  # MCP 서버 사용 가능 시 직접 API 호출로 전환
  # mcp_fallback:
  #   reddit: mcp__reddit__search(subreddit, query)
  #   twitter: mcp__twitter__search(query, filters)
```

**SNS 플랫폼 선택 기준**: Reddit을 최우선으로 검색합니다. 주제에 따라 X(Twitter)를 추가합니다.
Instagram/Facebook은 시각적 자료나 커뮤니티 의견이 필요한 경우에만 사용합니다.

#### Step 1-4: 출처 다양성 확인

수집된 출처를 다음 기준으로 분류:

| 출처 유형 | 신뢰도 | 예시 |
|-----------|--------|------|
| **공식 문서** | 최고 | RFC, 공식 가이드, 표준 문서 |
| **1차 자료** | 높음 | 원저자 블로그, 컨퍼런스 발표, 논문 |
| **기술 블로그** | 중간 | Engineering blog, 기술 기사 |
| **커뮤니티** | 참고 | Stack Overflow, GitHub Issues |
| **SNS/소셜 미디어** | 참고 (교차 검증 필수) | Reddit r/programming, X 전문가 스레드 |

**최소 2개 이상의 출처 유형**이 포함되어야 합니다. 부족하면 추가 검색을 수행합니다.

##### SNS 플랫폼별 조사 적합도

| SNS | 조사 적합도 | 주요 용도 |
|-----|------------|----------|
| **Reddit** | 높음 | 기술 토론, 실사용 경험, 패턴 비교 (r/programming, r/softwarearchitecture 등) |
| **X (Twitter)** | 중간 | 전문가 의견, 최신 트렌드, 릴리스 소식 |
| **Instagram** | 낮음 | 시각적 다이어그램, 인포그래픽 |
| **Facebook** | 낮음 | 그룹 토론, 커뮤니티 의견 |

#### Step 1-5: Phase 1 결과 정리

```yaml
phase1_findings:
  key_themes:
    - "[주요 테마 1]"
    - "[주요 테마 2]"
  authority_anchors:   # Step 1-2에서 식별
    - type: paper | standard | official_doc
      title: "[제목]"
      authors: ["[저자]"]
      citation_count: N
      url: "[URL]"
      relevance: "[권위 근거]"
  sources_collected: N
  source_diversity:
    official_docs: N
    primary_sources: N
    tech_blogs: N
    community: N
    sns: N
  keywords_for_phase2:
    - "[심화 검색용 키워드 1]"
    - "[심화 검색용 키워드 2]"
  initial_findings:
    - finding: "[발견 1]"
      source: "[출처]"
    - finding: "[발견 2]"
      source: "[출처]"
```

---

### Phase 2: 심화 탐색 (Deep Dive)

**목적**: Phase 1에서 발견한 핵심 주제를 깊이 파고들어 교차 검증

#### Step 2-0: Phase 1 이해도 기반 쿼리 재생성

Phase 1 완료 후, **mcp__sequential-thinking__sequentialthinking**을 사용하여:

1. Phase 1에서 수집한 findings를 분석하여 **지식 갭(knowledge gap)** 식별
   - "확인된 것" vs "아직 모르는 것" 구분
   - 초기 쿼리가 놓친 관점/키워드 식별
2. 지식 갭을 채우기 위한 **정제된 검색 쿼리** 생성
   - Phase 1에서 발견한 논문명, 저자명, 기술 용어를 활용
   - 초기 검색에서 사용하지 않은 동의어, 관련 개념 포함
   - authority_anchors의 저자/논문을 키워드에 반영
3. 각 쿼리에 **기대하는 근거(expected evidence)** 명시
   - "이 검색으로 X 주장의 직접 근거를 찾겠다"

```yaml
phase2_query_refinement:
  knowledge_gaps:
    - gap: "[아직 확인되지 않은 것]"
      initial_query_limitation: "[Phase 1 쿼리가 놓친 이유]"
      refined_query: "[개선된 검색 쿼리]"
      expected_evidence: "[이 검색으로 확인하려는 것]"
```

#### Step 2-1: 정제된 검색 + 원문 확인

Step 2-0의 정제된 쿼리를 사용하여:

1. **WebSearch**로 정제된 검색 2-3회 수행
2. **핵심 주장을 뒷받침하는 모든 출처**에 **WebFetch**로 원문 확인 (요약이 아닌 직접 인용 기록)
3. 특정 기술/패턴의 공식 문서를 직접 조회
4. WebFetch 시 **원문의 정확한 표현**을 기록

```yaml
source_verification:
  - claim: "[주장]"
    websearch_summary: "[WebSearch가 반환한 요약]"
    original_text: "[WebFetch로 확인한 원문의 직접 인용]"  # 필수
    matches_summary: true/false  # 요약과 원문이 일치하는지
    nuance_lost: "[요약에서 누락된 뉘앙스, 있다면]"
```

> **WebFetch 호출 안전 전략**: WebFetch는 봇 탐지에 취약하므로 다음 규칙을 따릅니다:
> - WebFetch 병렬 호출은 **최대 2개씩** 배치로 제한 (cascade 실패 영향 최소화)
> - 1개라도 403/timeout 발생 시 남은 URL은 **순차 실행**으로 전환
> - 403 실패 URL은 **Error Resilience Protocol**의 Fallback Tool Chain 적용
> - MCP Browser 도구는 단일 인스턴스이므로 **항상 순차 실행**

#### Step 2-1-1: SNS 심화 조사 (선택)

Phase 1에서 수집된 SNS 출처 중 유용한 토론/스레드가 있는 경우, **WebFetch**로 상세 내용을 확인합니다.

**SNS 데이터 신뢰도 판정 규칙**:

| 조건 | 확신도 태그 | 설명 |
|------|------------|------|
| SNS 단독 출처 (교차 검증 없음) | `[Unverified]` | 참고용으로만 사용 |
| 공식 문서/기술 블로그와 교차 검증 완료 | `[Likely]`로 승격 | 신뢰도 상향 |
| Reddit 높은 upvote + 다수 동의 댓글 | 커뮤니티 검증으로 간주 | `[Likely]` 부여 가능 |
| 전문가 계정(verified/known)의 X 스레드 | `[Likely]` 부여 가능 | 저자 권위성 고려 |

```yaml
sns_deep_dive:
  useful_threads:
    - platform: "reddit"
      url: "[URL]"
      relevance: "[관련성 설명]"
      community_signal: "upvotes: N, comments: N"
    - platform: "twitter"
      url: "[URL]"
      relevance: "[관련성 설명]"
      author_credibility: "[저자 신뢰도]"
```

#### Step 2-2: 교차 검증 (Cross-Validation)

수집된 정보를 교차 검증합니다:

```yaml
cross_validation:
  confirmed:       # 2개 이상 독립 출처에서 일치
    - claim: "[주장]"
      claim_type: descriptive | normative  # 서술적/규범적 구분
      sources: ["출처1", "출처2"]
      independence_verified: true/false     # 독립 출처 여부 확인

  contradicted:    # 출처 간 모순 발견
    - claim_a: "[주장 A]"
      source_a: "[출처 A]"
      claim_b: "[주장 B (반대)]"
      source_b: "[출처 B]"
      resolution: "[어떤 것이 더 신뢰할 수 있는지, 왜]"

  single_source:   # 단일 출처만 존재
    - claim: "[주장]"
      source: "[출처]"
      note: "추가 검증 필요"
```

##### 교차 검증 규칙

**(A) 서술적 주장 vs 규범적 주장 구분**:

| 유형 | 정의 | 예시 |
|------|------|------|
| **서술적(descriptive)** | 사실 진술 — "X를 사용했다/했다" | "2개 논문이 3명 에이전트를 사용했다" |
| **규범적(normative)** | 가치 판단 — "X가 최적이다/해야 한다" | "3명이 최적의 에이전트 수이다" |

> **규칙**: 서술적 주장의 일치가 규범적 주장의 근거가 되지 않습니다.
> - **잘못된 예**: "2개 논문이 3명 사용 → 3명이 최적 [Confirmed]"
> - **올바른 예**: "2개 논문이 3명 사용 → 3명은 흔한 설정 [Confirmed]. 최적 여부는 별도 근거 필요 [Uncertain]"

**(B) 독립 출처 검증**:

> **규칙**: 같은 원문을 인용하는 2차 출처는 독립 출처가 아닙니다.
> - 출처 A와 B가 **동일 1차 자료**를 참조하는지 확인
> - **잘못된 예**: "블로그A(논문X 인용) + 블로그B(논문X 인용) = 2개 독립 출처"
> - **올바른 예**: "실제 독립 출처는 논문X 1개. 블로그A/B는 파생 출처"

#### Step 2-3: 모순 식별 및 해결

출처 간 모순이 발견된 경우:

1. 각 출처의 **발행 시점** 확인 (최신이 우선)
2. 출처의 **권위성** 비교 (공식 문서 > 블로그)
3. **맥락 차이** 확인 (다른 버전, 다른 환경에서의 차이일 수 있음)
4. 해결이 불가능한 경우 **두 관점 모두 기록**

#### Step 2-4: 근거 충분성 검증

Phase 3으로 넘어가기 전, 다음 체크리스트를 검증합니다:

```
근거 충분성 체크:
- [ ] 핵심 주장별 최소 1건의 원문 직접 확인(WebFetch) 완료
- [ ] WebSearch 요약과 원문 간 뉘앙스 차이 기록 (source_verification)
- [ ] 지식 갭이 남아있는 경우 추가 검색 수행 또는 한계 명시
- [ ] 미충족 시: Phase 3에서 해당 주장에 [Uncertain] 또는 [Unverified] 부여
```

---

### Phase 3: 지식 합성 (Knowledge Synthesis)

**목적**: 수집된 정보를 구조화하고 확신도를 태깅하여 최종 결과물 생성

#### Step 3-0: Anti-Hallucination Gate (Phase 3 진입 전 필수)

Phase 3에서 합성을 시작하기 전, 다음 3개 Gate를 통과해야 합니다:

##### Gate 1: Evidence-First Check

모든 핵심 주장에 대해:
- 이 주장을 뒷받침하는 **원문 직접 인용**이 Step 2-1의 source_verification에 존재하는가?
- 원문이 이 주장을 "명시적으로" 지지하는가, 아니면 "해석"인가?
- 해석인 경우 → `[Synthesized]` 태그 필수

##### Gate 2: Attribution Specificity

모든 주장에서 다음 표현 사용 금지:

| 금지 표현 | 대체 표현 |
|-----------|-----------|
| "연구에 따르면" | "Du et al. (2024)에 따르면" |
| "전문가들은 ~를 권장" | "[이름]은 [출처]에서 ~를 권장" |
| "일반적으로" | "[출처]의 가이드라인에서" |
| "학계에서 합의" | "[학회/논문]에서 N건의 연구가 지지" |

##### Gate 3: Synthesis Necessity Check

여러 출처를 조합하여 새 결론을 도출하는 경우:
- 정말 조합이 필요한가, 아니면 개별 출처의 결론을 그대로 전달하면 되는가?
- 조합이 필요한 경우 → "A(출처1)와 B(출처2)를 종합하면" 형식 + `[Synthesized]` 태그

#### Step 3-1: 확신도 태깅 (Confidence Tagging)

모든 주요 주장/결론에 다음 태그를 부여합니다:

| 태그 | 기준 | 부여 조건 |
|------|------|-----------|
| `[Confirmed]` | 2개 이상 **독립** 출처에서 **원문 확인**(WebFetch)으로 검증됨 | WebSearch 요약만으로 부여 금지. Step 2-1의 source_verification 기록 필수 |
| `[Likely]` | 신뢰할 수 있는 1개 출처의 원문 확인 + 논리적 타당성 | 원문 확인 권장 |
| `[Synthesized]` | 여러 출처의 부분을 조합한 AI의 합성 결론 | Anti-Hallucination Gate 3 통과 필수. 개별 출처를 명시 |
| `[Uncertain]` | 출처 간 모순 또는 제한된 근거 | 모순 해결 시도 기록 포함 |
| `[Unverified]` | 검증할 수 있는 출처를 찾지 못함 | 참고용으로만 사용 |

#### Step 3-2: Edge Case 명시

```yaml
edge_cases:
  - scenario: "[특수 상황 설명]"
    impact: "[이 경우 결론이 어떻게 달라지는지]"
    recommendation: "[권고사항]"
```

#### Step 3-3: 최종 출력 형식

```markdown
## Deep Research: [주제]

### Executive Summary
[핵심 결론 3-5줄 요약]

### Findings

#### 1. [주요 발견 1]
[상세 설명]
- **확신도**: [Confirmed] / [Likely] / [Synthesized] / [Uncertain] / [Unverified]
- **출처**: [URL 또는 문서명]
- **근거**: [왜 이 결론에 도달했는지]

#### 2. [주요 발견 2]
...

### Comparisons (해당 시)

| 기준 | Option A | Option B | Option C |
|------|----------|----------|----------|
| ... | ... | ... | ... |

**권장**: [권장 옵션] — [Confirmed] 근거: ...

### Edge Cases & Caveats
- [특수 상황 1]: [영향]
- [특수 상황 2]: [영향]

### Contradictions Found
- [모순 1]: [출처 A] vs [출처 B] → [해결/미해결]

### Sources
1. [출처 1 제목](URL) — [출처 유형]
2. [출처 2 제목](URL) — [출처 유형]
...

### Research Metadata
- 검색 쿼리 수: N (일반 N + SNS N)
- 수집 출처 수: N
- 출처 유형 분포: 공식 N, 1차 N, 블로그 N, 커뮤니티 N, SNS N
- 확신도 분포: Confirmed N, Likely N, Synthesized N, Uncertain N, Unverified N
- SNS 출처: Reddit N건, X N건, Instagram N건, Facebook N건
- SNS 접근 방법: "WebSearch site: operator" | "MCP API"
```

---

## Quick Research (간소화 모드)

시간이 제한적이거나 단순 확인이 필요한 경우 **Quick Research**를 사용합니다:

### 트리거
- 사용자가 "빠르게", "간단히" 등의 표현 사용
- 단일 질문에 대한 사실 확인
- 이미 알고 있는 내용의 최신 업데이트 확인

### 실행 방법
- Phase 1만 수행 (WebSearch 1-2회)
- 교차 검증 생략
- 간단한 결과 형식:

```markdown
## Quick Research: [주제]

### 결과
[QuickResearch] [핵심 내용 — 확신도 태그 포함]

### 출처
- [출처 1](URL)
- [출처 2](URL)

### 주의
Quick Research 결과입니다. 중요한 의사결정에는 Full Research를 권장합니다.
**이 결과를 Full Research의 [Confirmed] 근거로 사용하지 마세요.**
```

---

## 오케스트레이션 연계

### Mode A: 개별 Agent 직접 호출

개별 아키텍트 에이전트가 직접 사용하는 경우:

```
User → Agent → Phase 1 → Phase 2 → Phase 3 → 응답에 통합
```

- 에이전트가 자신의 도메인 관점에서 3단계 모두 수행
- 결과를 리뷰/권고사항에 근거로 포함

### Mode B: 오케스트레이션 연계

`architect-orchestration` 스킬과 함께 사용하는 경우:

```
Orchestrator ─── Phase 1 (광역 탐색) ───────────────┐
                                                      │
              ┌───────────────────────────────────────┤
              ▼              ▼             ▼          │
         Agent A         Agent B       Agent C        │
         Phase 2         Phase 2       Phase 2        │
        (자기 도메인)   (자기 도메인)  (자기 도메인)   │
              └──────────────┬────────────┘           │
                             ▼                        │
                        Phase 3 (합성)                │
                     (오케스트레이터)                  │
```

1. **오케스트레이터가 Phase 1** 수행 → `research_context` 생성
2. `research_context`를 각 Agent 프롬프트에 주입
3. **각 Agent가 자기 도메인에 대해 Phase 2** 수행 (필요 시)
4. **오케스트레이터가 Phase 3** 수행 → 최종 합성

#### research_context 형식

```yaml
research_context:
  topic: "[조사 주제]"
  phase1_summary: "[Phase 1 핵심 발견 요약]"
  key_findings:
    - finding: "[발견]"
      confidence: "[Confirmed/Likely/Synthesized/Uncertain/Unverified]"
      source: "[출처]"
  relevant_to:
    security: "[보안 관련 발견]"
    data: "[데이터 관련 발견]"
    integration: "[통합 관련 발견]"
    # ... 관련 도메인별 요약
```

---

## Error Resilience Protocol

WebFetch는 단순 HTTP 클라이언트로 봇 탐지(Cloudflare, Medium, npm 등)에 취약하며,
Claude Code의 병렬 tool call 중 하나가 실패하면 나머지도 연쇄 취소되는 알려진 버그가 있습니다.
이 프로토콜은 조사 중단을 방지하고 대안 경로를 자동으로 탐색합니다.

### 알려진 실패 유형

| 에러 | 원인 | 빈도 |
|------|------|------|
| `HTTP 403 Forbidden` | 봇 탐지 (Cloudflare, User-Agent 차단, TLS fingerprinting) | 높음 |
| `Sibling tool call errored` | 병렬 tool call 중 하나 실패 시 나머지 연쇄 취소 (Claude Code 버그) | 높음 |
| `Request timeout` | 응답 지연 또는 무한 대기 | 중간 |
| `Unable to verify domain` | WebFetch 내부 도메인 검증 실패 | 낮음 |

### Fallback Tool Chain

WebFetch 실패 시 다음 순서로 대안을 시도합니다:

```
WebFetch 시도
  │
  ├─ 성공 → 계속 진행
  │
  └─ 실패 (403 / timeout / sibling error)
       │
       ├─ Playwright MCP 사용 가능? (무료)
       │    ├─ Yes → browser_navigate + browser_get_text 로 재시도
       │    └─ No → 아래 WebSearch 대체 경로
       │
       ├─ WebSearch 대체 검색
       │    "site:{domain} {핵심 키워드}" 로 캐시/요약 검색
       │
       └─ 모든 경로 실패
            → 해당 출처 건너뛰기
            → 대안 출처 추가 검색 (동일 주제, 다른 도메인)
```

### Playwright MCP 사용법

Playwright MCP가 설치된 경우 다음과 같이 사용합니다:

```
1. browser_navigate → URL 접속
2. browser_get_text → 페이지 텍스트 추출 (accessibility tree 기반)
```

- 실제 브라우저를 사용하므로 JavaScript 렌더링 및 기본적인 봇 탐지 우회 가능
- 단일 브라우저 인스턴스이므로 **순차 실행 필수**

### 403 차단 빈발 사이트 대응표

| 사이트 | 차단 방식 | 권장 경로 |
|--------|----------|----------|
| Medium | User-Agent 차단 | Playwright MCP → WebSearch 대체 |
| npm | AI agent 차단 | Playwright MCP → WebSearch 대체 |
| Cloudflare 보호 사이트 | Bot Fight Mode | Playwright MCP → WebSearch 대체 |
| Wikipedia | 간헐적 차단 | Playwright MCP → WebSearch 캐시 |
| 기업 개발자 문서 | WAF/봇 탐지 | Playwright MCP → WebSearch 대체 |

### Graceful Degradation

MCP Browser 도구가 설치되지 않은 환경에서는:

1. **WebFetch 1회 시도** → 실패 시 즉시 WebSearch 대체
2. WebSearch로 `"site:{domain} {keyword}"` 검색하여 캐시/요약 확인
3. 대안 도메인에서 동일 주제 검색 (예: Medium 차단 → dev.to, hashnode 검색)
4. 조사 품질 저하 시 사용자에게 한계를 명시하고 MCP 설치를 권장

---

## 품질 기준

### 충분한 조사의 기준

- [ ] 핵심 주장별 독립 출처 확인 (3개 이상 권장, 부족 시 한계 명시)
- [ ] 핵심 주장별 최소 1건 원문 직접 확인(WebFetch) 완료
- [ ] 2개 이상의 출처 유형 포함
- [ ] 모든 주요 주장에 확신도 태그 부여
- [ ] 발견된 모순점 명시 및 해결 시도
- [ ] Edge case 식별 (해당 시. 없으면 "N/A -- 특수 상황 미발견" 명시)
- [ ] 출처 URL 또는 문서명 명시
- [ ] SNS 출처 확인 시도 (해당 시. 기술 주제에 한함. 관련 없으면 생략 가능)
- [ ] SNS 정보는 다른 출처와 교차 검증 완료

> **원칙**: 근거 없는 내용을 채우는 것보다 "N/A" 또는 "해당 없음"을 명시하는 것이 낫다.
> 모든 섹션을 반드시 채울 필요 없음. 빈 섹션은 "조사했으나 해당 사항 없음"으로 기록.

### 조사 품질 저하 시

다음 경우 사용자에게 한계를 명시합니다:

- 검색 결과가 부족한 경우
- 출처 간 심각한 모순이 해결되지 않은 경우
- 최신 정보를 찾을 수 없는 경우
- 특정 도메인의 전문 지식이 필요한 경우

---

## SNS 조사 가이드

### 접근 방법 분기

```
SNS 조사 요청
    │
    ├─ MCP 서버 사용 가능? ──── Yes ──→ MCP API 직접 호출
    │                                    (구조화된 데이터, 필터링 가능)
    │
    └─ No ──→ WebSearch site: 연산자 사용
              (현재 기본 방법)
```

### 플랫폼별 검색 쿼리 예시

#### Reddit (우선순위 1)

```
# 기술 토론 검색
"site:reddit.com r/programming CQRS event sourcing"
"site:reddit.com r/softwarearchitecture microservices saga pattern"
"site:reddit.com r/devops kubernetes service mesh 2025"

# 특정 서브레딧 타겟
"site:reddit.com/r/java spring boot virtual threads"
"site:reddit.com/r/golang concurrency patterns"
```

#### X / Twitter (우선순위 2)

```
# 전문가 의견/최신 트렌드
"site:twitter.com CQRS event sourcing architecture"
"site:twitter.com microservices 2025 best practices"

# 특정 인물의 의견 (알려진 전문가)
"site:twitter.com from:martinfowler event driven"
```

#### Instagram / Facebook (우선순위 3-4)

```
# 시각적 자료 (Instagram)
"site:instagram.com software architecture diagram"

# 그룹 토론 (Facebook)
"site:facebook.com groups software architecture discussion"
```

### SNS 정보의 한계와 주의사항

| 항목 | 설명 |
|------|------|
| **편향 가능성** | SNS 의견은 특정 커뮤니티 편향이 있을 수 있음 (예: Reddit은 오픈소스 선호 경향) |
| **시점 의존성** | SNS 게시물은 특정 시점의 의견이며, 이후 변경되었을 수 있음 |
| **권위 부재** | 익명/비전문가 의견이 혼재하여 개별 게시물의 권위성 판단이 어려움 |
| **검증 필수** | SNS 정보는 반드시 공식 문서/기술 블로그와 교차 검증 후 사용 |
| **샘플 편향** | 특정 기술에 대한 부정적/긍정적 경험이 과대 대표될 수 있음 |

### MCP 서버 설정 (향후 참조용)

SNS API에 직접 접근하려면 MCP 서버를 설정합니다. 현재는 WebSearch `site:` 연산자로 충분하며,
API 접근이 필요해지면 아래 구성을 참고하세요:

```jsonc
// .mcp.json 예시 (향후 설정 시)
{
  "mcpServers": {
    "reddit": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-reddit"],
      "env": {
        "REDDIT_CLIENT_ID": "<your-client-id>",
        "REDDIT_CLIENT_SECRET": "<your-client-secret>"
      }
    }
    // Twitter/X API는 별도 MCP 서버 패키지 확인 필요
  }
}
```

> **참고**: MCP 서버 패키지명은 예시이며, 실제 사용 시 최신 패키지를 확인하세요.

---

## MCP 서버 설정 가이드 (Web Fetch 강화)

WebFetch의 봇 탐지 취약성을 보완하기 위해 MCP Browser 도구를 설정합니다.
Error Resilience Protocol의 Fallback Tool Chain에서 사용됩니다.

### Tier 1: Playwright MCP (무료, 기본 권장)

Microsoft 공식 Playwright MCP 서버. 실제 Chromium 브라우저를 headless로 실행하여
JavaScript 렌더링 및 기본적인 봇 탐지를 우회합니다.

**설치 (CLI)**:
```bash
claude mcp add playwright npx @playwright/mcp@latest -- --headless
```

**설정 (.mcp.json)**:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--headless"]
    }
  }
}
```

**주요 옵션**:
- `--headless`: 브라우저 창 없이 실행 (기본 권장)
- `--browser firefox`: Firefox 사용 (기본: Chrome)
- `--viewport-size 1280x720`: 뷰포트 크기 지정

**주요 도구**: `browser_navigate`, `browser_get_text`, `browser_click`, `browser_screenshot`

**한계**: Cloudflare Turnstile/CAPTCHA는 일관되게 통과하지 못할 수 있음

### 설정 확인

```bash
# 설치된 MCP 서버 목록 확인
claude mcp list

# 정상 연결 시 출력 예시
# playwright: npx @playwright/mcp@latest --headless - ✓ Connected
```

### Tool Selection Matrix (상황별 도구 선택)

| 상황 | 1차 시도 | 2차 Fallback | 3차 Fallback |
|------|---------|-------------|-------------|
| 일반 URL | WebFetch | Playwright MCP | WebSearch 캐시 |
| 403 차단 사이트 | Playwright MCP | WebSearch 대체 | 대안 도메인 검색 |
| Cloudflare 보호 | Playwright MCP | WebSearch 대체 | 출처 건너뛰기 |
| Medium/npm 등 | Playwright MCP | WebSearch 대체 | 대안 도메인 검색 |
| JS 렌더링 필요 | Playwright MCP | WebSearch 대체 | 출처 건너뛰기 |
| CAPTCHA 사이트 | WebSearch 대체 | 출처 건너뛰기 | - |
| 인용 수 기반 권위 판단 | Semantic Scholar API (WebFetch) | Survey 논문에서 수동 추출 | - |
| 논문 원문 확인 | arXiv WebFetch | Playwright → HTML 버전 | - |
| 블로그/기술 문서 | WebFetch | Playwright (Cloudflare 없는 경우만) | WebSearch 대체 |

> **Playwright headless 한계**: Cloudflare Turnstile, Google Scholar 봇 감지(IP 기반),
> Medium Cloudflare 등 고급 보안은 headless 브라우저로도 우회 불가.
> 학술 권위 판단에는 Semantic Scholar API가 유일하게 안정적인 경로.

---

## 관련 리소스

- 각 아키텍트 에이전트의 도메인 지식 (`.claude/agents/*.md`)
- 아키텍처 패턴 스킬 카드 (`.claude/skills/*/SKILL.md`)
- 오케스트레이션 프로토콜 (`.claude/skills/architect-orchestration/SKILL.md`)
