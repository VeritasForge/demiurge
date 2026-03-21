---
description: LLM Gateway 아키텍처, 모델 라우팅, Multi-provider 추상화, Streaming, Caching
user-invocable: false
---

# LLM Gateway Skill

다수의 LLM 프로바이더를 단일 API로 통합하고, 지능형 라우팅/복원력/비용 최적화를 제공하는 미들웨어 계층을 설계합니다.

## 핵심 역량

### Gateway 아키텍처

```
┌──────────────────────────────────────────────────────┐
│                   LLM Gateway                         │
│                                                       │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Request  │─>│  Router  │─>│ Provider │─> LLM API  │
│  │ Adapter  │  │          │  │ Adapter  │            │
│  └─────────┘  └──────────┘  └──────────┘            │
│       │            │             │                    │
│  ┌────▼────┐  ┌────▼────┐  ┌────▼────┐              │
│  │Input    │  │Rate     │  │Response │              │
│  │Guard    │  │Limiter  │  │Cache    │              │
│  └─────────┘  └─────────┘  └─────────┘              │
└──────────────────────────────────────────────────────┘
```

### 모델 라우팅 전략

| 전략 | 설명 | 적합 시나리오 |
|------|------|-------------|
| **Content-based** | 입력 복잡도로 모델 선택 | 비용 최적화 (30-46% 절감) |
| **Cost-based** | 예산 기반 라우팅 | 예산 제약 환경 |
| **Latency-based** | 응답 속도 기반 | 실시간 요구 |
| **Quality-based** | 품질 점수 기반 | 품질 우선 서비스 |
| **Confidence Escalation** | 저비용→고비용 점진 에스컬레이션 | 최대 비용 절감 (70%+) |

### Multi-Provider 추상화

```python
# 통합 인터페이스
class LLMGateway:
    async def complete(
        self,
        messages: list[Message],
        model: str = "auto",  # auto-routing
        fallback: list[str] = None,
        stream: bool = False,
        max_tokens: int = 1024,
    ) -> CompletionResponse: ...
```

### Fallback & Circuit Breaker

```
Provider A ──[정상]──> 응답
     │
     └──[실패]──> Circuit Breaker
                      │
                      ├──[CLOSED]──> Provider A 재시도
                      ├──[OPEN]───> Provider B (Fallback)
                      └──[HALF-OPEN]──> Provider A 탐지 요청
```

**Circuit Breaker 설정 권장값**:
- Failure threshold: 5회
- Reset timeout: 30초
- Half-open requests: 3회

### Rate Limiting (토큰 인지)

```yaml
# 요청 수 기반이 아닌 토큰 기반 Rate Limiting
rate_limit:
  strategy: token_based  # request_based보다 공정
  limits:
    - tier: free
      tokens_per_minute: 10000
      requests_per_minute: 60
    - tier: pro
      tokens_per_minute: 100000
      requests_per_minute: 600
```

### Streaming (SSE) 프록시

```
Client ←──SSE──← Gateway ←──SSE──← LLM Provider
         │                  │
    backpressure        format 변환
    handling           (provider별 차이 흡수)
```

**핵심 고려사항**:
- 모든 프로바이더의 SSE 포맷 차이 흡수
- Backpressure 핸들링 (클라이언트 느릴 때)
- 부분 응답도 캐싱 가능하도록 버퍼링

### 캐싱 전략

| 유형 | 히트율 | 비용 절감 | 적합 시나리오 |
|------|--------|----------|-------------|
| **Exact Match** | 15-30% | 15-30% | FAQ, 반복 쿼리 |
| **Semantic Cache** | 40-70% | 40-70% | 유사 질문이 많은 서비스 |
| **Provider Prompt Cache** | - | 75-90% | 긴 시스템 프롬프트 |
| **Multi-tier (L1+L2+L3)** | 60-80% | 50-80% | 프로덕션 |

## 대표 솔루션 비교

| 솔루션 | 유형 | Overhead | 프로바이더 수 | 적합 |
|--------|------|----------|-------------|------|
| **LiteLLM** | OSS (Python) | 8ms P95 | 100+ | 범용, 빠른 통합 |
| **Bifrost** | OSS (Go) | ~11μs | 주요 3사 | 극한 성능 |
| **Portkey** | SaaS | 20-40ms | 200+ | 관리형, 빠른 도입 |
| **Kong AI Gateway** | OSS | 1-5ms | 플러그인 | 기존 Kong 사용 시 |

## Build vs Buy 판단

```
                     ┌──────────────────┐
                     │  프로바이더 수?   │
                     └────────┬─────────┘
                    1-2개     │     3개+
                ┌─────────────┴──────────────┐
                ▼                             ▼
        SDK 직접 사용            ┌───────────────────┐
                                │ 커스텀 라우팅 필요? │
                                └────────┬──────────┘
                              No         │        Yes
                         ┌───────────────┴──────────────┐
                         ▼                               ▼
                   LiteLLM / Portkey              Custom Gateway
                     (OSS / SaaS)               (LiteLLM 기반 확장)
```

## 사용 시점
- LLM 프로바이더 선택/전환 검토
- Multi-provider 통합 설계
- 비용 최적화 전략 수립
- Streaming API 설계
- Rate Limiting / Quota 설계
- Fallback / Circuit Breaker 설계

## 참고 조사
- 상세 조사: [research/ai-backend/llm-gateway.md](../../../research/ai-backend/llm-gateway.md)
- 관련 조사: [research/ai-backend/caching.md](../../../research/ai-backend/caching.md)
