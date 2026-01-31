---
name: job-analysis
description: 이직 분석 4단계 프로토콜. 기업 심층 조사 → 직무 분석 → 이력서 매칭 → 최종 평가 리포트 생성.
allowed-tools: WebSearch, WebFetch, Read, Grep, Glob, Write
user-invocable: true
argument-hint: "<company_name> <job_description_url_or_text>"
---

# 🔍 Job Analysis Skill

## Overview

이직 준비를 위한 **4단계 직무 분석 프로토콜**입니다. 기업 심층 조사, 직무 역할 분석, 이력서 매칭, 최종 평가를 체계적으로 수행하여 근거 기반의 이직 의사결정을 지원합니다.

```
┌───────────────────────────────────────────────────────────────────┐
│                  Job Analysis Protocol (4-Phase)                   │
├───────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 0: 📋 입력 수집 + 분석 ID 생성                              │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  $ARGUMENTS 파싱 → 이력서 자동 감지 → career/ 준비     │       │
│  └───────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│  Phase 1: 🏢 기업 심층 조사 (Company Deep Research)                │
│  ┌───────────────────────▼─────────────────────────────────┐       │
│  │  광역 탐색 → 심화 탐색 (재무/레드플래그) → 지식 합성    │       │
│  │  ⚡ deep-research 3단계 프로토콜 적용                    │       │
│  └───────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│  Phase 2: 💼 직무 역할 분석 (Job Role Analysis)                    │
│  ┌───────────────────────▼─────────────────────────────────┐       │
│  │  JD 구조 분해 → 역할 인사이트 → 기술 스택 → 채용 프로세스│      │
│  └───────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│  Phase 3: 📊 이력서 매칭 분석 (Resume Matching)                    │
│  ┌───────────────────────▼─────────────────────────────────┐       │
│  │  6차원 분해 → 매칭률 산출 → 강점/약점/성장 기회          │       │
│  └───────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│  Phase 4: 🎯 최종 평가 (Final Assessment)                          │
│  ┌───────────────────────▼─────────────────────────────────┐       │
│  │  종합 판정 → Radar Chart → 전략적 권고 → 면접 예측      │       │
│  │  → career/{company}-{role}-analysis.md 저장               │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
└───────────────────────────────────────────────────────────────────┘
```

**⚠️ 필수 도구**: `mcp__sequential-thinking__sequentialthinking` — 모든 Phase에서 사용
**📖 참조 스킬**: `deep-research` — Phase 1에서 3단계 프로토콜 적용

---

## Input Specification

사용자 인자: `$ARGUMENTS`

| 항목 | 필수 | 설명 |
|------|------|------|
| **company_info** | ✅ | 기업명 + 웹사이트 또는 간략 설명 |
| **job_description** | ✅ | JD 텍스트 또는 URL |
| **resume** | ✅ (자동 감지) | 이력서 파일 경로 또는 직접 입력 |

### 이력서 자동 감지

다음 경로를 순서대로 탐색 (Glob 사용):

1. `resume.md`, `RESUME.md`
2. `career/resume.md`, `career/RESUME.md`
3. `**/resume.md`, `**/RESUME.md`

감지 실패 시 → 사용자에게 이력서 경로 또는 내용 입력 요청

---

## Sequential Thinking 사용 규칙

모든 Phase에서 `mcp__sequential-thinking__sequentialthinking`을 **반드시** 사용합니다:

1. **Phase 시작**: 분석 계획 수립 (목표, 수집할 정보, 판단 기준)
2. **핵심 판단**: 매칭률 산출, 등급 판정, 가중치 결정 시
3. **Phase 완료**: 결과 검증 + 다음 Phase 전환 판단
4. **사고 패턴**: 가설 → 근거 수집 → 검증 → 수정 (필요 시)

---

## Execution Protocol

### Phase 0: 📋 입력 수집 및 분석 ID 생성

