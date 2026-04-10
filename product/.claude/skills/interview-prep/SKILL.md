---
name: interview-prep
description: 면접 준비 문제 생성 스킬. 코딩 테스트 + 기술 면접 + 시스템 디자인 + 행동 면접 예상 문제를 조사 기반으로 생성.
allowed-tools: WebSearch, WebFetch, Read, Grep, Glob, Write, Agent, mcp__sequential-thinking__sequentialthinking
user-invocable: true
argument-hint: "<company_name> <JD_URL_or_text> [hints: topic1, topic2, ...]"
---

# Interview Prep Skill

## Overview

특정 회사/포지션의 면접 준비를 위한 **예상 문제 생성 스킬**입니다.
Build-time에 검증된 소스 DB + Runtime 회사 특화 조사를 결합하여, JD 전체 범위를 커버하는 문제를 생성합니다.

```
Phase 0: 입력 파싱 + JD 요구사항 맵 + 이력서 역량 맵
  ↓
Phase 1: 소스별 병렬 조사 (sources/*.md Base + Runtime 발굴)
  ↓
Phase 2: 카테고리별 병렬 문제 생성 (4 에이전트)
  ↓
Phase 3: 통합 출력 → career/{company}-{role}-interview-prep.md
```

---

## Input Specification

**ARGUMENTS**: $ARGUMENTS

| 항목 | 필수 | 설명 |
|------|------|------|
| **company_name** | 필수 | 회사명 (영문) |
| **JD** | 필수 | JD URL 또는 텍스트 |
| **hints** | 선택 | 리크루터 힌트 (예: `hints: Concurrency, Buffer, LinkedList`) |

### 자동 감지

- **이력서**: `resume/*-{company}*-en.md` > `resume/*-en.md` > `resume/*.md` 순서로 Glob 탐색
- **job-analysis**: `career/{company}*analysis.md` 패턴으로 Glob 탐색

---

## 핵심 원칙

### 1. 2-Layer Source 전략
- **Base Sources**: `sources/{category}.md` — Build-time 검증 소스
- **Runtime Sources**: 실행 시 회사 특화 추가 발굴
- **가중치**: Runtime 발견 내용 > Base 발견 내용. Runtime은 "기출 확인" 태그

### 2. 전체 범위 커버
- JD의 모든 요구사항(핵심 책임, 기술스택, 우대사항) 빠짐없이 커버
- 이력서의 모든 관련 경험 매핑
- **임의로 간추리거나 생략 금지**

### 3. 필수/조건부 출력
| 카테고리 | 조건 |
|----------|------|
| **코딩 예상 문제** | 필수 |
| **CS 기본 문제** | 필수 |
| **연습 문제 추천** (URL 포함) | 필수 |
| MCQ 예상 문제 | 조건부 — 조사/힌트에서 확인 시 |
| SQL 문제 | 조건부 — 조사/힌트에서 확인 시 |
| 기타 (Bit ops 등) | 조건부 — 힌트/조사에서 발견 시 |

---

## Execution Protocol

### Phase 0: 입력 파싱 및 컨텍스트 수집

1. `$ARGUMENTS`에서 회사명, JD, 힌트 파싱
2. JD가 URL이면 → WebFetch로 수집
3. `career/{company}*analysis.md` 자동 탐색 → 있으면 로드
4. `resume/` 에서 이력서 자동 탐색 → 로드
5. **JD 요구사항 맵**: 핵심 책임(R1~RN), 기술스택, 우대사항 전체 추출
6. **이력서 역량 맵**: 경험, 기술, 성과 추출
7. 힌트 목록 구조화

**Exit Criteria**: JD 요구사항 맵 + 이력서 역량 맵 + 힌트 목록 완성

---

### Phase 1: 소스별 병렬 조사

1. `sources/` 에서 4개 파일 로드: `coding.md`, `technical.md`, `system-design.md`, `behavioral.md`

2. 각 카테고리의 **Tier 1 소스** 중심으로 Agent 병렬 실행:

