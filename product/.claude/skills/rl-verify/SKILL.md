---
name: rl-verify
description: "수렴 검증 플랜 생성 + 실행. 사용자가 /rl-verify로 직접 호출."
disable-model-invocation: true
argument-hint: "[--force] <작업 설명 또는 문서 경로>"
---

# RL-Verify — 수렴 검증기

수렴 검증에 필요한 **플랜 + 리포트**를 생성하고, 사용자 동의 후 수렴 루프를 직접 실행합니다.

---

## Phase 0: 인자 파싱, slug 생성, 기존 산출물 감지

### 0-1. 인자 파싱

`$ARGUMENTS`에서 `--force` 옵션 존재 여부를 먼저 확인하고 제거합니다.
나머지 인자로 작업 대상을 파악하여 **slug**를 생성합니다.

**slug 생성 규칙:**
- 검증 대상의 핵심 키워드를 kebab-case로 변환
- 최대 30자
- 예: `security-audit`, `api-design`, `readme-check`, `pr-6168`

결과 폴더: `docs/demiurge/rl-verify/{slug}/`
산출물: `docs/demiurge/rl-verify/{slug}/plan.md`, `docs/demiurge/rl-verify/{slug}/report.md`

### 0-2. 기존 산출물 감지

`docs/demiurge/rl-verify/{slug}/plan.md`가 존재하는지 감지합니다.

```
기존 폴더 존재?
  ├─ NO → Phase 1로 진행 (폴더 신규 생성)
  └─ YES
       ├─ --force 옵션 있음
       │   → 기존 폴더를 타임스탬프로 리네임 후 신규 생성
       │     ({slug}/ → {slug}.{YYYYMMDD-HHmm}/)
       │
       └─ --force 옵션 없음
            → 사용자에게 질문:
              "이전 검증 결과가 있습니다. (docs/demiurge/rl-verify/{slug}/)"
              "1) 이어서 검증 (기존 plan/report 유지)"
              "2) 새로 시작 (기존 폴더 아카이브)"
              - 1) 선택 시 → 기존 plan/report 유지, Phase 2 스킵, Phase 4로 진행
              - 2) 선택 시 → 아카이브 후 Phase 1로 진행
```

> slug 기반 폴더 분리 덕분에 **다른 대상의 검증은 다른 폴더에 자동 생성**되므로 충돌하지 않습니다.
> 같은 디렉토리에서 여러 검증을 동시에 유지할 수 있습니다.

---

## Phase 1: 작업 파악

`$ARGUMENTS`(Phase 0에서 `--force` 제거 후)를 파싱하여 작업 유형을 자동 판별합니다.

**판별 규칙:**
- 파일 경로가 포함됨 → **"문서 검증"** 모드
- PR 번호 또는 URL이 포함됨 → **"코드 리뷰"** 모드
- 텍스트 설명만 있음 → **"리서치/아이디어 검증"** 모드

**실행:**
1. 인자에서 작업 유형 판별
2. 검증 대상 읽기 (Read 도구, MCP 도구 등으로 대상 내용 확인)
3. 대상의 도메인/키워드/기술스택 추출

---

## Phase 2: 도메인 분석 및 Orchestration 설계

단순 매칭이 아니라, **검증 케이스에 맞는 subagent 팀을 설계**합니다.

**실행:**

### 2-1. Tier 판별

검증 대상의 복잡도와 영향 범위를 분석하여 Tier를 결정합니다.