1. **sequentialthinking**으로 `$ARGUMENTS` 파싱 및 분석 전략 수립
2. 분석 ID 생성: `{company-slug}-{role-slug}-{YYYY-MM-DD}`
   - slug 규칙: 영문소문자 + 하이픈, 한글 → 영문 표기
   - role-slug: 직무명을 영문소문자 + 하이픈으로 변환 (예: CTO → cto, Backend Lead → backend-lead)
3. 이력서 자동 감지 (Glob으로 파일 탐색)
4. `career/` 디렉토리 존재 확인 (없으면 생성)
5. JD가 URL인 경우 → WebFetch로 내용 수집

---

### Phase 1: 🏢 기업 심층 조사 (Company Deep Research)

> ⚡ `deep-research` 스킬의 3단계 프로토콜을 적용합니다.

#### Step 1-1: 광역 탐색 (Broad Exploration)

**sequentialthinking**으로 검색 쿼리 분해 후:

- **WebSearch 3-5회** (기업 기본정보, 뉴스, 업계 평판)
- **WebSearch 1-2회** (SNS: `site:reddit.com`, `site:twitter.com` 등)
- 수집 항목:
  - 🏢 사업 내용 (What): 제품/서비스, 타깃 시장
  - ⚙️ 기술/비즈니스 모델 (How): 기술 스택, 수익 모델
  - 🎯 미션/비전 (Why): 핵심 가치, 문화
  - 📊 규모, 설립일, 위치, 핵심 인력

#### Step 1-2: 심화 탐색 (Deep Dive)

**a) 💰 재무 안전성 평가** (WebSearch 1-2회 + WebFetch)

- 투자 이력, 매출 모델, 런웨이
- 재무 안전성 등급:

| 등급 | 의미 | 기준 |
|------|------|------|
| 🟢 A (안전) | 안정적 | 흑자/대규모 투자/상장 |
| 🟡 B (보통) | 양호 | 시리즈B+ 또는 안정적 매출 |
| 🟠 C (주의) | 주의 필요 | 초기 투자/매출 불분명 |
| 🔴 D (위험) | 리스크 높음 | 자금난/구조조정/소송 다수 |

**b) 🚩 레드플래그 조사** (WebSearch 1-2회)

- 소송, 논란, 높은 퇴사율, 문화 이슈
- Glassdoor/블라인드 등 직원 리뷰

**c) 교차 검증 (Cross-Validation)**

- 2개 이상 출처에서 일치 확인
- 모순 발견 시 → 출처 권위성 + 발행 시점으로 판단

#### Step 1-3: 지식 합성 (Knowledge Synthesis)

**sequentialthinking**으로 전체 정보 통합:

- 신뢰도 태그 부여: `[✅ Confirmed]`, `[🔶 Likely]`, `[❓ Uncertain]`
- 기업 프로필 카드 생성

---

### Phase 2: 💼 직무 역할 분석 (Job Role Analysis)

#### Step 2-1: JD 구조 분해

**sequentialthinking**으로 JD 체계적 파싱:

- 핵심 책임 추출 (R1, R2, R3...) + 가중치:
  - 🔴 HIGH: 핵심 역할, 반드시 수행
  - 🟡 MEDIUM: 중요하지만 부차적
  - 🟢 LOW: 있으면 좋은 수준
- 필수 스킬 vs 우대 스킬 분류
- 기술 스택 추출 (언어, 프레임워크, 인프라, 도구)

#### Step 2-2: 역할 인사이트 분석

- 실제 업무 내용 추론 (JD 행간 읽기)
- 성장 경로 (이 역할 → 다음 단계)
- 시장 수요 (해당 역할의 수요/공급)

#### Step 2-3: 기술 스택 심화 (Optional)

- 생소한 기술 → WebSearch로 시장 채택도, 학습 곡선 조사

#### Step 2-4: 채용 프로세스 조사 (WebSearch 1-2회)

- `"{company} interview process engineer"` 검색
- `"{company} 면접 후기 채용 과정"` 검색
- 면접 단계 구조 파악 (서류 → 코딩테스트 → 면접 등)

---

