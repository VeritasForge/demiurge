# 엔진 레지스트리

SKILL.md의 Phase 3(엔진 선택)과 Phase 4(엔진 실행)에서 읽는다.

---

## 모든 엔진에 공통으로 강제하는 것

호출 프롬프트에 아래 세 줄을 그대로 넣는다. 특히 첫 줄이 중요하다 — 엔진 중 몇 개는 기본 동작이 "직접 게시"라서, 빼먹으면 병합되지 않은 원본이 PR에 따로 달린다.

```
- GitHub에 아무것도 게시하지 마세요. gh pr comment, gh api .../reviews, --comment 플래그 모두 금지입니다.
- 파일을 수정하지 마세요. 이 작업은 리뷰만 합니다.
- 결과를 다음 모양의 JSON 객체 **하나만** 반환하세요 — 그 앞뒤에 어떤 텍스트도 붙이지 마세요:
  {"findings": [{ ...아래 통합 발견 스키마... }], "coverage": ["실제로 읽은 파일 경로", "..."]}
```

통합 발견 스키마는 [merge.md](merge.md)의 "통합 발견 스키마" 절에 있다. `findings`는 그 스키마 배열이고, `coverage`는 그 엔진이 실제로 읽은 파일 목록이다.

**`coverage`를 JSON 안에 넣는 이유(실측 근거)**: 이전 버전은 JSON 뒤에 `COVERAGE:` 텍스트 줄을 별도로 요구했는데, "JSON으로만 반환하라"는 지시와 "JSON 뒤에 텍스트를 붙여라"는 지시가 문자 그대로 상충한다 — 엄격 JSON 파서를 쓰는 호출부라면 그 줄 때문에 파싱이 깨지거나, 반대로 그 줄만 따로 회수하려는 파서가 findings 배열은 놓칠 수 있다. 응답을 **하나의 유효 JSON 객체**로 고정하면 이 모호함이 사라진다.

**`coverage`가 계수의 근거다.** `covering_engines`("그 파일을 실제로 본 엔진 수")는 Phase 6 검증 게이트의 세 조건 중 하나인데, 엔진이 무엇을 읽었는지 안 말하면 **추정할 수밖에 없고 그 추정이 게이트 발화를 가른다.** 특히 문서 파일처럼 일부 엔진만 읽는 대상에서 갈린다.

목록을 안 주는 엔진은 다음 순서로 메운다:
1. ce는 JSON의 `coverage` 필드와 `reviewers` 목록을 쓴다
2. **읽은 것이 증명되는 파일은 읽은 것으로 센다** — 그 엔진이 `file:line`을 인용했거나, 그 파일에 대해 "확인했고 문제없다"고 기각한 경우다. 커버리지는 전부-아니면-전무가 아니라 **파일 단위**이므로, 목록이 없다고 해서 인용까지 무시할 이유가 없다
3. 그 밖의 파일은 **"변경 파일 전부를 봤다"고 가정하지 말고** `불명`으로 둔다
4. 추정이 들어갔다는 사실을 리포트 커버리지에 적는다

**`불명`은 어디서든 세지 않는다.** `covering_engines`를 읽는 곳이 셋이므로 한 곳만 정하면 나머지에서 흔들린다:

| 읽는 곳 | 불명 처리 |
|---|---|
| Phase 6 검증 게이트 (`>= 2`) | 미충족 — 게이트를 함부로 발화시키지 않는다 |
| 배지 (`== 1`이면 배지 없음) | 세지 않음 — 확인된 엔진만으로 판단 |
| 접기 규칙 (`>= 3`) | 미충족 — 근거가 불확실한 채로 발견을 숨기지 않는다 |

세 곳 모두 **불명이면 보수적인 쪽(발견을 살리는 쪽)**으로 기운다. 모르는 것을 근거로 발견을 지우거나 검증을 건너뛰지 않는다.

---

## E1. ce-code-review — 주력 엔진

