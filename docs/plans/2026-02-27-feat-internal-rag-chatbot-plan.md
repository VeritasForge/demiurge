---
title: "feat: Internal RAG Chatbot for Slack"
type: feat
status: active
date: 2026-02-27
deepened: 2026-02-27
origin: docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md
---

# Internal RAG Chatbot for Slack

## Enhancement Summary

**Deepened on:** 2026-02-27
**Sections enhanced:** 13 (11 existing + 2 new)
**Skills applied:** rag-architecture, ai-safety, llm-gateway, ai-agent, prompt-engineering, cloud-native, sre, testing-architecture
**Research sources:** Anthropic SDK docs, pgvector 0.8.0, Slack Bolt async, Presidio Korean, Claude Prompt Caching, MMTEB embeddings, Extended Thinking

### Key Improvements

1. **Prompt Caching 적용** — system prompt + tool definitions에 `cache_control` 추가로 반복 요청 비용 75-90% 절감 (MVP Day 3에 반영)
2. **Observability 섹션 신규 추가** — LLM 5 Pillars (Reliability, Quality, Safety, Cost, Governance) + Langfuse 통합
3. **Think Tool 활용** — 복잡한 질문에서 Claude가 tool 결과를 분석할 때 정확도 향상 (Anthropic 공식 권장)
4. **AI Safety 강화** — CQL/JQL Injection 방어, EU AI Act 면책 문구, Retrieval Guard 로드맵 구체화
5. **pgvector 최적화** — halfvec 사용으로 메모리 50% 절약, iterative scanning (relaxed_order), embedding_model_version 스키마 추가
6. **Cost Optimization 섹션 신규 추가** — Prompt Caching + Model Routing + 월간 비용 상세 분석
7. **LLM Evaluation 추가** — RAGAS 메트릭 (Faithfulness, Answer Relevancy) + Golden Dataset + promptfoo 리그레션 테스트
8. **Embedding 모델 로드맵** — text-embedding-3-small(MVP) → BGE-M3-ko 비교 테스트(Phase 2)

### New Considerations Discovered

- Claude의 Think Tool은 순차적 tool use 시나리오에서 extended thinking보다 적합 (Anthropic 2026-01 발표)
- pgvector 0.8.0의 iterative scanning (relaxed_order)이 WHERE 절 포함 쿼리에서 성능 최적
- Anthropic SDK에서 aiohttp 백엔드(`anthropic[aiohttp]`)가 httpx 기본값보다 async 성능 우수
- Presidio 한국어 NLP 모델 (spaCy/Stanza)을 별도 설정해야 context words 기반 탐지 정확도 향상
- EU AI Act 2026년 8월 전면 시행 — 사내 챗봇은 "제한 위험" 등급으로 AI 사용 고지 의무
- reply_broadcast=True는 채널 소음 유발 → 기본 False 권장

---

## Overview

사내 개발팀(20-100명)을 위한 Slack Bot 기반 Q&A 챗봇. Confluence, Jira, Slack의 정보를 실시간 검색하여 자연어로 답변을 생성하고, 출처를 함께 제공한다. Agentic RAG MVP로 시작하여 Hybrid RAG로 점진적 진화하는 전략을 따른다.

(see brainstorm: docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md)

---

## Problem Statement

개발팀이 Confluence 문서, Jira 이슈, Slack 대화에 흩어진 정보를 찾기 위해 많은 시간을 소비한다. 각 플랫폼의 검색 기능은 개별적으로만 동작하여, 올바른 정보를 찾으려면 3개 시스템을 각각 검색해야 한다. 특히 온보딩 중인 신규 팀원이나 크로스 팀 협업 시 정보 접근 비용이 크다.

**해결 목표**: Slack에서 자연어 질문 하나로 3개 데이터 소스를 동시 검색하여, 출처가 포함된 신뢰할 수 있는 답변을 5-15초 내 제공한다.

---

## Proposed Solution

### Architecture Diagram (Phase 1 MVP)

```
┌──────────┐     ┌──────────────────────────────────────────────────────────┐
│  Slack   │────→│  FastAPI Server (EKS Pod)                                │
│  User    │←────│                                                          │
└──────────┘     │  ┌──────────────────────────────────────────────────┐    │
                 │  │ Slack Bolt (AsyncApp + Socket Mode)              │    │
                 │  │  @mention / DM → async handler                  │    │
                 │  └──────────┬───────────────────────────────────────┘    │
                 │             │                                            │
                 │             v                                            │
                 │  ┌──────────────────┐   "🔍 검색 중..."                  │
                 │  │ Input Guard      │   (즉시 ack + ephemeral msg)       │
                 │  │ ├─ PII Filter    │                                    │
                 │  │ └─ Injection Chk │                                    │
                 │  └──────────┬───────┘                                    │
                 │             │                                            │
                 │             v                                            │
                 │  ┌──────────────────────────────────┐                    │
                 │  │ Semantic Cache (pgvector + HNSW)  │                    │
                 │  │ cosine similarity > 0.92          │                    │
                 │  │ ├─ HIT  → 캐시 응답 반환 (~50ms) │                    │
                 │  │ └─ MISS ↓                        │                    │
                 │  └──────────┬───────────────────────┘                    │
                 │             │                                            │
                 │             v                                            │
                 │  ┌──────────────────────────────────────────────────┐    │
                 │  │ Anthropic Messages API (Tool Use)                │    │
                 │  │ Model: claude-sonnet-4-5                         │    │
                 │  │ System Prompt: 사내 Q&A 전문가                    │    │
                 │  │                                                  │    │
                 │  │ Tools:                                           │    │
                 │  │  ├─ search_confluence(query, space_key?, label?) │    │
                 │  │  ├─ search_jira(query, project?, status?)        │    │
                 │  │  └─ search_slack(query, channel?, days_back=30)  │    │
                 │  │                                                  │    │
                 │  │ Max tool rounds: 5                               │    │
                 │  │ Timeout: 25초 (전체 30초 중 25초)                 │    │
                 │  └──────────┬───────────────────────────────────────┘    │
                 │             │                                            │
                 │             v                                            │
                 │  ┌──────────────────┐                                    │
                 │  │ Output Guard     │                                    │
                 │  │ ├─ PII Filter    │                                    │
                 │  │ └─ 출처 포맷팅   │                                    │
                 │  └──────────┬───────┘                                    │
                 │             │                                            │
                 │             v                                            │
                 │  chat.update → 답변 + 출처 링크                          │
                 │  + Semantic Cache 저장 (소스별 TTL)                       │
                 │                                                          │
                 │  ┌────────────────────────────────┐                      │
                 │  │ PostgreSQL + pgvector (RDS)     │                      │
                 │  │ ├─ semantic_cache 테이블        │                      │
                 │  │ └─ HNSW 인덱스 (cosine)         │                      │
                 │  └────────────────────────────────┘                      │
                 └──────────────────────────────────────────────────────────┘
                          AWS EKS
```

### SDK 선택 변경 권고

브레인스토밍에서 `claude_agent_sdk`를 선택했으나, 조사 결과 이 SDK는 **Claude Code CLI를 번들링한 에이전트 SDK**로 파일 읽기/쓰기/코드 실행 등 개발 도구에 최적화되어 있다. RAG 챗봇의 Tool Use 패턴에는 **Anthropic Python SDK (`anthropic`)의 Messages API + Tool Use**가 더 적합하다.

(see brainstorm: docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md — "기술 스택" 결정)

