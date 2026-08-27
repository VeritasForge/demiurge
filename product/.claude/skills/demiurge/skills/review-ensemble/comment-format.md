# PR 코멘트 게시 형식

SKILL.md의 Phase 9에서 읽는다. 발견사항이 이미 병합되어 있다는 전제이며, 병합 자체는 [merge.md](merge.md)가 담당한다.

---

## 1. GitHub PR Review API

### 엔드포인트

```
POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews
```

### 호출

```bash
gh api repos/{owner}/{repo}/pulls/{PR}/reviews --input /tmp/pr-review-{PR}.json
```

> **주의**: `gh api`에 인라인 JSON을 넘기면 셸 glob 확장 문제(`no matches found`)가 난다. 반드시 `--input` 파일을 쓴다.

### 페이로드

```json
{
  "commit_id": "<PR의 head commit SHA (headRefOid)>",
  "event": "COMMENT",
  "body": "<종합 요약 — 아래 2절>",
  "comments": [
    {
      "path": "src/auth/handler.ts",
      "line": 45,
      "side": "RIGHT",
      "body": "<인라인 코멘트 — 아래 3절>"
    }
  ]
}
```

| 필드 | 설명 |
|------|------|
| `commit_id` | `gh pr view --json headRefOid`로 얻은 PR head SHA |
| `event` | 항상 `"COMMENT"`. `"REQUEST_CHANGES"`는 쓰지 않는다 |
| `comments[].path` | 레포 루트 기준 경로. **워크트리 절대경로 접두사를 반드시 뗀다** |
| `comments[].line` | 신규 파일 기준 라인 번호 |
| `comments[].side` | **반드시 `"RIGHT"`를 넣는다.** 이 스킬은 신규 파일 기준 라인에만 코멘트를 다므로 항상 RIGHT다(삭제된 줄에 다는 경우는 Phase 9가 인라인에서 빼고 본문으로 돌리므로 여기 안 옴) |

**`side`를 빼면 게시가 "성공"한 것처럼 보이지만 실제로는 다르게 저장된다.** 실측 확인: `side` 없이 게시하면 GitHub API가 에러 없이 받아들이지만, 응답의 `line`이 `null`로 돌아오고 레거시 `position`(diff 안의 절대 줄 카운트) 방식으로 저장된다. `line`을 읽는 프로그램(다른 리뷰 도구·자동화)에는 이 코멘트가 위치 없는 것으로 보인다. 게시 직후 `line`이 채워졌는지 확인하는 것이 안전하다:

```bash
gh api "repos/{owner}/{repo}/pulls/{PR}/comments" --paginate \
  --jq '[.[] | select(.pull_request_review_id == {review_id} and .line == null)] | length'
```

`{review_id}`는 게시 응답의 `id`다. **이번 리뷰로 좁히고 `--paginate`를 붙인다** — 안 그러면 이전 라운드의 낡은 코멘트가 오탐을 내거나, 첫 페이지(30건, 오래된 순)에 방금 게시분이 아예 안 들어와 진짜 누락이 통과해버린다. 0이 아니면 `side` 누락 코멘트가 섞인 것이다.

인라인 코멘트는 한 리뷰당 50개 안팎이 실용 한계다. 넘으면 등급이 낮은 것부터 본문의 "추가 발견사항"으로 옮긴다.

---

## 2. 리뷰 본문

```markdown
## PR 리뷰

🔴 P0 {n} · 🟠 P1 {n} · 🟡 P2 {n} · 🔵 P3 {n}

독립적으로 실행한 리뷰 {N}건의 결과를 합쳤습니다. 그중 {m}건의 발견은 둘 이상의 리뷰가 같은 지적을 했습니다.

{워크플로 신호가 있었으면: CI 워크플로 변경이 포함되어 워크플로 전용 점검을 함께 돌렸습니다.}
{실패한 엔진이 있었으면: {관점 이름} 점검은 이번 실행에서 완료되지 못했습니다.}

### 추가 발견사항 (인라인 코멘트를 달 수 없는 위치)
- **{제목}** (`{file}:{line}`) — {why_it_matters}

### 기존 코드의 문제 (이번 변경과 무관)
- **{제목}** (`{file}:{line}`) — {why_it_matters}
```