```
┌─────────────────────────────────────────────────────────┐
│ Tier 1: 경량 검증                                        │
│ 조건: 단일 파일/문서, 영향 범위 제한적, 되돌리기 쉬움    │
│ 예: README 정확성, 단순 문서 검증                         │
│ → 최소 2개 관점 + EVALUATOR, CONTRARIAN 필수             │
├─────────────────────────────────────────────────────────┤
│ Tier 2: 표준 검증                                        │
│ 조건: 여러 파일/컴포넌트, 중간 영향 범위                  │
│ 예: 플랜 검증, PR 코드 리뷰                              │
│ → 최소 3개 관점 + EVALUATOR, CONTRARIAN 필수             │
├─────────────────────────────────────────────────────────┤
│ Tier 3: 심층 검증                                        │
│ 조건: 시스템 전체 영향, 되돌리기 어려운 결정,             │
│       외부 사실 확인 필요한 주장 포함                     │
│ 예: 아키텍처 결정, 리서치 검증, 보안 감사                 │
│ → 최소 4개 관점 + EVALUATOR, CONTRARIAN+RESEARCHER 필수  │
└─────────────────────────────────────────────────────────┘
```

**필수 역할 정의:**

| 역할 | 질문 | Tier 1 | Tier 2 | Tier 3 |
|------|------|--------|--------|--------|
| CONTRARIAN | "왜 틀린가?" — 반론/반례 구성 | **필수** | **필수** | **필수** |
| ARCHITECT | "구조적으로 타당한가?" — 건전성 검증 | 선택 | 선택 | 권장 |
| RESEARCHER | "증거가 있는가?" — 외부 근거 검증 | 선택 | 선택 | **필수** |
| SIMPLIFIER | "정말 필요한가?" — 최소 대안 제시 | 선택 | 선택 | 권장 |
| EVALUATOR | 종합 판정 | **필수** | **필수** | **필수** |

> 역할은 논리적 역할이며, 어떤 agent/skill로 구현할지는 기존 "관점별 Agent 할당" 로직(custom agent → skill → 페르소나)을 그대로 따름.

### 2-2. 검증 관점(Perspective) 도출

Tier별 최소 관점 수에 맞춰 검증 관점을 결정합니다.
- 예: 보안 계획서(Tier 3) → [코드 정확성, 보안 전문성, 아키텍처 타당성, 외부 근거 검증]
- 예: API 설계 문서(Tier 2) → [스펙 정확성, 성능 관점, 호환성 관점]
- 예: README 검증(Tier 1) → [사실 정확성, 대안 분석]

### 2-3. 관점별 Agent 할당

#### Step 1: 매핑 테이블 조회 → 실행 목록 생성

Phase 1에서 추출한 도메인 키워드를 아래 매핑 테이블에서 매칭한다.
복수 도메인이면 **합산** 후, **(이름 + 소스) 튜플 기준으로 중복 제거**한다.

> **중복 판별 기준**: 이름이 같아도 소스가 다르면 별개 (예: `deep-research (demiurge)` ≠ `deep-research (ouroboros)`).
> 동일 소스에서 동일 이름이 여러 행에서 중복 출현한 경우만 제거.

합산 결과는 "후보 풀"이 아니라 **실행 목록**이다. Tier별 최소 관점 수는 하한선(floor)으로만 작용하며, 매핑 테이블에서 나온 에이전트/스킬은 **전부 실행**한다.

