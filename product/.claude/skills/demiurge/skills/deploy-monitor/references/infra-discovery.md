# 레포 인프라 파악과 기록

레포 인프라 기록(`~/.claude/deploy-monitor/<레포 최상위 폴더 이름>.md`)이 없거나, 있는 기록에 "추가할 게 있는지 살펴보기"를 골랐을 때 이 문서를 따른다.

## 원칙: 묻기 전에 찾고, 찾은 것은 근거와 함께 제안한다

"로그 그룹은요? 리전은요?" 같은 빈칸 질문지를 내지 않는다. 레포를 먼저 읽고 조회 전용 AWS 호출로 확인한 뒤,
**값과 근거를 채운 기록 초안**을 보여 주고 "이대로 저장할까요, 고칠 곳이 있나요?"라고 묻는다.
실행자가 확정하기 전에는 기록 파일을 저장하지 않는다.

찾은 값끼리 어긋나면(예: README는 ap-northeast-2, 배포 설정은 ap-northeast-1) 실행자에게 고르라고 넘기지 않는다.
**실제 조회로 판정하고** 그 결과를 근거로 제안한다. 실행자에게는 판정 결과와 어긋남이 있었다는 사실을 함께 보여 준다.
조회 결과를 아직 못 받았어도 칸을 "확인 중"으로 비워 두지 않는다. 운영을 실제로 띄우는 파일(배포 워크플로·태스크 정의·terraform)의 값을
**제안값**으로 적고(예: "ap-northeast-1 — 배포 워크플로 `AWS_REGION`, 태스크 정의 `awslogs-region`. README의 ap-northeast-2와 어긋나 조회로 확인 중"),
조회 결과로 확정하거나 고친다. 문서(README·위키·티켓)는 배포 설정보다 늦게 고쳐지는 일이 많아 후순위다.

## 단서 목록 (이 순서로 본다)

| 찾을 값 | 단서 | 예 |
|---|---|---|
| 리전·클러스터·서비스 | 배포 워크플로(`.github/workflows/*deploy*`), 배포 스크립트(`deploy*.sh`), terraform | `AWS_REGION`, `ECS_CLUSTER`, `ECS_SERVICE`, `aws-region:` |
| 로그 그룹·로그 리전 | ECS 태스크 정의(`task-definition*.json`, terraform `aws_ecs_task_definition`)의 `logConfiguration.options` | `awslogs-group`, `awslogs-region` |
| 로그 형식 | 로깅 설정 코드(`logging.config`, `Formatter`, `structlog`, `pino`, `winston`) | JSON인지, 수준·메시지·위치를 담는 필드 이름 |
| 오류 추적 | `sentry_sdk.init`, `Sentry.init`, `SENTRY_DSN` | Sentry 조직·프로젝트(대개 DSN이나 설정 파일) |
| 배포 브랜치 | 워크플로의 `on.push.branches` | 운영 배포를 일으키는 브랜치 |
| 실재 확인 | 조회 전용 AWS 호출 | 아래 |

```bash
# 로그 그룹이 그 리전에 실제로 있는지 — 후보 리전마다
aws logs describe-log-groups --region ap-northeast-1 --log-group-name-prefix /ecs/shop-api --output json
aws logs describe-log-groups --region ap-northeast-2 --log-group-name-prefix /ecs/shop-api --output json
# 서비스가 그 클러스터·리전에 있는지 (배포 시각 근거로도 쓴다)
aws ecs describe-services --region ap-northeast-1 --cluster shop-prod --services shop-api-prod --output json
```

이 호출들은 읽기 전용이다. `aws login` 자격증명이 만료됐으면 실행자에게 `! aws login`을 부탁하고 확인을 마친 뒤 제안한다.

## 리전은 반드시 조회로 확인한다

README·위키·티켓에 적힌 리전을 그대로 믿지 않는다. 배포 설정에서 찾은 리전도 `describe-log-groups`로 로그 그룹이 실제로 있는지 본 뒤에 확정한다.
사례: AOTA-324 때 티켓에는 리전 이야기가 없었고, 처음에 ap-northeast-2로 짚었다가 실제 로그 그룹은 ap-northeast-1에 있었다.
리전이 틀리면 조회는 오류 없이 0건을 돌려주고, 모니터링은 하루 내내 "이상 없음"을 기록한다 — 가장 나쁜 조용한 실패다.

## AWS가 아닌 원천

로그가 GCP Logging, Datadog, Loki 등에 있으면 "아직 지원하지 않는 원천"이라고 알리고 그 원천은 빼고 진행한다.
기록의 "지원하지 않는 원천" 칸에 근거와 함께 남긴다. Sentry처럼 Claude Code에 연결된 도구는 함께 쓸 수 있다.

## 기록 파일 형식

값마다 **근거**(파일 경로와 줄, 또는 실행한 조회 명령과 그 결과 요지)와 확인한 날짜를 적는다. 자동 파악은 틀릴 수 있어서, 다음 실행 때 근거를 보고 다시 확인할 수 있어야 한다.
티켓마다 달라지는 내용(볼 대상, 주기, 종료 시각)은 여기에 적지 않는다.

```markdown
# heum-chat 인프라 기록

| 항목 | 값 | 근거 | 확인일 |
|---|---|---|---|
| 리전 | ap-northeast-1 | `aws logs describe-log-groups --region ap-northeast-1` 에 `chat-server-log-prod` 있음. 티켓엔 리전 언급 없음, ap-northeast-2 로 먼저 짚었다가 조회로 정정 | 2026-10-23 |
| 운영 로그 그룹 | chat-server-log-prod | 같은 조회 결과 | 2026-10-23 |
| 로그 형식 | JSON 한 줄, 필드 `logger_type`, `level`, `msg`, `func` | <로깅 설정 파일 경로:줄> + 그 필드로 집계한 Logs Insights 조회 | 2026-10-23 |
| 오류 수준 값 | `level = "ERROR"` | 같은 조회 | 2026-10-23 |
| ECS 클러스터·서비스 | <배포 워크플로에서 찾은 값> | `.github/workflows/deploy-ecs-common.yml` <줄> | <날짜> |
| 오류 추적 | Sentry <조직>/<프로젝트> | `sentry_sdk.init` 위치 | <날짜> |
| 운영 배포 브랜치 | main(수동 배포) | 레포 CLAUDE.md "Branching & Deployment" 절 | <날짜> |
| 지원하지 않는 원천 | 없음 | — | <날짜> |
```

로그 형식 칸은 회차 쿼리(`references/tick.md`)의 `level`·`func`·`sig`를 어느 필드에서 만들지 정하는 데 쓰인다. JSON이 아니면 `parse`로 수준과 메시지를 뽑는 식을 함께 적는다.