```
PR 모드:   Skill(skill: "compound-engineering:ce-code-review", args: "mode:agent {PR번호}")
로컬 모드: Skill(skill: "compound-engineering:ce-code-review", args: "mode:agent base:{Phase 1의 MERGE_BASE}")
```

**`mode:agent`를 반드시 붙인다.** 이게 없으면 사람이 읽는 마크다운 표가 나오고, 있으면 코드펜스 없는 순수 JSON 하나가 나온다 — 정규식으로 마크다운을 긁을 이유가 사라진다. 같은 내용이 `/tmp/compound-engineering/ce-code-review/<run-id>/review.json`에도 쓰이므로, 대화 출력이 잘렸으면 이 파일을 읽는다.

**PR 모드는 PR 번호를 그대로 넘기고 `base:`를 쓰지 않는다.** `base:`는 PR 메타데이터 조회를 건너뛰는 빠른 경로여서, PR 제목·본문으로 변경 의도를 파악하는 단계와 기존 리뷰 코멘트를 참고하는 관점이 함께 죽는다. 워크트리에 들어가 있으면 PR 번호만으로도 ce가 스스로 로컬 정렬을 판정한다.

**로컬 모드는 반대로 `base:`가 유일한 선택지다** — PR 자체가 없으니 넘길 PR 번호가 없다. `base:`는 ce의 "명시적 base, 자동 탐지 건너뛰기" 경로이므로 review-ensemble Phase 1이 이미 구한 `$MERGE_BASE`를 그대로 넘기면, ce가 같은 값을 또 계산하다 다른 결과에 도달하는 일이 없다.

**로컬 모드에서 ce는 untracked 신규 파일을 스스로 스코프에서 뺀다.** ce 자신의 문서 원문: "Untracked file handling: Always inspect UNTRACKED:. Untracked paths are out of scope unless staged. When non-empty, list excluded files in Coverage and continue on tracked changes only — never stop or prompt." 즉 조용히 빠지는 게 아니라 ce가 스스로 커버리지에 "이 파일들은 제외했다"고 밝힌다 — 그 값을 review-ensemble의 Phase 7 커버리지에도 그대로 옮긴다. 정말 untracked 파일까지 ce가 보게 하려면 사용자에게 먼저 `git add`를 권하는 수밖에 없다(이 스킬이 대신 스테이징하지 않는다 — 사용자 워킹트리 상태를 임의로 바꾸는 일이라 스킬의 "수정 금지" 원칙과 어긋난다).

받는 JSON의 최상위 필드 중 쓰는 것:

| 필드 | 용도 |
|------|------|
| `status` | `complete`/`degraded`/`failed`/`skipped`. `complete`가 아니면 커버리지에 사유 기록 |
| `findings` | 발견사항 전체. 각 항목에 `severity`·`file`·`line`·`confidence`·`evidence`·`suggested_fix`·`why_it_matters`·`pre_existing` |
| `reviewers` | 실제로 돌아간 관점 목록. 커버리지에 씀 |
| `coverage` | 건너뛴 항목·사유. Codex 교차 리뷰 실행 여부가 여기 들어온다 |
| `verdict` | 머지 판정 |

`triage_groups`는 쓰지 않는다 — 우리 병합이 여러 엔진을 가로질러 다시 묶으므로 ce 내부 묶음은 의미가 없다.

이 엔진은 등급도 확신도도 이미 우리 통합 스키마와 같은 체계라 정규화가 필요 없다.

---

## E2. 내장 code-review — 2차 의견

```
PR 모드:   Skill(skill: "code-review", args: "high {PR번호}")
로컬 모드: Skill(skill: "code-review", args: "high")
```

`quick` 프로파일에서는 `high` 대신 `medium`.

**로컬 모드는 PR 번호를 아예 넘기지 않는다.** 실측 확인(바이너리 내장 프롬프트): 인자가 없으면 이 엔진 스스로 `git diff @{upstream}...HEAD; git diff HEAD`로 현재 브랜치의 커밋된 변경과 미커밋 변경을 함께 진단해 diff로 잡는다 — 이게 바로 ce가 쓰는 것과 같은 "standalone(현재 브랜치)" 경로다.