| 도메인 키워드 | CONTRARIAN | ARCHITECT | RESEARCHER | SIMPLIFIER |
|---|---|---|---|---|
| 보안, OWASP, 인증, 암호화 | contrarian (ouroboros) | security-architect (demiurge), security-sentinel (compound) | deep-research (demiurge), best-practices-researcher (compound) | simplifier (ouroboros), code-simplicity-reviewer (compound) |
| 아키텍처, MSA, 설계, 패턴 | contrarian (ouroboros) | solution-architect (demiurge), application-architect (demiurge), architecture-strategist (compound) | deep-research (demiurge), repo-research-analyst (compound) | simplifier (ouroboros) |
| 데이터, DB, 마이그레이션, CQRS | contrarian (ouroboros) | data-architect (demiurge), data-integrity-guardian (compound), schema-drift-detector (compound) | deep-research (demiurge) | simplifier (ouroboros) |
| AI, LLM, RAG, 프롬프트, ML | contrarian (ouroboros) | llm-architect (demiurge), rag-architect (demiurge) | deep-research (demiurge), framework-docs-researcher (compound) | simplifier (ouroboros) |
| 성능, 확장성, 부하, 최적화 | contrarian (ouroboros) | sre-architect (demiurge), performance-oracle (compound) | deep-research (demiurge), best-practices-researcher (compound) | simplifier (ouroboros) |
| 클라우드, 인프라, K8s, Terraform | contrarian (ouroboros) | cloud-native-architect (demiurge), deployment-verification-agent (compound) | deep-research (demiurge) | simplifier (ouroboros) |
| API, 통합, 이벤트, EDA | contrarian (ouroboros) | integration-architect (demiurge) | deep-research (demiurge) | simplifier (ouroboros) |
| 코드 리뷰, PR, 코드 품질 | contrarian (ouroboros) | pattern-recognition-specialist (compound), architecture-strategist (compound) | repo-research-analyst (compound), requesting-code-review (superpowers skill) | code-simplicity-reviewer (compound) |
| 테스트, TDD, QA | contrarian (ouroboros) | testing-architecture (demiurge skill), test-driven-development (superpowers skill) | deep-research (demiurge) | simplifier (ouroboros) |
| 프론트엔드, UI, UX | contrarian (ouroboros) | frontend-design (compound skill) | framework-docs-researcher (compound), agent-browser (compound skill) | simplifier (ouroboros) |
| 리서치, 조사, 분석, Fact-Check | contrarian (ouroboros) | interview (ouroboros skill) | deep-research (demiurge), best-practices-researcher (compound), notion-research-documentation (notion skill) | simplifier (ouroboros) |
| 문서화, README, API 문서, 기술 문서 | contrarian (ouroboros) | writing-plans (superpowers skill), writing-skills (superpowers skill) | document-review (compound skill), compound-docs (compound skill) | simplifier (ouroboros), document-review (compound skill) |
| 디버깅, 버그, 오류 | contrarian (ouroboros) | systematic-debugging (superpowers skill) | deep-research (demiurge) | simplifier (ouroboros) |

**공통 EVALUATOR**: evaluator (ouroboros agent) — 모든 도메인에서 사용

#### Step 2: 실행 (이름 기반 호출)

매핑 테이블의 실행 목록을 다음 우선순위로 호출한다. 파일시스템 경로/버전 조회 불필요 — Claude Code가 이름으로 해결.

```
agent 항목  → Agent 도구 (subagent_type="{이름}")
skill 항목  → Skill 도구 ("{이름}")
매핑 테이블에 없는 도메인 → Explore agent + 전문가 페르소나 + 구체적 검증 지침
```

#### 필수 역할 포함 확인

Tier별 필수 역할(CONTRARIAN, RESEARCHER, EVALUATOR)이 실행 목록에 포함되었는지 확인한다.

**Orchestration 원칙:**
1. **Tier별 최소 관점 수는 하한선** — 매핑 테이블 결과가 더 많으면 전부 실행
2. **관점 간 독립성** — 같은 agent가 두 관점을 맡지 않도록 분리
3. **불일치 발생 시 제3 관점 투입** — EVALUATOR가 CONTESTED 판정 시 다음 iteration에서 새 관점 추가. 제3 관점 agent도 매핑 테이블 또는 페르소나 폴백을 따르되, CONTESTED 사유와 양쪽 이견을 프롬프트에 명시
4. **EVALUATOR는 매 iteration foreground subagent로 실행** — 검증 agent들의 출력을 종합하여 판정 라벨 부여. Main agent는 오케스트레이터로서 EVALUATOR 출력을 받아 안정 카운터 업데이트 + 리포트 갱신

---

## Phase 3: 산출물 2개 생성

### 산출물 1: `docs/demiurge/rl-verify/{slug}/report.md` — 빈 리포트 초기화

