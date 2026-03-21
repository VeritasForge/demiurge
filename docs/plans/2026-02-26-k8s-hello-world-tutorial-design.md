# K8s Hello World 실무형 튜토리얼 설계

> **작성일**: 2026-02-26
> **대상**: K8s 초보자
> **목표**: 로컬에서 Hello World API를 K8s로 운영하는 실무형 튜토리얼

---

## 결정 사항

| 항목 | 결정 | 이유 |
|------|------|------|
| 로컬 K8s | Minikube | 학습 자료 풍부, dashboard, 멀티노드 가능, 실무 유사도 높음 |
| 언어/프레임워크 | Python + FastAPI | 실무 추세, async 기본, 자동 Swagger |
| 배포 도구 | Helm 3 | 실무 표준, 환경별 분리, 롤백 용이 |
| 접근법 | 탑다운 B | 일단 돌리고 → 해부 → 실무 강화 |
| 핵심 제약 | 최대한 실무 패턴에 가깝게 | 초보 튜토리얼이지만 실무와 거리 먼 패턴 지양 |

## 실무 패턴 적용 범위

| 단계 | 초보 튜토리얼 (흔한) | 우리가 할 것 (실무 패턴) |
|------|---------------------|---------------------------|
| Dockerfile | `python app.py` 한 줄 | Multi-stage build, non-root user, `.dockerignore` |
| K8s 배포 | `kubectl run` 또는 단일 YAML | Helm 차트 (처음부터) |
| 설정 관리 | 환경변수 하드코딩 | ConfigMap + Secret |
| 서비스 노출 | NodePort | Ingress Controller (NGINX) |
| 헬스체크 | 없음 | liveness + readiness probe |
| 리소스 | 제한 없음 | requests/limits 설정 |
| 종료 | 그냥 꺼짐 | Graceful shutdown + preStop hook |
| 네임스페이스 | default | 전용 namespace |
| 로깅 | print | 구조화된 JSON 로깅 |

## 프로젝트 구조

```
k8s-hello-world/
├── app/
│   ├── main.py
│   └── requirements.txt
├── Dockerfile
├── .dockerignore
└── helm/
    └── hello-world/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
            ├── deployment.yaml
            ├── service.yaml
            ├── ingress.yaml
            ├── configmap.yaml
            ├── secret.yaml
            ├── hpa.yaml
            └── _helpers.tpl
```

## Part 구성

### Part 1: "일단 돌린다" (실습)

- Step 1-1: 환경 준비 (Minikube, Helm, Ingress addon)
- Step 1-2: FastAPI 앱 작성 (Hello World + health endpoints + graceful shutdown)
- Step 1-3: Dockerfile (Multi-stage, non-root)
- Step 1-4: Helm 차트 작성 + 배포
- 도달 목표: `curl http://hello.local/` → `{"message": "Hello World"}`

### Part 2: "방금 뭘 한 거지?" — K8s 아키텍처 해부 (개념)

- Step 2-1: K8s 전체 아키텍처 (Control Plane, Worker Node)
- Step 2-2: 리소스 계층 역추적 (Deployment → ReplicaSet → Pod)
- Step 2-3: 요청 흐름 (Ingress → Service → Pod)
- Step 2-4: Helm이 해준 것 vs 수동
- Step 2-5: kubectl로 까보기 (실습 커맨드)

### Part 3: "실무처럼 만들기" — 운영 품질 올리기 (실습)

- Step 3-1: ConfigMap/Secret으로 설정 분리
- Step 3-2: Health Probe 동작 확인 (의도적 실패 실험)
- Step 3-3: Resource Requests/Limits
- Step 3-4: Graceful Shutdown 구현 (eks-deploy-research 연구 적용)
- Step 3-5: Rolling Update 무중단 배포 실습

## 산출물

- `docs/tutorials/k8s-hello-world/tutorial.md` — 메인 튜토리얼 문서
- `docs/tutorials/k8s-hello-world/app/` — FastAPI 앱 소스
- `docs/tutorials/k8s-hello-world/helm/` — Helm 차트
- `docs/tutorials/k8s-hello-world/Dockerfile` — 컨테이너 이미지
