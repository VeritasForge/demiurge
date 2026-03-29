---
name: group-job-analysis
description: 그룹사/계열사 다수 JD 일괄 분석 프로토콜. JD 수집 → 공유 기업조사 → 스크리닝 → 풀분석 → 비교분석 → 최종 추천.
allowed-tools: WebSearch, WebFetch, Read, Grep, Glob, Write, AskUserQuestion, mcp__sequential-thinking__sequentialthinking
user-invocable: true
argument-hint: "<group_name> <jd_list_or_urls> [--top N] [--resume path]"
---

# 🏢 Group Job Analysis Skill

## Overview

**그룹사/계열사 다수 JD를 일괄 분석**하여 최적 N개 법인을 추천하는 7단계 퍼널 프로토콜입니다.

개별 `job-analysis`를 N번 반복하는 것 대비 **65%+ WebSearch 절감** + **비교 의사결정 프레임워크** 제공.

```
┌───────────────────────────────────────────────────────────────────┐
│            Group Job Analysis Protocol (7-Phase Funnel)            │
├───────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 0: 📋 입력 수집 + Group ID 생성                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  인자 파싱 → 이력서 감지 → career/{group-slug}/ 준비    │       │
│  └───────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│  Phase 1: 📥 JD 일괄 수집 (Batch Fetch)                           │
│  ┌───────────────────────▼─────────────────────────────────┐       │
│  │  N개 URL WebFetch → jd-raw/ 저장 → 요약 인덱스 생성     │       │
│  └───────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│  Phase 2: 🏢 공유 기업 조사 (Shared Research)                      │
│  ┌───────────────────────▼─────────────────────────────────┐       │
│  │  그룹 공통 + 법인별 델타 → company-research.md           │       │
│  │  ⚡ deep-research 프로토콜 적용                           │       │
│  └───────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│  Phase 3: 🔍 Quick Screening (전체 → Tier A/B/C)                  │
│  ┌───────────────────────▼─────────────────────────────────┐       │
│  │  5차원 점수화 → Tier 분류 → screening-matrix.md          │       │
│  └───────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│  Phase 4: 📊 Full Analysis (Tier A만)                              │
│  ┌───────────────────────▼─────────────────────────────────┐       │
│  │  job-analysis Phase 2-4 인라인 실행 (Phase 1 스킵)       │       │
│  │  → {slug}-analysis.md 개별 저장                          │       │
│  └───────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│  Phase 5: ⚖️ 비교 분석 (Comparative)                               │
│  ┌───────────────────────▼─────────────────────────────────┐       │
│  │  법인 레벨 비교 → Top N 추천 → comparative-analysis.md   │       │
│  └───────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│  Phase 6: 🤝 사용자 의사결정 (Interactive)                         │
│  ┌───────────────────────▼─────────────────────────────────┐       │
│  │  추천 논의 → 조정 → 최종 확정 → 파일 업데이트            │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
└───────────────────────────────────────────────────────────────────┘
```

**⚠️ 필수 도구**: `mcp__sequential-thinking__sequentialthinking` — 모든 Phase에서 사용
**📖 참조 프로토콜**: `job-analysis` Phase 2-4 — Phase 4에서 인라인 실행
**📖 참조 프로토콜**: `deep-research` — Phase 2에서 3단계 프로토콜 적용

---

## Input Specification

사용자 인자: `$ARGUMENTS`

| 항목 | 필수 | 설명 | 예시 |
|------|------|------|------|
| **group_name** | ✅ | 그룹사명 | "토스 그룹", "카카오 그룹" |
| **jd_list** | ✅ | JD 목록 (아래 3가지 형식 중 택1) | URL 나열, 파일 경로, 대화 내 입력 |
| **--top N** | ❌ (기본: 2) | 추천할 법인 수 | `--top 3` |
| **--resume** | ❌ (자동 감지) | 이력서 경로 | `--resume ~/resume.md` |

### JD 목록 입력 형식

**형식 1: 인라인 URL 목록** (대화 내 직접 입력)
```
- 토스 Product: https://toss.im/career/...
- 토스 Platform: https://toss.im/career/...
- 토스페이먼츠 3년이상: https://toss.im/career/...
```

**형식 2: 파일 경로**
```
/path/to/jd-list.md  (법인명, 포지션명, URL이 포함된 파일)
```

