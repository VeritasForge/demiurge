---
description: SRE Principles, SLO/SLI/SLA, Observability
user-invocable: false
---

# SRE Skill

신뢰성 엔지니어링, SLO, 모니터링, 인시던트 관리를 담당합니다.

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

## 사용 시점
- SLO 설정/검토
- 인시던트 대응
- 용량 계획
- 모니터링 설계
- 신뢰성 개선
