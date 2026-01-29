# Cloud-Native Rules

---
description: 클라우드 네이티브 애플리케이션 설계 규칙
globs:
  - "**/Dockerfile"
  - "**/docker-compose*.yml"
  - "**/k8s/**/*.yaml"
  - "**/helm/**/*.yaml"
  - "**/deployment/**/*.yaml"
---

## 12-Factor 필수 준수 항목

### Factor 3: Config (설정 분리)
```yaml
# Good - 환경 변수 사용
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: url

# Bad - 코드에 하드코딩
database_url = "mysql://localhost:3306/db"
```

### Factor 6: Processes (무상태)
```python
# Good - 외부 저장소 사용
session_data = redis_client.get(session_id)

# Bad - 인메모리 세션
sessions = {}  # 스케일아웃 시 유실
```

### Factor 9: Disposability (빠른 시작/종료)
```python
# Good - Graceful shutdown
import signal

def handle_sigterm(signum, frame):
    # 진행 중인 요청 완료 대기
    server.shutdown(wait=True)

signal.signal(signal.SIGTERM, handle_sigterm)
```

### Factor 11: Logs (stdout)
```python
# Good - stdout으로 출력
import logging
logging.basicConfig(stream=sys.stdout)

# Bad - 파일에 직접 기록
logging.basicConfig(filename='/var/log/app.log')
```

## Container Best Practices

### 이미지 최소화
```dockerfile
# Good - Multi-stage build
FROM node:18 AS builder
COPY . .
RUN npm ci && npm run build

FROM node:18-slim
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/main.js"]

# Bad - 빌드 도구 포함
FROM node:18
COPY . .
RUN npm install
CMD ["node", "src/main.js"]
```

### 비밀정보 관리
```yaml
# Good - Kubernetes Secret
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
data:
  api-key: <base64-encoded>

# Bad - 환경 변수에 평문
env:
  - name: API_KEY
    value: "my-secret-key"
```

### Health Checks
```yaml
# Liveness: 컨테이너 재시작 필요 여부
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

# Readiness: 트래픽 수신 가능 여부
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Kubernetes Resource Management

### Resource Limits 필수
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### PodDisruptionBudget
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2  # 또는 maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
```

## Resilience 패턴

### Circuit Breaker 필수 적용
```kotlin
// 외부 서비스 호출 시 Circuit Breaker 적용
@CircuitBreaker(name = "externalService", fallbackMethod = "fallback")
fun callExternalService(): Response {
    return externalClient.call()
}
```

### Timeout 설정
```yaml
# 모든 외부 호출에 타임아웃 설정
timeout:
  connect: 5s
  read: 30s
  write: 30s
```

### Retry with Backoff
```kotlin
@Retry(name = "externalService", fallbackMethod = "fallback")
// Initial interval: 500ms
// Multiplier: 2
// Max attempts: 3
// Jitter: 0.5
```