**형식 3: 사용자 대화에서 추출**
사용자가 대화 중 법인/포지션/URL을 언급하면 파싱

### 이력서 자동 감지

`job-analysis`와 동일 로직:
1. `resume.md`, `RESUME.md`
2. `career/resume.md`, `career/RESUME.md`
3. `**/resume.md`, `**/RESUME.md`

감지 실패 시 → `AskUserQuestion`으로 경로 요청

### 스크리닝 설정 (Optional)

| 항목 | 기본값 | 설명 |
|------|--------|------|
| **screening_weights** | 기술25/도메인20/시니어리티20/성장20/문화15 | 5차원 가중치 |
| **tier_a_threshold** | 3.5 | Tier A 최소 점수 |
| **tier_b_threshold** | 2.5 | Tier B 최소 점수 |

사용자가 별도 지정하지 않으면 기본값 사용. `AskUserQuestion`으로 "기본 가중치를 사용할까요?"  확인 가능.

---

## Sequential Thinking 사용 규칙

모든 Phase에서 `mcp__sequential-thinking__sequentialthinking`을 **반드시** 사용:

1. **Phase 시작**: 분석 계획 수립 (목표, 수집할 정보, 판단 기준)
2. **스크리닝 점수 산출**: 각 포지션별 5차원 점수화
3. **법인 레벨 비교**: 가중합산 + 순위 판단
4. **Phase 완료**: 결과 검증 + 다음 Phase 전환 판단

---

## Execution Protocol

### Phase 0: 📋 입력 수집 + Group ID 생성

1. **sequentialthinking**으로 `$ARGUMENTS` 파싱 및 전략 수립
2. Group ID 생성: `{group-slug}-{YYYY-MM-DD}`
   - slug 규칙: 영문소문자 + 하이픈 (예: toss-group, kakao-group)
3. 이력서 자동 감지 (Glob)
4. `career/{group-slug}/` 디렉토리 생성 (없으면)
5. `career/{group-slug}/jd-raw/` 하위 디렉토리 생성
6. JD 목록 파싱 → (법인, 포지션, URL) 튜플 리스트 구성
7. 스크리닝 가중치 확인 (사용자 지정 또는 기본값)

**Exit Criteria**: Group ID 생성, 디렉토리 존재, JD 리스트 파싱 완료, 이력서 위치 확인

---

### Phase 1: 📥 JD 일괄 수집 (Batch Fetch)

1. **sequentialthinking**으로 수집 전략 (URL 그룹핑, 실패 대비)
2. 각 URL에 대해 `WebFetch`로 JD 수집
   - 실패 시 → Playwright MCP (`browser_navigate` + `browser_snapshot`)로 대체
3. 수집된 JD를 구조화하여 파일 저장

**jd-raw 파일 템플릿**:
```markdown
# {Position} — {Subsidiary}

> URL: {url}

## 회사명
## 포지션명
## 팀소개
## 주요 업무
## 자격 요건 (필수)
## 우대 사항
## 기술 스택
## 채용 프로세스
## 기타
```

4. **JD 요약 인덱스** 생성 (컨텍스트 내 유지용, JD당 ~50토큰):

```
| # | 법인 | 포지션 | 핵심 기술 | 핵심 요건 |
|---|------|--------|-----------|-----------|
| 1 | 토스 | Platform | Kotlin/Spring/K8s | Gateway, 분산락 |
```

5. 파일 저장: `career/{group-slug}/jd-raw/{subsidiary-slug}-{position-slug}.md`

**컨텍스트 관리**: JD 전문은 파일에만 보관. 요약 인덱스만 컨텍스트에 유지.

**Exit Criteria**: 모든 JD 파일 저장 완료, 요약 인덱스 생성

---

### Phase 2: 🏢 공유 기업 조사 (Shared Company Research)

> ⚡ `deep-research` 스킬의 3단계 프로토콜을 적용합니다.

#### Part A: 그룹 공통 조사

**sequentialthinking**으로 검색 쿼리 분해 후:

**Step 2-A1: 광역 탐색** (WebSearch 5-7회)
- 그룹 기업 개요 (설립, 대표, 본사, 사업 구조)
- 기업가치, 투자/IPO 현황
- 뉴스, 업계 평판