| 기준 | `claude-agent-sdk` | `anthropic` SDK |
|------|-------------------|-----------------|
| 용도 | Claude Code 자동화 (파일/코드) | LLM API 직접 호출 (범용) |
| Tool 정의 | `@tool` + MCP Server 래핑 | JSON Schema 직접 정의 |
| 오버헤드 | CLI 바이너리 번들 (~무거움) | httpx 기반 (~가벼움) |
| Async | anyio (asyncio/trio) | AsyncAnthropic (httpx) |
| 비용 제어 | max_budget_usd (추상화) | token 단위 직접 제어 |
| Streaming | 지원 | 네이티브 SSE 지원 |
| Python | >=3.10 | >=3.9 |

**권고**: `anthropic` SDK의 Messages API + Tool Use로 변경. 가볍고, async native이며, 비용/토큰 제어가 세밀하다. `claude-agent-sdk`는 코드 자동화 시나리오에 더 적합하다.

---

## Technical Approach

### 프로젝트 구조

```
internal-rag-chatbot/
├── pyproject.toml              # uv 패키지 관리
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml          # 로컬 개발 (PostgreSQL + pgvector)
├── .env.example                # 환경 변수 템플릿
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 엔트리포인트 + lifespan
│   ├── config.py               # Pydantic Settings
│   │
│   ├── domain/                 # 도메인 레이어
│   │   ├── models.py           # Query, CachedResponse, Source 등 Value Objects
│   │   └── ports.py            # 인터페이스 (SearchPort, CachePort, EmbeddingPort)
│   │
│   ├── application/            # 애플리케이션 레이어
│   │   ├── query_handler.py    # 질문 처리 유스케이스 (오케스트레이션)
│   │   └── dto.py              # 입출력 DTO
│   │
│   ├── infrastructure/         # 인프라 레이어
│   │   ├── llm/
│   │   │   ├── claude_client.py      # Anthropic AsyncClient + Tool Use
│   │   │   ├── tools.py              # Tool 정의 (Confluence, Jira, Slack)
│   │   │   └── system_prompt.py      # System prompt 관리
│   │   ├── search/
│   │   │   ├── confluence_client.py  # Confluence REST API (CQL)
│   │   │   ├── jira_client.py        # Jira REST API v3 (JQL)
│   │   │   └── slack_client.py       # Slack search.messages
│   │   ├── cache/
│   │   │   ├── semantic_cache.py     # pgvector 기반 Semantic Cache
│   │   │   └── embedding_client.py   # OpenAI text-embedding-3-small
│   │   ├── security/
│   │   │   ├── pii_filter.py         # Presidio + Korean regex
│   │   │   └── input_guard.py        # Prompt injection detection
│   │   └── database/
│   │       ├── connection.py         # asyncpg pool 관리
│   │       └── migrations/           # SQL 마이그레이션
│   │
│   └── interfaces/             # 인터페이스 레이어
│       ├── slack_bot.py        # Slack Bolt AsyncApp + Socket Mode
│       └── health.py           # /health/live, /health/ready
│
├── helm/
│   └── rag-chatbot/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── configmap.yaml
│           ├── secret.yaml
│           ├── hpa.yaml
│           └── _helpers.tpl
│
└── tests/
    ├── unit/
    │   ├── test_query_handler.py
    │   ├── test_pii_filter.py
    │   ├── test_semantic_cache.py
    │   └── test_tools.py
    └── integration/
        ├── test_confluence_client.py
        ├── test_slack_bot.py
        └── test_e2e_pipeline.py
```

### 핵심 컴포넌트 설계

#### 1. Slack Bot (interfaces/slack_bot.py)

```python
# 의사 코드 — 실제 구현 시 참고
class SlackBot:
    """Slack Bolt AsyncApp + Socket Mode 핸들러"""

    # 핵심 흐름:
    # 1. @mention or DM 수신
    # 2. 즉시 "🔍 검색 중..." 임시 메시지 전송 (thread reply)
    # 3. asyncio.create_task로 query_handler 비동기 실행
    # 4. 완료 시 chat.update로 임시 메시지를 결과로 교체

    # 주의사항:
    # - Socket Mode는 AsyncSocketModeHandler 사용
    # - FastAPI lifespan에서 Socket Mode handler를 background task로 실행
    # - 메시지 중복 처리 방지: message_ts 기반 deduplication (30초 윈도우)
    # - thread_ts 사용하여 thread reply (reply_broadcast=True로 채널에도 표시)
```

**Slack Bot Token Scopes:**

| Scope | 용도 |
|-------|------|
| `app_mentions:read` | @mention 이벤트 수신 |
| `chat:write` | 메시지 전송 + 업데이트 |
| `im:history` | DM 읽기 |
| `im:read` | DM 메타데이터 |

**Slack Search 제약 (CRITICAL):**
- `search:read` scope는 **User Token** 전용이며 Bot Token으로 사용 불가
- **MVP 대안**: Slack 검색을 Phase 2로 이연하거나, OAuth User Token을 별도 확보
- **권고**: Phase 1에서는 Confluence + Jira 2개 소스로 시작, Slack 검색은 Phase 2에서 user token 기반으로 추가

