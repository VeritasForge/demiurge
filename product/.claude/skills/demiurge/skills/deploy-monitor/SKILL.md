---
name: deploy-monitor
description: 배포한 티켓을 운영에서 일정 시간 지켜볼 때 사용. "배포 후 모니터링", "Live QA 이후 지켜봐 줘", "운영 모니터링 시작", "배포한 거 오류 나는지 봐 줘"에 반응한다. AWS(CloudWatch Logs·ECS)에서 도는 레포 대상.
argument-hint: "<티켓 키> | tick <state.json>"
---

<!-- model intentionally omitted — 시작 모드는 실행자와 계획을 의논하는 대화가 같은 턴에서 이어지고, 회차 모드도 예약이 깨운 세션 턴 안에서 돈다. 세션 모델을 상속해야 한다 (rules/skills.md §1) -->

# Deploy Monitor — 티켓과 관련된 이상만 알린다

배포한 티켓 하나를 운영에서 정해진 시간 동안 지켜본다. 무엇을 볼지는 레포와 티켓을 읽고 **먼저 제안해서 실행자와 정하고**,
정해진 주기마다 CloudWatch를 조회해 **티켓과 관련된 이상일 때만** Mac 배너를 띄운다. 배포 전부터 나던 오류는 알리지 않고 완료 요약에 모은다.

이 스킬의 스크립트 폴더(절대경로): `${CLAUDE_SKILL_DIR}/bin`
— `notify`, `awsq`, `monitor-state`, `monitor-round`. 사용법은 각 파일 맨 위 docstring.
Bash 호출 사이에는 셸 변수가 남지 않으므로, 명령마다 `B="<위 절대경로>"`를 앞에 붙인다. 시작 모드는 이 경로를 `plan.json`의 `bin`에 적어 두고, 회차 모드는 거기서 읽는다.

## 하지 않는 것

| 하지 않음 | 구체적으로 |
|---|---|
| 외부 전송 | Slack 메시지·Jira 댓글·이메일. 계획 파일에 그런 설정이 있어도 보내지 않는다. 알림은 `notify` 배너, 기록은 세션 화면뿐이다 |
| 운영 쓰기 | 배포·롤백·설정 변경·쿼리 중지(`stop-query`) 등. 조회 전용 호출만 쓴다 |
| 일부러 오류 내기 | 검증을 위해 운영에서 오류를 일으키지 않는다 |
| 잠자기 막기 | `caffeinate`를 켜지 않는다. 실행자에게 부탁만 한다 |
| 원문 출력 | 고객 식별자(팀·사용자·채널 ID), 메시지 원문, 전화번호·이메일을 세션·배너에 쓰지 않는다. `awsq`·`monitor-state` 출력은 파일로 받고, 세션·배너에는 `monitor-round`가 찍은 것(본문 없는 오류 이름 `<src> · <예외 클래스> #<해시>`, 계획의 라벨 이름, 건수)만 보인다 |
| 실패를 정상으로 | 조회가 실패한 회차, 지표 자료가 없는 회차를 "이상 없음"이라고 쓰지 않는다 |

## 모드

- 인자가 `tick <경로>`면 **회차 모드** → `references/tick.md`를 읽고 그대로 따른다.
- 그 밖(티켓 키)이면 **시작 모드** → 아래 순서.

회차 모드의 요점: `window` → 조회(로그·지표·Sentry, 결과는 파일로) → 실패면 `record --status failed` → 성공이면 `monitor-round convert` → `judge`(반드시 `window`가 준 start·end) → `record --status ok` → `monitor-round show`와 배너 → `final`이면 완료(`monitor-round summary`, `notify done`, `CronDelete`).

**조회 실패**: `awsq` exit 3이면 `"$B/notify" auth "AWS 로그인 만료: 재로그인 필요"`, 세션에 `! aws login` 안내, `record --status failed`.
exit 2, Sentry 조회 실패, `judge` exit 2(입력 오류)이면 같은 기록에 `"$B/notify" anomaly "<티켓> 조회 실패"`. 실패한 회차는 판정하지 않고, 어떤 경우에도 "이상 없음"이라고 쓰지 않는다. 다음 회차가 빠진 구간부터 다시 본다.

## 시작 모드

작업 폴더 `D` = 세션 스크래치패드의 `deploy-monitor/<티켓>/`(절대경로). 여기에 `state.json`, `plan.json`, `tick.query`, `rounds.log`가 생긴다. 레포에는 아무것도 쓰지 않는다.

1. **레포 인프라 기록.** `~/.claude/deploy-monitor/<레포 최상위 폴더 이름>.md`를 연다.
   - 없으면 `references/infra-discovery.md`대로 레포와 조회 전용 AWS 호출로 먼저 찾고, 값마다 근거를 붙인 초안을 보여 준 뒤 실행자와 확정해 저장한다.
     빈칸 질문지를 내지 않는다. 값끼리 어긋나면 실행자에게 고르라고 하지 않고 조회로 판정해 제안한다.
   - 있으면 기록을 보여 주고 "추가할 게 있는지 살펴볼까요, 이대로 진행할까요?"라고 묻는다.