**Step 2-A2: 심화 탐색** (WebSearch 3-5회)
- 💰 재무 안전성 (매출, 영업이익, 흑자/적자, 런웨이)
- 🛠️ 공통 기술 스택 및 엔지니어링 문화 (기술 블로그, 컨퍼런스)
- 🎤 면접 프로세스 (공통 구조, 문화적합성 면접 특징)
- 💵 보상 구조 (연봉 밴드, 스톡옵션/RSU, 복리후생)
- 🚩 레드플래그 (워라밸, 퇴사율, 소송, 블라인드/잡플래닛)

**Step 2-A3: 지식 합성**
- 신뢰도 태그: `[✅ Confirmed]`, `[🔶 Likely]`, `[❓ Uncertain]`
- 재무 안전성 등급: 🟢A / 🟡B / 🟠C / 🔴D

#### Part B: 법인별 델타 조사

각 법인에 대해 (WebSearch 1-2회씩):
- 도메인/제품 포커스
- 직원수, 매출 (법인 단독)
- 규제 환경 특성
- 법인 고유 레드플래그 또는 장점
- 면접 프로세스 변형 (사전과제, 라이브코딩 등)

**파일 저장**: `career/{group-slug}/company-research.md`

**WebSearch 추정**: 그룹 공통 8-12회 + 법인당 1-2회 = 5개 법인 시 ~18-22회
(vs. 개별 job-analysis 5회 = ~50+회, **55-65% 절감**)

**Exit Criteria**: company-research.md 저장, Part A + 모든 법인 Part B 포함, 신뢰도 태그 부여

---

### Phase 3: 🔍 Quick Screening

**sequentialthinking**으로 이력서 핵심 역량 대비 각 포지션 점수화.

#### Step 3-1: 스크리닝 차원 확정

| 차원 | 기본 가중치 | 평가 내용 |
|------|------------|-----------|
| D1: 기술 스택 적합도 | 25% | JD 요구 기술 ↔ 이력서 기술 직접 중첩 |
| D2: 도메인 근접도 | 20% | 이력서 도메인 경험과의 유사성 |
| D3: 시니어리티 매칭 | 20% | 연차에 맞는 역할 범위 (IC vs Lead) |
| D4: 성장 잠재력 | 20% | 커리어 성장 기회, 임팩트 범위 |
| D5: 문화/실용 | 15% | 근무 환경, 팀 규모, 문화 신호 |

#### Step 3-2: 포지션별 점수 산출

각 포지션에 대해 5차원 × 1-5점 → 가중합산:
- JD 요약 인덱스 + company-research.md 참조
- 이력서 핵심 역량과 매칭하여 근거 기반 점수

#### Step 3-3: Tier 분류

| Tier | 점수 범위 | 행동 |
|------|----------|------|
| **A** | ≥ {tier_a_threshold} | Full Analysis 대상 |
| **B** | ≥ {tier_b_threshold} | 예비, 시간 여유 시 분석 |
| **C** | < {tier_b_threshold} | 제외 |

#### Step 3-4: Full Analysis 대상 선정

- Tier A 중 **법인별 최고 점수 포지션**을 선정
- 법인별 최소 1개 포지션 포함 (전 법인 비교 보장)
- Tier A가 과다 시 (8개+) → 법인별 대표 1개로 축소

**파일 저장**: `career/{group-slug}/screening-matrix.md`

**Exit Criteria**: 전 포지션 점수 산출, Tier 분류, Full Analysis 대상 확정, 파일 저장

---

### Phase 4: 📊 Full Analysis (Tier A 포지션)

> 📖 **참조 프로토콜**: `job-analysis` SKILL.md Phase 2-4 — 동일 프로토콜을 인라인으로 실행

각 Tier A 포지션에 대해 **순차적으로** 실행:

#### Step 4-1: Phase 1 대체 (Company Research 참조)

- `career/{group-slug}/company-research.md`에서 해당 법인 프로필 추출
- 분석 파일의 Phase 1 섹션으로 삽입
- 헤더: `> 상세: career/{group-slug}/company-research.md 참조`

#### Step 4-2: job-analysis Phase 2 (직무 분석) 실행

- JD 구조 분해 (핵심 책임 + 가중치)
- 역할 인사이트 분석
- 기술 스택 심화
- 채용 프로세스 조사

#### Step 4-3: job-analysis Phase 3 (이력서 매칭) 실행

- 6차원 분해 (D1~D6)
- 차원별 매칭률 산출 + Bar Chart
- 강점/약점/성장기회 분석