**이 자체 감지 스코프가 Phase 1의 `$MERGE_BASE`와 갈릴 수 있다 — 실측 지적, 사전 감지로 대응한다.** `@{upstream}`은 "이 브랜치가 추적하는 원격 브랜치"이지 "이 브랜치가 갈라져 나온 base 브랜치"가 아니다. `main` 위에서 로컬 전용 변경을 리뷰할 때처럼 `@{upstream}`이 우연히 base 역할까지 겸하면 문제없지만, **`git push -u`로 이미 푸시해둔 일반적인 기능 브랜치**에서는 `@{upstream}`이 로컬 HEAD와 거의 같아져 E2가 사실상 빈 diff를 본다 — 정작 `$MERGE_BASE`(기본 브랜치) 기준으로는 diff가 큰데도.

E2를 부르기 전에 값싸게 미리 감지한다. **`@{upstream}...HEAD`만 보면 오탐이 난다** — 실측 확인: E2는 커밋 diff(`@{upstream}...HEAD`)뿐 아니라 `git diff HEAD`로 미커밋 변경도 따로 잡으므로, 커밋·푸시를 전부 마치지 않은 일반적인 "구현 중 자체 점검" 상황에서는 upstream 쪽이 비어 있어도 미커밋 변경이 그 자리를 메운다. **진짜 위험은 커밋도 푸시도 전부 끝난 경우뿐**이다 — 그때만 두 경로 모두 빈다:

```bash
MERGE_BASE="{Phase 1의 MERGE_BASE}"   # 이 스니펫 자체에는 할당문이 없다 — Phase 1 값을 그대로 대입해서 쓴다
UPSTREAM=$(git rev-parse --abbrev-ref @{upstream} 2>/dev/null)
if [ -z "$UPSTREAM" ]; then
  echo "E2 스코프 경고: upstream 미설정 — @{upstream}...HEAD 자체가 에러난다. git diff HEAD(미커밋)만 남는데, 그마저 비어 있으면(전부 커밋됨) E2는 아무것도 못 본다"
else
  UPSTREAM_EMPTY=$([ -z "$(git diff "$UPSTREAM"...HEAD --stat)" ] && echo 1 || echo 0)
  WORKTREE_EMPTY=$([ -z "$(git diff HEAD --stat)" ] && echo 1 || echo 0)
  MERGE_BASE_HAS_DIFF=$([ -n "$(git diff "$MERGE_BASE"...HEAD --stat)" ] && echo 1 || echo 0)
  if [ "$UPSTREAM_EMPTY" = "1" ] && [ "$WORKTREE_EMPTY" = "1" ] && [ "$MERGE_BASE_HAS_DIFF" = "1" ]; then
    echo "E2 스코프 경고: 커밋·푸시가 전부 끝나 upstream=HEAD이고 미커밋 변경도 없음. E2가 거의 빈 diff를 볼 수 있음"
  fi
fi
```

경고가 뜨면 Phase 7 커버리지에 "E2는 이 실행에서 스코프가 제한됐을 수 있음 — E1이 `$MERGE_BASE` 기준으로 정확히 봤으므로 그쪽을 우선한다"를 명시한다. E2에게 임의 base ref를 강제로 넘길 확인된 방법은 없다 — 인자가 PR 번호·브랜치명·파일경로만 받는다(바이너리 확인). 완전히 우회하기보다 **한계를 정직하게 드러내는 쪽**을 택한다.

