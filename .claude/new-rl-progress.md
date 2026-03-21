# Progress Tracker

## Status
- total: 5
- completed: 5
- current: DONE
- retries: 0

## Requirements
- [x] 1. writing-skills 스킬 정의 + Anthropic best practices 문서 참조 여부 확인
- [x] 2. CSO 약자 및 의미 설명
- [x] 3. description 워크플로우 요약 금지 패턴 상세 설명
- [x] 4. discipline-enforcing 및 Anti-Hallucination Gate 개념 설명
- [x] 5. retroactive 테스트 의미 설명

## Log
### Req 1: ✅ writing-skills = "스킬을 만드는 방법을 가르치는 메타-스킬". TDD 방법론 적용. Anthropic best practices를 명시적으로 참조(anthropic-best-practices.md 로컬 번들). 관계: 교과서(Anthropic) + 실습 워크북(writing-skills) 보완 관계.

### Req 2: ✅ CSO = Claude Search Optimization. SEO의 Claude 버전. 핵심 차이: SEO는 description 요약 권장, CSO는 요약 금지(Claude가 본문을 건너뛰기 때문). deep-research 이슈: description이 워크플로우를 요약하여 Anti-Hallucination Gate 등 핵심 메커니즘이 무시될 위험.

### Req 3: ✅ "shortcut" = description에 워크플로우가 있으면 Claude가 이미 알고 있다고 판단하여 본문 디테일을 건너뛰는 현상. 실험으로 확인됨(1 review vs 2 review 사례). deep-research에서 Authority Discovery, Anti-Hallucination Gate, source_verification 등 20+ 세부 절차가 "광역→심화→합성" 3단어에 뭉개질 위험.

### Req 4: ✅ Discipline-Enforcing = "규칙을 강제하는 스킬"(축구의 심판). 4가지 스킬 유형 중 유일하게 행동 규율 목적. Anti-Hallucination Gate = Phase 3 진입 전 3중 검문소(Evidence-First, Attribution Specificity, Synthesis Necessity). deep-research는 Technique+Discipline 혼합 → Rationalization Table 필요.

### Req 5: ✅ Retroactive = 소급적용. deep-research(v3.3)는 writing-skills Iron Law("실패 테스트 없이 스킬 만들지 마라") 도입 전에 생성되어 TDD 사이클을 거치지 않음. retroactive 테스트 = 이미 만든 스킬에 pressure scenario를 사후 적용하여 Anti-Hallucination Gate, Error Resilience 등이 실제 작동하는지 검증하는 것.