#### Step 4-4: job-analysis Phase 4 (최종 평가) 실행

- 종합 판정 (STRONG/GOOD/MODERATE/WEAK/NOT_RECOMMENDED)
- Radar Chart
- 면접 준비 포인트, 예상 질문
- Executive Summary

#### Step 4-5: 파일 저장

- 경로: `career/{subsidiary-slug}-{position-slug}-analysis.md`
- career/ 루트에 저장 (group-slug 하위가 아님 — 기존 job-analysis 컨벤션 유지)

#### 컨텍스트 관리

- **L1 요약만 유지**: 풀 분석 저장 후 컨텍스트에는 L1만 남김:
  ```
  {법인} {포지션}: {판정} {매칭률}% | 강점: {top} | 리스크: {top}
  ```
- **Compact 트리거**: 풀 분석 **2개 완료마다** 컨텍스트 정리
- **순차 실행**: 병렬 금지 (컨텍스트 공유 + ralph-loop 제약)

**Exit Criteria**: 모든 Tier A 포지션의 분석 파일 저장, L1 요약 수집

---

### Phase 5: ⚖️ 비교 분석 (Comparative Analysis)

**sequentialthinking**으로 법인 레벨 종합 판단.

#### Step 5-1: 법인별 대표 포지션 확정

각 법인에서 가장 높은 매칭률의 포지션을 대표로 선정.

#### Step 5-2: 법인 비교 매트릭스 작성

```markdown
| | {법인1} | {법인2} | {법인3} | ... |
|---|:---:|:---:|:---:|:---:|
| **대표 포지션** | ... | ... | ... | |
| **매칭률** | XX% | XX% | XX% | |
| **재무 등급** | 🟢A | 🟡B | ... | |
| **매출** | ... | ... | ... | |
| **직원수** | ... | ... | ... | |
| **성장률** | ... | ... | ... | |
| **워라밸 리스크** | 🔴높 | 🟢낮 | ... | |
| **면접 특이점** | ... | ... | ... | |
| **법인 점수** | X.XX | X.XX | X.XX | |
```

#### Step 5-3: 법인 점수 산출

| 기준 | 가중치 | 설명 |
|------|--------|------|
| 최고 포지션 매칭률 | 30% | 대표 포지션의 종합 매칭률 |
| 재무 건전성 | 15% | company-research의 재무 등급 |
| 도메인 성장 잠재력 | 20% | 법인 도메인의 시장 궤적 |
| 커리어 성장 경로 | 20% | 역할 범위, 리더십 기회, 다음 단계 |
| 레드플래그 심각도 | 15% | 역수 점수 (적을수록 높은 점수) |

#### Step 5-4: Top N 추천 생성

각 추천 법인에 대해:
- Verdict Box (판정 + 매칭률)
- 차원별 매칭률 Bar Chart
- 지원 전략 (강조할 강점 Top 3)
- 면접 준비 Top 5
- 최대 리스크 + 대응 전략
- 연봉 협상 포인트

#### Step 5-5: 부가 섹션

- 미추천 법인 요약 (법인별 1-2줄 이유)
- 다음 라운드 후보 (Tier B 중 잠재력 있는 법인)
- 준비 Timeline (주차별)
- 두 면접의 차별화 전략 (다른 축으로 어필)

**파일 저장**: `career/{group-slug}-comparative-analysis.md`

**Exit Criteria**: 비교 분석 파일 저장, Top N 추천 + 지원 전략 포함

---

### Phase 6: 🤝 사용자 의사결정 (Interactive)

1. 비교 분석 Executive Summary를 콘솔에 출력
2. 사용자와 추천 결과 논의
   - "이 조합이 괜찮으신가요?" → `AskUserQuestion` 활용
   - 사용자가 다른 선호를 제시하면 → Phase 5 결과를 기반으로 대안 분석
3. 추천 조정이 필요하면:
   - 비교 분석 파일 업데이트 (최종 결론 섹션 수정)
   - 새로운 법인/포지션 추가 분석 필요 시 → Phase 4로 돌아가 추가 실행
4. 사용자 최종 확정 시:
   - 비교 분석 파일에 "사용자 최종 확정" 마크 추가

**Exit Criteria**: 사용자가 최종 선택을 확정, 파일 업데이트 완료

---

## Output File Structure