**untracked 신규 파일은 위 사전 감지에 아예 안 잡힌다 — 별도로 확인한다.** 위 블록은 `git diff`류만 보는데, 추적되지 않는 새 파일(Phase 1의 `UNTRACKED` 목록)은 커밋·미커밋 여부와 무관하게 애초에 diff 대상이 아니다. **로컬 모드 한정 문제다** — PR 모드는 `gh pr diff`가 PR의 커밋 히스토리 전체를 보므로 해당 없음. E2는 인자 없이 부르면(로컬 모드) 스스로 `git diff`로만 스코프를 정하므로 이런 파일을 구조적으로 못 본다 — E3(전문 렌즈)처럼 프롬프트에 `UNTRACKED` 목록을 실어 보낼 방법도 없다(Skill 호출은 문자열 인자 하나뿐이라 파일 목록을 따로 못 넘긴다).

```bash
if [ -n "$UNTRACKED" ]; then
  echo "E2 스코프 경고: untracked 신규 파일 $(echo "$UNTRACKED" | wc -l | tr -d ' ')개 — E2는 이들을 볼 방법이 없음: $UNTRACKED"
fi
```

경고가 뜨면 Phase 7 커버리지에 "E2는 신규 미추적 파일 {n}개({목록})를 보지 못했다"를 명시한다. `deep` 프로파일이면 E3(전문 렌즈)가 같은 `UNTRACKED` 목록을 받아 이 파일들을 커버하므로 실질적 공백이 메워지지만, `quick`·`standard`(E3 미실행)에서는 실제 사각지대로 남는다 — 새로 만든 파일은 `git add` 후 재실행하거나 `deep`으로 돌리라고 리포트에 안내한다.

> ⚠️ **이름이 겹친다.** 접두사 없는 `code-review`가 하니스 내장이고, `code-review:code-review`는 플러그인이다. 플러그인 쪽은 아래 "제외한 엔진"에 있으니 부르지 않는다. Skill 호출 시 접두사 없이 정확히 `code-review`를 쓴다.

**`--comment`와 `--fix`를 절대 붙이지 않는다.** `--comment`는 인라인 코멘트를 직접 달고, `--fix`는 워킹트리를 고친다. 둘 다 이 스킬의 역할 분리를 깬다.

이 엔진은 `ReportFindings`로 결과를 낸다. 등급 필드가 없고 `category`·`verdict`·`failure_scenario`만 있으므로 [merge.md](merge.md)의 정규화표를 거쳐야 한다.

ce와 관점이 일부 겹치는 것은 **의도된 것**이다. 겹치는 지점에서 두 엔진이 같은 지적을 하면 그게 교차확인 신호가 된다.

### 워크트리 경로를 넘길 수 없다 (PR 모드 한정)

**로컬 모드는 이 문단 전체가 해당 없다.** 세션이 이미 리뷰 대상 디렉터리에 있으므로 "경로를 넘길 수 없다"는 문제 자체가 생기지 않는다 — E2에게는 로컬 모드가 이 스킬이 지원하는 상황 중 가장 안전한 경우다.

Skill 호출은 인자 문자열 하나만 받는다 — Agent 호출처럼 프롬프트에 "이 디렉토리를 보라"를 실어 보낼 수단이 없다. 따라서 PR 모드에서 이 엔진이 워크트리를 보게 하는 방법은 **세션이 그 안에 들어가 있는 것**뿐이고, 그건 Phase 2의 세션 진입이 성공했을 때만 성립한다.

진입이 실패하면 이 엔진은 자기가 알아서 PR을 가져온다(레포를 새로 복제하기도 한다 — 실측 확인). 리뷰는 되지만 두 가지를 알고 있어야 한다:
- 디스크와 시간을 추가로 쓴다 (수백 MB 규모의 복제가 일어날 수 있다)
- 그 트리는 이 스킬이 관리하지 않으므로 Phase 10 정리 대상에 안 들어간다 — 커버리지에 남겨 사용자가 알게 한다

Agent로 부르는 전문 렌즈는 이 제약이 없다. 프롬프트에 절대경로를 직접 넣으므로 세션 위치와 무관하게 워크트리를 본다.

### 출력이 산문으로 올 수 있다