### Phase 3: 📊 이력서 매칭 분석 (Resume Matching)

#### Step 3-1: 이력서 차원 분해

**sequentialthinking**으로 이력서를 6개 차원으로 구조화:

| # | 차원 | 설명 |
|---|------|------|
| D1 | 🛠️ 기술 스택 | 프로그래밍 언어, 프레임워크, 도구 일치도 |
| D2 | 🏥 도메인 경험 | 산업/도메인 경험 관련성 |
| D3 | 👥 리더십 | 팀 리딩, 프로젝트 관리, 멘토링 경험 |
| D4 | 🤝 문화 적합 | 회사 문화/가치관과의 부합도 |
| D5 | 🌱 성장 가능성 | 학습 능력, 적응력, 잠재력 |
| D6 | 🎓 교육/자격 | 학력, 자격증, 교육 이수 |

#### Step 3-2: 차원별 매칭률 산출

**sequentialthinking**으로 각 차원 점수 산출 + 근거 명시:

```
D1 기술 스택     ████████░░  78%  🟡
D2 도메인 경험   ██████████  95%  🟢
D3 리더십        ██████░░░░  58%  🟠
D4 문화 적합     ████████░░  82%  🟢
D5 성장 가능성   █████████░  88%  🟢
D6 교육/자격     ███████░░░  70%  🟡
```

범위별 이모지: 🟢 ≥80% / 🟡 60-79% / 🟠 40-59% / 🔴 <40%

#### Step 3-3: 💪 강점 분석

각 강점에 대해:
- 경쟁 우위 포인트
- 면접 활용법 (구체적 스토리텔링 예시)
- 근거 (이력서의 어느 부분?)

#### Step 3-4: 📉 약점 분석 + 보완 전략

각 약점에 대해:
- 갭 심각도: 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW
- 단기 준비 (1-2주): 즉시 할 수 있는 것
- 중기 준비 (1-3개월): 체계적 학습
- 면접 설명 전략: 약점을 성장 기회로 프레이밍하는 스토리텔링 공식

#### Step 3-5: 🌱 성장 기회 분석

- 이 역할에서 얻을 수 있는 기술/경험
- 커리어 성장에 미치는 영향
- 장기적 가치 (2-3년 후 시나리오)

---

### Phase 4: 🎯 최종 평가 (Final Assessment)

#### Step 4-1: 종합 판정

**sequentialthinking**으로 Phase 1-3 통합 판단:

- 종합 매칭률 (%) 산출
- 판정 기준:

| 판정 | 범위 | 의미 |
|------|------|------|
| 🌟 STRONG_MATCH | ≥80% | 매우 적합, 적극 지원 권장 |
| ✅ GOOD_MATCH | 65-79% | 적합, 준비 후 지원 권장 |
| 🔶 MODERATE_MATCH | 50-64% | 보통, 전략적 판단 필요 |
| ⚠️ WEAK_MATCH | 35-49% | 약한 적합, 상당한 준비 필요 |
| 🚫 NOT_RECOMMENDED | <35% | 비추천, 다른 포지션 탐색 권장 |

#### Step 4-2: 📊 Radar Chart 시각화

6축 Radar Chart (ASCII) + Bar 스타일 병행:

```
        기술 스택 (78%)
            ╱╲
           ╱  ╲
  교육/   ╱    ╲  도메인
  자격   ╱  ▓▓  ╲  경험
  (70%) ╱  ▓▓▓▓  ╲ (95%)
        ╲  ▓▓▓▓  ╱
  성장   ╲  ▓▓  ╱  리더십
  가능성  ╲    ╱   (58%)
  (88%)   ╲  ╱
        문화 적합
          (82%)
```

#### Step 4-3: 전략적 권고

- 🎯 면접 준비 포인트 5개+
- ❓ 회사에 물어볼 질문 3개+
- 💰 연봉 협상 포인트

#### Step 4-4: 🎯 예상 과제 & 면접 질문

**sequentialthinking**으로 JD + 기업 분석 결과 기반 예측:

**a) 📝 채용 전형별 예상 과제 유형**

- Take-home assignment 예상 문제 (기업 기술 스택 + JD 키워드 기반)
- 코딩 테스트 예상 범위 (알고리즘/시스템 설계)
- 시스템 설계 문제 예상

**b) 🔧 기술 면접 예상 질문 (10개+)**

- JD 핵심 역량별 예상 질문
- 이력서 기반 예상 꼬리 질문
- 기업 도메인 관련 질문

**c) 🤝 컬처핏 면접 예상 질문 (5개+)**

- 기업 문화/가치관 기반 질문
- 동기 부여/커리어 방향성 질문

**d) 💡 답변 전략 가이드**

- 각 질문에 대한 STAR 프레임워크 적용 힌트
  - **S**ituation → **T**ask → **A**ction → **R**esult
- 약점 질문 대응 전략

#### Step 4-5: 📌 Executive Summary (종합 판정 요약)

분석 파일의 **마지막 섹션**으로 Executive Summary를 생성합니다.
콘솔 출력과 동일한 내용을 파일에 포함하여, 파일만으로도 핵심 결론을 즉시 파악할 수 있도록 합니다.

필수 포함 요소:
- Verdict Box (판정 등급 + 종합 매칭률 + 한 줄 판정문)
- 차원별 매칭률 Bar Chart (6개 차원)
- 핵심 요약 테이블: 최대 강점 / 최대 리스크 / 기업 재무 / 레드플래그 / 핵심 전략
- 한 문단 종합 코멘트 (포지션 본질 + 차별화 포인트 + 합격 핵심 변수)

```markdown
---

## 📌 Executive Summary

{verdict box}

### 차원별 매칭률
{bar charts per dimension}

### 핵심 요약

| | 내용 |
|---|---|
| **최대 강점** | {top strength} |
| **최대 리스크** | {top risk} |
| **기업 재무** | {financial grade + one-liner} |
| **레드플래그** | {red flag summary} |
| **핵심 전략** | {key preparation strategy} |

{one paragraph overall comment}
```

#### Step 4-6: 💾 결과 저장

- 파일 경로: `career/{company-slug}-{role-slug}-analysis.md`
- Write 도구로 전체 분석 결과 저장 (Executive Summary 포함)
- 콘솔 출력 시에도 Executive Summary 섹션을 그대로 출력

---

## Output Template

생성되는 분석 파일의 구조:

```markdown
# 🔍 Job Analysis: {Company Name} — {Position}

> 📅 분석일: {date} | 🆔 분석 ID: {analysis-id}
> 🎯 종합 판정: {verdict_emoji} {verdict} ({overall_match}%)

---

## 📋 분석 개요

| 항목 | 내용 |
|------|------|
| 🏢 기업 | {company_name} |
| 💼 포지션 | {position} |
| 📍 위치 | {location} |
| 📊 종합 매칭률 | {overall_match}% |

---

## Phase 1: 🏢 기업 프로필

### 기업 기본 정보
{company profile card}

### 💰 재무 안전성: {financial_grade}
{financial assessment}

### 🚩 레드플래그 체크
{red flags or "특이사항 없음"}

### 🔍 출처 신뢰도
{confidence tags per finding}

---

## Phase 2: 💼 직무 분석

### 핵심 책임
{responsibilities with weights}

### 🛠️ 기술 스택
| 구분 | 기술 |
|------|------|
| 필수 | {required} |
| 우대 | {preferred} |

### 📋 채용 프로세스
{interview process if found}

---

## Phase 3: 📊 매칭 분석

### 차원별 매칭률
{bar charts per dimension}

### 💪 강점
{strengths with interview leverage}

### 📉 약점 + 보완 전략
{weaknesses with mitigation plans}

### 🌱 성장 기회
{growth opportunities}

---

## Phase 4: 🎯 최종 평가

### 종합 판정
{verdict box}

### 📊 Radar Chart
{ASCII radar chart}

### 🎯 면접 준비 포인트
{interview prep points}

### ❓ 회사에 물어볼 질문
{questions to ask}

### 💰 연봉 협상 포인트
{negotiation points}

### 📝 예상 과제
{expected assignments}

### 🔧 기술 면접 예상 질문
{technical questions with STAR hints}

### 🤝 컬처핏 예상 질문
{culture fit questions}

### 💡 답변 전략 가이드
{answer strategy guide}

---

## 📚 Sources
{numbered source list with URLs}

---

## 📌 Executive Summary

{verdict box}

### 차원별 매칭률
{bar charts per dimension}

### 핵심 요약

| | 내용 |
|---|---|
| **최대 강점** | {top strength} |
| **최대 리스크** | {top risk} |
| **기업 재무** | {financial grade + one-liner} |
| **레드플래그** | {red flag summary} |
| **핵심 전략** | {key preparation strategy} |

{one paragraph overall comment}
```