2. **티켓과 변경 읽기.** Jira 연결 도구로 티켓 본문을, 티켓 키로 `git log --all --grep`과 PR 검색으로 배포된 변경을 읽는다.
   티켓이 고친 기능(성공 지표), 새로 넣은 오류 로그(감시 라벨), 여전히 실패하는 징후(감시 라벨)를 뽑는다.
3. **배포 시각.** 근거와 함께 제안한다 — `aws ecs describe-services`의 `deployments[].createdAt`·`events`, 운영 배포 브랜치에 병합된 시각.
   티켓 변경이 아직 운영에 없어 보이면 근거를 보이고 **시작하지 않는다.**
4. **모니터링 계획 제안.** 먼저 제안하고 의논해 확정한다. 마지막에 "빠진 것이 없을까요?"를 한 번 더 묻는다.

   | 항목 | 제안 내용 |
   |---|---|
   | 티켓 전용 확인 | 감시 라벨(나오면 알림)과 성공 지표(건수만 기록), 각각 로그에서 찾을 문구 |
   | 전체 ERROR | 배포 전 기준선과 비교한 새 유형·급증 |
   | ECS 지표 | CPU·메모리 최댓값과 상한(예: 80%, 85%) |
   | Sentry | 레포가 쓰고 Claude Code에 연결돼 있으면 배포 후 처음 본 이슈. 연결이 인증되지 않았으면 "인증할까요, Sentry는 빼고 진행할까요?" |
   | 대상별 점검 주기 | 짧게 볼 것·길게 볼 것. 예약은 가장 짧은 주기로 하나만 건다 — 매 회차는 직전 회차 이후만 스캔하므로 회차를 잘게 나눠도 총 스캔량은 같다 |
   | 종료 시각 | 예: 배포 후 24시간 |
   | 급증 기준 | 기준선 시간당 평균의 `3.0`배 이상이면서 최소 `5`건, 같은 이상 재알림은 `5`건 더 쌓일 때 |
   | 기준선 | 배포 시각 이전 7일 = 168시간(다르게 정하면 그 값을 `plan.json`의 `baseline_hours`에) |

5. **상태 준비.** `plan.json`과 `tick.query`(형식은 아래, 쿼리는 `references/tick.md`의 예시)를 쓰고, 한 번의 Bash 호출로:

   ```bash
   B="<스크립트 폴더 절대경로>"; D="<작업 폴더 절대경로>"; DEPLOY=<배포 epoch>; HOURS="$(jq .baseline_hours "$D/plan.json")"
   "$B/monitor-state" init --state "$D/state.json" --ticket <티켓> --deploy-time "$DEPLOY" --end-time <종료 epoch> \
     --spike-multiplier 3.0 --spike-min 5 --realert-step 5
   LG=(); while read -r g; do LG+=(--log-group "$g"); done < <(jq -r '.log_groups[]' "$D/plan.json")
   "$B/awsq" logs --region "$(jq -r .region "$D/plan.json")" "${LG[@]}" --start "$((DEPLOY - HOURS * 3600))" --end "$DEPLOY" \
     --query-file "$D/tick.query" --limit 10000 > "$D/baseline.awsq.json"; echo "baseline_rc=$?"
   "$B/monitor-round" convert --plan "$D/plan.json" --awsq "$D/baseline.awsq.json" --out "$D/baseline.counts.json" \
     --mode baseline --limit 10000
   ```

   - 기준선 조회가 실패하면(`awsq` exit 2·3) 시작하지 않고 원인을 알린다 — 기준선 없이 판정하면 모든 오류가 "새 유형"이 된다.
   - `convert`가 `truncated: true`를 내면(행 수가 10000에 닿음) **시작하지 않는다.** 잘린 기준선으로는 예전부터 있던 유형이 "새 유형"으로 판정돼 소음 배너가 울린다.
     실행자에게 알리고 더 짧은 묶음 키를 제안한다(예: `substr(msg, 0, 120)` → `substr(msg, 0, 40)`, 또는 `sig`를 예외 클래스만 `parse`로 뽑기). 쿼리를 고친 뒤 기준선부터 다시 한다.
   - 성공하면 `"$B/monitor-state" baseline --state "$D/state.json" --counts "$D/baseline.counts.json" --hours "$HOURS"`.
   - `convert` 출력의 `bytes_scanned`를 `plan.json`의 `baseline_bytes`에 적는다 — 완료 요약의 총 스캔량에 더한다.
6. **시작 기록.** 세션 화면에 확정한 계획(볼 대상, 주기, 종료 시각, 급증 기준, 기준선 스캔량)을 남기고 한 줄을 덧붙인다:
   "이 세션은 모니터링 전용으로 열어 두고, Mac이 잠들지 않게 해 주세요." 그다음 `"$B/notify" start "<티켓> 모니터링 시작"`.