이 엔진의 구조화된 발견 목록 출력 경로는 세션 설정에 따라 없을 수 있고, 그러면 같은 내용이 마크다운 산문으로 온다. **실패가 아니다** — 결과를 버리지 말고 [merge.md](merge.md)의 산문 매핑표로 옮긴 뒤, 매핑을 거쳤다는 사실을 커버리지에 적는다.

### 체크아웃 필요 여부 (바이너리 내장 프롬프트로 확인, claude v2.1.235 기준)

- **diff 확보에는 체크아웃이 필요 없다.** 내장 프롬프트의 스코프 단계는 "If a PR number, branch name, or file path was passed as an argument, review that target instead" — 체크아웃 지시가 없고, PR 타깃이면 모델이 `gh pr diff`(읽기 전용)로 diff를 받아온다.
- **단, medium 이상 레벨은 주변 맥락을 로컬 트리에서 읽는다.** 프롬프트가 "Read the enclosing function for each hunk", "find its callers (Grep for the symbol)"를 지시하는데, 이 Read/Grep은 현재 워킹트리를 본다. ce의 `pr-remote` 같은 오래된-트리 가드가 **없다.** 따라서 로컬 HEAD가 PR head가 아니면 주변 맥락 근거가 낡은 코드일 수 있다.
- **결론**: standard·deep은 워크트리 안에서 돌므로 문제없다. `quick`(워크트리 없음)에서 로컬 HEAD ≠ PR head이면, 리포트 커버리지에 "주변 맥락은 로컬 트리 기준이라 낡았을 수 있음"을 명시한다. low 레벨 프롬프트는 hunk만 보고 파일을 읽지 않으므로("No subagents, no full-file reads") 이 위험이 없다 — quick의 근거 신선도가 중요하면 레벨을 `low`로 낮추는 선택지도 있다.
- **로컬 모드는 이 문제가 구조적으로 없다.** 로컬 HEAD가 곧 리뷰 대상 그 자체이므로 "낡은 근거"라는 개념이 성립하지 않는다.

---

## E3. 전문 렌즈 에이전트 — deep 프로파일 전용

`pr-review-toolkit` 플러그인의 에이전트를 **커맨드가 아니라 에이전트로 직접** 부른다. 커맨드(`/pr-review-toolkit:review-pr`)를 부르면 그쪽 자체 오케스트레이션이 우리 것과 겹치고, 우리가 원하는 것은 ce에 없는 렌즈뿐이다.

| 렌즈 | subagent_type | 선택 조건 | ce에 없는 이유 |
|------|---------------|-----------|----------------|
| 조용한 실패 | `pr-review-toolkit:silent-failure-hunter` | `error-handling` 신호 | ce의 reliability 관점은 재시도·타임아웃 중심이고, 삼켜진 예외·무의미한 폴백을 전담하지 않음 |
| 테스트 커버리지 | `pr-review-toolkit:pr-test-analyzer` | `tests` 신호 또는 신규 로직 | ce의 testing 관점은 약한 지적을 `testing_gaps`로 강등해 인라인 코멘트에서 사라짐 |
| 타입 설계 | `pr-review-toolkit:type-design-analyzer` | `new-types` 신호 | ce에 캡슐화·불변식 전담 관점이 없음 |
| 주석 정확성 | `pr-review-toolkit:comment-analyzer` | 주석·독스트링 대량 추가 | ce에 주석 부패 전담 관점이 없음 |

**부르지 않는 것**: `pr-review-toolkit:code-reviewer`(ce의 correctness·project-standards와 정면 중복), `pr-review-toolkit:code-simplifier`(리뷰 도구가 아니라 코드를 고치는 도구).

### 디스패치 프롬프트 틀

**PR 모드**:
```
{PR번호}번 PR을 {렌즈 이름} 관점으로만 리뷰하세요.

작업 디렉토리: {워크트리 절대경로}
이 디렉토리의 워킹트리가 PR head입니다. 여기의 파일을 그대로 읽으면 됩니다.

리뷰 범위: git diff {merge-base SHA} 의 결과에 포함된 변경분.
범위 밖 기존 코드의 문제는 pre_existing: true 로 표시하고 별도로 분리하세요.

변경 의도: {Phase 1에서 얻은 PR 제목·본문 요약}
```

