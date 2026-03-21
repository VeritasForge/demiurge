# Perplexity AI 아키텍처 심층 분석 — 교정 버전

> **교정 이력**
> - 원본: Deep Research (이전 세션, ByteByteGo / FrugalTesting 등 2차 출처 기반)
> - 교정일: 2026-03-06
> - 교정 방법: Playwright MCP + WebSearch를 통한 1차 출처 직접 검증
> - 주요 1차 출처:
>   - research.perplexity.ai/articles/architecting-and-evaluating-an-ai-first-search-api (Sep 25, 2025)
>   - research.perplexity.ai/articles/disaggregated-prefill-and-decode (Aug 1, 2025)
>   - vespa.ai 공식 파트너십 발표 (Apr 15, 2025)
>   - docs.perplexity.ai (Sonar 모델 공식 문서)

---

## 개요

Perplexity AI는 2022년 창업 이후, 초기에는 외부 검색 API(Bing 등)에 의존하다 빠르게 독자적인 AI-First 검색 인프라를 구축한 회사다. 2025년 현재 일 2억 쿼리(200 million daily queries)를 처리하는 완전 독자적 검색 엔진 위에 LLM 응답 생성 레이어를 결합한 구조를 운영한다.

---

## 1. 검색 인프라: Vespa.ai 기반 독자 구축

### 1.1 Vespa.ai 파트너십 [CONFIRMED]

Perplexity는 Vespa.ai를 검색 플랫폼 기반으로 채택했다. 2025년 4월 15일 공식 파트너십이 BusinessWire를 통해 발표됐으며, Vespa.ai는 다음 기능을 제공한다:

- 텍스트(lexical) + 벡터(semantic) 인덱스를 단일 서빙 엔진에서 처리
- 실시간 인덱스 업데이트 (쿼리 중단 없이)
- 분산 ML 인퍼런스 통합 (랭킹 모델 포함)
- 100ms 이내 응답 목표, 초당 수천 하이브리드 쿼리 처리

### 1.2 인덱스 규모 [CONFIRMED — 수치 교정]

> **[교정]** 이전 Deep Research에서 "200억+(20 billion+) 고유 URL"로 기술했으나,
> 공식 논문 원문은 **"200 billion(2,000억)"**이다. 정확히 10배 오류.

공식 원문:
> *"Our search index tracks over **200 billion** unique URLs, with capacity to track many hundreds of billions more."*
> — Perplexity Research, Sep 25, 2025

- 크롤러 + 인덱싱 fleet: 수만 개(tens of thousands) CPU, 수백 TB RAM
- 초당 수만 건(tens of thousands) 인덱싱 작업 처리
- Cold/Warm 스토리지 혼합, ML 기반 재인덱싱 우선순위 결정

---

## 2. 크롤링 인프라: PerplexityBot [CONFIRMED]

Perplexity는 자체 크롤러 **PerplexityBot**을 운영한다.

공식 원문:
> *"**PerplexityBot**, our search crawler, complies with explicit limits set forth in robots.txt files, or in the absence of domain-specified limits, industry-standard norms concerning request rates."*

- robots.txt 준수
- 사이트 불가용 감지 시 크롤링 속도 자동 조절
- 수만 건 동시 크롤링에서도 rate limit 분산 적용

---

## 3. 멀티스테이지 랭킹 파이프라인 [CONFIRMED]

공식 논문에서 확인된 파이프라인:

```
[쿼리 입력]
    ↓
[Stage 1] Hybrid Retrieval
  - Lexical 검색 (lexical index)
  - Semantic 검색 (embedding/vector index)
  - 두 결과를 병합 → hybrid candidate set
    ↓
[Stage 2] Pre-filtering
  - 기본 휴리스틱, 관련 없는/오래된 콘텐츠 제거
    ↓
[Stage 3] 초기 랭킹
  - Lexical scorer + Embedding-based scorer (속도 최적화)
    ↓
[Stage 4] 최종 랭킹
  - Cross-encoder reranker (정밀도 최적화)
    ↓
[결과] 문서 + Sub-document 단위 결과 (LLM context용)
```

