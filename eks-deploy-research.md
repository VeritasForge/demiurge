# EKS 배포 시 Graceful Shutdown Deep Research

> **연구 일자**: 2026-02-26
> **연구 방법**: Deep Research Protocol (3-Phase) + 2 Rounds of Subagent Cross-Validation
> **연구 동기**: 새 회사에서 K8s 도입 시 "graceful shutdown 필수"라는 문서를 받았으나, 과거 blue/green·canary 배포 경험에서 명시적 graceful shutdown 처리를 한 적이 없어 fact check 필요

---

## Executive Summary

**결론: 새 회사의 "graceful shutdown 필요" 주장은 기술적으로 정당하다.**

Kubernetes 환경에서 graceful shutdown은 배포 전략(Rolling Update, Blue/Green, Canary)과 **독립적으로** 필요한 운영 위생(operational hygiene)이다. 과거 경험에서 문제가 없었던 것은 환경 차이(전통 VM Blue/Green, 프레임워크 내부 처리, 서비스 메시 보완 등)로 설명 가능하다.

핵심 이유 3가지:
1. **K8s의 Endpoints 제거와 SIGTERM은 동시(concurrently) 발생** — race condition이 구조적으로 존재
2. **SIGTERM은 배포 전략과 무관하게 항상 전송** — DB 연결, 메시지 큐, 캐시 정리는 트래픽 유무와 무관
3. **Blue/Green조차 keep-alive 연결, WebSocket, Envoy sidecar 등에서 edge case 존재**

---

## Table of Contents

