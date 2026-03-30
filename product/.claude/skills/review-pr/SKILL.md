---
name: review-pr
description: Use when reviewing a GitHub PR and posting inline comments. Triggers on PR numbers, GitHub PR URLs, or requests to review pull requests with multi-agent analysis. /review-pr 으로 실행.
disable-model-invocation: true
argument-hint: <PR번호 또는 URL> [-f]
---

# Review PR

PR에 대해 CE(compound-engineering) 다중 에이전트 리뷰를 실행하고, 발견사항을 GitHub PR 인라인 코멘트로 게시한다.

**핵심 원리**: CE `workflows:review`가 리뷰 엔진(에이전트 선택/실행/종합)을 담당하고, 이 스킬은 **PR diff 수집 + CE 호출 + 코멘트 변환/게시**하는 얇은 오케스트레이션 레이어.

---

## Phase 0: 인자 파싱

`$ARGUMENTS`에서 옵션과 PR 식별자를 분리한다.

1. `-f` 또는 `--force` 플래그 존재 여부 확인 → `FORCE_MODE` 설정 후 인자에서 제거
2. 나머지 인자에서 PR 번호 추출:
   - 순수 숫자 (예: `6286`) → PR 번호
   - GitHub URL (예: `https://github.com/.../pull/6286`) → 정규식으로 PR 번호 추출
   - 빈 인자 → 에러: "PR 번호 또는 URL을 입력해주세요"
3. `owner/repo` 추출:
   ```bash
   gh repo view --json nameWithOwner -q .nameWithOwner
   ```

---

## Phase 1: PR 데이터 수집

두 명령을 병렬 실행하여 PR 메타데이터와 diff를 수집한다.

**메타데이터**:
```bash
gh pr view {PR_NUMBER} --json number,title,body,baseRefName,headRefName,headRefOid,files,additions,deletions
```

**Diff** (auto-generated 파일 필터링):
```bash
gh pr diff {PR_NUMBER}
```

필터링 대상: `uv.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Gemfile.lock`, `go.sum`, `poetry.lock`, `Pipfile.lock`, `*.min.js`, `*.min.css`

diff가 매우 큰 경우 (8000줄 초과), auto-generated 파일을 필터링한 결과를 `/tmp/pr-{PR_NUMBER}-diff.txt`에 저장한다.

---

## Phase 2: CE review 실행

`compound-engineering:workflows:review` 스킬을 호출하여 리뷰를 위임한다.

**호출 방법**: Skill 도구로 `compound-engineering:workflows:review`를 호출하되, 다음을 프롬프트에 포함:

```
PR #{PR_NUMBER} - {title} 리뷰.

다음 지시를 반드시 따르세요:
1. PR diff를 분석하여 적절한 리뷰 에이전트를 선택/실행하세요.
2. 종합 리포트를 작성할 때, 각 발견사항을 반드시 다음 형식으로 정리하세요:

### Finding: {제목}
- **Severity**: P1 | P2 | P3
- **File**: {파일 경로}
- **Line**: {신규 파일 기준 라인 번호}
- **Agent**: {에이전트 이름}
- **Body**: {상세 설명}

3. todo 파일 생성은 건너뛰세요. 발견사항만 위 형식으로 정리하면 됩니다.

PR diff는 다음과 같습니다:
{diff 내용 또는 diff 파일 경로}
```

> CE review는 내부적으로 `compound-engineering.local.md` 설정 또는 PR 파일 패턴에 따라 security-sentinel, architecture-strategist, performance-oracle, kieran-*-reviewer 등을 자동 선택한다.

---

## Phase 3: 결과 수집 + 종합 리포트

CE review 결과에서 발견사항을 추출하여 종합 리포트를 생성한다.

**추출 방법**: CE 출력에서 `### Finding:` 패턴을 파싱하여 각 발견사항의 severity, file, line, agent, body를 수집한다.

**종합 리포트 형식**:

```markdown
## PR Review Complete

**PR #{number}:** {title}
**Branch:** {headRefName} → {baseRefName}
**리뷰 에이전트:** {사용된 에이전트 목록}

### Findings Summary
- 🔴 P1 CRITICAL: {count} — 머지 차단
- 🟡 P2 IMPORTANT: {count} — 수정 권장
- 🔵 P3 NICE-TO-HAVE: {count} — 개선 제안

### 🔴 P1 CRITICAL
1. **{title}** ({agent}) — `{file}:{line}`
   {body 요약}

### 🟡 P2 IMPORTANT
...

### 🔵 P3 NICE-TO-HAVE
...
```

종합 리포트를 대화에 출력한다.

---

## Phase 4: 리뷰 품질 검증 (조건부 /rl-verify)

P1 발견사항의 정당성을 교차 검증한다. 조건에 따라 자동 호출 또는 스킵.

**자동 호출 조건**:
- P1 발견사항 ≥ 1건 **AND**
- 해당 P1의 파일을 분석한 다른 에이전트가 해당 이슈를 언급하지 않은 경우 (에이전트 간 불일치)

**호출 시**:
```
/rl-verify PR #{PR_NUMBER}의 P1 발견사항 정당성 검증.

검증 대상:
{P1 발견사항 목록 + 각 에이전트의 분석 범위}

검증 질문: 각 P1 지적이 실제 위험인가, 과잉 지적인가?
```

- rl-verify가 `CONFIRMED` 판정 → P1 유지
- rl-verify가 `CONTESTED` 판정 → P2로 다운그레이드 또는 제거
- 결과를 종합 리포트에 반영

**스킵 조건**:
- P1 = 0건
- 모든 P1이 여러 에이전트에서 일관되게 지적됨

---

## Phase 5: 사용자 확인 (조건부)

`FORCE_MODE`가 설정된 경우 (-f 플래그) → Phase 6로 바로 진행.

그 외: AskUserQuestion 도구로 게시 범위를 확인한다.

```
위 리뷰 결과를 PR #{PR_NUMBER}에 인라인 코멘트로 게시할까요?
1) 전체 게시 (P1 + P2 + P3)
2) P1 + P2만 게시
3) P1만 게시
4) 게시하지 않음
```

사용자가 4)를 선택하면 종료.

---

## Phase 6: PR 코멘트 게시

[comment-format.md](comment-format.md) 참조하여 GitHub PR Review API 페이로드를 생성하고 게시한다.

### 6-1. JSON 페이로드 생성

Phase 5에서 선택된 게시 범위에 해당하는 발견사항만 포함.

```json
{
  "commit_id": "{headRefOid}",
  "event": "COMMENT",
  "body": "## Multi-Agent PR Review\n\n🔴 P1: {count} | 🟡 P2: {count} | 🔵 P3: {count}\n\n_Reviewed by: {agent_list}_\n\nCo-Reviewed-By: Claude Code <noreply@anthropic.com>",
  "comments": [
    {
      "path": "{file}",
      "line": {line},
      "body": "{severity_prefix} | `{agent}`\n\n{body}"
    }
  ]
}
```

심각도 접두사:
- P1 → `🔴 **P1 CRITICAL**`
- P2 → `🟡 **P2 IMPORTANT**`
- P3 → `🔵 **P3 NICE-TO-HAVE**`

### 6-2. 라인 유효성 검증

각 코멘트의 `line`이 diff 범위 내에 있는지 확인:
- 유효 → `comments[]`에 포함
- 유효하지 않음 → `comments[]`에서 제외, 리뷰 `body`의 "추가 발견사항" 섹션에 추가

### 6-3. 게시

```bash
# JSON 파일로 저장
# /tmp/pr-review-{PR_NUMBER}.json

# gh api로 게시
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/reviews --input /tmp/pr-review-{PR_NUMBER}.json
```

> `gh api`에 인라인 JSON을 전달하면 shell glob 문제(`no matches found`)가 발생한다. 반드시 `--input` 파일을 사용할 것.

### 6-4. 결과 출력

게시 성공 시 리뷰 URL을 출력:
```
✅ PR #{PR_NUMBER}에 {count}개의 인라인 코멘트를 게시했습니다.
🔗 {review_html_url}
```