```
career/
├── {group-slug}/
│   ├── jd-raw/
│   │   ├── {subsidiary-slug}-{position-slug}.md   (N개)
│   │   └── ...
│   ├── company-research.md                         (공유 기업조사)
│   └── screening-matrix.md                         (전체 스크리닝)
├── {subsidiary-slug}-{position-slug}-analysis.md   (Tier A 개별 분석)
├── ...
└── {group-slug}-comparative-analysis.md            (비교 분석 + 추천)
```

---

## Visualization Templates

### 1. 스크리닝 매트릭스

```
| # | 법인 | 포지션 | D1 | D2 | D3 | D4 | D5 | 가중합 | Tier |
|---|------|--------|:--:|:--:|:--:|:--:|:--:|:------:|:----:|
| 1 | 토스페이먼츠 | 3년이상 | 5 | 5 | 4 | 4 | 3 | 4.30 | A ⭐⭐ |
```

### 2. 법인 순위 Bar

```
1위  {법인1}  ████████████████████████░  4.50  ⭐⭐
2위  {법인2}  ████████████████████░░░░░  4.05  ⭐
3위  {법인3}  ████████████████████░░░░░  4.05
```

### 3. Verdict Box

```
┌─────────────────────────────────────────┐
│  🌟 STRONG MATCH — 종합 매칭률 82%      │
│                                          │
│  "{한 줄 판정문}"                        │
└─────────────────────────────────────────┘
```

### 4. 차원별 매칭률 Bar Chart

```
D1 기술 스택     █████████░  92%  🟢
D2 도메인 경험   █████████░  90%  🟢
D3 리더십        ████████░░  75%  🟡
```

블록 매핑: 1블록 = 10%, `█` = 채움, `░` = 빈칸
이모지: 🟢 ≥80% / 🟡 60-79% / 🟠 40-59% / 🔴 <40%

### 5. 비교 최종 결론 테이블

```
| | 1순위: {법인} | 2순위: {법인} |
|---|---|---|
| **포지션** | ... | ... |
| **매칭률** | 🌟 XX% | ✅ XX% |
| **핵심 이유** | ... | ... |
| **어필 축** | 도메인/비즈니스 | 인프라/플랫폼 |
```

---

## Efficiency Comparison

| 항목 | 개별 job-analysis × N | group-job-analysis |
|------|----------------------|-------------------|
| WebSearch (5법인) | ~50+회 | ~20-25회 |
| 기업조사 | 5회 반복 | 1회 (공유+델타) |
| 비교 분석 | 없음 (수동) | 자동 |
| 파일 산출물 | 5개 (독립) | ~20개 (연결된 체계) |
| 의사결정 | 개별 판단 | 퍼널 기반 비교 |

---

## Quality Checklist

분석 완료 전 반드시 확인:

- [ ] Phase 0: group-id 생성, career/{group-slug}/ 디렉토리 존재
- [ ] Phase 1: 모든 JD 수집 + jd-raw/ 저장 완료
- [ ] Phase 1: JD 요약 인덱스 생성 (컨텍스트 내)
- [ ] Phase 2: deep-research 프로토콜 적용 (광역→심화→합성)
- [ ] Phase 2: Part A (그룹 공통) + Part B (법인별 델타) 포함
- [ ] Phase 2: 출처 최소 3개 교차 검증, 신뢰도 태그 부여
- [ ] Phase 2: company-research.md 저장
- [ ] Phase 3: 전 포지션 5차원 점수 산출 + Tier 분류
- [ ] Phase 3: screening-matrix.md 저장
- [ ] Phase 3: 법인별 최소 1개 Tier A 포지션 보장
- [ ] Phase 4: 모든 Tier A 포지션에 sequentialthinking 사용
- [ ] Phase 4: 각 분석에 6차원 매칭률 + Radar/Bar Chart 포함
- [ ] Phase 4: 각 분석에 면접 질문 10개+ 포함
- [ ] Phase 4: 개별 analysis.md 파일 저장
- [ ] Phase 4: 풀분석 2개마다 컨텍스트 관리 (L1만 유지)
- [ ] Phase 5: 법인별 비교 매트릭스 + 법인 점수 산출
- [ ] Phase 5: Top N 추천 + 지원 전략 + 준비 Timeline
- [ ] Phase 5: comparative-analysis.md 저장
- [ ] Phase 6: 사용자 최종 확인
- [ ] Sources: 모든 참조 URL 기록
