# 회차 모드 — 한 번의 점검

`/demiurge:deploy-monitor tick <state.json 절대경로>`로 깨어났을 때 이 문서를 처음부터 끝까지 따른다.
대화가 압축돼 앞선 계획을 기억하지 못해도 이 문서와 작업 폴더만으로 회차를 돌릴 수 있어야 한다.

## 모든 Bash 호출 맨 앞에 붙이는 머리말

Bash 호출 사이에는 셸 변수가 남지 않는다. 그래서 **회차의 모든 Bash 호출 맨 앞에** 아래 두 줄을 그대로 붙인다(`<…>`만 tick 인자로 바꾼다).
스크립트 폴더 경로는 시작 모드가 `plan.json`의 `bin`에 절대경로로 적어 두었으므로 거기서 읽는다.

```bash
STATE="<tick 인자로 받은 state.json 절대경로>"; D="$(dirname "$STATE")"; B="$(jq -r .bin "$D/plan.json")"; T="$(jq -r .ticket "$D/plan.json")"
START="$(jq -r '.start // empty' "$D/window.json" 2>/dev/null)"; END="$(jq -r '.end // empty' "$D/window.json" 2>/dev/null)"
```

## 작업 폴더

| 파일 | 내용 | 누가 쓰나 |
|---|---|---|
| `state.json` | 덮인 구간, 기준선, 알림 누적, 기존 오류 누적, 조회 실패, 총 스캔량 | `monitor-state`만 |
| `plan.json` | bin 경로, 리전, 로그 그룹, 감시 라벨, 성공 지표, 지표 상한, Sentry, 주기, 예약 job ID, 기준선 길이·스캔량 | 시작 모드 |
| `tick.query` | 회차마다 쓰는 Logs Insights 쿼리 | 시작 모드 |
| `window.json` | 이번 회차의 창 | 회차 1단계 |
| `rounds.log` | 회차마다 한 줄(구간, 성공·실패, 성공 지표 건수) | `monitor-round log` |
| `round.awsq.json`, `metric.<label>.json`, `sentry.json`, `round.counts.json`, `judge.json`, `summary.json`, `baseline.*` | 조회·판정 원본. **원문이 섞여 있다** | 회차·시작 모드 |

마지막 줄의 파일들은 **세션에 내용을 출력하지 않는다.** `cat`·`Read`·`jq .`·`jq .existing` 등으로 열지 않는다.
집계 쿼리라도 메시지 안에 고객 이름·식별자·문장이 섞여 나오고, `monitor-state`의 정규화는 ID·숫자만 가린다.
세션과 배너에 보이는 것은 `monitor-round`가 찍는 것뿐이다. 그 출력의 오류 이름은 `<src> · <예외 클래스> #<해시 6자리>` 꼴로 **메시지 본문을 담지 않는다**
(예: `notify_customer #3f9a1c`, `payments · GatewayTimeoutError #b20e47`). 같은 유형은 회차가 달라도 같은 이름이다. 감시 라벨·성공 지표는 계획에서 정한 이름 그대로 보인다.
이름만으로 원인을 알 수 없으면 실행자에게 CloudWatch에서 그 `src`(함수·로거)와 시각으로 찾아보라고 안내한다.

## 순서

```
1 window ─┬─ empty:true → "새 구간 없음" 한 줄, 끝
          └─ 2 로그 조회 → 3 지표 조회 → 4 Sentry ─┬─ 하나라도 실패 → 실패 처리, 끝 (final이어도 완료하지 않음)
                                                   └─ 5 변환 ─┬─ 실패 → 실패 처리, 끝
                                                              └─ 6 judge ─┬─ exit 2 → 실패 처리
                                                                          ├─ exit 3 → 중복 기상, 한 줄, 끝
                                                                          └─ 7 record ok → 8 표시·배너 → 9 회차 기록 → final이면 10 완료
```

