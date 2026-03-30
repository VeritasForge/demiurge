# PR Comment Format Reference

SKILL.md의 Phase 6(PR 코멘트 게시)에서 참조하는 API 스펙 및 포맷 가이드.

---

## 1. CE Review 결과에서 추출할 데이터

CE review 종합 리포트에서 각 발견사항을 다음 필드로 구조화:

| 필드 | 타입 | 설명 |
|------|------|------|
| `severity` | `"P1"` \| `"P2"` \| `"P3"` | 심각도 |
| `title` | string | 발견사항 제목 (한 줄) |
| `file` | string | 파일 경로 (PR diff 기준, 예: `src/auth/handler.ts`) |
| `line` | number | 신규 파일 기준 라인 번호 (diff의 `+` 쪽) |
| `body` | string | 마크다운 형식의 상세 설명 |
| `agent` | string | 발견한 에이전트 이름 |

---

## 2. GitHub PR Review API 페이로드

### 엔드포인트

```
POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews
```

### 호출 방법

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/reviews --input /tmp/pr-review-{pr}.json
```

> **주의**: `gh api`에 인라인 JSON을 전달하면 shell glob 확장 문제(`no matches found`)가 발생한다. 반드시 `--input` 파일을 사용할 것.

### JSON 페이로드 구조

```json
{
  "commit_id": "<PR의 head commit SHA (headRefOid)>",
  "event": "COMMENT",
  "body": "## Multi-Agent PR Review\n\n🔴 P1: {count} | 🟡 P2: {count} | 🔵 P3: {count}\n\n_Reviewed by: {agent_list}_\n\nCo-Reviewed-By: Claude Code <noreply@anthropic.com>",
  "comments": [
    {
      "path": "src/auth/handler.ts",
      "line": 45,
      "body": "🔴 **P1 CRITICAL** | `security-sentinel`\n\n{finding body}"
    }
  ]
}
```

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `commit_id` | Yes | PR의 HEAD commit SHA. `gh pr view --json headRefOid`로 획득 |
| `event` | Yes | 항상 `"COMMENT"` 사용. `"REQUEST_CHANGES"` 사용 금지 |
| `body` | Yes | 리뷰 본문 (종합 요약) |
| `comments` | Yes | 인라인 코멘트 배열 (최대 ~50개) |
| `comments[].path` | Yes | 파일 경로 (repo root 기준) |
| `comments[].line` | Yes | 신규 파일 기준 라인 번호 |
| `comments[].body` | Yes | 코멘트 본문 (마크다운) |

---

## 3. 라인 매핑 규칙

### 기본 규칙

GitHub PR Review API의 `line`은 **신규 파일(new version) 기준 라인 번호**를 사용한다.

- diff의 `@@ -old_start,old_count +new_start,new_count @@` 헤더에서 `new_start`부터 시작하는 번호
- `+` 줄과 컨텍스트 줄(변경 없는 줄)에만 코멘트 가능
- `-` 줄(삭제된 줄)에는 코멘트 불가

### Fallback 규칙

**유효하지 않은 라인**(diff 범위 밖, 삭제된 줄 등)에 코멘트를 달아야 하는 경우:

1. 해당 코멘트를 `comments[]`에서 제외
2. 대신 리뷰 `body`에 추가:
   ```
   ### 추가 발견사항 (인라인 코멘트 불가)
   - **{title}** (`{file}:{line}`) — {body}
   ```

---

## 4. 심각도별 코멘트 접두사

| 심각도 | 접두사 | 의미 |
|--------|--------|------|
| P1 | `🔴 **P1 CRITICAL**` | 머지 차단 — 보안 취약점, 데이터 손상 위험 |
| P2 | `🟡 **P2 IMPORTANT**` | 수정 권장 — 성능, 아키텍처, 코드 품질 |
| P3 | `🔵 **P3 NICE-TO-HAVE**` | 개선 제안 — 문서화, 정리, 최적화 |

### 코멘트 본문 템플릿

```markdown
{심각도 접두사} | `{agent_name}`

{상세 설명}

{수정 제안이 있으면 코드 블록으로}
```

---

## 5. Auto-Generated 파일 필터링

diff에서 제외할 파일 패턴 (CE review에 전달하기 전 필터링):

- `uv.lock`, `poetry.lock`, `Pipfile.lock`
- `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- `Gemfile.lock`, `go.sum`
- `*.min.js`, `*.min.css`
- `*.generated.*`

### 필터링 방법

```bash
gh pr diff {PR} | awk '/^diff --git/{file=$0} /\.(lock|min\.(js|css))/{skip=1; next} /^diff --git/{skip=0} skip{next} {print}'
```

또는 diff가 너무 크면 파일별로 분리하여 제외 패턴에 해당하는 파일을 건너뜀.