공식 원문:
> *"Earlier stages rely on **lexical and embedding-based scorers** optimized for speed. As the candidate set is gradually winnowed down, we then use more powerful **cross-encoder reranker models** to perform the final sculpting of the result set."*

**주석**: 이전 분석에서 "BM25"라고 구체화했으나, 공식 문서는 "lexical retrieval"이라 표현. BM25 계열과 기능적으로 동일하나, 정확한 구현 명칭은 공식 미확인.

---

## 4. 추론 엔진 [PARTIALLY UNVERIFIED — 명칭 교정]

### 4.1 "ROSE" 엔진 명칭 [UNVERIFIABLE]

> **[교정]** 이전 Deep Research에서 "ROSE 추론 엔진"으로 기술했으나,
> Perplexity 공식 자료(research.perplexity.ai, blog.perplexity.ai, docs.perplexity.ai) 어디에도
> "ROSE"라는 엔진 명칭이 등장하지 않는다.

**공식 자료에서 확인된 것**:
- LLM 엔진(batch scheduler, forward pass 파이프라인)을 자체 개발
- **추측적 디코딩(Speculative Decoding) 지원**: 공식 논문에서 명시
  > *"In the MTP and speculative decoding mechanisms..."* — Disaggregated Prefill 논문 (Aug 2025)
- 기술 스택: Python, Rust, C++, PyTorch, Triton, CUDA (채용공고 확인)
- FlashInfer, libfabric, RDMA(EFA/ConnectX NIC) 활용 확인

**결론**: 추론 엔진이 존재하고 고성능 기능(speculative decoding 포함)을 갖추고 있음은 확인. 단, "ROSE"라는 명칭은 ByteByteGo 2차 분석에서만 등장하는 코드명이거나 오기일 수 있으며, **공식 검증 불가**.

### 4.2 Disaggregated Prefill-Decode 아키텍처 [CONFIRMED — 신규 추가]

2025년 8월 공식 논문에서 밝힌 추가 인프라:

- **Prefill-Decode 분리**: Prefiller 노드와 Decoder 노드를 물리적으로 분리
  - Prefiller: KV 캐시 채우기 담당, 처리량 최적화
  - Decoder: 토큰 생성 담당, 지연시간(latency) 최적화
- **KV Messenger**: RDMA 기반 KV 캐시 전송 시스템 (libfabric 기반)
- **결과**: DeepSeek-R1 기준 혼합 방식 50 TPS → 분리 방식 90+ TPS 달성
- 배포 모델: DeepSeek-R1, Qwen3-Coder (480B), Sonar 모델군

---

## 5. Sonar 모델: 자체 파인튜닝 LLM [CONFIRMED]

**Perplexity의 자체 모델**:

| 모델 | 특성 |
|------|------|
| **Sonar** | Llama 3.3 70B 기반 파인튜닝, 경량/빠름/인용 지원 |
| **Sonar Pro** | 기업용, 멀티스텝 쿼리, 평균 2배 인용 수 |

공식 원문 (docs.perplexity.ai):
> *"Built on top of Llama 3.3 70B, **Sonar has been further trained** to enhance answer factuality and readability"*

공식 논문 (Disaggregated Prefill):
> *"Since the **Sonar models** of Perplexity support structured output..."*

파인튜닝 방향:
- 답변 사실성(factuality) 향상
- 인용(citation) 생성 최적화
- 검색 결과 기반 응답 특화

---

## 6. 외부 LLM 혼합 사용 [CONFIRMED]

Perplexity Pro 구독자는 자체 Sonar 외에 외부 frontier 모델을 선택 가능:

- OpenAI GPT-4o / GPT 시리즈
- Anthropic Claude (Sonnet 등)

이 모델들은 Perplexity 서버에서 직접 실행되지 않고, 각 회사의 API를 통해 호출된다. 기본(default) 모델은 Sonar이며, 외부 모델은 사용자가 명시적으로 선택할 때만 활성화된다.

---

## 7. Grounding 원칙: 검색 기반 응답 [PARTIALLY CONFIRMED]

