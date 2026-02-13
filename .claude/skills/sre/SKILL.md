---
description: SRE Principles, SLO/SLI/SLA, Observability, LLM Observability, 토큰/비용 추적
user-invocable: false
---

# SRE Skill

신뢰성 엔지니어링, SLO, 모니터링, 인시던트 관리, LLM Observability를 담당합니다.

## 핵심 역량

### Google SRE 핵심 원칙
1. **Embracing Risk**: 적절한 신뢰성 수준 결정
2. **SLOs and Error Budgets**: 신뢰성의 정량적 측정
3. **Eliminating Toil**: 자동화 가능한 작업 제거
4. **Monitoring**: 4 Golden Signals
5. **Release Engineering**: 안전한 배포
6. **Simplicity**: 복잡성은 신뢰성의 적

### 4 Golden Signals
| Signal | 설명 | 메트릭 예시 |
|--------|------|-------------|
| Latency | 요청 처리 시간 | p50, p95, p99 |
| Traffic | 시스템 수요 | RPS, QPS |
| Errors | 실패율 | 5xx 비율 |
| Saturation | 리소스 포화도 | CPU, Memory, Queue |

### SLI → SLO → SLA
```
SLA (외부 계약, 법적 구속력)
 └── SLO (내부 목표, 더 엄격)
      └── SLI (실제 측정 지표)
```

### Error Budget 계산
```
Error Budget = 1 - SLO

예: SLO 99.9% (월간)
Error Budget = 0.1% = 43.2분/월
```

## Error Budget 정책

| Budget 잔여 | 조치 |
|-------------|------|
| > 50% | 새 기능 개발 우선 |
| 20-50% | 균형 있는 접근 |
| < 20% | 신뢰성 작업 우선 |
| 소진 | 기능 동결, 신뢰성 집중 |

## 인시던트 심각도

| Severity | 정의 | 응답 시간 |
|----------|------|-----------|
| SEV1 | 전체 시스템 장애 | 15분 |
| SEV2 | 주요 기능 장애 | 30분 |
| SEV3 | 부분 기능 저하 | 2시간 |
| SEV4 | 경미한 이슈 | 24시간 |

## Post-mortem 템플릿

```markdown
# Incident: [제목]

## Summary
- Duration: [시간]
- Impact: [영향]
- Root Cause: [원인]

## Timeline
| Time | Event |
|------|-------|

## Action Items
| Priority | Action | Owner |
|----------|--------|-------|

## Lessons Learned
- What went well:
- What went wrong:
- Where we got lucky:
```

## LLM Observability

### LLM 5 Pillars of Observability

| Pillar | 메트릭 | 도구 |
|--------|--------|------|
| **Reliability** | Error Rate, TTFT, E2E Latency | OTel, Datadog |
| **Quality** | Hallucination Rate, User Satisfaction | Langfuse, Braintrust |
| **Safety** | Injection 차단율, PII 노출 | Guardrails 메트릭 |
| **Cost** | Token Usage, Cost per Request | Helicone, Langfuse |
| **Governance** | Audit Log, Compliance | 커스텀 |

### LLM 핵심 메트릭

| 메트릭 | 설명 | 권장 목표 |
|--------|------|----------|
| **TTFT** | Time to First Token | < 500ms |
| **TPOT** | Time per Output Token | < 50ms |
| **E2E Latency** | 전체 응답 시간 | < 3s (간단 쿼리) |
| **Token Cost** | 요청당 토큰 비용 | 모니터링 |
| **Hallucination Rate** | 환각 발생률 | < 5% |

### LLM Tracing (OpenTelemetry)

```
Trace: user_request_123
├── Span: input_guard (2ms)
├── Span: prompt_assembly (5ms)
├── Span: cache_lookup (1ms) → MISS
├── Span: llm_call (1200ms)
│   ├── model: claude-3.5-sonnet
│   ├── input_tokens: 1500
│   ├── output_tokens: 300
│   └── cost: $0.012
├── Span: output_guard (3ms)
└── Span: total (1215ms)
```

### Observability 플랫폼 비교

| Platform | 유형 | 강점 | 가격 |
|----------|------|------|------|
| **Langfuse** | OSS | 종합 (Trace+Eval+Cost) | 무료/저렴 |
| **Helicone** | SaaS | 비용 추적 특화, 1줄 통합 | 무료 tier |
| **LangSmith** | SaaS | LangChain 네이티브 | 유료 |
| **Arize Phoenix** | OSS | ML 관찰성 확장 | 무료 |

## 사용 시점
- SLO 설정/검토
- 인시던트 대응
- 용량 계획
- 모니터링 설계
- 신뢰성 개선
- LLM 비용/품질 모니터링 설계
- LLM 트레이싱 아키텍처 설계
- AI 시스템 SLO 정의

## 참고 조사
- LLM Observability 상세: [research/ai-backend/observability.md](../../../research/ai-backend/observability.md)