1. [배경: 사용자 경험 vs 새 회사 문서](#1-배경)
2. [Round 1: 문서 Fact Check (12개 주장 검증)](#2-round-1-문서-fact-check)
3. [Round 2: 카나리 + B/G 하이브리드 패턴 검증](#3-round-2-카나리--bg-하이브리드-패턴-검증)
4. [핵심 기술 개념 상세](#4-핵심-기술-개념-상세)
5. [배포 전략별 비교표](#5-배포-전략별-비교표)
6. [Spring Boot 버전별 Graceful Shutdown 타임라인](#6-spring-boot-버전별-graceful-shutdown-타임라인)
7. [프레임워크별 Graceful Shutdown 구현](#7-프레임워크별-graceful-shutdown-구현)
8. [최종 결론 및 권고](#8-최종-결론-및-권고)
9. [출처 목록](#9-출처-목록)
10. [Research Metadata](#10-research-metadata)

---

## 1. 배경

### 사용자의 과거 경험

> "blue/green 배포를 하든 k8s pod에 카나리 배포를 하든, LB를 새로 배포된 서버로 연결하고, 이전 서버로는 요청이 안가게 했었다. 자연스럽게 이전 서버에 연결된 요청은 처리가 완료되면 응답을 완료하고 더 이상 요청이 안들어오니 아무 작업을 안하게 되었다."

### 새 회사의 주장

K8s 도입 시 graceful shutdown이 필수이며, SIGTERM 핸들링 + 종료 예산(time budget) 관리가 필요하다.

### 왜 경험이 달랐는가?

| 과거 환경 (전통 VM Blue/Green) | 새 환경 (K8s) |
|------|------|
| LB 전환 → (시간 경과) → 서버 종료 | Endpoints 제거 + SIGTERM **동시 발생** |
| 트래픽 차단과 서버 종료가 시간적으로 분리 | Race condition이 구조적으로 존재 |
| 이전 서버는 한참 뒤에 수동/자동 종료 | terminationGracePeriodSeconds(기본 30초) 후 SIGKILL |
| LB가 완전히 전환된 후 서버 종료 | kube-proxy iptables 전파 지연으로 SIGTERM 후에도 트래픽 유입 가능 |

**핵심 차이**: 전통적 Blue/Green은 LB 전환 완료 → 충분한 대기 → 서버 종료의 순서가 보장되었다. K8s에서는 이 순서가 보장되지 않는다.

---

## 2. Round 1: 문서 Fact Check

원본 문서의 12개 핵심 주장을 검증했다. 결과: **9/12 CONFIRMED, 3/12 PARTIALLY_CORRECT**.

### CONFIRMED (9건)

#### FC1: Graceful Shutdown 정의 — `[Confirmed]`

> "새 작업을 더 이상 받지 않고, 이미 처리 중인 in-flight 작업을 마무리하고, 리소스를 정리하고, 제한 시간 내에 exit한다"

- **근거**: Spring Boot, .NET Generic Host, Go net/http 공식 문서 모두 이 4단계 정의와 일치
- **Spring Boot**: "When enabled, shutdown of the application will include a grace period of configurable duration. During this grace period, existing requests will be allowed to complete but no new requests will be permitted"
- **.NET**: "stops the server and triggers CancellationToken and waits for the server to shut down"
- **Go**: `Server.Shutdown(ctx)` — "does not interrupt any active connections. Shutdown works by first closing all open listeners, then closing all idle connections"

#### FC2: K8s Pod 종료 라이프사이클 — `[Confirmed]`

> "terminationGracePeriodSeconds(기본 30초), preStop → SIGTERM → grace period → SIGKILL"

- **K8s 공식 문서 원문**: "The kubelet triggers the container runtime to send a SIGTERM signal to process 1 inside each container. [...] If a container still has a process running after the grace period expires, the kubelet triggers forcible shutdown."
- **기본값 30초**: "terminationGracePeriodSeconds defaults to 30"
- **preStop 훅**: "If a preStop hook is configured, the kubelet runs that hook inside of the container"

#### FC3: preStop과 Grace Period 예산 공유 — `[Confirmed]`

> "preStop 시간 + 컨테이너 종료 시간이 grace period 예산을 함께 쓴다"

- **K8s 공식 문서**: "If the preStop hook is still running after the grace period expires, the kubelet requests a small, one-off grace period extension of 2 seconds"
- preStop이 hang되면 terminationGracePeriodSeconds 만료 후 SIGKILL

#### FC4: Docker SIGTERM → timeout → SIGKILL — `[Confirmed]`

> "docker stop은 SIGTERM을 보내고, grace period 후 SIGKILL을 보낸다"

- **Docker 공식 문서**: "The main process inside the container will receive SIGTERM, and after a grace period, SIGKILL"
- STOPSIGNAL로 기본 종료 시그널 변경 가능

#### FC5: AWS ALB Deregistration Delay — `[Confirmed]`

> "기본 300초, target이 먼저 연결 끊으면 500-level 에러"

- **AWS 공식 문서**: "The default value is 300 seconds"
- **AWS 경고**: "If the target closes the connection before the deregistration delay elapses, the client receives a 500-level error response"

#### FC6: systemd TimeoutStopSec — `[Confirmed]`

> "stop 동작/서비스 종료를 기다리는 시간이며 만료 후 FinalKillSignal"

- **systemd 매뉴얼**: "Configures a timeout for waiting for each ExecStop= command and is applied to all commands, one after another."

#### FC7: PID 1 문제 — `[Confirmed]`

> "shell이 entrypoint(PID 1)인 경우, SIGTERM이 앱에 전달되지 않을 수 있다"

- **AWS ECS 공식 문서**: shell form (`/bin/sh -c my-app`)에서 shell이 SIGTERM을 무시하거나 자식에게 전달하지 않음
- **해결**: exec form 사용 또는 tini/dumb-init 도입

#### FC8: 종료 예산 정렬 — `[Confirmed]`

> "LB 드레인 시간 >= 앱 드레인 시간, 앱 드레인 시간 + preStop 훅 시간 <= 강제 종료 예산"

- 각 레이어의 timeout 문서를 종합한 합리적 설계 원칙
- AWS, K8s, Docker, systemd 모두 "강제 종료(SIGKILL) 전에 time budget 제공" 패턴

#### FC9: readiness probe 실패 시 엔드포인트 제거 — `[Confirmed]`

> "readiness probe가 실패하면 Kubernetes가 해당 Pod를 서비스 엔드포인트에서 제거한다"

- **K8s 공식 문서**: "If the readiness probe fails, the endpoints controller removes the Pod's IP address from the endpoints of all Services that match the Pod"

### PARTIALLY_CORRECT (3건)

#### FC10: Spring Boot Graceful Shutdown "기본 활성화" — `[Partially Correct]`

> 원본 문서: "graceful shutdown은 기본적으로 활성화"

**실제 사실**:
- Spring Boot **2.3** (2020): `server.shutdown` 속성 도입, **기본값 `IMMEDIATE`** (graceful 아님)
- Spring Boot **3.3.x** 이하: 여전히 기본값 `IMMEDIATE`
- Spring Boot **3.4.0-M3** (2024-09-19): **기본값이 `GRACEFUL`로 변경**
  - GitHub 커밋: `814369e8` — "Change default value of server.shutdown to graceful"
- **판정**: 3.4+ 사용 시에만 "기본 활성화"가 맞음. 그 이전 버전은 명시적 설정 필요

#### FC11: Go Server.Shutdown "active connection을 끊지 않고" — `[Partially Correct]`

> 원본 문서: "Shutdown은 active connection을 끊지 않고 graceful shutdown을 수행"

**실제 사실**:
- **Go 공식 문서**: "Shutdown does not attempt to close nor wait for hijacked connections such as WebSockets"
- 일반 HTTP 요청은 정확하지만, **WebSocket 등 hijacked connection은 별도 처리 필요**
- `RegisterOnShutdown`으로 추가 정리 로직 등록 가능

#### FC12: "Endpoints 제거 → SIGTERM" 순서 — `[Partially Correct]`

> 원본 문서에서 암시하는 "readiness 실패 → 엔드포인트 제거 → 트래픽 차단 → SIGTERM" 순서

**실제 사실 (매우 중요)**:
- **K8s 공식 문서 원문**: "**At the same time** as the kubelet is starting graceful shutdown, the control plane evaluates whether to remove that shutting-down Pod from EndpointSlice"
- Endpoints 제거와 SIGTERM은 **순차적이 아니라 동시(concurrently)** 발생
- kube-proxy가 iptables를 업데이트하기까지 지연이 있어, SIGTERM 후에도 트래픽이 old Pod로 라우팅될 수 있음
- **이것이 preStop hook이 필요한 근본적 이유**

---

## 3. Round 2: 카나리 + B/G 하이브리드 패턴 검증

사용자의 과거 경험 — "K8s에서 카나리 배포를 했는데, 각 노드의 Pod를 blue/green으로 처리했다" — 에 대한 심화 검증.

### 3.1 Flagger 소스코드 레벨 분석

#### Canary Release vs Blue/Green 구분 — `[Confirmed]`

- Flagger에서 Canary Release와 Blue/Green은 **별개의 전략**
- "traffic is routed to canary before primary rolling update" 원문은 **Blue/Green 섹션에만** 존재
- Canary Release에서 primary rolling update 시작 시점 트래픽은 `maxWeight%` (100%가 아님)

#### Flagger 소스코드 — `[Confirmed]`

- `scheduler.go`에서 Canary와 Blue/Green의 실행 경로가 분리됨
- Blue/Green: `router.SetRoutes` → primary로 100% 라우팅 전환 후 → old pod scale down
- Canary: weight를 점진적으로 증가시키며 분석

#### Kubernetes Provider 한계 — `[Confirmed]`

- Flagger의 **Kubernetes provider**에서는 traffic routing 자체가 불가능 (Service Mesh 또는 Ingress 필요)
- Kubernetes provider 사용 시 Canary는 실질적으로 A/B testing만 가능

### 3.2 Argo Rollouts 분석

#### scaleDownDelaySeconds — `[Confirmed]`

- **기본값 30초** — 이 설정이 존재하는 이유 자체가 race condition의 존재를 증명
- 목적: old ReplicaSet의 Pod가 즉시 종료되면 아직 라우팅 중인 트래픽이 끊길 수 있으므로 지연
- `dynamicStableScale` 사용 시 "no healthy upstream" 오류 발생 사례 (Issue #3681)

### 3.3 Race Condition이 "완화"되지만 "제거"되지 않는 3가지 독립적 메커니즘

Flagger/Argo Rollouts 같은 고급 배포 도구를 사용해도 graceful shutdown이 필요한 이유:

| # | 메커니즘 | 설명 | 해결 주체 |
|---|---------|------|----------|
| 1 | **kube-proxy iptables 전파 지연** | Endpoints 제거 후에도 iptables 업데이트까지 지연 존재 | preStop hook (sleep) |
| 2 | **keep-alive 연결** | LB 전환 후에도 기존 TCP 연결은 유지됨 | 앱의 connection draining |
| 3 | **Envoy sidecar 경쟁** | Istio 환경에서 Envoy가 앱보다 먼저 종료되면 503 | preStop hook + EXIT_ON_ZERO_ACTIVE_CONNECTIONS |

### 3.4 Graceful Shutdown은 배포 전략과 독립적으로 필요

> **packagemain.tech 원문 인용**: "complementary, not substitutes"
> — Graceful shutdown과 배포 전략은 대체 관계가 아니라 **상호 보완** 관계

SIGTERM이 전송되면 (배포 전략과 무관하게) 다음 작업은 반드시 필요:

- DB 커넥션 풀 정리 (connection leak 방지)
- 메시지 큐 consumer 정리 (in-flight 메시지 ACK/NACK)
- 캐시 flush
- 백그라운드 작업/스케줄러 중지
- 임시 파일 정리

**Flagger 공식 문서에서도 preStop hook을 명시적으로 권장.**

---

## 4. 핵심 기술 개념 상세

### 4.1 Kubernetes Pod Termination Lifecycle

```
API Server: "Pod 삭제"
    │
    ├──────────────────────────────┐
    │                              │
    ▼                              ▼
kubelet                    EndpointSlice Controller
    │                              │
    │                              ▼
    │                    Endpoints에서 Pod IP 제거
    │                              │
    │                              ▼
    │                    kube-proxy iptables 업데이트
    │                    (지연 발생 가능!)
    │
    ▼
preStop hook 실행 (있는 경우)
    │
    ▼
SIGTERM 전송
    │
    ▼
terminationGracePeriodSeconds 대기 (기본 30초)
    │
    ▼
SIGKILL (강제 종료)
```

**핵심**: kubelet의 SIGTERM과 EndpointSlice Controller의 Endpoints 제거가 **동시에(concurrently)** 시작된다. 이것이 race condition의 근원.

### 4.2 preStop Hook의 역할

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sleep", "15"]
    # 또는 K8s 1.30+ (KEP-3960):
    # sleep:
    #   seconds: 15
```

- SIGTERM **전에** 실행
- kube-proxy iptables 전파를 기다리는 시간 확보
- 권장 sleep: **5~15초**
- terminationGracePeriodSeconds 예산을 공유하므로 너무 길면 안 됨

### 4.3 KEP-1669: ProxyTerminatingEndpoints

- K8s **1.28 (stable)** 에서 도입
- terminating 상태의 endpoints를 kube-proxy가 인식
- **하지만**: 근본적인 concurrent 설계는 유지됨 — race condition을 완전히 제거하지 않음

### 4.4 Istio/Envoy 관련

- VirtualService weight 0% 후에도 **keep-alive 연결은 유지**됨
- `EXIT_ON_ZERO_ACTIVE_CONNECTIONS` (Istio v1.12+): active connection이 0이 되면 Envoy 종료
- Envoy sidecar가 앱보다 먼저 종료되면 **503 에러** 발생

---

## 5. 배포 전략별 비교표

| 항목 | K8s Rolling Update | Flagger / Argo Rollouts | 전통 VM Blue/Green |
|------|-------------------|------------------------|-------------------|
| **트래픽 전환 방식** | kube-proxy iptables (Endpoints 기반) | Service Mesh / Ingress weight | LB 타겟 그룹 전환 |
| **Endpoints 제거 vs SIGTERM** | **동시** (race condition) | 도구가 순서 제어 시도 (완벽하지 않음) | LB 전환 완료 → (시간 경과) → 서버 종료 |
| **Race condition** | 구조적으로 존재 | 완화되지만 제거되지 않음 | 거의 없음 (시간적 분리) |
| **preStop hook 필요성** | **필수** | **권장** (Flagger 공식 문서 명시) | 불필요 |
| **Graceful shutdown 필요성** | **필수** | **필수** | 선택적 (리소스 정리 관점) |
| **keep-alive 연결 문제** | 있음 | 있음 | 있음 (ALB deregistration delay로 처리) |
| **SIGTERM 전송** | 항상 | 항상 | 수동/자동 서버 종료 시에만 |
| **리소스 정리** | 앱 책임 | 앱 책임 | 앱 책임 (또는 서버 재시작으로 대체) |

---

## 6. Spring Boot 버전별 Graceful Shutdown 타임라인

| 버전 | 날짜 | `server.shutdown` 기본값 | 비고 |
|------|------|-------------------------|------|
| 2.3.0 | 2020-05 | `IMMEDIATE` | graceful shutdown 기능 최초 도입 |
| 2.3.x ~ 3.3.x | 2020~2024 | `IMMEDIATE` | 명시적으로 `graceful` 설정 필요 |
| **3.4.0-M3** | **2024-09-19** | **`GRACEFUL`** | 기본값 변경 (커밋 `814369e8`) |
| 3.4.0+ | 2024-11+ | `GRACEFUL` | 별도 설정 없이 graceful shutdown 활성화 |

### 설정 방법 (3.3.x 이하)

```yaml
# application.yml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s  # 기본 30초
```

### 3.4.0+ (설정 불필요)

```yaml
# 기본적으로 graceful shutdown 활성화
# timeout만 필요 시 조정
spring:
  lifecycle:
    timeout-per-shutdown-phase: 45s
```

---

## 7. 프레임워크별 Graceful Shutdown 구현

### 7.1 Go (net/http)

```go
// Server.Shutdown(ctx):
// 1. 모든 open listener 닫기
// 2. 모든 idle connection 닫기
// 3. active connection이 idle로 돌아오길 기다리기
// 주의: WebSocket 등 hijacked connection은 자동으로 닫지 않음!

srv := &http.Server{Addr: ":8080"}

go func() {
    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, syscall.SIGTERM, syscall.SIGINT)
    <-sigCh

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    srv.Shutdown(ctx)  // active connection 유지, hijacked는 미처리
}()
```

- `RegisterOnShutdown`: WebSocket 등 정리 로직 등록 가능

### 7.2 Node.js (http)

```javascript
process.on('SIGTERM', () => {
  server.close(() => {
    // 새 연결 중단 + idle/비활성 연결 정리 후 콜백
    process.exit(0);
  });
});
```

- **v19.0.0 이전**: `server.close()`는 새 연결만 차단, idle connection은 그대로 유지
- **v19.0.0 이후**: idle connection 즉시 닫기 추가
- `server.closeAllConnections()`: 강제 종료 API (최후 수단)
- **주의**: SIGTERM 핸들러를 등록하면 Node의 기본 종료 동작이 사라짐 → 직접 `process.exit()` 호출 필요

### 7.3 .NET (Generic Host)

```
Graceful Shutdown 단계:
1. ApplicationStopping 이벤트 트리거
2. 서버 중지 (새 연결 차단)
3. 기존 연결의 요청 완료 대기 (ShutdownTimeout까지)
4. IHostedService.StopAsync 호출
5. ApplicationStopped 이벤트 트리거
```

- **ShutdownTimeout**: 기본 30초 — `IHost.StopAsync` 전체 scope (IHostedService만이 아님)
- CancellationToken이 요청되면 빠르게 반환해야 함

### 7.4 Spring Boot

```
Graceful Shutdown 단계 (GRACEFUL 모드):
1. SIGTERM 수신
2. 새 요청 거부 (503 반환)
3. 기존 in-flight 요청 완료 대기
4. timeout-per-shutdown-phase 만료 시 강제 종료
5. ApplicationContext 종료 (Bean destroy, 리소스 정리)
```

- embedded 서버별 구현: Tomcat, Jetty, Reactor Netty, Undertow
- **IDE에서 종료 시 즉시 종료로 보일 수 있음** → 실환경 SIGTERM 기반으로 테스트 필요

---

## 8. 최종 결론 및 권고

### 8.1 사용자 경험에 대한 해석

과거에 graceful shutdown 없이도 문제가 없었던 이유:

1. **전통 VM Blue/Green**: LB 전환과 서버 종료가 시간적으로 분리되어 race condition 없음
2. **프레임워크 내부 처리**: Spring Boot 3.4+, .NET Generic Host 등은 내부적으로 graceful shutdown 수행
3. **서비스 메시 보완**: Istio/Envoy가 트래픽 드레이닝을 대신 처리했을 가능성
4. **짧은 요청 위주**: P99 < 1초 수준이면 race condition 윈도우에 걸릴 확률이 낮음
5. **에러를 인지하지 못함**: 배포 시 간헐적 5xx가 있었지만 모니터링에서 놓쳤을 가능성

### 8.2 K8s 환경에서의 권고

#### 필수 사항

1. **preStop hook 설정**: `sleep 5~15` (kube-proxy 전파 대기)
2. **SIGTERM 핸들러 구현**: 프레임워크의 graceful shutdown 기능 활성화
3. **terminationGracePeriodSeconds 조정**: preStop + 앱 드레인 시간 + 여유 버퍼
4. **PID 1 확인**: Dockerfile에서 exec form 사용 또는 tini/dumb-init 도입
5. **readiness probe 설정**: 종료 시 즉시 실패하도록 구현

#### 종료 예산 정렬 공식

```
terminationGracePeriodSeconds >= preStop sleep + 앱 graceful shutdown timeout + 버퍼(5초)

예시:
  preStop sleep: 10초
  앱 shutdown timeout: 30초
  버퍼: 5초
  → terminationGracePeriodSeconds: 45초
```

#### ALB/ECS 환경 추가

```
ALB deregistration delay >= 앱 graceful shutdown timeout
앱 graceful shutdown timeout < ECS stop timeout (또는 K8s grace period)
```

### 8.3 배포 전략과 무관하게 Graceful Shutdown이 필요한 이유

```
"Graceful shutdown과 배포 전략은 complementary, not substitutes"
```

- **Rolling Update**: race condition으로 인해 필수
- **Blue/Green (Flagger/Argo)**: 완화되지만 keep-alive, sidecar 문제로 필요
- **전통 VM Blue/Green**: 리소스 정리 관점에서 권장 (필수는 아님)
- **모든 전략**: SIGTERM은 항상 전송되므로, DB 연결·메시지 큐·캐시 정리는 공통 필요

---

## 9. 출처 목록

### Kubernetes 공식 문서

1. [Pod Lifecycle - Termination of Pods](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination) — Pod 종료 라이프사이클
2. [Container Lifecycle Hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/) — preStop hook
3. [Probe Configuration](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) — readiness probe
4. [KEP-3960: Sleep Action for preStop Hook](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/3960-pod-lifecycle-sleep-action) — K8s 1.30 native sleep

### Docker 공식 문서

5. [docker stop](https://docs.docker.com/engine/reference/commandline/stop/) — SIGTERM → SIGKILL
6. [Dockerfile STOPSIGNAL](https://docs.docker.com/engine/reference/builder/#stopsignal)

### AWS 공식 문서

7. [ALB Target Group - Deregistration Delay](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html#deregistration-delay) — 기본 300초
8. [ECS Graceful Shutdown](https://aws.amazon.com/blogs/containers/graceful-shutdowns-with-ecs/) — PID 1 문제, SIGTERM 핸들링

### 프레임워크 공식 문서

9. [Spring Boot - Graceful Shutdown](https://docs.spring.io/spring-boot/docs/current/reference/html/web.html#web.graceful-shutdown) — server.shutdown 설정
10. [Spring Boot 3.4 릴리스 노트](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.4-Release-Notes) — 기본값 변경
11. [Spring Boot GitHub 커밋 814369e8](https://github.com/spring-projects/spring-boot/commit/814369e8) — "Change default value of server.shutdown to graceful"
12. [Go net/http Server.Shutdown](https://pkg.go.dev/net/http#Server.Shutdown) — active connection 유지, hijacked 미처리
13. [Node.js http.Server.close()](https://nodejs.org/api/http.html#serverclosecallback) — v19.0.0 변경사항
14. [.NET Generic Host - Graceful Shutdown](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/host/generic-host#ihostlifetime) — ShutdownTimeout

### systemd 문서

15. [systemd.service - TimeoutStopSec](https://www.freedesktop.org/software/systemd/man/systemd.service.html) — FinalKillSignal

### 배포 도구 문서

16. [Flagger - Canary Deployments](https://docs.flagger.app/usage/how-it-works) — Canary vs Blue/Green 구분
17. [Argo Rollouts - Blue-Green Strategy](https://argoproj.github.io/argo-rollouts/features/bluegreen/) — scaleDownDelaySeconds
18. [Argo Rollouts Issue #3681](https://github.com/argoproj/argo-rollouts/issues/3681) — dynamicStableScale 문제

### Istio/Envoy

19. [Istio - EXIT_ON_ZERO_ACTIVE_CONNECTIONS](https://istio.io/latest/docs/reference/commands/pilot-agent/) — Envoy sidecar 종료

### 기타

20. [packagemain.tech - Graceful Shutdown](https://packagemain.tech/) — "complementary, not substitutes"

---

## 10. Research Metadata

```yaml
research_protocol: "Deep Research Protocol (3-Phase) + 2 Rounds Cross-Validation"

round_1:
  description: "원본 문서 12개 주장 Fact Check"
  search_queries: 14 (일반 10 + SNS 4)
  sources_collected: 20+
  webfetch_verifications: 12
  result: "9 CONFIRMED, 3 PARTIALLY_CORRECT"
  subagents: 5 (FC1~FC5 병렬)

round_2:
  description: "카나리 + B/G 하이브리드 패턴 검증"
  search_queries: 12 (일반 8 + SNS 4)
  sources_collected: 18+
  webfetch_verifications: 8
  result: "Flagger/Argo가 race condition을 완화하지만 제거하지 않음"
  subagents: 4 (FC6~FC9 병렬)

confidence_distribution:
  confirmed: 9
  partially_correct: 3
  uncertain: 0
  unverified: 0

source_type_distribution:
  official_docs: 12
  primary_sources: 5
  tech_blogs: 3
  community: 2
  sns: 2

key_corrections:
  - "Spring Boot 'graceful shutdown 기본 활성화' → 3.4+ 이후에만 맞음"
  - "Endpoints 제거 → SIGTERM 순서 → 실제로는 동시(concurrent)"
  - "Go Server.Shutdown hijacked connection 미처리"
  - "Node.js server.close() v19.0.0 전후 동작 차이"
  - ".NET ShutdownTimeout 범위는 IHostedService만이 아닌 전체 Host 종료 프로세스"
```