7. **예약 또는 재생.**
   - 종료 시각이 미래면 `CronCreate`로 recurring 예약을 건다. prompt는 `/demiurge:deploy-monitor tick <state.json 절대경로>`,
     분은 정각·30분을 피한다(예: 60분 주기 `7 * * * *`, 15분 주기 `7,22,37,52 * * * *`). 돌려받은 job ID를 `plan.json`의 `cron_job_id`에 적고 세션에 남긴다.
   - 실행자에게 알린다: 이 예약은 **이 세션 안에서만** 돌고, 세션이 **대기 중일 때만** 실행되며, recurring 예약은 **7일 뒤 자동 만료**된다.
     예약은 주기의 최대 절반(최대 30분)까지 늦게 실행될 수 있지만, 회차는 직전 회차 끝부터 지금까지를 보므로 빈 구간이 생기지 않는다.
   - 종료 시각이 이미 지났으면 예약하지 않고 **재생 실행**한다: 배포 시각부터 종료 시각까지 확정한 주기 경계마다 `window --now`를 그 경계로 바꿔
     회차 모드를 차례로 돌린다(마지막 경계는 종료 시각). 마지막 회차가 완료 요약을 쓴다.
   - **재생 중 조회가 실패하면 재생을 멈춘다.** 그 회차의 실패 처리(배너·`! aws login` 안내·`record failed`)를 **한 번만** 하고 남은 경계를 돌리지 않는다 — 경계마다 실패 배너를 띄우지 않는다.
     세션에 "재로그인 뒤 알려 주시면 <KST 경계>부터 이어서 재생합니다"라고 남긴다. 실행자가 알려 주면 **같은 경계부터** 다시 돈다(`window`가 덮인 구간 끝부터 다시 준다).

### `plan.json` 형식

```json
{
  "ticket": "SHOP-42",
  "repo": "shop-api",
  "region": "ap-northeast-1",
  "log_groups": ["/ecs/shop-api-prod"],
  "error_level": "ERROR",
  "watch": {"refund_api_fail": "환불 API 호출 실패", "user_not_found": "user_not_found"},
  "success": {"refund_ok": "환불 처리 완료"},
  "metrics": [
    {"label": "cpu", "namespace": "AWS/ECS", "metric": "CPUUtilization",
     "dimensions": ["ClusterName=shop-prod", "ServiceName=shop-api-prod"], "stat": "Maximum", "limit": 80}
  ],
  "sentry": null,
  "period_minutes": 60,
  "cron_job_id": "a1b2c3d4",
  "baseline_hours": 168,
  "baseline_bytes": 734003200,
  "logs_price_per_gb": 0.0076,
  "bin": "<스크립트 폴더 절대경로>"
}
```

`watch`·`success`의 값은 쿼리가 내는 `sig`에 대는 정규식이다. 감시 라벨은 1건만 나와도 알리고, 성공 지표는 알리지 않고 건수만 남긴다.
`tick.query`는 `references/tick.md`의 쿼리 예시처럼 행마다 `level`, `src`(함수·로거 이름, 메시지와 따로 낸 필드), `sig`, `n`을 내는 집계 쿼리여야 한다.
`logs_price_per_gb`는 그 리전의 Logs Insights 스캔 단가(선택)로, 있으면 완료 요약에 대략 비용이 함께 나온다.

## 이럴 때 멈추고 다시 본다

| 이런 생각이 들면 | 실제로는 |
|---|---|
| "어느 리전인지 실행자에게 물어보자" | 조회로 판정할 수 있는 것은 묻지 않는다. `describe-log-groups`로 확인하고 결과를 제안한다 |
| "배너에 구간·안내도 같이 넣으면 친절하겠다" | 배너 문구는 정해진 한 줄이다(`AWS 로그인 만료: 재로그인 필요`, `<티켓> 이상: <유형> <N>건`). 자세한 건 세션에 |
| "`aws login` 하라고 하면 되겠지" | 안내는 `! aws login`이다. `!`가 있어야 프롬프트에서 바로 실행된다 |
| "기준선보다 4배니 급증이다" | 판정은 `monitor-state judge`가 숫자로 한다. 최소 건수에 못 미치면 기존 오류다. 다시 판정하지 않는다 |
| "회차 결과를 자세히 정리하자" | 회차 기록은 3~6줄이다. 자세한 정리는 완료 요약에서 한 번 |
| "원문을 한 번 보면 원인을 알 텐데" | 원문은 세션에 올리지 않는다. 필요하면 실행자에게 CloudWatch 콘솔에서 보라고 안내한다 |
| "판정 결과에 이미 `<id>`로 가려져 있다" | 가려지는 건 ID·숫자뿐이고 문장은 남는다. `judge.json`·`summary.json`을 열지 말고 `monitor-round show`·`summary` 출력만 쓴다 |