각 에이전트 프롬프트:
```
Research "{company_name}" "{position}" interview information from {source_name}.
Search: {search_query_template with company/position substituted}

Collect ALL:
- Coding test: OA format, questions, difficulty, platform
- Technical interview: questions, follow-ups, topics
- System design: design problems, architecture topics
- Behavioral: questions, evaluation criteria

Tag: [Confirmed] (multiple sources), [Likely] (single source), [Uncertain]
Mark: Base or Runtime source
```

3. 모든 에이전트 결과를 카테고리별 통합

**Exit Criteria**: 카테고리별 통합 조사 결과 완성

---

### Phase 2: 카테고리별 병렬 문제 생성

Phase 1 결과 + JD 맵 + 이력서 맵 + 힌트를 4개 에이전트에 분배.

**가중치**:
- Runtime 소스 기출 → 2x 가중치 + "기출 확인" 태그
- Base 소스 패턴 → 보충 문제
- 힌트 주제 → 해당 주제 문제 수 증가

#### Agent A: 코딩 테스트
- 입력: 조사(코딩) + JD 기술스택 전체 + 힌트 + 이력서 기술
- 출력: [필수] 코딩 예상 + CS 기본 + 연습 추천(URL) / [조건부] MCQ, SQL, 기타
- 검증: JD 기술스택 모든 항목에 최소 1개 문제

#### Agent B: 기술 면접
- 입력: 조사(기술) + JD 핵심 책임(R1~RN) + 기술스택 + 이력서 역량
- 출력: 책임별 예상 질문 + 꼬리질문 2-3개 + 이력서 매핑 + 약점 대응
- 형식:
```
Q: "질문"
  ├── 꼬리 1: "후속"
  ├── 꼬리 2: "후속"
  └── 꼬리 3: "후속"
📎 내 경험: {이력서 매칭 경험}
```
- 검증: JD 핵심 책임 전체 + 기술스택 전체에 최소 1개 질문

#### Agent C: 시스템 디자인
- 입력: 조사(설계) + JD 도메인/아키텍처 키워드 + 이력서 설계 경험
- 출력: 예상 설계 문제 + 접근 프레임워크 + 내 경험 매핑
- 검증: JD 아키텍처 키워드 전체 커버

#### Agent D: 행동 면접
- 입력: 조사(행동) + JD 리더십/협업 요구 + 이력서 전체 경험
- 출력: STAR 기반 질문 + 답변 초안 + 일반 질문 + 경험 매핑
- 검증: JD 리더십 항목 + 이력서 주요 경험 전체 매핑

---

### Phase 3: 통합 출력

4개 에이전트 결과 통합 → `career/{company}-{role}-interview-prep.md` 저장.

출력 구조:
```markdown
# Interview Prep: {Company} — {Position}

> 생성일: YYYY-MM-DD
> JD 기반 | 조사 소스 N개 (Base M + Runtime K) | 이력서 개인화

## 시험 구조 (조사 기반)

## 1. 코딩 테스트
### 1.1 코딩 예상 문제 (필수)
### 1.2 CS 기본 문제 (필수)
### 1.3 연습 문제 추천 (필수)
### 1.4 MCQ 예상 문제 (조건부)
### 1.5 SQL 문제 (조건부)
### 1.6 기타 (조건부)

## 2. 기술 면접
### 2.1 JD 책임별 예상 질문 + 꼬리질문
### 2.2 기술스택별 예상 질문 + 꼬리질문
### 2.3 약점 대응 전략

## 3. 시스템 디자인
### 3.1 예상 설계 문제 + 접근 프레임워크
### 3.2 내 경험 활용 사례

## 4. 행동 면접
### 4.1 예상 질문 + STAR 답변 초안
### 4.2 내 경험 매핑

## 5. 준비 플랜
### 7일 / 14일 / 30일 로드맵

## 6. 조사 출처
### 소스별 신뢰도 + URL + Base/Runtime 구분
```