1. **창 정하기.**

   ```bash
   <머리말>
   "$B/monitor-state" window --state "$STATE" --now "$(date +%s)" > "$D/window.json"; cat "$D/window.json"
   ```

   재생 실행이면 `$(date +%s)` 대신 지정된 경계 시각을 넣는다.
   이후 모든 단계는 `window.json`의 `start`·`end`(머리말의 `START`·`END`)를 그대로 쓴다. 직접 계산하지 않는다 — `judge`는 start가 덮인 구간 끝과 다르면 exit 2로 거부한다.
   창은 `[START, END)`다. `awsq logs`가 Logs Insights에 `END-1`을 끝 시각으로 넘기므로 경계의 초가 두 회차에 겹쳐 세지지 않는다.
   `empty: true`면 판정하지 않는다(`judge`는 길이 0인 창에 exit 2). 예약이 밀려 늦게 깨어나도 `window`가 직전 끝부터 지금까지를 주므로 따로 보정하지 않는다.
2. **로그 조회.** 결과는 파일로만 받는다.

   ```bash
   <머리말>
   R="$(jq -r .region "$D/plan.json")"; LG=(); while read -r g; do LG+=(--log-group "$g"); done < <(jq -r '.log_groups[]' "$D/plan.json")
   "$B/awsq" logs --region "$R" "${LG[@]}" --start "$START" --end "$END" --query-file "$D/tick.query" > "$D/round.awsq.json"; echo "logs_rc=$?"
   ```

3. **지표 조회.** `plan.json`의 `metrics` 항목을 모두 돈다. 가장 나쁜 종료 코드를 남긴다(3이 2보다 우선).

   ```bash
   <머리말>
   R="$(jq -r .region "$D/plan.json")"; RC=0
   while read -r m; do
     DIMS=(); while read -r x; do DIMS+=(--dimension "$x"); done < <(jq -r '.dimensions[]' <<<"$m")
     "$B/awsq" metric --region "$R" --namespace "$(jq -r .namespace <<<"$m")" --metric "$(jq -r .metric <<<"$m")" \
       "${DIMS[@]}" --stat "$(jq -r '.stat // "Maximum"' <<<"$m")" --start "$START" --end "$END" \
       > "$D/metric.$(jq -r .label <<<"$m").json"
     rc=$?; if [ "$rc" -eq 3 ] || { [ "$rc" -ne 0 ] && [ "$RC" -eq 0 ]; }; then RC=$rc; fi
   done < <(jq -c '.metrics[]' "$D/plan.json")
   echo "metrics_rc=$RC"
   ```

