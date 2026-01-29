---
description: MLOps, Model Serving, Feature Store
user-invocable: false
---

# ML Platform Skill

ML 모델 서빙, MLOps 파이프라인, 모델 모니터링을 설계합니다.

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

## 사용 시점
- 새 모델 배포 검토
- 모델 성능 저하 분석
- Feature Engineering 설계
- 앙상블 전략 변경