**로컬 모드**:
```
현재 브랜치({Phase 1의 CURRENT_BRANCH})의 미병합·미커밋 변경사항을 {렌즈 이름} 관점으로만 리뷰하세요.
이것은 PR을 열기 전 자체 점검입니다.

작업 디렉토리: {현재 워킹트리 절대경로 — 세션이 이미 여기 있음}
여기의 파일을 그대로 읽으면 됩니다. 별도 워크트리는 없습니다.

리뷰 범위: git diff {Phase 1의 MERGE_BASE} 의 결과에 포함된 변경분(커밋된 것 + 미커밋 변경 전부).
{Phase 1의 UNTRACKED 목록이 비어있지 않으면 추가: 다음 신규 파일도 반드시 포함해서 읽으세요 — git diff에는 안 잡히는 untracked 파일입니다: {UNTRACKED 목록}}
범위 밖 기존 코드의 문제는 pre_existing: true 로 표시하고 별도로 분리하세요.

변경 의도: {Phase 1의 커밋 로그 요약}
```

이어서 두 모드 공통:
```

- GitHub에 아무것도 게시하지 마세요. gh pr comment, gh api .../reviews, --comment 플래그 모두 금지입니다.
- 파일을 수정하지 마세요. 이 작업은 리뷰만 합니다.
- 결과를 다음 모양의 JSON 객체 하나만 반환하세요 — 그 앞뒤에 어떤 텍스트도 붙이지 마세요:
  {"findings": [{ ...아래 통합 발견 스키마... }], "coverage": ["실제로 읽은 파일 경로", "..."]}

{merge.md의 통합 발견 스키마}

engine 값은 "{디스패치하는 렌즈의 값 하나만: lens:silent-failure / lens:tests / lens:types / lens:comments}"로 고정하세요. 스키마 예시에 보이는 다른 값들은 당신 것이 아닙니다.

등급 기준:
- P0 크리티컬 파손, 악용 가능한 취약점, 데이터 손실·손상
- P1 정상 사용 경로에서 부딪히는 고영향 결함, 계약 위반
- P2 의미 있는 손해가 있는 중간 이슈 (엣지 케이스, 성능 퇴행, 유지보수 함정)
- P3 영향이 작고 범위가 좁은 개선 제안

확신도는 0·25·50·75·100 중 하나만 쓰세요.
75 이상으로 매기려면 근거 배열의 첫 항목이 그 지적을 성립시키는 **원문 그대로의 코드 줄**이어야 합니다.
인용할 수 없으면 50으로 낮추세요.
```

마지막 두 줄은 ce의 확신도 앵커 규약을 그대로 가져온 것이다. 이게 있어야 여러 엔진의 확신도가 같은 자를 쓰게 되고, 병합할 때 비교가 성립한다.

**수거 후 `engine` 필드는 review-ensemble이 직접 덮어쓴다.** E1·E2는 review-ensemble이 스스로 태깅하는데 E3만 에이전트의 자기 신고를 믿으면, 렌즈 하나가 엉뚱한 값(스키마 예시의 7값 enum 중 다른 것)을 돌려줬을 때 Phase 5의 `engine_count`·`covering_engines` 계수가 검증 단계 없이 조용히 틀어진다(실측 지적). 어느 렌즈를 디스패치했는지는 호출자가 이미 아는 사실이므로, 반환값과 무관하게 그 값으로 통일한다.

---

## E4. 레포 로컬 워크플로 렌즈 — 조건부

대상 레포에 `.claude/skills/github-actions-review/`가 있고 `workflows` 신호가 켜졌을 때만 부른다.

```bash
ls -d .claude/skills/github-actions-review 2>/dev/null
```