(see brainstorm: docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md — "전제 조건" #4)

#### Research Insights: Slack Bot

**reply_broadcast 기본값 변경 (MVP — HIGH PRIORITY):**
- 현재 플랜: `reply_broadcast=True` → 모든 thread reply가 채널에도 표시되어 소음 유발
- **권고**: 기본 `reply_broadcast=False` (thread 내에서만 표시)
- 사용자 또는 채널별 설정으로 override 가능하게 구성 (Phase 1.5)
- DM에서는 reply_broadcast 불필요 (1:1 대화)

**메시지 중복 처리 구체화 (MVP):**
- Slack은 네트워크 불안정 시 동일 이벤트를 재전송할 수 있음
- `message_ts` + `channel_id` 조합을 키로 30초 TTL 메모리 캐시 (dict 또는 TTLCache)
- asyncio.Lock 사용하여 race condition 방지

**Async 필수 사항:**
- Slack Bolt AsyncApp에서 모든 미들웨어/리스너는 async 함수여야 함
- ack, say 등 유틸리티 메서드에 반드시 await 사용
- Socket Mode WebSocket 재연결은 Bolt 내장 기능으로 자동 처리
- 참고: [Slack Bolt Socket Mode](https://docs.slack.dev/tools/bolt-python/concepts/socket-mode/)

#### 2. Query Handler (application/query_handler.py)

```python
# 의사 코드 — 오케스트레이션 흐름
class QueryHandler:
    """질문 처리 유스케이스 — 전체 파이프라인 오케스트레이션"""

    async def handle(self, question: str, user_id: str, channel_id: str) -> Answer:
        # Step 1: Input Guard (PII masking + injection check)
        safe_question = await self.input_guard.process(question)

        # Step 2: Semantic Cache lookup
        cached = await self.cache.find_similar(safe_question, threshold=0.92)
        if cached:
            return cached.answer  # ~50ms

        # Step 3: Claude Agent call with tools (5-25초)
        answer = await asyncio.wait_for(
            self.claude_client.ask(safe_question),
            timeout=25.0  # 전체 30초 중 25초
        )

        # Step 4: Output Guard (PII re-check)
        safe_answer = await self.output_guard.process(answer)

        # Step 5: Cache 저장 (비동기, 사용자 응답에 영향 없음)
        asyncio.create_task(self.cache.store(safe_question, safe_answer))

        return safe_answer
```

#### 3. Claude LLM Client (infrastructure/llm/claude_client.py)

```python
# 의사 코드 — Anthropic SDK Messages API + Tool Use
class ClaudeClient:
    """Anthropic AsyncAnthropic 기반 Tool Use 클라이언트"""

    # 설정:
    # - model: "claude-sonnet-4-5-20250929"
    # - max_tokens: 4096
    # - max_retries: 3
    # - timeout: 25초
    # - tools: [search_confluence, search_jira]  # Phase 1
    #
    # Tool Use 루프:
    # 1. messages.create() 호출
    # 2. stop_reason == "tool_use" → tool 실행 → 결과를 messages에 추가 → 재호출
    # 3. stop_reason == "end_turn" → 최종 답변 반환
    # 4. max 5 라운드 후 강제 종료
    #
    # System Prompt 핵심 지시:
    # - 사내 기술 문서 Q&A 전문가 역할
    # - 반드시 출처(URL) 인용
    # - 모르면 "확인되지 않음" 명시 (hallucination 방지)
    # - 한국어로 답변 (질문 언어 따라감)
    # - <user_data>...</user_data> Spotlighting 적용
```

**Tool 정의:**

```python
# search_confluence tool schema
{
    "name": "search_confluence",
    "description": "Confluence에서 기술 문서, 가이드, 회의록을 검색합니다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "검색 키워드 또는 CQL 쿼리"},
            "space_key": {"type": "string", "description": "특정 Space로 제한 (선택)"},
            "label": {"type": "string", "description": "라벨 필터 (선택)"}
        },
        "required": ["query"]
    }
}

# search_jira tool schema
{
    "name": "search_jira",
    "description": "Jira에서 이슈, 버그, 태스크를 검색합니다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "검색 키워드 또는 JQL 쿼리"},
            "project": {"type": "string", "description": "프로젝트 키 (선택)"},
            "status": {"type": "string", "description": "이슈 상태 필터 (선택)"}
        },
        "required": ["query"]
    }
}
```

**Atlassian API 인증:**
- Cloud 환경: API Token + Basic Auth (`email:api_token` base64)
- **Jira REST API v3** 사용 필수 (v2 deprecated)
  - 검색: `POST /rest/api/3/search/jql`
- **Confluence REST API v1** (CQL 검색은 v1에서 안정)
  - 검색: `GET /wiki/rest/api/content/search?cql=...`

#### Research Insights: Claude LLM Client

**Prompt Caching (MVP 적용 — HIGH PRIORITY):**
- System prompt (~2K tokens) + tool definitions (~1K tokens)에 `cache_control` 적용
- Cache write: 1.25x 기본 입력 가격 (5분 캐시), read: 0.1x 기본 입력 가격
- 반복 요청에서 **75-90% input token 비용 절감** → MVP에서도 적용 필수
- 2026-02-05부터 workspace-level isolation으로 변경 (organization → workspace)
- 참고: [Prompt caching - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

**Think Tool 활용 (MVP 적용 — HIGH PRIORITY):**
- 복잡한 질문에서 Claude가 tool 결과를 분석할 때 "think" tool 사용으로 정확도 향상
- System prompt에 `think` tool을 정의하여 Claude가 복잡한 추론 시 활용하도록 유도
- **적합 시나리오**: 다수 tool 결과 비교 분석, 정책 준수 판단, 순차적 의사결정
- Extended thinking은 tool_choice auto만 지원 → Think Tool이 agentic loop에서 더 유연
- 참고: [Claude Think Tool](https://www.anthropic.com/engineering/claude-think-tool)

**aiohttp 백엔드 (MVP 적용 — MEDIUM PRIORITY):**
- `pip install anthropic[aiohttp]` → `DefaultAioHttpClient()` 사용
- httpx 기본값 대비 async I/O 성능 개선 (특히 동시 tool call 시)
- 참고: [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)

**Lost-in-the-Middle 배치 전략 (Phase 1.5):**
- 검색 결과를 Context Window에 배치할 때 관련도 높은 문서를 처음과 끝에 배치
- 정확도 +20-40% 개선 (rag-architecture 스킬 참조)
- System prompt에 "가장 관련도 높은 출처를 우선 인용" 지시 추가

#### 4. Semantic Cache (infrastructure/cache/semantic_cache.py)

**DB 스키마:**

```sql
-- pgvector extension 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- Semantic Cache 테이블
CREATE TABLE semantic_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_text TEXT NOT NULL,
    question_embedding vector(1536) NOT NULL,  -- text-embedding-3-small
    answer_text TEXT NOT NULL,
    sources JSONB NOT NULL,                    -- [{type, title, url}]
    data_source_types TEXT[] NOT NULL,          -- ['confluence', 'jira']
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,           -- 소스별 TTL 기반
    hit_count INTEGER DEFAULT 0
);

-- HNSW 인덱스 (cosine distance)
CREATE INDEX idx_cache_embedding_hnsw
    ON semantic_cache
    USING hnsw (question_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- TTL 만료 정리용 인덱스
CREATE INDEX idx_cache_expires_at ON semantic_cache (expires_at);
```

**소스별 TTL:**

| 소스 | TTL | 근거 |
|------|-----|------|
| Confluence 전용 | 4시간 | 문서 변경 빈도 낮음, 브레인스토밍의 48h에서 보수적으로 조정 |
| Jira 전용 | 30분 | 이슈 상태 빈번히 변경 |
| Confluence + Jira 혼합 | 30분 | 가장 짧은 TTL 적용 |

(see brainstorm: docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md — "Semantic Cache")

**캐시 조회 쿼리:**

```sql
-- Cosine similarity 검색 (threshold > 0.92)
SELECT id, question_text, answer_text, sources,
       1 - (question_embedding <=> $1::vector) AS similarity
FROM semantic_cache
WHERE expires_at > now()
  AND 1 - (question_embedding <=> $1::vector) > 0.92
ORDER BY question_embedding <=> $1::vector
LIMIT 1;
```

**HNSW 검색 파라미터:** `SET hnsw.ef_search = 100;` (기본 40보다 높여 recall 향상)

#### Research Insights: Semantic Cache

**halfvec 사용 (MVP 적용 — HIGH PRIORITY):**
- `vector(1536)` 대신 `halfvec(1536)` 사용 시 메모리 50% 절약 + 성능 향상
- HNSW 인덱스 footprint: ~4-6 KB per 1536-dim halfvec (m=16)
- 스키마 변경: `question_embedding halfvec(1536)`, 인덱스: `halfvec_cosine_ops`
- 참고: [pgvector 0.8.0 on Amazon Aurora](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/)

**embedding_model_version 스키마 추가 (MVP 적용 — HIGH PRIORITY):**
- 향후 모델 변경 시 캐시 전체 재생성 방지를 위해 모델 버전을 캐시 키에 포함
- `embedding_model TEXT NOT NULL DEFAULT 'text-embedding-3-small'` 컬럼 추가
- 캐시 조회 시 `WHERE embedding_model = $current_model` 조건 추가

**pgvector 0.8.0 iterative scanning (Phase 1.5):**
- WHERE 절이 많은 후보를 필터링할 때 자동으로 검색 범위 확장
- `SET hnsw.iterative_scan = 'relaxed_order';` — 필터링 쿼리에서 최적 성능/정확도 균형
- 소스별 TTL 필터(`expires_at > now()`)와 함께 사용 시 특히 효과적

**Semantic Cache 히트율 최적화 전략:**
- llm-gateway 스킬에 따르면 Semantic Cache는 40-70% 히트율 달성 가능
- 플랜 목표 30%(1주)→50%(4주)는 보수적이지만 합리적 → 히트율 향상 전략:
  - 질문 정규화: 불필요한 조사/접속사 제거 후 임베딩 (한국어 형태소 분석)
  - threshold 튜닝: 0.92는 높은 편 → 실 데이터로 0.88-0.95 범위에서 A/B 테스트
  - 인기 질문 pre-warming: 자주 묻는 질문을 캐시에 사전 등록

#### 5. PII Filter + Input Guard (infrastructure/security/)

**5-Layer 방어 아키텍처 (MVP 범위):**

| Layer | 내용 | Phase 1 | Phase 2 |
|-------|------|---------|---------|
| Layer 1: Input Guard | PII 탐지 + 마스킹 | ✅ Presidio + 한국어 regex | NER 확장 |
| Layer 2: System Prompt | Spotlighting | ✅ `<user_data>` 태그 | 강화 |
| Layer 3: Retrieval Guard | RAG 결과 내 injection 감지 | ❌ | ✅ |
| Layer 4: Output Guard | 응답 PII 재확인 | ✅ (regex) | Presidio |
| Layer 5: Tool Guard | Tool 파라미터 검증 | ✅ (기본) | allowlist 강화 |

(see brainstorm: docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md — "PII Filter Layer")

**한국어 PII 패턴 (Presidio 내장 + 커스텀):**

| 패턴 | 예시 | 방식 |
|------|------|------|
| 주민등록번호 | 920315-1234567 | Presidio `KR_RRN` (체크섬 검증) |
| 전화번호 | 010-1234-5678 | regex `\d{2,3}-\d{3,4}-\d{4}` |
| 이메일 | user@company.com | Presidio `EMAIL_ADDRESS` |
| 카드번호 | 1234-5678-9012-3456 | regex `\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}` |

**PII 마스킹 전략 (Selective Masking):**
- **마스킹 대상**: 주민등록번호, 카드번호, 개인 전화번호 → Claude에 전달 전 마스킹
- **통과 대상**: 이름, 사내 이메일 → 검색 품질 유지를 위해 Claude에 전달 (내부 시스템이므로)
- **Output Guard**: 주민등록번호, 카드번호만 마스킹 (이름/이메일은 사내 정보이므로 허용)

#### Research Insights: Security & AI Safety

**CQL/JQL Injection 방어 (MVP 적용 — HIGH PRIORITY):**
- Tool Guard에 쿼리 파라미터 검증 추가 (OWASP LLM Top 10 #7 Insecure Plugin)
- `search_confluence` query에서 CQL 특수문자 이스케이프: `"`, `\`, `(`, `)`, `[`, `]`
- `search_jira` query에서 JQL 예약어 필터: `DROP`, `DELETE`, `UPDATE`, `--`
- space_key/project 파라미터에 allowlist 검증 (알려진 Space/Project만 허용)

**EU AI Act 면책 문구 (MVP 적용 — HIGH PRIORITY):**
- 사내 챗봇은 "제한 위험" 등급 → AI 사용 고지 의무 (2026년 8월 전면 시행)
- 모든 응답 하단에 면책 문구 추가: "이 답변은 AI가 생성했습니다. 정확성을 보장하지 않으며, 중요한 결정 시 원문을 확인해주세요."
- 출처 링크 제공으로 검증 가능성 보장 (이미 플랜에 포함)

**Retrieval Guard 로드맵 (Phase 2 — MEDIUM PRIORITY):**
- Indirect Prompt Injection: Confluence/Jira 문서에 악의적 콘텐츠 삽입 → Agent가 지시로 해석할 위험
- Phase 2에서 Layer 3 Retrieval Guard 구현: RAG 결과에서 instruction-like 패턴 감지
- 참고: ai-safety 스킬 5계층 방어 아키텍처 Layer 3

**Presidio 한국어 설정 강화 (MVP — MEDIUM PRIORITY):**
- 한국어 NLP 모델 설정 필요: `spaCy`의 `ko_core_news_sm` 또는 `Stanza` 한국어 모델
- Context words를 한국어로 업데이트해야 탐지 정확도 향상 (예: "주민번호", "전화번호", "카드번호")
- KR_RRN 체크섬 검증은 2020년 10월 이전 발급 번호에만 적용 → 이후 발급분은 regex 보완 필요
- 참고: [Presidio Multi-language support](https://microsoft.github.io/presidio/analyzer/languages/)

**Red Teaming 프로세스 (Phase 2):**
- ai-safety 스킬 프로덕션 체크리스트: 정기 Red Teaming 수행 권장
- Phase 2에서 Prompt Injection 테스트 시나리오 20개+ 구성
- jailbreak 시도, indirect injection, PII 유출 시도 포함

#### 6. FastAPI Server (app/main.py)

```python
# 의사 코드 — FastAPI + Slack Bolt 통합
# 핵심 포인트:
# 1. lifespan으로 startup/shutdown 관리 (deprecated on_startup 사용 금지)
# 2. startup: DB pool 초기화, Slack Socket Mode handler 시작
# 3. shutdown: graceful shutdown (SIGTERM → 진행 중 요청 완료 대기)
# 4. Socket Mode handler는 asyncio.create_task로 background 실행
# 5. Health check 엔드포인트: /health/live, /health/ready

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     app.state.db_pool = await create_asyncpg_pool()
#     app.state.slack_handler = AsyncSocketModeHandler(slack_app, app_token)
#     asyncio.create_task(app.state.slack_handler.start_async())
#     yield
#     # Shutdown
#     await app.state.slack_handler.close_async()
#     await app.state.db_pool.close()
```

### 에러 처리 설계

| 실패 시나리오 | 동작 | 사용자 메시지 |
|---------------|------|---------------|
| Confluence API 실패 | 해당 소스 스킵, 나머지로 답변 | "⚠️ Confluence 검색에 일시적 문제가 있어 Jira 결과만 포함합니다." |
| Jira API 실패 | 동일 스킵 + 알림 | "⚠️ Jira 검색에 일시적 문제가 있어 Confluence 결과만 포함합니다." |
| 모든 소스 실패 | 에러 로깅 + 안내 | "❌ 현재 검색 서비스에 문제가 있습니다. 잠시 후 다시 시도해주세요." |
| Claude API 타임아웃 (25초) | 타임아웃 종료 | "⏰ 답변 생성에 시간이 오래 걸리고 있습니다. 잠시 후 다시 질문해주세요." |
| Claude API 429 (Rate Limit) | exponential backoff 3회 | 3회 실패 시: "🔄 요청이 많아 처리가 지연되고 있습니다." |
| pgvector DB 연결 실패 | 캐시 우회, Agent 직접 호출 | (사용자에게 비노출, 로그만 기록) |
| Slack Socket Mode 끊김 | 자동 재연결 (Bolt 내장) | (사용자에게 비노출) |
| PII Filter 실패 | 질문 거부 (보안 우선) | "⚠️ 질문을 처리할 수 없습니다. 다시 시도해주세요." |

**전체 타임아웃 버짓:**

```
총 30초
├── Input Guard:     ~100ms
├── Cache lookup:    ~50ms (HIT 시 여기서 반환)
├── Claude + Tools:  ~25초 (max)
│   ├── Tool call 1: ~3-5초
│   ├── Tool call 2: ~3-5초
│   └── 답변 생성:   ~3-5초
├── Output Guard:    ~100ms
└── Cache store:     비동기 (사용자 응답에 영향 없음)
```

#### Research Insights: Error Handling & Resilience

**Circuit Breaker 구체 설정값 (llm-gateway 스킬 권장):**
- Anthropic API Circuit Breaker:
  - Failure threshold: 5회 연속 실패
  - Reset timeout: 30초
  - Half-open requests: 3회 탐지 요청
- Atlassian API Circuit Breaker:
  - Failure threshold: 3회 (API가 더 불안정할 수 있으므로 민감하게)
  - Reset timeout: 60초
- 구현: `tenacity` 라이브러리 또는 커스텀 데코레이터

**Graceful Degradation 계층 (cloud-native 스킬):**
```
Level 0: 정상 — 모든 소스 + 캐시 작동
Level 1: 캐시 장애 — Agent 직접 호출 (느려짐)
Level 2: 일부 소스 장애 — 가용 소스만으로 답변 + 경고
Level 3: 모든 소스 장애 — "검색 불가" 안내 + 에러 로깅
Level 4: Claude API 장애 — "서비스 일시 중단" 안내
```

**Bulkhead 패턴 (Phase 1.5):**
- Atlassian API 호출과 Claude API 호출의 connection pool 분리
- 하나의 외부 서비스 장애가 다른 서비스 호출에 영향을 주지 않도록 격리

### 인프라 설계 (AWS EKS)

**Kubernetes 리소스:**

```yaml
# deployment.yaml 핵심 설정
spec:
  replicas: 1  # Phase 1 (10 concurrent users)
  template:
    spec:
      containers:
        - name: rag-chatbot
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          lifecycle:
            preStop:
              exec:
                command: ["sleep", "10"]  # kube-proxy propagation
      terminationGracePeriodSeconds: 45
```

**Secrets 관리:**
- AWS Secrets Manager + External Secrets Operator (ESO)
- 4개 시크릿: `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `ANTHROPIC_API_KEY`, `DATABASE_URL`
- Atlassian: `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`, `ATLASSIAN_BASE_URL`

**Health Checks:**
- `/health/live`: 프로세스 생존 확인 (FastAPI 응답 가능?)
- `/health/ready`: 서비스 준비 확인 (DB 연결 OK? Socket Mode 연결 OK?)

---

## Implementation Phases

### Phase 1: Agentic RAG MVP (Week 1-2)

#### Week 1: 기반 + 핵심 파이프라인

| Day | 태스크 | 산출물 |
|-----|--------|--------|
| 1 | 프로젝트 셋업 (pyproject.toml, uv, 디렉토리 구조) | `internal-rag-chatbot/` 프로젝트 |
| 1 | FastAPI 서버 기본 + lifespan + health check | `app/main.py`, `app/interfaces/health.py` |
| 2 | Slack Bolt AsyncApp + Socket Mode 연결 | `app/interfaces/slack_bot.py` |
| 2 | 기본 핸들러: @mention → "검색 중..." → thread reply | E2E Slack 연동 확인 |
| 3 | Anthropic SDK 통합 + Tool Use 루프 + **Prompt Caching** + **Think Tool** | `app/infrastructure/llm/claude_client.py` |
| 3 | System prompt 설계 + Spotlighting + **EU AI Act 면책 문구** | `app/infrastructure/llm/system_prompt.py` |
| 4 | search_confluence tool (CQL → REST API) | `app/infrastructure/search/confluence_client.py` |
| 4 | search_jira tool (JQL → REST API v3) | `app/infrastructure/search/jira_client.py` |
| 5 | PII Filter (Presidio + 한국어 regex) | `app/infrastructure/security/pii_filter.py` |
| 5 | Input Guard (Prompt injection 기본 방어 + **CQL/JQL Injection 방어**) | `app/infrastructure/security/input_guard.py` |
| 5 | E2E 통합: Slack → Guard → Claude → Guard → Slack | 전체 파이프라인 작동 확인 |

#### Week 2: 캐시 + 배포 + 운영

| Day | 태스크 | 산출물 |
|-----|--------|--------|
| 6 | pgvector 스키마 (**halfvec** + **embedding_model_version**) + HNSW 인덱스 + 마이그레이션 | SQL 마이그레이션 파일 |
| 6 | Embedding 서비스 (text-embedding-3-small) | `app/infrastructure/cache/embedding_client.py` |
| 7 | Semantic Cache 조회 + 저장 + TTL | `app/infrastructure/cache/semantic_cache.py` |
| 7 | docker-compose (로컬 PostgreSQL + pgvector) | `docker-compose.yml` |
| 8 | Dockerfile (multi-stage, non-root) | `Dockerfile` |
| 8 | Helm chart 작성 | `helm/rag-chatbot/` |
| 9 | K8s Secrets (External Secrets Operator) | `helm/rag-chatbot/templates/secret.yaml` |
| 9 | HPA + Liveness/Readiness probes | deployment 완성 |
| 10 | 구조화된 로깅 (structlog JSON, stdout) + **LLM Tracing spans** + **SLI 메트릭 로깅** | 로깅 + Observability |
| 10 | /help 명령어 + "결과 없음" 응답 | 사용자 경험 완성 |
| 10 | E2E 테스트 + 배포 검증 | EKS 배포 완료 |

#### Phase 1 성공 기준:
- [ ] Slack에서 @mention으로 질문하면 Confluence/Jira 검색 후 출처 포함 답변 제공
- [ ] 캐시 히트 시 ~50ms, 캐시 미스 시 15초 이내 응답
- [ ] "검색 중..." 임시 메시지 표시 후 결과로 교체
- [ ] 주민등록번호, 카드번호 PII 마스킹
- [ ] EKS에 안정적으로 배포되어 운영

### Observability & Monitoring (신규 섹션)

> sre 스킬의 LLM 5 Pillars + Langfuse 기반 설계

**LLM 5 Pillars of Observability:**

| Pillar | 메트릭 | MVP 구현 | Phase 2 |
|--------|--------|----------|---------|
| **Reliability** | Error Rate, TTFT, E2E Latency | structlog JSON 로깅 | Langfuse tracing |
| **Quality** | Faithfulness, User Satisfaction | 수동 피드백 | RAGAS + LLM-as-Judge |
| **Safety** | Injection 차단율, PII 노출 | 로그 카운터 | Guardrails 대시보드 |
| **Cost** | Token Usage, Cost per Request | Anthropic 대시보드 | Langfuse cost tracking |
| **Governance** | Audit Log | 구조화 로깅 | 전용 audit 테이블 |

**핵심 메트릭 (SLI 기반):**

| SLI | 측정 | SLO 목표 | 알림 조건 |
|-----|------|----------|-----------|
| E2E Latency (cache hit) | 요청~응답 | p95 < 200ms | p95 > 500ms |
| E2E Latency (cache miss) | 요청~응답 | p95 < 20s | p95 > 25s |
| Error Rate | 5xx / total | < 5% | > 10% (5분 윈도우) |
| Cache Hit Rate | hits / total | > 30% (1주) | < 15% |
| Claude API Latency | TTFT | < 2s | > 5s |

**LLM Tracing (MVP: structlog, Phase 2: Langfuse):**

```
Trace: query_{message_ts}
├── Span: input_guard (duration, pii_detected_count)
├── Span: cache_lookup (duration, hit/miss, similarity_score)
├── Span: llm_call (duration, model, input_tokens, output_tokens, cost)
│   ├── Span: tool_call:search_confluence (duration, results_count)
│   └── Span: tool_call:search_jira (duration, results_count)
├── Span: output_guard (duration, pii_filtered_count)
└── Span: cache_store (duration, ttl)
```

**MVP 구현 (Day 10):**
- structlog JSON 포맷으로 모든 파이프라인 단계 로깅
- 각 로그에 `trace_id` (message_ts), `user_id`, `channel_id` 포함
- CloudWatch Logs Insights로 메트릭 쿼리 (EKS 기본 연동)

**Phase 2: Langfuse 통합:**
- OSS 무료, Docker Compose로 자체 호스팅 가능
- Anthropic SDK와 1줄 통합: `from langfuse.anthropic import AnthropicWrapper`
- 토큰 비용 자동 추적 + 프롬프트 버전 관리 + eval 파이프라인
- 참고: [Langfuse](https://langfuse.com/)

### Cost Optimization Strategy (신규 섹션)

> llm-gateway, prompt-engineering 스킬 기반 설계

**월간 비용 상세 분석 (Sonnet 4.6 기준):**

```
가정: 일 50 질문, 월 22 영업일 = 1,100 질문/월
      캐시 히트율 30% (1주차) → 50% (4주차)

[Cache Miss 시나리오] (770 질문/월, 히트율 30%)
├── Input:  ~4K tokens/요청 × 770 = 3.08M tokens × $3/M   = $9.24
├── Output: ~1K tokens/요청 × 770 = 770K tokens × $15/M    = $11.55
├── Embedding: 1 질문 + 1 캐시 저장 = 1,540 호출 × $0.02/M = $0.03
└── 소계: ~$20.82/월

[Prompt Caching 적용 시]
├── System prompt (~2K) + Tools (~1K) = 3K cached tokens
├── Cache read: 3K × 770 × $0.3/M = $0.69 (vs $6.93 without = 90% 절감)
├── Cache write: 최초 1회 + 5분마다 갱신 ≈ 무시 가능
└── 소계: ~$14.58/월 (30% 절감)

[Model Routing 추가 적용 시 (Phase 2)]
├── FAQ 질문 (50%): Haiku → $0.80/M input, $4/M output
├── 복잡한 질문 (50%): Sonnet → $3/M input, $15/M output
└── 소계: ~$10.50/월 (50% 절감)
```

**비용 제어 메커니즘:**

| 메커니즘 | 구현 | 효과 |
|----------|------|------|
| Prompt Caching | `cache_control` on system + tools | 75-90% input 절감 |
| Semantic Cache | pgvector 유사 질문 재사용 | 30-50% 전체 요청 절감 |
| max_tokens 제한 | `max_tokens=4096` | 과도한 출력 방지 |
| Max tool rounds | 5라운드 제한 | 무한 루프 방지 |
| 월간 예산 알림 | Anthropic 대시보드 + CloudWatch | $200/월 초과 시 알림 |

**Phase 2: Content-based Model Routing (30-46% 추가 절감):**
- 질문 복잡도 분류기: 키워드 기반 (MVP) → 임베딩 기반 (Phase 2)
- 단순 FAQ/상태 조회 → Haiku (빠르고 저렴)
- 복합 분석/비교 질문 → Sonnet (정확도 우선)
- Confidence Escalation: Haiku 응답의 confidence 낮으면 Sonnet으로 재시도

### Phase 2: Vector DB Hybrid + Slack 검색 (Week 3-4)

| 태스크 | 설명 |
|--------|------|
| Confluence 문서 인덱싱 | pgvector에 문서 청크 저장 (Semantic Chunking, 500-1000 토큰) |
| Hybrid Search | Vector + BM25 (RRF 결합) — pgvector 한계로 별도 BM25 인덱스 필요 |
| Slack 검색 추가 | OAuth User Token 확보 → search_slack tool 활성화 |
| 캐시 무효화 | Confluence webhook → 관련 캐시 무효화 |
| 접근 제어 기본 | 채널/사용자 allowlist 설정 |

(see brainstorm: docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md — "Phase Roadmap")

### Phase 3: 고도화 (이후)

| 태스크 | 설명 |
|--------|------|
| Re-ranker | Cross-encoder 기반 재순위화 (+33% 정확도, 복잡 쿼리 +52%) |
| 피드백 루프 | 👍/👎 Slack reaction → 품질 개선 신호 |
| 멀티턴 대화 | Thread 기반 대화 이력 유지 |
| 대시보드 | 사용 통계 (쿼리 수, 캐시 히트율, 비용) — Langfuse 기반 |
| Retrieval Guard | RAG 결과 내 indirect injection 감지 (Layer 3) |
| Model Routing | FAQ→Haiku, 복잡→Sonnet (Content-based, 30-46% 비용 절감) |
| Prompt Compression | LLMLingua로 context 압축 (60-70% 토큰 절약, 품질 손실 < 5%) |
| DSPy 최적화 | BootstrapFewShot / MIPROv2로 system prompt 자동 최적화 |

#### Research Insights: Testing & Evaluation

**LLM Evaluation 파이프라인 (Phase 2 — MEDIUM PRIORITY):**

```
Golden Dataset (20+ Q&A 쌍)
    ↓
RAGAS 메트릭 자동 평가:
├── Faithfulness: 답변이 검색 결과에 근거하는가
├── Answer Relevancy: 답변이 질문에 적합한가
├── Context Precision: 검색 결과가 관련 있는가
└── Context Recall: 필요한 정보를 모두 찾았는가
    ↓
promptfoo CI/CD 통합:
├── 프롬프트 변경 시 자동 eval 실행
├── 품질 게이트: score < threshold → 배포 차단
└── 리그레션 감지 (58.8% 프롬프트 조합에서 업데이트 시 하락 발생)
```

**Golden Dataset 구성 (Phase 1.5):**
- 핵심 시나리오 20개+ 질문-답변 쌍:
  - Confluence 문서 검색 (5개): 온보딩 가이드, API 문서, 아키텍처 결정 등
  - Jira 이슈 검색 (5개): 버그 상태, 스프린트 진행, 담당자 확인 등
  - 혼합 검색 (5개): 여러 소스 결합 필요한 질문
  - 답변 불가 (3개): 존재하지 않는 정보 → "확인되지 않음" 응답 기대
  - Edge case (2개+): PII 포함 질문, 매우 긴 질문

**LLM-as-Judge (Phase 2):**
- Pointwise Evaluation: 답변 품질 1-5점 자동 평가
- 주의: Position Bias (~40%) → 순서 교체 후 평균
- 참고: testing-architecture 스킬 LLM Evaluation 섹션

---

## Alternative Approaches Considered

| 접근 방식 | 장점 | 단점 | 불채택 이유 |
|-----------|------|------|-------------|
| Traditional RAG (처음부터) | 응답 속도 1-3초, 검색 정밀도 높음 | MVP 4-6주, 인덱싱 파이프라인 필요 | MVP 타임라인(2주) 초과 |
| Hybrid (처음부터) | 최적 성능 | MVP 6주+, 운영 복잡도 높음 | 복잡도 과다 |
| OpenAI API 사용 | 성숙한 SDK | 사용자 요구사항과 불일치 | 브레인스토밍에서 Claude 결정 |
| Web UI + Slack | 풍부한 UI | 추가 개발 비용, 접근성 낮음 | 기존 도구(Slack) 활용이 더 효과적 |
| Redis VSS | 캐시 특화 | 별도 인프라, Phase 2 재활용 불가 | pgvector로 캐시 + VectorDB 통합 |

(see brainstorm: docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md — "Approach 선택")

---

## System-Wide Impact

### Interaction Graph

```
[User @mention]
  → Slack Events API (Socket Mode WebSocket)
    → Slack Bolt AsyncApp.handle_mention()
      → QueryHandler.handle() [asyncio.create_task]
        → InputGuard.process() [PII + Injection]
          → SemanticCache.find_similar() [pgvector query]
            ├─ HIT → return cached
            └─ MISS → ClaudeClient.ask()
                        → Anthropic Messages API
                          → Tool Use: search_confluence()
                            → Confluence REST API (CQL)
                          → Tool Use: search_jira()
                            → Jira REST API v3 (JQL)
                          → Final answer generation
                        → OutputGuard.process() [PII re-check]
                        → SemanticCache.store() [background task]
      → Slack chat.update() [결과로 교체]
```

### Error Propagation

```
Confluence API error (timeout/5xx)
  → confluence_client raises SearchError
    → ClaudeClient catches, returns partial tool_result with error note
      → Claude generates answer from available sources + disclaimer
        → User sees answer with "⚠️ Confluence 검색 제한" 경고

Anthropic API error (429/5xx)
  → anthropic SDK auto-retries (max 3, exponential backoff)
    → 3회 실패 → raises APIError
      → QueryHandler catches, returns error message
        → Slack bot sends "답변 생성 실패" 메시지

pgvector connection error
  → asyncpg raises ConnectionError
    → SemanticCache returns None (cache bypass)
      → QueryHandler proceeds without cache (Agent 직접 호출)
        → User gets answer (cache miss와 동일 경험, 다소 느림)
```

### State Lifecycle Risks

| 상태 | 위험 | 완화 |
|------|------|------|
| 캐시 저장 중 서버 종료 | 캐시 미저장 (답변은 이미 전송됨) | 무해 — 다음 동일 질문 시 재생성 |
| Tool 호출 중 서버 종료 | 진행 중 요청 유실 | graceful shutdown (25초 대기) |
| DB 마이그레이션 실패 | 캐시 테이블 부재 | 캐시 없이 작동 가능 (graceful degradation) |

### Integration Test Scenarios

1. **Cache HIT E2E**: 동일 질문 2회 → 2번째 응답이 50ms 이내
2. **Partial source failure**: Confluence mock 503 → Jira 결과만으로 답변 + 경고 메시지
3. **PII round-trip**: 주민번호 포함 질문 → Claude 응답에 주민번호 미포함 확인
4. **Timeout**: Claude mock 30초 지연 → 25초 후 타임아웃 메시지
5. **Socket Mode reconnect**: WebSocket 강제 종료 → 자동 재연결 후 메시지 수신

---

## Acceptance Criteria

### Functional Requirements

- [ ] Slack @mention으로 질문 시 Confluence + Jira 검색 후 답변 생성
- [ ] 답변에 출처 링크(Confluence 페이지 URL, Jira 이슈 URL) 포함
- [ ] "검색 중..." 임시 메시지 즉시 표시 후 결과로 교체
- [ ] Thread reply로 응답 (reply_broadcast=true)
- [ ] DM으로 질문 시에도 동일하게 작동
- [ ] `/help` 명령어로 봇 기능 안내
- [ ] 검색 결과 없을 시 "관련 정보를 찾지 못했습니다" 안내

### Non-Functional Requirements

- [ ] 캐시 히트: p95 < 200ms
- [ ] 캐시 미스: p95 < 20초
- [ ] 가용성: 99.5% (월간 다운타임 < 3.6시간)
- [ ] 동시 사용자 10명 처리
- [ ] 주민등록번호, 카드번호 100% 마스킹

### Quality Gates

- [ ] Unit 테스트 커버리지 > 80% (핵심 로직)
- [ ] Integration 테스트: E2E 파이프라인 5개 시나리오
- [ ] PII 필터 테스트: 10개 이상 한국어 PII 패턴
- [ ] CQL/JQL Injection 방어 테스트: 5개 이상 injection 시나리오
- [ ] Prompt Caching 동작 확인: cache read/write 로그 검증
- [ ] LLM Tracing 로그: 전체 파이프라인 span이 structlog에 기록됨

---

## Success Metrics

| 메트릭 | 목표 | 측정 방법 |
|--------|------|-----------|
| 응답 시간 (캐시 히트) | p95 < 200ms | 로그 분석 |
| 응답 시간 (캐시 미스) | p95 < 20초 | 로그 분석 |
| 캐시 히트율 | > 30% (1주차), > 50% (4주차) | pgvector 쿼리 통계 |
| 일일 사용량 | > 20 질문/일 (팀 20명 기준) | 로그 카운트 |
| 에러율 | < 5% | 에러 로그 비율 |
| Claude API 비용 | < $200/월 (sonnet 기준) | Anthropic 대시보드 |
| 사용자 만족도 | 정성적 피드백 (Phase 1) | Slack 설문 |

---

## Dependencies & Prerequisites

### 구현 전 확인 필수 (from brainstorm)

| # | 항목 | 가정 | 확인 방법 | 상태 |
|---|------|------|-----------|------|
| 1 | Atlassian 환경 | Cloud (`*.atlassian.net`) | 관리자 확인 | ❓ |
| 2 | Slack 플랜 | Bot Token scopes 사용 가능 | Slack 관리자 확인 | ❓ |
| 3 | AWS RDS | PostgreSQL 14+ (pgvector 호환) | 기존 RDS 확인 or 신규 생성 | ❓ |
| 4 | Anthropic API Key | 사용 가능한 API 키 | Anthropic 콘솔 | ❓ |
| 5 | OpenAI API Key | text-embedding-3-small 사용 | OpenAI 콘솔 | ❓ |
| 6 | EKS 클러스터 | 기존 클러스터 or 신규 생성 | DevOps 확인 | ❓ |
| 7 | Slack App 생성 | Bot Token + App-Level Token | Slack admin 승인 | ❓ |

(see brainstorm: docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md — "전제 조건")

### 기술 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| Python | >=3.10 | 런타임 (Anthropic SDK, FastAPI 제약) |
| `anthropic[aiohttp]` | ~0.84.0 | Claude Messages API + Tool Use + **aiohttp 백엔드** |
| `fastapi` | ~0.128.0 | HTTP 서버 + lifespan |
| `uvicorn` | latest | ASGI 서버 |
| `slack-bolt` | 1.27.0 | Slack Bot 프레임워크 |
| `aiohttp` | latest | Slack Bolt async 지원 + Anthropic 백엔드 |
| `asyncpg` | latest | PostgreSQL async driver |
| `pgvector` | 0.4.2 | pgvector Python client (**halfvec 지원**) |
| `openai` | ~2.11.0 | Embedding API |
| `presidio-analyzer` | latest | PII 탐지 |
| `presidio-anonymizer` | latest | PII 마스킹 |
| `spacy` | latest | 한국어 NLP 모델 (`ko_core_news_sm`) — Presidio 한국어 탐지 강화 |
| `pydantic-settings` | latest | 환경 변수 관리 |
| `structlog` | latest | 구조화된 로깅 + LLM tracing |
| `tenacity` | latest | Retry + Circuit Breaker 패턴 |

---

## Risk Analysis & Mitigation

| 리스크 | 심각도 | 가능성 | 완화 방안 |
|--------|--------|--------|-----------|
| 캐시 통한 권한 상승 | HIGH | HIGH | MVP: 봇 서비스 계정이 접근 가능한 공개 콘텐츠만 제공. Phase 2: per-user OAuth |
| Prompt injection | HIGH | MEDIUM | Spotlighting + tool parameter validation. Phase 2: retrieval guard |
| Claude API 비용 초과 | MEDIUM | MEDIUM | max_tokens 제한, 모델 선택 (sonnet), 캐시 히트율 모니터링 |
| Atlassian API rate limit | MEDIUM | MEDIUM | exponential backoff, 캐시로 API 호출 감소 |
| Slack search:read 제약 | HIGH | CONFIRMED | Phase 1에서 Slack 검색 제외, Phase 2에서 User Token 확보 |
| 한국어 PII 미탐지 | MEDIUM | LOW | Presidio KR 패턴 + 커스텀 regex + 한국어 NLP 모델(spaCy ko) 설정, 테스트 강화 |
| pgvector 0.92 threshold 부적합 | MEDIUM | MEDIUM | 실 데이터로 A/B 테스트, 0.88-0.95 범위 튜닝 |
| Socket Mode 연결 불안정 | LOW | LOW | Slack Bolt 내장 재연결, readiness probe |
| CQL/JQL Injection | HIGH | LOW | Tool Guard에서 특수문자 이스케이프 + allowlist 검증 |
| Indirect Prompt Injection (RAG) | MEDIUM | MEDIUM | Phase 1: Spotlighting으로 경감, Phase 2: Retrieval Guard 도입 |
| EU AI Act 비준수 | MEDIUM | LOW | AI 생성 면책 문구 + 출처 표시 (2026년 8월 전면 시행) |

---

## Future Considerations

- **Embedding 모델 업그레이드**: text-embedding-3-small → BGE-M3-ko (한국어 특화) 또는 Cohere embed-v4 (다국어)
  - BGE-M3-ko: 한국어 최적화, 자체 호스팅 필요 (GPU or CPU inference)
  - Cohere embed-v4: $0.10/1M, 100+ 언어, 관리형 API
  - 주의: 모델 변경 시 `embedding_model` 컬럼으로 분리 관리 (halfvec 스키마에 이미 반영)
  - 참고: [MMTEB Benchmark](https://arxiv.org/abs/2502.13595)
- **Multi-turn 대화**: Thread 기반 대화 이력 → Claude messages에 포함
- **Hybrid Search**: pgvector는 하이브리드 검색 미지원 (rag-architecture 스킬 확인)
  - 대안 1: PostgreSQL `ts_vector` + GIN 인덱스로 BM25 검색 → RRF 결합 (k=60, NDCG 26-31% 개선)
  - 대안 2: Weaviate/Qdrant로 Vector DB 전환 (내장 BM25)
  - RRF Score = Σ 1/(k + rank_i), k=60 기본
- **비용 최적화**: ~~Claude Prompt Caching~~ → **MVP에서 이미 적용** (Enhancement Summary 참조)
  - Phase 2: Content-based Model Routing (30-46% 추가 절감)
  - Phase 3: Prompt Compression (LLMLingua, 60-70% 토큰 절약)
- **Observability**: ~~Langfuse 도입~~ → **MVP에서 structlog 기반 tracing 적용**, Phase 2에서 Langfuse 통합
- **DSPy 자동 최적화**: MIPROv2 optimizer로 system prompt + few-shot 자동 최적화
  - Golden Dataset 확보 후 적용 가능 (Phase 3)
- **Corrective RAG**: Agent가 검색 결과 품질을 자체 판단하고 보정
  - Faithfulness +15% 개선 기대 (rag-architecture 스킬 참조)

---

## Sources & References

### Origin

- **Brainstorm document:** [docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md](docs/brainstorms/2026-02-27-internal-rag-chatbot-brainstorm.md)
  - Key decisions carried forward: Agentic RAG MVP → Hybrid 전략, Slack Bot Socket Mode, pgvector Semantic Cache
  - **SDK 변경 권고**: `claude_agent_sdk` → `anthropic` SDK (Messages API + Tool Use)

### Internal References (Repository Skills)

| 스킬 | 활용 내용 |
|------|-----------|
| `rag-architecture` | RAG 진화 경로, pgvector 평가, Hybrid Search RRF |
| `ai-safety` | 5-layer 방어 아키텍처, Presidio PII, Spotlighting |
| `llm-gateway` | Semantic Cache 히트율, Circuit Breaker 설정 |
| `ai-agent` | Tool Use 루프, action limit, timeout |
| `sre` | LLM 5 Pillars Observability, TTFT/TPOT 메트릭 |
| `cloud-native` | 12-Factor, K8s probes, graceful shutdown |
| `prompt-engineering` | System prompt 설계, Dynamic Assembly |

### External References

| 항목 | URL/출처 |
|------|----------|
| Anthropic Python SDK | https://github.com/anthropics/anthropic-sdk-python |
| Claude Agent SDK | https://github.com/anthropics/claude-agent-sdk-python |
| Slack Bolt for Python | https://github.com/slackapi/bolt-python |
| pgvector | https://github.com/pgvector/pgvector |
| pgvector-python | https://github.com/pgvector/pgvector-python |
| OpenAI Embeddings | https://platform.openai.com/docs/guides/embeddings |
| Presidio | https://github.com/microsoft/presidio |
| FastAPI Lifespan | https://fastapi.tiangolo.com/advanced/events/ |
| Jira REST API v3 | Atlassian Developer Documentation |

### Research Findings

- **Jira v2 API deprecated**: `POST /rest/api/3/search/jql` 사용 필수
- **HNSW vs IVFFlat**: 100K 벡터에서 HNSW가 15.5x 빠름
- **Presidio 한국어**: KR_RRN (체크섬 검증) + 4개 한국어 엔티티 내장
- **Slack `search:read`**: Bot Token 불가, User Token 필요
- **Moveworks 패턴**: Vector DB(안정 문서) + Live API(실시간) 병행이 Enterprise RAG 표준

### Deepening Research Findings (2026-02-27)

- **Prompt Caching**: system prompt + tools 캐시 → read 0.1x, write 1.25x (5분), workspace-level isolation (2026-02-05~)
- **Think Tool vs Extended Thinking**: 순차 tool use → Think Tool 적합, 비순차 → Extended Thinking 적합 ([Anthropic Blog](https://www.anthropic.com/engineering/claude-think-tool))
- **pgvector halfvec**: 반정밀도로 메모리 50% 절약, ~4-6 KB per 1536-dim (m=16) ([AWS Blog](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/))
- **pgvector iterative scanning**: 0.8.0 `relaxed_order` 모드가 필터링 쿼리에서 최적 ([Crunchy Data](https://www.crunchydata.com/blog/hnsw-indexes-with-postgres-and-pgvector))
- **Anthropic SDK aiohttp**: `anthropic[aiohttp]` + `DefaultAioHttpClient()`로 async 성능 개선 ([SDK GitHub](https://github.com/anthropics/anthropic-sdk-python))
- **Presidio 한국어 NLP**: spaCy `ko_core_news_sm` 설정 필요, context words 한국어 업데이트 권장 ([Presidio Docs](https://microsoft.github.io/presidio/analyzer/languages/))
- **BGE-M3-ko**: 한국어 최적화 embedding 모델, text-embedding-3-small 대비 한국어 성능 우수 가능성 ([PromptLayer](https://www.promptlayer.com/models/bge-m3-ko))
- **EU AI Act**: 2026년 8월 전면 시행, 챗봇은 "제한 위험" → AI 사용 고지 의무
- **RRF (Hybrid Search)**: Score = Σ 1/(k+rank_i), k=60, NDCG 26-31% 개선 (rag-architecture 스킬)
- **RAGAS**: Faithfulness, Answer Relevancy, Context Precision, Context Recall 4대 메트릭 (testing-architecture 스킬)
- **LLM 5 Pillars**: Reliability, Quality, Safety, Cost, Governance (sre 스킬)
- **Re-ranker 효과**: 정확도 +33%, 복잡한 쿼리 +52% (rag-architecture 스킬)

### Skills Applied

| 스킬 | 적용 포인트 | 핵심 기여 |
|------|------------|-----------|
| rag-architecture | 5 | Hybrid Search RRF, Lost-in-the-Middle, Corrective RAG, pgvector 한계 |
| ai-safety | 5 | OWASP LLM Top 10, EU AI Act, Retrieval Guard, CQL/JQL Injection |
| llm-gateway | 4 | Prompt Cache, Semantic Cache 히트율, Circuit Breaker, Model Routing |
| ai-agent | 3 | Think Tool, Action Limits, Tool Sandboxing |
| prompt-engineering | 3 | Dynamic Assembly, DSPy, Prompt Compression |
| sre | 4 | LLM 5 Pillars, Langfuse, TTFT/TPOT, SLI/SLO |
| cloud-native | 2 | 12-Factor 검증, Resilience 계층 (Graceful Degradation) |
| testing-architecture | 3 | RAGAS, LLM-as-Judge, Golden Dataset, promptfoo |