> **[교정]** 이전 분석에서 "hard constraint"로 기술했으나, 공식 기술 문서에서 이 용어 미확인.

**확인된 것**: CEO Aravind Srinivas 발언으로 원칙 확인:
> *"you're not supposed to say anything that you don't retrieve"*

**공식 논문 표현**: "context curation", "context engineering"으로 기술. 검색에서 가져온 내용으로 LLM context를 구성하는 방식이 핵심 설계 원칙임은 맞으나, 기술적 "하드 컨스트레인트" 구현 여부는 공식 기술 문서에서 명시하지 않음.

공식 논문:
> *"In a world of AI agents, a search API must also carefully curate the context provided to developers' models to ensure those models perform optimally and incorporate maximally accurate information."*

---

## 8. 검색 독립성: Google/Bing 의존도 [NEEDS REVISION]

> **[교정]** 이전 분석에서 "Google/Bing API + 자체 인덱스 하이브리드"로 기술했으나,
> 이는 **2022년 초기 아키텍처**에 대한 묘사다.

**현재(2025) 아키텍처**: 완전 독자적 인프라

공식 논문이 명시한 전환 배경:
> *"The very first version of Perplexity's answer engine actually incorporated some of these [third-party API] offerings."*
> *"as users flocked to Perplexity, we quickly realized that these APIs weren't going to scale with our growth. The prices we encountered were exorbitant, with one leading API provider charging **$200 per thousand queries**."*

현재 구조:
- 자체 PerplexityBot으로 직접 크롤링
- 자체 2,000억 URL 인덱스 (Vespa.ai 기반)
- 외부 SERP API 미사용 (평가 섹션에서 "SERP Based* (Tavily)"를 경쟁사로 분류)
- 완전히 독립적인 검색 파이프라인

---

## 9. 공개 연구 논문 현황 [INCORRECT → 교정]

> **[교정]** 이전 분석에서 "4건"으로 기술했으나, 현재 최소 7건 이상 공개됨.

**research.perplexity.ai 확인 목록** (2026-03-06 기준):

| # | 제목 | 날짜 | 카테고리 |
|---|------|------|---------|
| 1 | pplx-embed: State-of-the-Art Embedding Models for Web-Scale Retrieval | Feb 26, 2026 | Featured |
| 2 | Evaluating Deep Research Performance in the Wild with the DRACO Benchmark | Feb 4, 2026 | research |
| 3 | BrowseSafe: Understanding and Preventing Prompt Injection Within AI Browser Agents | Dec 2, 2025 | security |
| 4 | RDMA Point-to-Point Communication for LLM Systems | Nov 5, 2025 | systems |
| 5 | Enabling Trillion-Parameter Models on AWS EFA | Nov 4, 2025 | systems |
| 6 | Architecting and Evaluating an AI-First Search API | Sep 25, 2025 | search |
| 7 | Disaggregated Prefill and Decode | Aug 1, 2025 | systems |
| + | 추가 논문 (Load More) | — | — |

연구 영역: 검색(search), 시스템(systems), 보안(security), 임베딩(embedding), 에이전트 평가

---

## 10. 처리 규모 [CONFIRMED]

공식 원문:
> *"our production search infrastructure that processes **200 million daily queries**"*
> — Perplexity Research, Sep 25, 2025

| 지표 | 수치 |
|------|------|
| 일 쿼리 수 | 2억 (200 million) |
| 검색 API 중간값 레이턴시 | 358ms (p50) |
| 95 퍼센타일 레이턴시 | 763ms (p95) |
| 인덱스 크기 | 2,000억 URL (200 billion) |

---

## 교정 요약표

