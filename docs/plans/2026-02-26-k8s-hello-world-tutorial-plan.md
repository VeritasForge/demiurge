# K8s Hello World 실무형 튜토리얼 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** K8s 초보자가 Minikube에서 FastAPI Hello World를 Helm으로 배포하고, 실무 수준의 운영 패턴을 체험하는 튜토리얼을 만든다.

**Architecture:** 튜토리얼 문서(tutorial.md)를 중심으로, 사용자가 직접 타이핑할 소스 코드 파일들을 함께 제공한다. Part 1(실습) → Part 2(아키텍처 이해) → Part 3(실무 강화)의 탑다운 구조.

**Tech Stack:** Python 3.12, FastAPI, uvicorn, Docker multi-stage build, Minikube, Helm 3, NGINX Ingress Controller

**참조 설계:** `docs/plans/2026-02-26-k8s-hello-world-tutorial-design.md`
**참조 연구:** `eks-deploy-research.md` (graceful shutdown 심층 연구)
**참조 스킬:** `cloud-native` (12-Factor, K8s Patterns, Deployment Strategies)

---

## Task 1: 프로젝트 디렉토리 + FastAPI 앱 소스 생성

**Files:**
- Create: `docs/tutorials/k8s-hello-world/app/main.py`
- Create: `docs/tutorials/k8s-hello-world/app/requirements.txt`

**Step 1: requirements.txt 생성**

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
```

**Step 2: main.py 생성**

FastAPI 앱 — 다음 엔드포인트 포함:
- `GET /` → Hello World 응답
- `GET /health/live` → liveness probe
- `GET /health/ready` → readiness probe (토글 가능)
- `POST /admin/toggle-ready` → readiness 상태 토글 (Part 3 실험용)
- `GET /slow?seconds=5` → 느린 요청 시뮬레이션 (Part 3 graceful shutdown 실험용)
- `GET /info` → 앱 버전, Pod 이름 등 메타 정보 (ConfigMap/환경변수에서 읽기)

구현 요구사항:
- 구조화된 JSON 로깅 (uvicorn access log + app log)
- SIGTERM 핸들러로 graceful shutdown
- `@app.on_event("shutdown")`에서 리소스 정리 로그 출력
- 환경변수: `APP_ENV`, `APP_VERSION`, `LOG_LEVEL`, `POD_NAME` (기본값 있음)

**Step 3: 로컬에서 동작 확인 커맨드 작성**

```bash
cd docs/tutorials/k8s-hello-world/app
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
# 별도 터미널: curl http://localhost:8080/
```

**Step 4: Commit**

```bash
git add docs/tutorials/k8s-hello-world/app/
git commit -m "feat(tutorial): add FastAPI hello world app source"
```

---

## Task 2: Dockerfile + .dockerignore 생성

**Files:**
- Create: `docs/tutorials/k8s-hello-world/Dockerfile`
- Create: `docs/tutorials/k8s-hello-world/.dockerignore`

**Step 1: .dockerignore 생성**

```
__pycache__
*.pyc
.git
.gitignore
*.md
.env
helm/
```

**Step 2: Dockerfile 생성 (Multi-stage, non-root)**

```dockerfile
# ---- Builder Stage ----
FROM python:3.12-slim AS builder

WORKDIR /build
COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime Stage ----
FROM python:3.12-slim

# non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# builder에서 설치한 패키지만 복사
COPY --from=builder /install /usr/local
COPY app/ .

# non-root로 전환
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/health/live')"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]
```

핵심 포인트 (튜토리얼에서 설명할 것):
- Multi-stage: builder에서 pip install → runtime에 결과만 복사 (이미지 크기 절감)
- non-root: 보안 필수 (root로 실행하면 컨테이너 탈출 시 호스트 위험)
- HEALTHCHECK: Docker 자체 헬스체크 (K8s에서는 probe로 대체되지만 Docker 단독 실행 시 유용)
- exec form CMD: PID 1 문제 방지 (SIGTERM이 앱에 직접 전달됨)

**Step 3: Commit**

```bash
git add docs/tutorials/k8s-hello-world/Dockerfile docs/tutorials/k8s-hello-world/.dockerignore
git commit -m "feat(tutorial): add multi-stage Dockerfile with non-root user"
```

---

## Task 3: Helm 차트 생성

**Files:**
- Create: `docs/tutorials/k8s-hello-world/helm/hello-world/Chart.yaml`
- Create: `docs/tutorials/k8s-hello-world/helm/hello-world/values.yaml`
- Create: `docs/tutorials/k8s-hello-world/helm/hello-world/templates/_helpers.tpl`
- Create: `docs/tutorials/k8s-hello-world/helm/hello-world/templates/namespace.yaml`
- Create: `docs/tutorials/k8s-hello-world/helm/hello-world/templates/configmap.yaml`
- Create: `docs/tutorials/k8s-hello-world/helm/hello-world/templates/deployment.yaml`
- Create: `docs/tutorials/k8s-hello-world/helm/hello-world/templates/service.yaml`
- Create: `docs/tutorials/k8s-hello-world/helm/hello-world/templates/ingress.yaml`

**Step 1: Chart.yaml**

```yaml
apiVersion: v2
name: hello-world
description: K8s Hello World Tutorial - FastAPI App
type: application
version: 0.1.0
appVersion: "1.0.0"
```

**Step 2: values.yaml**

모든 설정의 중앙 관리 — 환경별로 오버라이드 가능:

```yaml
replicaCount: 2