---

## Visualization Templates

### 1. 📊 Bar Chart

```
기술 스택     ████████░░  78%  🟡
도메인 경험   ██████████  95%  🟢
리더십        ██████░░░░  58%  🟠
```

블록 매핑: 1블록 = 10%, `█` = 채움, `░` = 빈칸
이모지: 🟢 ≥80% / 🟡 60-79% / 🟠 40-59% / 🔴 <40%

### 2. 🏆 Verdict Box

```
┌─────────────────────────────────────────┐
│  🌟 STRONG MATCH — 종합 매칭률 84%      │
│                                          │
│  "해당 포지션에 높은 적합도를 보이며,    │
│   적극적인 지원을 권장합니다."           │
└─────────────────────────────────────────┘
```

### 3. 📋 Comparison Matrix

```
| 요구사항 | JD 요구 | 내 수준 | 갭 |
|----------|---------|---------|-----|
| Python   | 🔴 필수 | ⭐⭐⭐  | ✅  |
| K8s      | 🟡 우대 | ⭐      | 🟡  |
```

### 4. 📅 준비 Timeline

```
[1주차] ──── 기술 스택 갭 학습 시작
[2주차] ──── 포트폴리오 정리 + 자기소개서
[3-4주차] ── 모의 면접 + 코딩 테스트 준비
```

### 5. 🎯 Interview Q&A Card

```
┌─ Q: "대규모 트래픽 처리 경험이 있나요?"
│
│  📌 STAR 힌트:
│  S: {프로젝트 배경}
│  T: {담당 과제}
│  A: {구체적 행동}
│  R: {정량적 결과}
│
└─ 💡 키포인트: 수치로 증명, 의사결정 과정 강조
```

---

## Quality Checklist

분석 완료 전 반드시 확인:

- [ ] 모든 Phase에서 sequentialthinking 사용 완료
- [ ] Phase 1에서 deep-research 프로토콜 적용 (광역→심화→합성)
- [ ] 출처 최소 3개 교차 검증
- [ ] 모든 약점에 보완 전략 포함
- [ ] Radar + Bar chart 시각화 포함
- [ ] 이모지가 섹션 헤더 및 판정 결과에 사용됨
- [ ] 예상 과제 유형 + 면접 질문 10개+ 포함
- [ ] `career/{company}-{role}-analysis.md` 파일 저장 완료
- [ ] Sources 섹션에 모든 참조 URL 기록
- [ ] Executive Summary 섹션이 파일 마지막에 포함됨 (콘솔 출력과 동일)

---

## Output File Convention

- **경로**: `career/{company-slug}-{role-slug}-analysis.md`
- **slug 규칙**: 영문소문자 + 하이픈, 한글 → 영문 표기
- **role-slug**: 직무명을 영문소문자 + 하이픈으로 변환
- **예시**:
  - 카카오 CTO → `career/kakao-cto-analysis.md`
  - PhynxLab Backend Lead → `career/phynxlab-backend-lead-analysis.md`
  - 네이버 클라우드 SRE Engineer → `career/naver-cloud-sre-engineer-analysis.md`
