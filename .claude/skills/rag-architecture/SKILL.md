---
description: RAG Pipeline 아키텍처, Chunking, Embedding, Vector DB, Hybrid Search, Re-ranking
user-invocable: false
---

# RAG Architecture Skill

Retrieval-Augmented Generation 파이프라인을 설계합니다. Ingestion, Retrieval, Generation의 3단계와 Advanced RAG 패턴을 다룹니다.

## 핵심 역량

### RAG 패턴 진화

```
Naive RAG ──> Advanced RAG ──> Modular RAG ──> Agentic RAG
  (2023)        (2024)          (2025)          (2026)

Naive:    Query → Retrieve → Generate
Advanced: Query Transform → Hybrid Search → Rerank → Generate
Modular:  플러그인 방식으로 각 단계를 교체 가능
Agentic:  Agent가 검색 전략을 동적으로 결정
```

### 전체 파이프라인 아키텍처

```
┌─── Ingestion Pipeline ────────────────────────────────┐
│                                                        │
│  Document → Parse → Chunk → Embed → Index (Vector DB) │
│                                                        │
└────────────────────────────────────────────────────────┘

┌─── Retrieval Pipeline ────────────────────────────────┐
│                                                        │
│  Query → Transform → Hybrid Search → Rerank → Context │
│    │                   │         │                      │
│    ├─ Multi-query      ├─ Dense  ├─ Cross-encoder     │
│    ├─ HyDE             ├─ Sparse ├─ ColBERT           │
│    └─ Step-back        └─ Graph  └─ Cohere Rerank     │
│                                                        │
└────────────────────────────────────────────────────────┘

┌─── Generation Pipeline ───────────────────────────────┐
│                                                        │
│  Context + Prompt Template → LLM → Citation → Response│
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Chunking 전략 비교

| 전략 | Faithfulness | 적합 시나리오 |
|------|-------------|-------------|
| **Fixed-size** | 0.47-0.51 | 빠른 프로토타입 |
| **Recursive** | 0.60-0.65 | 일반적인 문서 |
| **Semantic** | 0.79-0.82 | 품질 중시 프로덕션 |
| **Document-aware** | 0.83-0.88 | 구조화된 문서 (PDF, HTML) |

**권장**: Semantic Chunking + 500-1000 토큰 + 20% overlap

### Embedding 모델 선택

| 모델 | 차원 | MTEB 점수 | 가격 | 적합 시나리오 |
|------|------|----------|------|-------------|
| `text-embedding-3-large` | 3072 | 64.6 | $0.13/1M | 범용, 관리형 |
| `Cohere embed-v4` | 1024 | 67.1 | $0.10/1M | 다국어, 멀티모달 |
| `BGE-M3` | 1024 | 65.0 | 무료 | 자체 호스팅, 다국어 |
| `GTE-large-en-v1.5` | 1024 | 65.4 | 무료 | 자체 호스팅, 영어 |

**핵심**: 도메인 특화 Fine-tuning으로 10-30% 성능 향상 가능

### Vector DB 비교

| DB | 유형 | 최대 벡터 | 하이브리드 검색 | 적합 시나리오 |
|----|------|----------|---------------|-------------|
| **Pinecone** | Managed | 10억+ | ✅ | 관리형, 빠른 도입 |
| **Weaviate** | OSS/Cloud | 10억+ | ✅ (BM25) | 풍부한 필터링 |
| **Qdrant** | OSS/Cloud | 10억+ | ✅ | 고성능, Rust 기반 |
| **pgvector** | Extension | 수백만 | ❌ | PostgreSQL 이미 사용 시 |
| **Milvus** | OSS | 10억+ | ✅ | 대규모, GPU 가속 |

### Hybrid Search (Dense + Sparse)

```
Query ─┬─> Dense Retrieval (Embedding) ──┐
       │                                   ├─> Reciprocal Rank Fusion ─> Results
       └─> Sparse Retrieval (BM25) ───────┘

RRF Score = Σ 1 / (k + rank_i)   (k=60 기본)
```

**효과**: NDCG 26-31% 개선 (Dense-only 대비)

### Re-ranking

```
Top-K 후보 (100개) ──> Cross-encoder Reranker ──> Top-N (5-10개)

효과: 정확도 +33%, 복잡한 쿼리에서 +52%
```

**권장 Reranker**: Cohere Rerank v3, BGE-reranker-v2, ColBERT

### Advanced RAG 패턴

| 패턴 | 핵심 아이디어 | 성능 향상 |
|------|-------------|----------|
| **Self-RAG** | Reflection 토큰으로 자기 비판 | PopQA +270% |
| **Corrective RAG** | 검색 결과 품질 판단 후 보정 | Faithfulness +15% |
| **Adaptive RAG** | 쿼리 복잡도별 전략 동적 선택 | 비용 대비 최적 |
| **Graph RAG** | 지식 그래프 기반 검색 | 관계 추론 +40% |
| **Agentic RAG** | Agent가 검색 전략 결정 | 2026 baseline |

### Lost-in-the-Middle 대응

```
┌──────────────────────────────────────┐
│ Context Window 배치 전략              │
│                                       │
│  [가장 관련 높은 문서]  ← 처음에 배치  │
│  [중간 관련도 문서들]                  │
│  [두 번째로 관련 높은 문서] ← 끝에 배치 │
│                                       │
│  효과: 정확도 +20-40% 개선            │
└──────────────────────────────────────┘
```

## 의사결정 매트릭스

```
                    ┌──────────────┐
                    │ 데이터 규모?  │
                    └──────┬───────┘
               < 1M tokens │  > 1M tokens
            ┌──────────────┴───────────────┐
            ▼                               ▼
    CAG (Context-         ┌─────────────────────┐
    Augmented Gen)        │ 업데이트 빈도?       │
    40.5x 속도 향상       └────────┬────────────┘
                          낮음     │      높음
                     ┌─────────────┴──────────────┐
                     ▼                              ▼
              Naive/Advanced RAG           Agentic RAG + Streaming Index
```

## 사용 시점
- RAG 시스템 설계 / 아키텍처 리뷰
- Vector DB 선택
- Chunking/Embedding 전략 결정
- 검색 품질 개선 (Hybrid Search, Re-ranking)
- Graph RAG / Agentic RAG 도입 검토

## 참고 조사
- 상세 조사: [research/ai-backend/rag-pipeline.md](../../../research/ai-backend/rag-pipeline.md)