4. **Sentry.** 먼저 지난 회차의 결과를 지운다 — `sentry`가 null이어도 한다(남은 파일이 5단계에 실려 옛 이슈로 판정되는 것을 막는다):

   ```bash
   <머리말>
   rm -f "$D/sentry.json"
   ```

   `plan.json`의 `sentry`가 null이 아닐 때만 아래를 한다. 연결된 Sentry 도구로 그 프로젝트에서 **처음 본 시각(first seen)이 `[START, END)` 안**인 이슈만 찾는다. 배포 전부터 있던 이슈는 보지 않는다.
   결과를 `{"<short ID>": <이벤트 수>}` 꼴로 `$D/sentry.json`에 쓴다(없으면 `{}`). 이슈 제목은 원문이 섞일 수 있어 파일에도 쓰지 않는다.
   Sentry 조회가 실패하면 그 회차는 실패다(아래 [조회 실패](#조회-실패), 사유 `sentry`).
5. **변환.** 2~4단계가 모두 성공했을 때만. 지난 회차의 `round.counts.json`을 먼저 지운다 — 변환이 실패했는데 옛 파일이 남아 있으면 6단계가 새 창을 옛 건수로 판정하고 구간을 덮어 버린다.

   ```bash
   <머리말>
   rm -f "$D/round.counts.json"
   METRIC_ARGS=(); while read -r l; do METRIC_ARGS+=(--metric "$l=$D/metric.$l.json"); done < <(jq -r '.metrics[].label' "$D/plan.json")
   SENTRY_ARGS=(); [ -f "$D/sentry.json" ] && SENTRY_ARGS=(--sentry "$D/sentry.json")
   "$B/monitor-round" convert --plan "$D/plan.json" --awsq "$D/round.awsq.json" --out "$D/round.counts.json" "${METRIC_ARGS[@]}" "${SENTRY_ARGS[@]}"; echo "convert_rc=$?"
   ```

   `convert_rc`가 0이 아니면(`ROUND_ERROR`) 그 회차는 실패다. 사유 `convert`로 [조회 실패](#조회-실패) 처리하고 6단계로 가지 않는다.

   출력은 행 수·잘림 여부·라벨별 건수·지표별 최댓값과 점 개수(`metrics`)·스캔량뿐이다. 회차 기록의 지표 값은 여기서 옮긴다(`metric.*.json`을 열지 않는다). 감시 라벨·성공 지표에 걸린 행은 오류 유형에서 빠지고(같은 일로 배너 두 번 방지),
   지표는 상한을 넘은 점 개수가 `metric:<label>><상한>`, **점이 하나도 없으면 `nodata:<label>`** 감시 라벨이 된다 — 빈 `datapoints`는 "정상"이 아니라 "자료 없음"이다.
   `truncated: true`면 쿼리 `--limit`(기본 1000)에 걸려 유형이 잘렸을 수 있으니 회차 기록에 적는다.
6. **판정.** 반드시 `window.json`의 값으로.

   ```bash
   <머리말>
   "$B/monitor-state" judge --state "$STATE" --counts "$D/round.counts.json" --start "$START" --end "$END" > "$D/judge.json"; echo "judge_rc=$?"
   ```

   - exit 0: 덮인 구간이 이미 `END`로 전진했다.
   - exit 2(입력 오류): 그 회차는 실패다. 사유 `judge_input`으로 [조회 실패](#조회-실패) 처리, 배너는 `"$T 조회 실패"`. "이상 없음"이라고 쓰지 않는다.
   - exit 3(이미 판정한 창과 겹침): 같은 회차가 두 번 깨어난 것이다. 기록·배너 없이 한 줄 남기고 끝낸다.
7. **기록.**

   ```bash
   <머리말>
   "$B/monitor-state" record --state "$STATE" --start "$START" --end "$END" --status ok --bytes-scanned "$(jq .bytes_scanned "$D/round.awsq.json")"
   ```

   `record ok`는 구간을 뒤로 돌리지 않고 스캔량을 누적한다.
8. **표시와 배너.**

   ```bash
   <머리말>
   "$B/monitor-round" show --judge "$D/judge.json" --ticket "$T"
   ```

   찍히는 줄: `ALERT <종류> <이름> <건수>건 누적 <합계>`, `EXISTING <k>유형 <n>건`, 알림이 있으면 `BANNER <문구>`.
   `BANNER` 줄이 있으면 그 문구 그대로 `"$B/notify" anomaly "<BANNER 뒤 문구>"`. 없으면 배너를 띄우지 않는다.
   기존 오류만 늘어난 회차는 `judge`가 상태에 누적해 두었으므로 완료 요약에서 보인다. "Traceback이 기준선보다 4배"처럼 보여도 `judge`가 existing으로 냈으면 이상이 아니다(최소 건수 기준 미달). 직접 다시 판정하지 않는다.
   `notify`가 exit 1이면 회차 기록에 "배너 실패"를 적고 넘어간다.
9. **회차 기록.** 세션에 아래 형식으로 쓰고, `rounds.log`에 남긴다.

   ```bash
   <머리말>
   "$B/monitor-round" log --rounds "$D/rounds.log" --start "$START" --end "$END" --status ok --counts "$D/round.counts.json"
   ```

10. `window.json`이 `final: true`였으면 [완료](#완료).

## 쿼리 예시 — 확인 여럿을 한 번에

같은 로그 그룹을 보는 확인(전체 ERROR 유형, 티켓 감시 라벨, 성공 지표)은 **한 쿼리**로 합친다. 스캔량 과금이 쿼리 수만큼 늘기 때문이다.
행마다 `level`, `src`(함수·로거 이름 — 메시지와 **따로 낸 필드**), `sig`(메시지 앞부분), `n`을 내는 것이 `monitor-round convert`와의 약속이다. 레포마다 필드 이름이 다르면 `as`로 맞춘다.

아래 예시는 JSON 로그 필드가 `lvl`(수준)·`fn`(함수 이름)·`text`(메시지)인 레포다. 필드 이름은 레포 인프라 기록의 "로그 형식" 칸에서 가져온다.

```
fields if(ispresent(lvl), lvl, "ERROR") as level,
       if(ispresent(lvl), fn, "stderr") as src,
       substr(if(ispresent(lvl), text, @message), 0, 120) as sig
| filter lvl = "ERROR"
      or text like /환불 API 호출 실패|user_not_found|환불 처리 완료/
      or (not ispresent(lvl) and @message like /Traceback|Exception ignored/)
| stats count(*) as n by level, src, sig
```

- 마지막 `filter` 줄은 **수준 필드가 없는 오류 줄**(JSON 로거를 거치지 않고 표준 오류로 바로 찍히는 Python `Traceback …`, `Exception ignored in …` 같은 줄)을 잡는 분기다.
  이런 줄은 `lvl = "ERROR"`에 걸리지 않아 빠뜨리기 쉽다. `src`는 고정값 `stderr`, 수준은 `ERROR`로 묶는다.
  이 분기의 문구는 레포 인프라 기록의 "수준 없는 오류 줄" 칸에 적힌 패턴을 쓴다. 기록에 "없음"이면 이 분기를 뺀다.

- 원문 행(`fields @message` 그대로)을 내보내는 쿼리를 쓰지 않는다. 늘 `stats count(*) … by`로 집계해서 받는다.
- `sig`는 유형을 가를 만큼만 자른다(`substr`). 감시 문구는 메시지 앞부분에 오는 것을 고른다 — 잘린 뒤에 있으면 못 잡는다.
- 배포 전 기준선도 같은 쿼리를 쓴다. 기준선은 `--limit 10000`으로 조회한다(SKILL.md 시작 모드 5단계).
- 조회 시간이 길어 `awsq`가 기다리다 포기해도 쿼리를 멈추는 호출(`stop-query`)은 하지 않는다. 조회 전용으로 만든 설계라서다 — 쿼리는 AWS 쪽 시간 제한에 맞춰 스스로 끝난다.
  회차 조회의 대기 한도는 `awsq logs`의 기본값 120초다. 넘기면 `AWS_ERROR: query did not finish within …s … (queryId …)`(exit 2)로 그 회차는 실패이고,
  queryId(쿼리 번호, 고객 정보 아님)를 회차 기록에 적는다. 같은 회차 안에서 다시 돌리지 않는다 — 다시 돌리면 같은 구간의 스캔을 한 번 더 산다.

## 조회 실패

로그(2단계)·지표(3단계)·Sentry(4단계) 중 하나라도 실패하면 그 회차는 실패다. 남은 조회를 이어 하지 않는다. 변환(5단계) 실패와 `judge` exit 2도 같은 처리다.

| 원인 | 배너 | 세션 | 사유 |
|---|---|---|---|
| `awsq` exit 3 (`AWS_AUTH_EXPIRED`) | `"$B/notify" auth "AWS 로그인 만료: 재로그인 필요"` | "`! aws login`을 실행해 주세요." | `auth` |
| `awsq` exit 2 (`AWS_ERROR`) | `"$B/notify" anomaly "$T 조회 실패"` | `AWS_ERROR` 줄의 요지 | `aws_error` |
| Sentry 실패 | `"$B/notify" anomaly "$T 조회 실패"` | Sentry 연결 확인 요청 | `sentry` |
| `monitor-round convert` 실패 | `"$B/notify" anomaly "$T 조회 실패"` | `ROUND_ERROR` 요지 | `convert` |
| `judge` exit 2 | `"$B/notify" anomaly "$T 조회 실패"` | `STATE_ERROR` 요지 | `judge_input` |

```bash
<머리말>
BYTES="$(jq -r '.bytes_scanned // 0' "$D/round.awsq.json" 2>/dev/null || echo 0)"   # 로그 조회는 성공했으면 그 스캔량도 센다
"$B/monitor-state" record --state "$STATE" --start "$START" --end "$END" --status failed --reason <사유> --bytes-scanned "${BYTES:-0}"
"$B/monitor-round" log --rounds "$D/rounds.log" --start "$START" --end "$END" --status failed
```

- 배너 문구는 표 그대로 쓴다. 구간·안내를 덧붙이지 않는다(배너는 한 줄, 자세한 건 세션에).
- 재로그인 안내는 반드시 `! aws login` 형태다. 앞의 `!`가 Claude Code 프롬프트에서 셸 명령을 바로 실행하게 한다.
- 실패한 회차는 **판정하지 않는다**(`judge` 금지). 판정하면 그 구간이 덮인 것으로 처리되어 다시 보지 않는다.
- 이 회차를 "이상 없음", "정상", "문제 없음"이라고 쓰지 않는다. "조회 실패 — 판정 못 함"이라고 쓴다.
- `record failed`는 덮인 구간을 그대로 두므로 다음 회차의 `window`가 이번 창부터 다시 준다. 세션에 그렇게 적는다.
- 같은 회차 안에서 재로그인을 기다리거나 조회를 되풀이하지 않는다. 다음 예약 회차가 다시 본다.
- `final` 회차가 실패하면 완료하지 않고 예약을 남긴다. 다음 회차가 마지막 구간을 다시 보고 완료한다.
- 재생 실행 중이면 SKILL.md 시작 모드 7단계의 재생 실패 규칙을 따른다(배너 한 번, 재생 멈춤).

## 회차 기록 형식 (세션, 3~6줄)

```
[LEDGER-42 회차] 10-22 20:06–21:08 KST · 조회 2건(로그 1·지표 1) · 스캔 46.0 MB
알림 1건: new notify_customer #3f9a1c 3건 (배너 보냄)
기존 오류 1유형 1건 (완료 요약에 모음) · 성공 지표 refund_ok 5건 · CPU 최대 40.1% / 상한 80%
```

실패 회차:

```
[LEDGER-42 회차] 10-22 20:06–21:08 KST · 조회 실패(AWS 로그인 만료) — 판정 못 함
`! aws login`을 실행해 주세요. 다음 회차가 20:06부터 다시 조회합니다.
```

시각은 KST로 쓴다. 오류 이름은 `monitor-round show`가 찍은 그대로 옮긴다. 이상 근거(왜 티켓과 관련 있다고 보는지)는 알림이 있을 때만 한 줄 덧붙인다.

## 완료

```bash
<머리말>
"$B/monitor-state" summary --state "$STATE" > "$D/summary.json"
"$B/monitor-round" summary --summary "$D/summary.json" --plan "$D/plan.json" --rounds "$D/rounds.log"
```

`monitor-round summary`가 찍은 요약을 **그대로** 세션에 옮긴다(목차: 티켓 전용 확인 결과 → 이상 알림 → 기존 오류 → 조회 실패 구간 → 총 스캔량).
`summary.json`을 직접 열어 보충하지 않는다. 급증으로 알린 유형은 "급증 회차 N건 + 평소 수준 회차 M건"으로 함께 나온다.
마지막 `BANNER` 줄의 문구로 `"$B/notify" done "<문구>"`, `plan.json`의 `cron_job_id`로 `CronDelete`(재생 실행이라 예약이 없으면 생략), `plan.json`에 `"done": true`를 적는다.
이미 `"done": true`면(예약 해제 전에 한 번 더 깨어난 경우) 아무것도 하지 않고 한 줄만 남긴다.