있으면 먼저 **그 스킬 본문을 열어 게시 동작이 박혀 있는지 확인한다.** 대상 레포가 제공하는, 이 스킬이 감사한 적 없는 코드다 — 아래 제외 표에서 플러그인(`code-review:code-review`)을 "항상 자기 결과를 게시해서" 뺀 것과 같은 기준을 여기에도 적용한다(실측 지적: 이전 버전은 게시 금지 지시도 사전 확인도 없이 그대로 실행해, 그 스킬이 마지막에 `gh pr comment`를 하도록 짜여 있으면 병합 전 원본이 중복으로 달렸다).

```bash
grep -nE 'gh pr comment|gh api .*(reviews|comments)|--comment' .claude/skills/github-actions-review/SKILL.md
```

- 걸린 줄이 게시를 **무조건 실행**하는 구조면 → 이 렌즈를 건너뛰고 커버리지에 "레포 로컬 워크플로 렌즈: 자체 게시가 내장돼 있어 제외"를 적는다
- 안 걸리거나 조건부(사용자 확인 뒤에만)면 → 실행하되, 호출 인자에 이 문서 서두의 공통 3줄(게시 금지·수정 금지·JSON 계약)을 그대로 붙인다

실행은 PR 모드는 워크트리 안에서, 로컬 모드는 현재 디렉터리에서 하고, 결과를 통합 스키마로 변환해 달라고 요청한다. 스킬이 아예 없으면 조용히 건너뛴다 — 이 렌즈는 특정 레포에만 있는 것이라 부재가 정상이다.

이 렌즈가 잡는 것은 다른 엔진이 구조적으로 못 잡는 종류다. 워크플로 YAML 자체는 흠이 없는데 그 안의 환경변수 이름이 앱 테스트가 읽는 이름과 달라, 테스트 여럿이 조용히 건너뛰어지면서 CI는 초록불이었던 사례가 근거다. 문법 린터도 보안 린터도 아무 말을 하지 않았다.

---

## 제외한 엔진과 그 이유

| 엔진 | 제외 이유 |
|------|-----------|
| `code-review:code-review` (플러그인) | 워크플로 마지막 단계가 **항상** `gh pr comment`로 자기 결과를 게시한다. report-only로 돌릴 방법이 없어 중복 코멘트가 확정된다. 내용도 내장 code-review와 거의 같다 |
| `codex:rescue` / adversarial-review | ce가 워크트리 정렬 시 Codex 교차 리뷰를 이미 내부에서 돌린다. 따로 부르면 같은 모델에 같은 브리핑을 두 번 보내는 셈 |
| `superpowers:requesting-code-review` | 범용 리뷰라 ce와 관점이 거의 완전히 겹친다. 추가 신호가 없다 |
| `security-review` (내장) | ce에 보안 관점이 이미 있다. 인증·결제·비밀값을 크게 건드리는 PR에서 수동으로 추가할 수는 있으나 기본 구성에는 넣지 않는다 |

---

## 실패 처리

엔진 하나가 실패해도 나머지로 계속한다. 다만 **실패를 조용히 넘기지 않는다** — 실패한 엔진이 봤어야 할 관점이 통째로 비었는데 리포트가 정상으로 보이면, 읽는 사람이 커버리지를 실제보다 넓게 믿는다.

| 상황 | 처리 |
|------|------|
| 엔진 1개 실패 | 계속 진행. 커버리지에 "실패: {엔진}, 사유 한 줄" 기록 |
| 엔진 전부 실패 | 중단. 게시하지 않고 사유를 알린다 |
| ce가 `status: skipped` 반환 | ce의 자체 판단(사소한 자동 PR 등). 사유를 그대로 커버리지에 옮기고 나머지 엔진으로 계속 |
| ce가 `status: degraded` 반환 | 발견사항은 쓰되 커버리지에 부분 실패임을 명시 |

교차확인 계수를 계산할 때 **실패한 엔진은 `covering_engines`에서 뺀다.** 빼지 않으면 "그 파일을 둘이 봤는데 하나만 지적했다"는 판정이 거짓이 되어, 멀쩡한 발견이 논쟁으로 분류된다.