**엔진 이름·프로파일 이름·내부 워크플로 용어를 쓰지 않는다.** 이 본문은 팀원이 읽는다. "독립적으로 실행한 리뷰 3건" 은 되고, "ce-code-review + 내장 code-review + 조용한 실패 렌즈" 는 안 된다.

마지막 줄에 붙인다:

```
Co-Reviewed-By: Claude Code <noreply@anthropic.com>
```

---

## 3. 인라인 코멘트

```markdown
{등급 접두사} {배지}

{why_it_matters}

{also_at이 있으면: "같은 결함이 여기서도 발현됩니다: `{file}:{line}`" 줄 추가 — 병합이 대표 위치 하나로 합친 발견의 나머지 발현 위치를 코멘트에서 버리지 않는다}

{suggested_fix가 있으면 코드 블록으로}
```

### 등급 접두사

| 등급 | 접두사 | 의미 |
|------|--------|------|
| P0 | `🔴 **P0 CRITICAL**` | 머지 차단 — 크리티컬 파손, 악용 가능한 취약점, 데이터 손실 |
| P1 | `🟠 **P1 HIGH**` | 수정 필요 — 정상 경로에서 부딪히는 고영향 결함, 계약 위반 |
| P2 | `🟡 **P2 MEDIUM**` | 수정 권장 — 엣지 케이스, 성능 퇴행, 유지보수 함정 |
| P3 | `🔵 **P3 LOW**` | 개선 제안 — 영향이 작고 범위가 좁음 |

기존 3단계(P1/P2/P3)에서 **P0가 추가되었다.** ce-code-review가 P0~P3 4단계를 쓰므로 이전 3단계 체계에는 취약점·데이터 손상 발견을 담을 칸이 없었다.

### 배지

[merge.md](merge.md)의 배지표 중 "PR 코멘트" 열을 쓴다. 개수만 쓰고 엔진 이름은 쓰지 않는다.

### 결정 필요 항목

처방이 갈린 항목은 수정 지시가 아니라 **질문**으로 단다. 한쪽 처방만 적으면 저자가 그것을 결론으로 읽는다.

```markdown
⚔️ **결정 필요** ({등급 접두사에 해당하는 등급})

{무엇을 정해야 하는지 한 문장}

- **{선택지 A}** — {그렇게 하면 무엇이 좋아지고 무엇을 잃는지}
- **{선택지 B}** — {같은 형식}

두 리뷰가 이 자리를 각각 다르게 봤고, 어느 쪽이 맞는지는 {갈리는 기준}에 달려 있어 저자 판단이 필요합니다.
```

수정 제안 코드 블록을 넣지 않는다 — 제안이 붙으면 한쪽이 정답처럼 보인다.

### 예시

```markdown
🔴 **P0 CRITICAL** ✅ 독립 리뷰 2건이 같은 지적

사용자가 보낸 `redirect_uri` 를 검증 없이 그대로 리다이렉트에 사용합니다.
공격자가 자기 도메인을 넣으면 인증 코드가 그쪽으로 전달됩니다.

```diff
- return redirect(req.query.redirect_uri)
+ if (!ALLOWED_REDIRECTS.has(req.query.redirect_uri)) throw new BadRequest()
+ return redirect(req.query.redirect_uri)
```
```

---

## 4. 라인 매핑

`line`은 **신규 파일(new version) 기준** 라인 번호다.

- diff의 `@@ -old_start,old_count +new_start,new_count @@` 헤더에서 `new_start`부터 세는 번호
- `+` 줄과 컨텍스트 줄에만 코멘트를 달 수 있다
- `-` 줄(삭제된 줄)에는 달 수 없다

### 유효하지 않은 위치일 때

1. 해당 코멘트를 `comments[]`에서 뺀다
2. 리뷰 본문의 "추가 발견사항" 섹션으로 옮긴다

**절대 라인 번호를 추측해서 맞추지 않는다.** 엉뚱한 줄에 달린 코멘트는 코멘트가 없는 것보다 나쁘다 — 읽는 사람이 그 줄에서 있지도 않은 문제를 찾느라 시간을 쓴다.

---

## 5. 게시 후

```
✅ PR #{PR}에 인라인 코멘트 {n}건을 게시했습니다. (본문으로 옮긴 {m}건 포함, 총 {n+m}건)
🔗 {review_html_url}
```
