---
description: Prompt Management, 버저닝, A/B Testing, DSPy, Dynamic Assembly, Prompt Lifecycle
user-invocable: false
---

# Prompt Engineering Skill

프롬프트 생명주기 관리, 중앙 레지스트리, 버저닝/배포, A/B 테스트, 자동 최적화를 설계합니다.

## 핵심 역량

### Prompt Lifecycle

```
작성 (Author) ──> 테스트 (Test) ──> 배포 (Deploy) ──> 모니터링 (Monitor)
     │                 │                │                    │
  Template          Eval Suite      Canary/A-B          Quality Metrics
  Registry          Golden Set      Rollback             Cost Tracking
  Version Control   LLM-as-Judge    Feature Flag         Drift Detection
```

### Prompt as Code vs Prompt as Data

| 접근 | 장점 | 단점 | 적합 |
|------|------|------|------|
| **as Code** (Git) | 버전 관리, 코드 리뷰, CI/CD | 비개발자 참여 어려움 | 엔지니어 중심 팀 |
| **as Data** (Registry) | 비개발자 편집, 즉시 배포 | 버전 관리 약함 | 비즈니스 팀 협업 |
| **Hybrid** | 양쪽 장점 | 복잡도 증가 | 성숙한 조직 |

### Prompt Template 아키텍처

```python
# 3계층 템플릿 구조
class PromptTemplate:
    system: str           # 시스템 프롬프트 (역할, 규칙)
    few_shot: list[Example]  # 동적 Few-shot 예시 선택
    user: str             # 사용자 입력 템플릿

# Dynamic Assembly
prompt = (
    system_prompt(role="analyst", rules=["no_pii", "json_output"])
    + few_shot_selector(query, k=3, strategy="semantic")
    + user_template(input=user_query, context=rag_context)
)
```

### Prompt Engineering 패턴

| 패턴 | 효과 | 비용 영향 |
|------|------|----------|
| **Zero-shot** | 기본 | 최소 |
| **Few-shot** | +15-30% 품질 | 토큰 증가 |
| **Chain-of-Thought** | +20-40% 추론 | 출력 토큰 증가 |
| **Self-Consistency** | +10-20% 정확도 | N배 비용 |
| **Tree-of-Thought** | +30-50% 복잡 추론 | 5-10배 비용 |

### DSPy (Programmatic Prompt Optimization)

```
기존: 수동 프롬프트 작성 → 시행착오 → 개선
DSPy: 메트릭 정의 → 자동 최적화 → 최적 프롬프트 생성

핵심 Optimizer:
├── BootstrapFewShot: Few-shot 예시 자동 생성
├── MIPROv2: 프롬프트 + 데모 동시 최적화
├── COPRO: LLM이 프롬프트를 생성/평가
└── SIMBA: 대규모 프로그램 최적화
```

```python
import dspy

# 1. Signature 정의
class QA(dspy.Signature):
    """주어진 컨텍스트에서 질문에 답변"""
    context: str = dspy.InputField()
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

# 2. Module 구성
qa_module = dspy.ChainOfThought(QA)

# 3. Optimizer로 자동 최적화
optimizer = dspy.MIPROv2(metric=answer_exact_match)
optimized = optimizer.compile(qa_module, trainset=train_data)
```

### Prompt Compression (LLMLingua)

```
원본 프롬프트 (1000 토큰)
    ↓ LLMLingua 압축 (불필요 토큰 제거)
압축 프롬프트 (300 토큰) — 품질 손실 < 5%

비용 절감: 60-70% 토큰 절약
```

### A/B Testing Pipeline

```
┌─────────────────────────────────────────┐
│  Traffic Splitter (Feature Flag)         │
│                                          │
│  90% ──> Prompt v2.1 (Control)          │
│  10% ──> Prompt v2.2 (Variant)          │
│                                          │
│  Metrics:                                │
│  ├── Quality: LLM-as-Judge score        │
│  ├── Latency: TTFT, E2E                 │
│  ├── Cost: tokens per request           │
│  └── User: thumbs up/down ratio         │
│                                          │
│  Statistical Significance:               │
│  ├── Bootstrap CI (n=1000)              │
│  └── 최소 500 샘플 per variant          │
└─────────────────────────────────────────┘
```

### Prompt CI/CD

```yaml
# GitHub Actions for Prompt Deployment
on:
  push:
    paths: ['prompts/**']

jobs:
  eval:
    steps:
      - run: promptfoo eval --config prompts/eval.yaml
      - run: |  # 품질 게이트
          if score < threshold: fail
  deploy:
    needs: eval
    steps:
      - run: deploy-prompt --canary 10%
      - run: monitor --duration 1h
      - run: deploy-prompt --full  # 또는 rollback
```

## 플랫폼 비교

| Platform | 유형 | 버저닝 | A/B | 특징 | 적합 |
|----------|------|--------|-----|------|------|
| **Langfuse** | OSS | ✅ | ✅ | Observability 통합 | OSS 선호 |
| **Braintrust** | SaaS | ✅ | ✅ | Eval 통합, 강력한 UI | 팀 협업 |
| **Promptfoo** | OSS | ✅ | ❌ | CI/CD 특화, CLI 중심 | 개발자 중심 |
| **Humanloop** | SaaS | ✅ | ✅ | 비개발자 친화적 | PM 협업 |

## 사용 시점
- 프롬프트 관리 체계 수립
- A/B 테스트 파이프라인 설계
- DSPy 자동 최적화 도입
- 프롬프트 CI/CD 구축
- 비용 최적화 (압축, 캐싱)

## 참고 조사
- 상세 조사: [research/ai-backend/prompt-management.md](../../../research/ai-backend/prompt-management.md)
