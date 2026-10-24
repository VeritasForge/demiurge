# 회차 모드 — 한 번의 점검

`/demiurge:deploy-monitor tick <state.json 절대경로>`로 깨어났을 때 이 문서를 처음부터 끝까지 따른다.
대화가 압축돼 앞선 계획을 기억하지 못해도 이 문서와 작업 폴더만으로 회차를 돌릴 수 있어야 한다.

## 작업 폴더

`state.json`이 있는 폴더(`D`)에 시작 모드가 만든 파일이 모여 있다. 회차는 이 파일들만 믿는다.

| 파일 | 내용 | 누가 쓰나 |
|---|---|---|
| `state.json` | 덮인 구간, 기준선, 알림 누적, 기존 오류 누적, 조회 실패, 총 스캔량 | `monitor-state`만 |
| `plan.json` | 리전, 로그 그룹, 감시 라벨, 성공 지표, 지표 상한, Sentry, 주기, 예약 job ID | 시작 모드 |
| `tick.query` | 회차마다 쓰는 Logs Insights 쿼리 | 시작 모드 |
| `rounds.log` | 회차마다 한 줄 JSON(건수만) — 성공 지표 합계·Sentry 실패를 요약에 쓰기 위해 | 회차 |
| `round.awsq.json`, `metric.<label>.json`, `round.counts.json`, `judge.json`, `summary.json`, `baseline.*.json` | 조회·판정 원본. **원문이 섞일 수 있다** | 회차(덮어씀)·시작 모드 |

마지막 줄의 파일들은 **세션에 내용을 출력하지 않는다.** `cat`·`Read`·`jq .`(전체 출력)로 열지 않는다. `jq .bytes_scanned`처럼 숫자 하나를 꺼내는 것만 된다.
쿼리가 집계를 해도 오류 메시지 안에 고객 식별자나 메시지 원문이 섞여 나온다(예: `Slack 전송 실패 channel=C0…: 환불 문의드립니다 010-…`).
`monitor-state`의 정규화는 ID·숫자만 가리고 문장은 남기므로, judge 출력도 그대로 보이면 원문이 샌다.
세션에 보이는 것은 아래 두 스크립트 조각이 찍는 **잘린 유형 이름과 건수**뿐이다.

## 순서

```
window ─┬─ empty:true ──────────────────────────→ "새 구간 없음" 한 줄, 끝
        └─ start/end ─→ 조회(로그·지표·Sentry) ─┬─ 실패 → record failed → 실패 알림 → (final이어도 완료하지 않음)
                                                └─ 성공 → 변환 → judge → record ok → 표시 → 알림 → final이면 완료
```

```bash
B="${CLAUDE_SKILL_DIR}/bin"
STATE="<state.json 절대경로>"; D="$(dirname "$STATE")"
NOW=$(date +%s)          # 재생 실행이면 지정된 경계 시각
"$B/monitor-state" window --state "$STATE" --now "$NOW" > "$D/window.json"; cat "$D/window.json"
START=$(jq .start "$D/window.json"); END=$(jq .end "$D/window.json")
```

1. **창 정하기.** `window`가 돌려준 `start`·`end`를 이 회차 끝까지 그대로 쓴다. 직접 계산하지 않는다.
   `judge`는 start가 직전 끝과 이어지는지 검사하지 않으므로, 다른 값을 넣으면 빈 구간이나 겹침이 생긴다.
   `empty: true`면 판정하지 않는다(`judge`는 길이 0인 창에 exit 2). 예약이 밀려 늦게 깨어나도 `window`가 직전 끝부터 지금까지를 주므로 따로 보정하지 않는다.
