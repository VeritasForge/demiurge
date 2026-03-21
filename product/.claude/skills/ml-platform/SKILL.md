---
description: MLOps, Model Serving, Feature Store, LLM Fine-tuning, GPU Serving
user-invocable: false
---

# ML Platform Skill

ML 모델 서빙, MLOps 파이프라인, 모델 모니터링, LLM Fine-tuning, GPU 서빙 인프라를 설계합니다.

## 핵심 역량

### MLOps Maturity Model
| Level | 이름 | 특징 |
|-------|------|------|
| 0 | Manual | 수동 실험, 수동 배포 |
| 1 | ML Pipeline | 자동화된 학습 파이프라인 |
| 2 | CI/CD for ML | 자동화된 모델 빌드/테스트/배포 |
| 3 | Full MLOps | 자동 재학습, 드리프트 감지 |

### 앙상블 전략
```
10개 모델 예측:
├── Model 1: prediction_1
├── Model 2: prediction_2
├── ...
└── Model 10: prediction_10

최종 결과:
├── mean = avg(predictions) → 점수
└── std = std(predictions) → 불확실성
```

## 모델 모니터링 메트릭

### 성능 메트릭
- **Inference Latency**: p50, p95, p99
- **Throughput**: predictions/second
- **Model Error Rate**: 실패한 추론 비율

### 품질 메트릭
- **Prediction Distribution**: 예측값 분포 모니터링
- **Confidence Distribution**: 불확실성(std) 분포
- **Data Drift**: 입력 데이터 분포 변화

## LLM Fine-tuning

### Fine-tuning 방법론 선택

| 방법 | 적합 시나리오 | 비용 | 품질 |
|------|-------------|------|------|
| **SFT** | 도메인 적응, 포맷 학습 | 낮음 | 기본 |
| **DPO** | 선호도 정렬, RLHF 대체 | 중간 | 높음 |
| **RLHF** | 정교한 정렬 | 높음 | 최고 |
| **LoRA/QLoRA** | PEFT, 메모리 절약 | 낮음 | SFT와 유사 |

### Prompting vs RAG vs Fine-tuning 판단

```
             ┌───────────────────┐
             │ 도메인 지식 필요?  │
             └────────┬──────────┘
              No      │      Yes
         ┌────────────┴─────────────┐
         ▼                           ▼
   Prompting              ┌─────────────────┐
   (Zero/Few-shot)        │ 지식 업데이트    │
                          │ 빈번?           │
                          └────────┬────────┘
                          Yes      │     No
                     ┌─────────────┴──────────┐
                     ▼                         ▼
                   RAG                    Fine-tuning
```

### GPU Serving 엔진 비교

| 엔진 | 핵심 기술 | 적합 시나리오 |
|------|----------|-------------|
| **vLLM** | PagedAttention, 14-24x 처리량 | 범용 LLM 서빙 (사실상 표준) |
| **TGI** | HuggingFace 생태계, Rust | HF 모델 빠른 배포 |
| **TensorRT-LLM** | NVIDIA 최적화 | 극한 성능 (NVIDIA GPU) |
| **Ray Serve** | 파이프라인 오케스트레이션 | 복잡한 ML 파이프라인 |

### Continuous Batching

```
전통 배칭: [Req1, Req2, Req3] → 가장 긴 요청 끝날 때까지 대기
Continuous: [Req1 완료] → 즉시 Req4 슬롯 투입 (2-4x 처리량 향상)
```

## 사용 시점
- 새 모델 배포 검토
- 모델 성능 저하 분석
- Feature Engineering 설계
- 앙상블 전략 변경
- LLM Fine-tuning 전략 수립
- GPU 서빙 엔진 선택
- 모델 양자화 (GPTQ, AWQ) 결정

## 참고 조사
- LLM Fine-tuning 상세: [research/ai-backend/fine-tuning-pipeline.md](../../../research/ai-backend/fine-tuning-pipeline.md)
- GPU 서빙 상세: [research/ai-backend/common-infra.md](../../../research/ai-backend/common-infra.md)