| 항목 | 이전 Deep Research (교정 전) | 교정 후 | 출처 |
|------|------------------------------|---------|------|
| URL 인덱스 수 | 200억+ (20B+) | **2,000억+ (200B+)** | 공식 논문 원문 |
| 추론 엔진 명칭 | ROSE 엔진 | **명칭 미확인** (내부 코드명 가능성) | ByteByteGo 2차 출처만 |
| Hard constraint | 기술적 하드 컨스트레인트 | **CEO 발언 수준 확인, 기술 구현 명칭 미확인** | 논문은 "context curation" |
| 논문 수 | 4건 | **7건 이상 (계속 증가)** | Playwright 직접 확인 |
| Google/Bing 의존도 | 하이브리드 사용 | **초기(2022) 구조; 현재 완전 독자 인프라** | 공식 논문 전환 이력 |
| Vespa | 확인 | **확인** (공식 파트너십 발표) | BusinessWire + Vespa.ai |
| 멀티스테이지 랭킹 | 확인 | **확인** (cross-encoder reranker 명시) | 공식 논문 |
| PerplexityBot | 확인 | **확인** (원문 직접 인용) | 공식 논문 |
| Sonar 모델 | 확인 | **확인** (Llama 3.3 70B 기반 파인튜닝) | 공식 API 문서 |
| 외부 LLM (GPT-4, Claude) | 확인 | **확인** (Pro 구독 공식 지원) | 공식 구독 페이지 |
| 일 2억 쿼리 | 확인 | **확인** (원문 정확 일치) | 공식 논문 |

---

## 아키텍처 전체 구조도 (교정 버전)

```
사용자 쿼리
    │
    ▼
┌───────────────────────────────────────────────────────┐
│               Perplexity Answer Engine                │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │           AI-First Search API (독자 구축)        │  │
│  │                                                 │  │
│  │  ┌──────────┐    ┌────────────────────────────┐ │  │
│  │  │Perplexity│───▶│   Vespa.ai 서빙 엔진        │ │  │
│  │  │   Bot    │    │                            │ │  │
│  │  │(크롤러)   │    │ ┌──────────┐ ┌──────────┐ │ │  │
│  │  └──────────┘    │ │ Lexical  │ │ Vector   │ │ │  │
│  │       │          │ │  Index   │ │  Index   │ │ │  │
│  │       ▼          │ └────┬─────┘ └────┬─────┘ │ │  │
│  │  ┌──────────┐    │      └─────┬──────┘       │ │  │
│  │  │ 200B URL │    │            ▼               │ │  │
│  │  │  Index   │    │   Hybrid Candidate Set     │ │  │
│  │  └──────────┘    │            ▼               │ │  │
│  │                  │   Pre-filter (heuristics)  │ │  │
│  │  자체 콘텐츠      │            ▼               │ │  │
│  │  이해 모듈        │   Lexical+Embedding Scorer │ │  │
│  │  (Self-improving │            ▼               │ │  │
│  │   AI rulesets)   │  Cross-Encoder Reranker    │ │  │
│  │                  └──────────────┬─────────────┘ │  │
│  └────────────────────────────────│─────────────────┘  │
│                                   ▼                   │
│  ┌────────────────────────────────────────────────┐   │
│  │        LLM Generation Layer                    │   │
│  │                                                │   │
│  │  Sonar (default) | Sonar Pro | GPT-4o | Claude │   │
│  │                                                │   │
│  │  Disaggregated Prefill-Decode                 │   │
│  │  (Prefiller nodes ──RDMA──▶ Decoder nodes)    │   │
│  │  + Speculative Decoding                       │   │
│  └────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────┘
    │
    ▼
인용 포함 답변
```

---

## 불확실 항목 (Unverifiable)

다음 항목들은 공식 1차 출처에서 확인되지 않아 기술 시 주의 필요:

1. **"ROSE" 엔진 명칭**: ByteByteGo 2차 분석에서만 등장. 공식 미확인.
2. **"Rust 이전 중"**: 채용공고에서 Rust 스택 확인, 하지만 "이전 중" 여부는 공식 미확인.
3. **BM25 구체적 구현**: 공식 문서는 "lexical"로만 기술. BM25 계열 추정이나 단정 불가.

---

*교정 방법론: Playwright MCP headless browser로 JS 렌더링 페이지 직접 접근, WebSearch로 공식 파트너십/API 문서 확인, WebFetch로 Vespa.ai 공식 페이지 확인. 총 1차 출처 4개 이상 확보.*