2. **조회.** 로그·지표를 모두 조회한 뒤에 판정한다. 결과는 파일로만 받는다.

   ```bash
   R=$(jq -r .region "$D/plan.json")
   LG=(); while read -r g; do LG+=(--log-group "$g"); done < <(jq -r '.log_groups[]' "$D/plan.json")
   "$B/awsq" logs --region "$R" "${LG[@]}" --start "$START" --end "$END" \
     --query-file "$D/tick.query" > "$D/round.awsq.json"; LOGS_RC=$?
   # plan.json metrics 항목마다
   "$B/awsq" metric --region "$R" --namespace AWS/ECS --metric CPUUtilization \
     --dimension ClusterName=<클러스터> --dimension ServiceName=<서비스> \
     --start "$START" --end "$END" --stat Maximum > "$D/metric.cpu.json"; RC=$?
   ```

   한 번이라도 exit 0이 아니면 그 회차는 실패다 → [조회 실패](#조회-실패). 판정으로 넘어가지 않는다.
3. **변환.** 집계 행을 `judge` 입력으로 바꾼다. 감시 라벨·성공 지표에 걸린 행은 오류 유형에서 뺀다(같은 일로 배너가 두 번 울리지 않게).
   지표는 상한을 넘은 점의 개수를 `metric:<label>><상한>` 감시 라벨로, 점이 하나도 없으면 `nodata:<label>`로 넣는다.
   **빈 `datapoints`는 "정상"이 아니라 "자료 없음"이다** — 서비스가 멈췄거나 차원 값이 틀렸을 수 있어 감시 라벨로 올린다.

   ```bash
   python3 -I - "$D" round <<'PY'
   import json, re, sys
   d, mode = sys.argv[1], sys.argv[2]
   plan = json.load(open(f"{d}/plan.json"))
   rows = json.load(open(f"{d}/{mode}.awsq.json"))["rows"]
   errors, watch, success = {}, {}, {}
   for row in rows:
       text, n = row.get("sig", ""), int(float(row.get("n", 0)))
       hit = False
       for table, labels in ((watch, plan.get("watch", {})), (success, plan.get("success", {}))):
           for label, pattern in labels.items():
               if re.search(pattern, text):
                   table[label] = table.get(label, 0) + n
                   hit = True
       if not hit and row.get("level") == plan.get("error_level", "ERROR"):
           key = f'{row["func"]} | {text}' if row.get("func") else text
           errors[key] = errors.get(key, 0) + n
   if mode == "baseline":
       payload = errors
   else:
       for m in plan.get("metrics", []):
           points = json.load(open(f'{d}/metric.{m["label"]}.json'))["datapoints"]
           over = sum(1 for p in points if p["v"] > m["limit"])
           if not points:
               watch[f'nodata:{m["label"]}'] = 1
           elif over:
               watch[f'metric:{m["label"]}>{m["limit"]}'] = over
       payload = {"errors": errors, "watch": watch, "success": success}
   json.dump(payload, open(f"{d}/{mode}.counts.json", "w"), ensure_ascii=False)
   print(json.dumps({"rows": len(rows), "truncated": len(rows) >= 1000,
                     "error_types": len(errors), "error_count": sum(errors.values()),
                     "watch": watch, "success": success}, ensure_ascii=False))
   PY
   ```

   이 조각이 찍는 줄에는 라벨 이름과 건수만 있다. `truncated: true`면 쿼리 `--limit`(기본 1000)에 걸려 유형이 잘렸을 수 있으니 회차 기록에 적는다.
4. **판정과 기록.** `judge` 출력도 파일로 받는다.

   ```bash
   "$B/monitor-state" judge --state "$STATE" --counts "$D/round.counts.json" \
     --start "$START" --end "$END" > "$D/judge.json"
   "$B/monitor-state" record --state "$STATE" --start "$START" --end "$END" \
     --status ok --bytes-scanned "$(jq .bytes_scanned "$D/round.awsq.json")"
   ```

   `judge`가 성공하면 덮인 구간이 이미 `end`로 전진한다. `record ok`는 구간을 뒤로 돌리지 않으며 스캔량을 누적한다.
   `judge` exit 3(이미 판정한 창과 겹침)은 같은 회차가 두 번 깨어난 것이다 — 기록 없이 한 줄 남기고 끝낸다.
5. **표시.** 세션에 보일 이름을 만든다. 이름은 signature에서 `func | ` 다음 첫 `: ` 앞까지, 최대 60자다.
   예: `send_to_channel | Slack 전송 실패 channel=<id> team=<id> user=<id>: 환불 문의…` → `send_to_channel | Slack 전송 실패 channel=<id> team=<id> user=<id>`.

   ```bash
   python3 -I - "$D/judge.json" <<'PY'
   import json, sys
   def name(sig):
       head, sep, rest = sig.partition(" | ")
       body = (rest if sep else head).split(": ", 1)[0][:60]
       return f"{head} | {body}" if sep else body
   j = json.load(open(sys.argv[1]))
   for a in j.get("alerts", []):
       print(f'ALERT {a["kind"]} {name(a["signature"])} {a["count"]}건 누적 {a["total"]}')
   ex = j.get("existing", {})
   print(f"EXISTING {len(ex)}유형 {sum(ex.values())}건")
   PY
   ```

6. **알림.** `ALERT`가 하나라도 있으면 회차당 배너 하나:
   `"$B/notify" anomaly "<티켓> 이상: <첫 ALERT 이름> <건수>건"` (둘 이상이면 끝에 ` 외 <k>건`).
   `ALERT`가 없으면 배너를 띄우지 않는다 — 기존 오류만 늘어난 회차는 `judge`가 `existing`으로 상태에 누적해 두었으므로 완료 요약에서 보여 준다.
   "Traceback이 기준선보다 4배"처럼 보여도 `judge`가 existing으로 냈으면 이상이 아니다(최소 건수 기준에 못 미친 것). 직접 다시 판정하지 않는다.
   `notify`가 exit 1이면 회차 기록에 "배너 실패"를 적고 넘어간다.
7. **회차 기록**(아래 형식)을 세션에 쓰고 `rounds.log`에 한 줄 덧붙인다.

   ```bash
   jq -nc --argjson s "$START" --argjson e "$END" --arg st ok \
     --argjson c "$(jq .success "$D/round.counts.json")" \
     '{start:$s,end:$e,status:$st,success:$c}' >> "$D/rounds.log"
   ```

   실패 회차도 `{start, end, status:"failed"}` 한 줄을 남긴다. Sentry만 실패했으면 `sentry_failed:true`를 더한다.

8. `window`가 `final: true`였고 이 회차가 성공했으면 [완료](#완료).

## 쿼리 예시 — 확인 여럿을 한 번에

같은 로그 그룹을 보는 확인(전체 ERROR 유형, 티켓 감시 라벨, 성공 지표)은 **한 쿼리**로 합친다. 스캔량 과금이 쿼리 수만큼 늘기 때문이다.
행마다 `level`, `sig`, `n`(그리고 있으면 `func`)을 내는 것이 변환 조각과의 약속이다. 레포마다 필드 이름이 다르면 `as`로 맞춘다.

```
fields level, func, substr(msg, 0, 120) as sig
| filter level = "ERROR" or msg like /환불 API 호출 실패|user_not_found|환불 처리 완료/
| stats count(*) as n by level, func, sig
```

- 원문 행(`fields @message` 그대로)을 내보내는 쿼리를 쓰지 않는다. 늘 `stats count(*) … by`로 집계해서 받는다.
- `sig`는 유형을 가를 만큼만 자른다(`substr`). 감시 문구는 메시지 앞부분에 오는 것을 고른다 — 잘린 뒤에 있으면 못 잡는다.
- 배포 전 기준선도 같은 쿼리를 쓴다(변환 조각을 `baseline` 모드로).
- 조회 시간이 길어 `awsq`가 기다리다 포기해도 쿼리를 멈추는 호출(`stop-query`)은 하지 않는다. 조회 전용으로 만든 설계라 그렇다 — 쿼리는 AWS 쪽에서 제 시간 제한에 끝난다.

## 지표

`plan.json`의 `metrics` 항목마다 `awsq metric`을 창 `[start, end]`로 부른다. 판정은 계획에서 정한 상한을 넘은 점이 있느냐 하나다.
넘으면 `metric:<label>><상한>` 감시 라벨이 되어 `judge`가 처음 한 번 알리고, 이후 재알림 기준만큼 더 쌓였을 때 다시 알린다.

## Sentry (계획에 있을 때만)

연결된 Sentry 도구로 `plan.json`의 프로젝트에서 **처음 본 시각(first seen)이 `[start, end)` 안**인 이슈만 찾는다. 배포 전부터 있던 이슈는 보지 않는다.
찾은 이슈는 `sentry:<short ID>` 감시 라벨(값 = 이벤트 수)로 `round.counts.json`의 `watch`에 더해 `judge` 전에 넣는다. 이슈 제목은 원문이 섞일 수 있어 세션에는 short ID와 예외 클래스 이름만 쓴다.
Sentry 조회가 실패하면 회차 전체를 실패로 돌리지 않는다. 회차 기록과 `rounds.log`에 `"sentry_failed": true`를 남기고, 완료 요약의 "조회 실패 구간"에 넣는다.

## 조회 실패

| `awsq` 종료 코드 | 할 일 |
|---|---|
| 3 (`AWS_AUTH_EXPIRED`) | `"$B/notify" auth "AWS 로그인 만료: 재로그인 필요"` → 세션에 "`! aws login`을 실행해 주세요" → `record --status failed --reason auth` |
| 2 (`AWS_ERROR`) | `"$B/notify" anomaly "<티켓> 조회 실패"` → `record --status failed --reason aws_error` |

- 배너 문구는 위 그대로 쓴다. 구간·안내를 덧붙이지 않는다(배너는 한 줄, 자세한 건 세션에).
- 재로그인 안내는 반드시 `! aws login` 형태로 쓴다. 앞의 `!`가 Claude Code 프롬프트에서 셸 명령을 바로 실행하게 한다.
- 실패한 회차는 **판정하지 않는다**(`judge` 금지). 판정하면 그 구간이 덮인 것으로 처리되어 다시 보지 않는다.
- 이 회차를 "이상 없음", "정상", "문제 없음"이라고 쓰지 않는다. "조회 실패 — 판정 못 함"이라고 쓴다.
- `record failed`는 덮인 구간을 그대로 두므로 다음 회차의 `window`가 이번 창부터 다시 준다. 세션에 그렇게 적는다.
- 같은 회차 안에서 재로그인을 기다리거나 조회를 되풀이하지 않는다. 다음 예약 회차가 다시 본다.
- `final` 회차가 실패하면 완료하지 않고 예약을 남긴다. 다음 회차가 마지막 구간을 다시 보고 완료한다.

## 회차 기록 형식 (세션, 3~6줄)

```
[SHOP-42 회차] 10-22 20:06–21:08 KST · 조회 2건(로그 1·지표 1) · 스캔 46.0 MB
알림 1건: new send_to_channel | Slack 전송 실패 channel=<id> team=<id> user=<id> 3건 (배너 보냄)
기존 오류 1유형 1건 (완료 요약에 모음) · 성공 지표 refund_ok 5건 · CPU 최대 40.1% / 상한 80%
```

실패 회차:

```
[SHOP-42 회차] 10-22 20:06–21:08 KST · 조회 실패(AWS 로그인 만료) — 판정 못 함
`! aws login`을 실행해 주세요. 다음 회차가 20:06부터 다시 조회합니다.
```

시각은 KST로 쓴다. 이상 근거(왜 티켓과 관련 있다고 보는지)는 알림이 있을 때만 한 줄 덧붙인다.

## 완료

```bash
"$B/monitor-state" summary --state "$STATE" > "$D/summary.json"
```

`summary.json`도 signature를 담으므로 5단계의 `name()` 규칙으로 잘라 보인다. 목차는 이 순서다.

1. **티켓 전용 확인 결과** — 감시 라벨별 누적 건수(0건이면 0건이라고), `rounds.log`의 성공 지표 합계. 예: "고친 기능 정상: 환불 처리 완료 52건, user_not_found 0건".
2. **이상 알림 목록** — `alerts`의 종류·이름·누적 건수·처음 알린 시각(KST). 급증(`spike`)으로 알린 유형은 급증 회차 건수만 `total`에 쌓이고, 급증이 아니었던 회차 건수는 `existing`에 쌓인다. 같은 유형이면 두 숫자를 나란히 보인다(예: "급증 회차 12건 + 평소 수준 회차 7건").
3. **기존 오류 묶음** — `existing`의 유형별 건수. 알리지 않은 이유(배포 전부터 비슷한 빈도) 한 줄.
4. **조회 실패 구간** — `failures`의 구간(KST)과 이유, `rounds.log`의 Sentry 실패. 없으면 "없음".
5. **총 스캔량** — `bytes_scanned_total` + `plan.json`의 `baseline_bytes`를 GB로, 그 리전 Logs Insights 단가를 곱한 대략 비용.

그다음 `"$B/notify" done "<티켓> 모니터링 완료: 이상 <N>건"`, `plan.json`의 `cron_job_id`로 `CronDelete`(재생 실행이라 예약이 없으면 생략), `plan.json`에 `"done": true`를 적는다.
이미 `"done": true`면(예약 해제 전에 한 번 더 깨어난 경우) 아무것도 하지 않고 한 줄만 남긴다.
