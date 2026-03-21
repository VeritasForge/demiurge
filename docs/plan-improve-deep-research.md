⏺ Deep Research 스킬 — Best Practice 준수 평가 결과

  writing-skills 스킬의 체크리스트를 기준으로 deep-research SKILL.md를 평가한 결과입니다.

  ---
  종합 점수: B+ (잘 만들어졌으나 Critical CSO 이슈 존재)

  ┌─────────────────────────────────────────────────────────────┐
  │                  평가 항목별 점수 카드                         │
  ├──────────────────────┬───────┬──────────────────────────────┤
  │ 항목                  │ 점수  │ 상태                          │
  ├──────────────────────┼───────┼──────────────────────────────┤
  │ Name                 │  A    │ ✅ "deep-research" 규칙 준수   │
  │ Description (CSO)    │  F    │ ❌ 워크플로우 요약 (critical)  │
  │ Overview             │  A    │ ✅ 핵심 원칙 + 시각화          │
  │ When to Use          │  A    │ ✅ 트리거/제외 조건 테이블      │
  │ Implementation       │  A+   │ ✅ Phase 1-2-3 매우 상세       │
  │ Quick Reference      │  D    │ ❌ 없음                       │
  │ Common Mistakes      │  F    │ ❌ 없음                       │
  │ Token Efficiency     │  D    │ ❌ ~3000+ words (권장 500)     │
  │ File Organization    │  C    │ ⚠️ heavy reference 분리 필요   │
  │ Flowcharts           │  B+   │ ✅ 대부분 적절                 │
  │ Cross-References     │  B    │ ✅ @link 미사용               │
  │ Keyword Coverage     │  B    │ ⚠️ description에 키워드 부족   │
  │ TDD Testing          │  N/A  │ 사전 도입 스킬                │
  └──────────────────────┴───────┴──────────────────────────────┘

  ---
  Critical Issues (P0 — 반드시 수정)

  1. Description이 워크플로우 요약 — CSO 최대 위반

  현재:
  description: 3단계 심층 조사 프로토콜. 광역 탐색 → 심화 탐색 → 지식 합성을 통해 근거 기반 아키텍처
  의사결정을 지원.

  문제: writing-skills가 명시적으로 금지하는 패턴
  "descriptions that summarize workflow create a shortcut Claude will take. The skill body becomes
  documentation Claude skips."

  Claude가 이 description만 읽고 "3단계 해야지"로 shortcut을 타면서, Anti-Hallucination Gate,
  Cross-Validation 규칙 등 핵심 본문을 건너뛸 위험이 있습니다.

  수정안:
  description: Use when architecture decisions need evidence-based research — technology comparisons,
  latest trends, trade-off analysis, standards verification, or when existing knowledge is
  insufficient for confident recommendations

  ---
  Important Issues (P1 — 단기 개선)

  2. Quick Reference 테이블 없음

  Phase별 핵심 활동을 한눈에 스캔할 수 있는 요약이 없습니다. 추가 제안:

  ## Quick Reference

  | Phase | 목적 | 핵심 활동 | 산출물 |
  |-------|------|-----------|--------|
  | 1. 광역 탐색 | 지형 파악 | Query Decomposition → WebSearch x4-7 | phase1_findings |
  | 2. 심화 탐색 | 교차 검증 | Knowledge Gap → WebFetch 원문 확인 | cross_validation |
  | 3. 지식 합성 | 구조화 | Anti-Hallucination Gate → Confidence Tagging | 최종 리포트 |

  3. Common Mistakes 섹션 없음

  본문에 산재한 주의사항들을 모아야 합니다:

  ## Common Mistakes
  - WebSearch 요약만으로 [Confirmed] 부여 → 반드시 WebFetch 원문 확인 필요
  - 같은 1차 자료를 인용하는 블로그 2개를 "독립 출처 2개"로 착각
  - 서술적 주장의 일치로 규범적 결론 도출 ("2개 논문이 3명 사용 → 3명이 최적")
  - Quick Research 결과를 Full Research의 [Confirmed] 근거로 사용
  - Phase 2 건너뛰고 Phase 1 결과만으로 합성 시도

  4. Token Efficiency — Heavy Reference 분리 필요

  현재 ~816줄 / ~3,000+ words → 권장치 500 words의 6배

  분리 제안:
  deep-research/
    SKILL.md                # 핵심 프로토콜 (~300 words)
    error-resilience.md     # Error Resilience Protocol + Tool Selection Matrix
    sns-research-guide.md   # SNS 조사 가이드 + 플랫폼별 쿼리 예시
    mcp-setup.md            # MCP 서버 설정 가이드

  ---
  Nice-to-have (P2 — 중기)

  5. Rationalization Table 부재

  deep-research는 discipline-enforcing 성격도 가지고 있어(Anti-Hallucination Gate 등), agent가
  합리화할 수 있는 패턴에 대한 대응이 필요합니다:

  ┌──────────────────────────────────┬───────────────────────────────────────┐
  │              Excuse              │                Reality                │
  ├──────────────────────────────────┼───────────────────────────────────────┤
  │ "WebSearch 요약만으로 충분하다"  │ 요약은 뉘앙스를 누락함. WebFetch 필수 │
  ├──────────────────────────────────┼───────────────────────────────────────┤
  │ "시간이 없어서 Phase 2 건너뛴다" │ Phase 2 없이 [Confirmed] 부여 불가    │
  ├──────────────────────────────────┼───────────────────────────────────────┤
  │ "출처 2개니까 독립 검증 완료"    │ 같은 1차 자료 인용 여부 확인 필수     │
  └──────────────────────────────────┴───────────────────────────────────────┘

  6. TDD Pressure Scenario 테스트 미수행

  이 스킬은 writing-skills 도입 전에 생성(v3.3)되었으므로 retroactive 테스트를 권장합니다.

  ---
  잘된 점 (Keep)

  - 트리거 조건/제외 조건 본문 내 명확한 테이블 정의
  - Anti-Hallucination Gate 3중 검증 (Evidence-First, Attribution Specificity, Synthesis Necessity)
  - Cross-Validation 규칙 서술적/규범적 구분 + 독립 출처 검증
  - Error Resilience Protocol 실용적 fallback chain
  - YAML template 실행 가능한 형태로 제공
  - 확신도 태깅 체계 5단계 (Confirmed → Unverified) 부여 조건 명확

  ---
  사고 과정 요약

  ┌──────────────────────┐
  │ writing-skills 로드   │ ← Skill tool
  └──────────┬───────────┘
             ▼
  ┌──────────────────────┐
  │ deep-research 읽기    │ ← Read tool (816줄)
  └──────────┬───────────┘
             ▼
  ┌──────────────────────────────────────────────────┐
  │ sequential-thinking (9 steps)                     │
  │                                                    │
  │ Step 1: 평가 기준 9개 항목 도출                    │
  │ Step 2: Frontmatter — description 위반 발견        │
  │ Step 3: CSO — 워크플로우 요약 금지 위반 확인        │
  │ Step 4: Structure — Common Mistakes/Quick Ref 부재 │
  │ Step 5: Token Efficiency — 6배 초과                │
  │ Step 6: Flowchart — 대체로 적절                    │
  │ Step 7: Cross-Ref, Naming, File Org               │
  │ Step 8: TDD Testing, Rationalization Table         │
  │ Step 9: 종합 점수 + 우선순위 로드맵                │
  └──────────────────────────────────────────────────┘

  수정 진행을 원하시면 우선순위별로 작업하겠습니다.