```markdown
# 수렴 검증 리포트

> 작업: {설명}
> 시작: {일시}
> 모드: {문서검증 | 코드리뷰 | 리서치}
> 사용 Agent/Skill: {매칭 결과}

## (Iteration 1에서 결과가 추가됩니다)
```

### 산출물 2: `docs/demiurge/rl-verify/{slug}/plan.md` — 상세 플랜

이 파일에 반드시 포함해야 하는 섹션:

1. **검증 항목** 테이블
2. **Tier 및 필수 역할**
3. **검증 관점 및 Agent 할당** 테이블
4. **Agent별 상세 프롬프트** (EVALUATOR 포함)
5. **EVALUATOR 판정 기준**
6. **안정 카운터 업데이트 규칙**
7. **수렴 판정 기준**
8. **리포트 갱신 형식** (iteration별, 최종 리포트)
9. **완료 조건**
10. **하지 말 것**

**플랜 파일 템플릿:**

```markdown
# 수렴 검증 플랜

## 대상
{작업 설명 / 문서 경로}

## Tier
{Tier 1 | Tier 2 | Tier 3} — {판별 근거}

## 검증 항목
| # | 항목 | 검증 방법 | 사용 Agent/Skill |
|---|------|----------|-----------------|

## 검증 관점 및 Agent 할당
| 관점 | 역할 | 사용 Agent/Skill | 필수 여부 |
|------|------|-----------------|----------|

## Agent별 상세 프롬프트
### 관점 1: {관점명} ({역할})
- Agent: {agent type}
- 프롬프트: {구체적 검증 지시}

### 관점 2: {관점명} ({역할})
- Agent: {agent type}
- 프롬프트: {구체적 검증 지시}

### EVALUATOR
- Agent: {agent type}
- 프롬프트: 위 관점 Agent들의 출력을 종합하여 각 발견사항에 판정 라벨을 부여하라.

## EVALUATOR 판정 기준
| 라벨 | 조건 |
|------|------|
| CONFIRMED | 다수 agent 동의 + 외부 근거 존재 |
| LIKELY | 다수 agent 동의, 외부 근거 미확인 |
| CONTESTED | Agent 간 의견 분열 (핵심 이견 명시) |
| REFUTED | 다수 agent 반대 또는 외부 근거가 반박 |
| UNGROUNDED | 외부 검증 불가 + 자기 참조만 존재 |

## 안정 카운터 업데이트 규칙
- EVALUATOR 판정이 이전과 동일 → 안정 카운터 +1
- EVALUATOR 판정이 이전과 다름 → 안정 카운터 = 0
- 신규 발견 → 안정 카운터 = 0, "신규" 표시
  + 기존 합의 항목에 영향 시 해당 항목 안정 카운터 리셋
- CONTESTED → 다음 iteration에서 제3 관점 투입
- 이전 발견이 이번에 없음 → "취소 후보", 안정 카운터 = 0

## 수렴 판정 기준
- Tier 1-2: 모든 발견사항의 안정 카운터 >= 2 (EVALUATOR 판정 2회 연속 동일)
- Tier 3: 모든 발견사항의 안정 카운터 >= 3 (EVALUATOR 판정 3회 연속 동일)
- 새로운 발견 0건
- CONTESTED 항목 0건

## 리포트 갱신 형식

### Iteration별 갱신
| # | 항목 | EVALUATOR 판정 | 신뢰도 | 근거 요약 | 안정 카운터 |
|---|------|---------------|--------|----------|-------------|

### 최종 리포트
#### 확정된 발견사항 (안정 카운터 >= {Tier별 임계값})
| # | 심각도 | 내용 | 판정 라벨 | 검증 관점 | 안정 카운터 | 확정 iteration |

#### 취소된 발견사항 (재검증으로 부정됨)
| # | 내용 | 취소 사유 | 취소 관점 | iteration |

#### Orchestration 기록
| 관점 | 역할 | 사용 Agent/Skill | 담당 항목 |

## 완료 기준
- [ ] 모든 발견사항의 안정 카운터 >= {Tier별 임계값: Tier 1-2는 2, Tier 3는 3}
- [ ] 새로운 발견 0건
- [ ] CONTESTED 항목 0건

## 하지 말 것
- 검증 대상 문서를 수정하지 마
- 추측으로 수렴했다고 판단하지 마 — 실제 비교 근거 필요
- subagent를 background로 실행하지 마
- 수렴하지 않았는데 COMPLETE를 출력하지 마
```