image:
  repository: hello-world
  tag: "1.0.0"
  pullPolicy: IfNotPresent

namespace: hello

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: true
  className: nginx
  host: hello.local

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 250m
    memory: 256Mi

probes:
  liveness:
    path: /health/live
    initialDelaySeconds: 10
    periodSeconds: 10
    failureThreshold: 3
  readiness:
    path: /health/ready
    initialDelaySeconds: 5
    periodSeconds: 5
    failureThreshold: 3

gracefulShutdown:
  terminationGracePeriodSeconds: 45
  preStopSleepSeconds: 10

config:
  appEnv: production
  logLevel: info

app:
  version: "1.0.0"
```

**Step 3: _helpers.tpl**

```
{{- define "hello-world.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "hello-world.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "hello-world.labels" -}}
app.kubernetes.io/name: {{ include "hello-world.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Values.app.version | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "hello-world.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hello-world.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

**Step 4: namespace.yaml**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: {{ .Values.namespace }}
  labels:
    {{- include "hello-world.labels" . | nindent 4 }}
```

**Step 5: configmap.yaml**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "hello-world.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "hello-world.labels" . | nindent 4 }}
data:
  APP_ENV: {{ .Values.config.appEnv | quote }}
  APP_VERSION: {{ .Values.app.version | quote }}
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
```

**Step 6: deployment.yaml**

핵심 — probes, resource limits, preStop hook, graceful shutdown 전부 포함:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "hello-world.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "hello-world.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "hello-world.selectorLabels" . | nindent 6 }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        {{- include "hello-world.selectorLabels" . | nindent 8 }}
    spec:
      terminationGracePeriodSeconds: {{ .Values.gracefulShutdown.terminationGracePeriodSeconds }}
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          envFrom:
            - configMapRef:
                name: {{ include "hello-world.fullname" . }}
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
          livenessProbe:
            httpGet:
              path: {{ .Values.probes.liveness.path }}
              port: http
            initialDelaySeconds: {{ .Values.probes.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.liveness.periodSeconds }}
            failureThreshold: {{ .Values.probes.liveness.failureThreshold }}
          readinessProbe:
            httpGet:
              path: {{ .Values.probes.readiness.path }}
              port: http
            initialDelaySeconds: {{ .Values.probes.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.readiness.periodSeconds }}
            failureThreshold: {{ .Values.probes.readiness.failureThreshold }}
          resources:
            requests:
              cpu: {{ .Values.resources.requests.cpu }}
              memory: {{ .Values.resources.requests.memory }}
            limits:
              cpu: {{ .Values.resources.limits.cpu }}
              memory: {{ .Values.resources.limits.memory }}
          lifecycle:
            preStop:
              exec:
                command: ["sleep", "{{ .Values.gracefulShutdown.preStopSleepSeconds }}"]
```

**Step 7: service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "hello-world.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "hello-world.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "hello-world.selectorLabels" . | nindent 4 }}
```

**Step 8: ingress.yaml**

```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "hello-world.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "hello-world.labels" . | nindent 4 }}
spec:
  ingressClassName: {{ .Values.ingress.className }}
  rules:
    - host: {{ .Values.ingress.host }}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {{ include "hello-world.fullname" . }}
                port:
                  name: http
{{- end }}
```

**Step 9: Commit**

```bash
git add docs/tutorials/k8s-hello-world/helm/
git commit -m "feat(tutorial): add Helm chart with production patterns"
```

---

## Task 4: 튜토리얼 문서 Part 1 작성 — "일단 돌린다"

**Files:**
- Create: `docs/tutorials/k8s-hello-world/tutorial.md` (Part 1 섹션)

**Step 1: 문서 헤더 + 목차 작성**

- 튜토리얼 제목, 대상 독자, 사전 요구사항, 소요 시간
- Part 1/2/3 목차

**Step 2: Step 1-1 환경 준비 작성**

내용:
- macOS 기준 Homebrew로 설치: `brew install minikube`, `brew install helm`
- `minikube start --driver=docker --cpus=2 --memory=4096`
- `minikube addons enable ingress`
- `minikube addons enable metrics-server` (Part 3에서 사용)
- 설치 확인: `kubectl cluster-info`, `helm version`
- `/etc/hosts`에 `hello.local` 추가: `echo "$(minikube ip) hello.local" | sudo tee -a /etc/hosts`

**Step 3: Step 1-2 FastAPI 앱 작성 섹션**

내용:
- 프로젝트 디렉토리 생성 안내
- `requirements.txt` 코드 + 각 패키지 설명
- `main.py` 코드 + 각 엔드포인트/기능 설명
- "왜 이렇게?" 박스: JSON 로깅, health endpoint, graceful shutdown의 이유
- 로컬 테스트: `uvicorn main:app --port 8080` → `curl localhost:8080`

**Step 4: Step 1-3 Dockerfile 작성 섹션**

내용:
- `.dockerignore` 코드 + 왜 필요한지
- `Dockerfile` 코드 + 각 라인 주석 설명
- "왜 이렇게?" 박스: multi-stage, non-root, exec form
- Docker 빌드 테스트: Minikube Docker 환경 사용
  - `eval $(minikube docker-env)`
  - `docker build -t hello-world:1.0.0 .`

**Step 5: Step 1-4 Helm 배포 섹션**

내용:
- Helm 차트 구조 설명 (간단히 — 상세는 Part 2에서)
- 각 파일 코드 + 핵심 부분 주석
- 배포 커맨드:
  - `helm install hello ./helm/hello-world`
  - `kubectl get all -n hello`
  - `kubectl get ingress -n hello`
- 접근 확인:
  - `curl http://hello.local/`
  - `curl http://hello.local/health/live`
  - `curl http://hello.local/info`
- 문제 해결 (Troubleshooting): Pod이 안 뜰 때, Ingress가 안 될 때

**Step 6: Commit**

```bash
git add docs/tutorials/k8s-hello-world/tutorial.md
git commit -m "feat(tutorial): write Part 1 - deploy hello world to k8s"
```

---

## Task 5: 튜토리얼 문서 Part 2 작성 — "방금 뭘 한 거지?"

**Files:**
- Modify: `docs/tutorials/k8s-hello-world/tutorial.md` (Part 2 섹션 추가)

**Step 1: Step 2-1 K8s 전체 아키텍처 작성**

내용:
- Control Plane 구성 요소 ASCII 다이어그램
  - API Server: "접수 창구" — 모든 요청이 여기로
  - etcd: "기록 장부" — 클러스터 상태 저장
  - Scheduler: "배치 담당자" — Pod를 어떤 Node에 배치할지
  - Controller Manager: "감시자" — 원하는 상태 vs 현재 상태 비교
- Worker Node 구성 요소
  - kubelet: "현장 관리자" — Pod 실행/모니터링
  - kube-proxy: "교환원" — 네트워크 규칙 관리
- Minikube에서는 Control Plane + Worker가 하나의 노드
- "Part 1에서 `helm install`했을 때 일어난 일" 흐름도

**Step 2: Step 2-2 리소스 계층 역추적 작성**

내용:
- Deployment → ReplicaSet → Pod → Container 계층 다이어그램
- Service → Endpoints → Pod 연결 다이어그램
- Ingress → Service 라우팅 다이어그램
- 각 리소스의 비유 + 역할 설명
- `kubectl get deployment,replicaset,pod -n hello` 실행 결과 예시

**Step 3: Step 2-3 요청 흐름 작성**

내용:
- `curl http://hello.local/` 요청이 Pod에 도달하기까지 ASCII 흐름도
- DNS → Ingress Controller → Service → kube-proxy → Pod
- 각 단계 설명

**Step 4: Step 2-4 Helm이 해준 것 작성**

내용:
- Helm 없이 수동 배포 시 필요한 커맨드 목록 vs Helm 한 줄
- values.yaml의 역할 — 환경별 분리
- `helm template` 으로 실제 생성되는 YAML 확인
- `helm history`, `helm rollback` 설명

**Step 5: Step 2-5 kubectl 실습 커맨드 작성**

내용 (각 커맨드 + 출력 예시 + 무엇을 보는지 설명):
- `kubectl get all -n hello`
- `kubectl describe pod <name> -n hello` — Events 섹션 중점
- `kubectl logs <pod> -n hello` — JSON 로그 확인
- `kubectl exec -it <pod> -n hello -- sh` — 컨테이너 내부 탐색
- `kubectl get endpoints -n hello` — Service가 바라보는 Pod IP
- `kubectl top pod -n hello` — 리소스 사용량

**Step 6: Commit**

```bash
git add docs/tutorials/k8s-hello-world/tutorial.md
git commit -m "feat(tutorial): write Part 2 - k8s architecture deep dive"
```

---

## Task 6: 튜토리얼 문서 Part 3 작성 — "실무처럼 만들기"

**Files:**
- Modify: `docs/tutorials/k8s-hello-world/tutorial.md` (Part 3 섹션 추가)

**Step 1: Step 3-1 ConfigMap/Secret 실습 작성**

내용:
- 12-Factor Factor 3 설명
- ConfigMap에서 환경변수가 Pod에 주입되는 구조
- 실습: `values.yaml`에서 `LOG_LEVEL`을 `debug`로 변경
- `helm upgrade hello ./helm/hello-world --set config.logLevel=debug`
- `curl http://hello.local/info` → 변경 확인
- Secret 개념 설명 (실습은 Secret 생성 + 마운트 예시)

**Step 2: Step 3-2 Health Probe 실험 작성**

내용:
- liveness vs readiness 차이 다이어그램
- 실습 1: readiness 끄기
  - `curl -X POST http://hello.local/admin/toggle-ready`
  - `kubectl get endpoints -n hello` → Pod IP 사라지는 것 확인
  - `curl http://hello.local/` → 다른 Pod가 응답하는 것 확인 (replica=2)
  - 다시 토글 → 복구
- 실습 2: liveness 실패 시뮬레이션
  - `kubectl describe pod` → restart count 확인
- "실무에서는?": DB 연결 체크를 readiness에 넣어서 DB 장애 시 트래픽 차단

**Step 3: Step 3-3 Resource Requests/Limits 작성**

내용:
- requests vs limits 비유: "최소 보장 좌석" vs "절대 한계"
- `kubectl top pod -n hello` → 실제 사용량 확인
- `kubectl describe node` → Allocatable vs Allocated 확인
- values.yaml에서 설정 위치 설명
- "실무에서는?": OOMKilled 경험, CPU throttling 증상

**Step 4: Step 3-4 Graceful Shutdown 작성 (핵심)**

내용:
- Pod 종료 라이프사이클 ASCII 다이어그램 (eks-deploy-research.md에서 가져옴)
- "왜 preStop hook이 필요한가?" — race condition 설명
- 종료 예산 정렬 공식:
  - `terminationGracePeriodSeconds(45) >= preStop(10) + app shutdown(30) + buffer(5)`
- 코드에서 SIGTERM 핸들링하는 부분 설명 (main.py 참조)
- deployment.yaml에서 preStop, terminationGracePeriodSeconds 설명
- "실무에서는?": DB 커넥션 풀 정리, 메시지 큐 consumer 정리 등

**Step 5: Step 3-5 Rolling Update 무중단 배포 실습 작성**

내용:
- 실습 준비: 별도 터미널에서 반복 요청
  - `while true; do curl -s http://hello.local/ && echo; sleep 0.5; done`
- 앱 버전 올려서 배포:
  - `helm upgrade hello ./helm/hello-world --set app.version=2.0.0 --set image.tag=2.0.0`
  - (사전에 v2 이미지 빌드: main.py에서 메시지를 "Hello World v2"로 변경)
- 관찰:
  - 반복 요청 터미널: 502/503 없이 v1 → v2 전환 확인
  - `kubectl rollout status deployment -n hello`
  - `kubectl get pods -n hello -w` (watch 모드)
  - 로그로 graceful shutdown 확인: `kubectl logs <old-pod> -n hello`
- 롤백 실습:
  - `helm rollback hello 1`
  - 다시 v1으로 돌아가는 것 확인
- "실무에서는?": Canary 배포, Argo Rollouts, Flagger 소개 (링크)

**Step 6: 정리 및 다음 단계 작성**

내용:
- `helm uninstall hello`
- `minikube stop`
- 이 튜토리얼에서 배운 것 요약 체크리스트
- 다음 단계 추천: HPA, PDB, NetworkPolicy, Prometheus/Grafana 모니터링

**Step 7: Commit**

```bash
git add docs/tutorials/k8s-hello-world/tutorial.md
git commit -m "feat(tutorial): write Part 3 - production-grade operations"
```

---

## Task 7: 최종 검토 + README

**Files:**
- Create: `docs/tutorials/k8s-hello-world/README.md`

**Step 1: README 작성**

- 튜토리얼 개요 (1줄)
- 사전 요구사항 목록
- 빠른 시작 커맨드
- 디렉토리 구조 설명
- tutorial.md 링크

**Step 2: 전체 문서 검토**

- tutorial.md에서 코드 블록이 소스 파일과 일치하는지
- 커맨드 순서가 논리적인지
- 누락된 설명이 없는지
- ASCII 다이어그램이 깨지지 않는지

**Step 3: Final Commit**

```bash
git add docs/tutorials/k8s-hello-world/
git commit -m "feat(tutorial): K8s hello world production-grade tutorial complete"
```
