---
description: 12-Factor App, K8s Patterns, Deployment Strategies
user-invocable: false
---

# Cloud-Native Skill

12-Factor App, Kubernetes 패턴, 배포 전략을 담당합니다.

## 핵심 역량

### 12-Factor App (Essential)

| # | Factor | 핵심 |
|---|--------|------|
| 3 | **Config** | 환경 변수로 설정 |
| 6 | **Processes** | 무상태 프로세스 |
| 9 | **Disposability** | 빠른 시작/종료 |
| 11 | **Logs** | stdout 스트림 |

### Kubernetes Pod Patterns

| Pattern | 용도 | 예시 |
|---------|------|------|
| **Sidecar** | 보조 기능 추가 | Envoy, Fluentd |
| **Ambassador** | 외부 접근 프록시 | API Gateway |
| **Adapter** | 출력 표준화 | Prometheus exporter |
| **Init Container** | 초기화 작업 | DB migration, 설정 |

### Deployment Strategies

| 전략 | 특징 | 롤백 |
|------|------|------|
| **Blue-Green** | 환경 전환 | 즉시 (라우팅) |
| **Canary** | 점진적 트래픽 | 자동 (메트릭 기반) |
| **Rolling** | 순차 교체 | 자동 (K8s 기본) |

### Resilience Patterns

```
Circuit Breaker States:
CLOSED → (failures) → OPEN → (timeout) → HALF-OPEN
  ↑                                          │
  └──────────── (success) ──────────────────┘
```

| Pattern | 목적 |
|---------|------|
| **Circuit Breaker** | 연쇄 장애 방지 |
| **Retry + Backoff** | 일시적 장애 복구 |
| **Bulkhead** | 리소스 격리 |
| **Timeout** | 무한 대기 방지 |

### Service Mesh

```
Data Plane: Sidecar 프록시 (Envoy)
Control Plane: 설정 관리 (Istio/Linkerd)

제공 기능:
- mTLS (서비스 간 암호화)
- Traffic Management
- Observability
```

## 평가 체크리스트

- [ ] 12-Factor 준수?
- [ ] 무상태 설계?
- [ ] Health check 구현?
- [ ] Graceful shutdown?
- [ ] Resource limits 설정?
- [ ] Circuit Breaker 적용?

## 사용 시점
- 클라우드 마이그레이션
- 컨테이너화 전략 수립
- 배포 전략 결정
- 복원력 패턴 적용