---

## Phase 4: 사용자 동의 및 수렴 루프 실행

1. 플랜 요약 제시 (검증 대상, Tier, 관점, Agent, 수렴 기준)
2. AskUserQuestion 도구로 동의 여부 질문:
   "위 플랜으로 수렴 검증을 시작하시겠습니까?
    1) 시작
    2) 플랜 수정 (피드백 입력)"
3. 선택에 따른 분기:
   - 1) 선택 → Phase 5 (수렴 루프 실행)로 진행
   - 2) 선택 → 피드백 반영하여 Phase 2로 돌아가 플랜 수정 후 다시 Phase 4

---

## Phase 5: 수렴 루프 실행

plan.md를 읽고 수렴 검증을 직접 실행합니다.

매 iteration:

```
report.md 읽기 → plan.md 읽기
    ↓
검증 Agent 실행 (Tier별 관점 수, foreground subagent)
  + CONTESTED 항목 있으면 제3 관점 agent 추가 투입
    ↓
EVALUATOR 실행 (foreground subagent): 모든 Agent 출력 종합 → 판정 라벨 부여
    ↓
Main agent가 안정 카운터 업데이트 (EVALUATOR 판정 기준):
  - 동일 판정 → +1
  - 다른 판정 → 0
  - 신규 → 0 (영향받는 기존 항목도 리셋)
  - CONTESTED → 다음 iteration에서 제3 관점 투입
  - 소멸 → "취소 후보", 0
    ↓
report.md 갱신
    ↓
모든 항목 안정 >= {Tier별: 2 또는 3} + CONTESTED 0건 → COMPLETE
```

**안정 카운터 예시:**
```
항목 A: Turn1=발견, Turn2=EVALUATOR확인(안정1), Turn3=새발견C로 재검토(안정0), Turn4=EVALUATOR재확인(안정1), Turn5=EVALUATOR확인(안정2) OK
항목 B: Turn1=발견, Turn2=EVALUATOR확인(안정1), Turn3=EVALUATOR확인(안정2) OK
항목 C: Turn3=신규(안정0), Turn4=EVALUATOR확인(안정1), Turn5=EVALUATOR확인(안정2) OK
→ Turn5에서 모든 항목 안정>=2 → COMPLETE (Tier 1-2 기준)
```

수렴 조건 충족 시 최종 리포트 작성 후 종료.

---

## 커버하는 작업 유형

| 유형 | 예시 | 수렴 기준 |
|------|------|----------|
| 플랜 검증 | 이행 계획서 Fact-Check | 파일/라인/설명 오류 0건 |
| 코드 리뷰 | PR 변경사항 검토 | 발견사항 불일치 0건 |
| 아이디어 검증 | 아키텍처 설계 타당성 | 반론/우려 해소 |
| 리서치 | 기술 조사, 대안 분석 | 새로운 발견 0건 |
| 문서 검증 | API 문서, README 정확성 | 오류 0건 |

---

## 절대 규칙

1. 외부 스킬이나 플러그인 코드를 수정하지 않는다
2. 검증 대상 코드/문서를 수정하지 않는다
3. 수렴하지 않았는데 종료하지 않는다
4. 추측으로 "수렴했다"고 판단하지 않는다 — 실제 비교 근거 필요
5. 사용자 동의 없이 수렴 루프를 시작하지 않는다
