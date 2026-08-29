---
name: review-ensemble
description: Use when reviewing a GitHub PR (posts inline comments) or self-reviewing local/uncommitted work before opening one. Runs multiple review engines in parallel and merges results. /review-ensemble 으로 실행.
argument-hint: [PR번호 또는 URL — 생략하면 현재 브랜치를 로컬 검증] [quick|standard|deep] [-f] [--no-worktree]
---

# Review PR

여러 개의 독립된 리뷰 엔진을 같은 대상에 돌리고, 결과를 하나로 병합해 리포트한다. **두 모드**가 있다:

- **PR 모드** — PR 번호·URL을 주면, 병합 결과를 GitHub PR 인라인 코멘트로 게시한다
- **로컬 모드** — 아무것도 안 주면, 현재 브랜치·워킹트리의 변경사항을 대상으로 돌리고 터미널에 리포트만 낸다. 구현 중이거나 구현 직후 PR을 열기 전에 스스로 점검할 때 쓴다

**핵심 원리**: 엔진들은 발견사항만 만들고 아무것도 게시하지 않는다. GitHub에 쓰는 권한은 이 스킬 하나만 갖고, 그마저도 PR 모드에서만 쓴다.

```
PR 모드:
                    ┌─── (A) 준비 ───┐
  review-ensemble ──(1)fetch + worktree──> [워크트리: PR head]
      │
      ├──(2)호출──> ce-code-review ──읽기──> 워크트리 · gh pr diff
      │                  └──셸아웃──> Codex CLI  ※(1)이 있어야 켜짐
      ├──(3)호출──> 내장 code-review ──읽기──> 워크트리
      └──(4)호출──> 전문 렌즈 에이전트들 ──읽기──> 워크트리

                    ┌─── (B) 병합 ───┐
      발견사항 전부 ──정규화──> 하나의 스키마 ──중복제거──> 교차확인 계수

                    ┌─── (C) 게시 ───┐
  review-ensemble ──(5)게시──> GitHub PR 인라인 코멘트     ← 쓰기는 여기뿐

로컬 모드 — (A)가 사라진다. 이미 그 코드 위에 있으므로 fetch·워크트리가 불필요:
                    ┌─── (B) 병합 ───┐  (동일)
      ├──호출──> ce-code-review ──읽기──> 현재 워킹트리 (base:)
      ├──호출──> 내장 code-review ──읽기──> 현재 워킹트리 (인자 없음)
      └──호출──> 전문 렌즈 에이전트들 ──읽기──> 현재 워킹트리
                    │
                    ▼
             터미널에 리포트만 출력 — (C) 없음, 게시할 PR 자체가 없다
```

(2)(3)(4)는 **엔진을 부르는 구간**이고, (5)는 **GitHub에 쓰는 구간**이다. 엔진이 자기 결과를 따로 게시하면 병합 전 원본이 중복으로 달리므로, 모든 엔진은 report-only로 부른다. 로컬 모드는 (5) 자체가 없다.

참조 문서 두 개를 각 단계에서 읽는다:
- **[engines.md](engines.md)** — Phase 3·4에서. 엔진별 호출 방법과 금지사항
- **[merge.md](merge.md)** — Phase 5에서. 등급 정규화표·중복제거·교차확인 규칙
- **[comment-format.md](comment-format.md)** — Phase 9에서. GitHub API 페이로드

---

**필요 조건**: E1·E3·Phase 6 표2는 별도 설치가 필요한 플러그인/CLI에 의존한다. 지금 당장 읽을 필요는 없다 — Phase 4에서 엔진이 플러그인 부재로 실패하거나 사용자가 설치 여부를 물으면 그때 [references/prerequisites.md](references/prerequisites.md)를 읽어 안내한다.

---

## Phase 0: 인자 파싱

`$ARGUMENTS`에서 다음을 분리한다. 토큰은 인식 즉시 제거하고, 남은 것을 PR 식별자로 본다.

| 토큰 | 효과 |
|------|------|
| `quick` | 엔진 1개(내장 code-review medium). 워크트리 없음. 급할 때 |
| `standard` | **기본값.** 엔진 2개(ce + 내장). 워크트리 사용 |
| `deep` | standard + 전문 렌즈 에이전트 + 조건부 레포 로컬 렌즈 |
| `-f`, `--force` | Phase 8 사용자 확인을 건너뛰고 전체 게시. **로컬 모드에선 의미 없음** — Phase 8·9가 애초에 안 돎 |
| `--no-worktree` | 워크트리를 만들지 않음. 코드를 읽는 엔진은 자동 제외. **로컬 모드에선 의미 없음** — 로컬 모드는 원래 워크트리를 안 만듦 |

PR 식별자:
- 순수 숫자(`6286`) → PR 번호 → **PR 모드**
- GitHub URL → 정규식으로 번호 추출 → **PR 모드**
- 비어 있음 → **로컬 모드**(`LOCAL_MODE=true`). 현재 브랜치·워킹트리를 대상으로 한다

로컬 모드도 진짜로 리뷰할 게 있는지는 확인해야 한다 — Phase 1에서 확인하고, 없으면 거기서 중단한다.

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

---

## Phase 1: 메타데이터 + 중단 조건

### PR 모드

```bash
gh pr view {PR} --json number,title,body,state,isDraft,url,baseRefName,headRefName,headRefOid,isCrossRepository,files,additions,deletions
gh pr diff {PR} --color=never > /tmp/review-ensemble-{PR}.diff   # diff 본문 → 파일로. 아래 diff 신호 판정용 — 파일 경로만으론 본문 신호를 못 잡는다
```

**중단 조건** — 해당하면 엔진을 하나도 띄우지 않고 종료한다:
- `state`가 `CLOSED` 또는 `MERGED` → "PR이 닫혔거나 병합되었습니다. 리뷰하지 않습니다."
- 변경 파일이 자동생성 파일뿐 → "자동생성 파일만 변경되었습니다."

Draft PR은 정상적으로 리뷰한다.

### 로컬 모드

`gh pr view`가 없으므로 git으로 직접 구한다. ce-code-review 자신의 "인자 없음(standalone, 현재 브랜치)" 경로와 같은 로직이다.

```bash
BASE_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
if git fetch --no-tags origin "$BASE_BRANCH" >/dev/null 2>&1; then
  MERGE_BASE=$(git merge-base FETCH_HEAD HEAD)
else
  MERGE_BASE=""   # fetch 실패 — 아래 중단 조건("베이스 브랜치를 찾을 수 없습니다")으로 이어진다.
                   # FETCH_HEAD를 그대로 쓰면 이전 fetch(다른 실행의 잔여물)의 값을 잘못 재사용한다 — 실측 지적
fi
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git diff --name-only "$MERGE_BASE"          # 커밋된 변경 파일 목록
{ git diff "$MERGE_BASE"; git diff HEAD; } > /tmp/review-ensemble-local.diff   # diff 본문(커밋+미커밋) → 파일로. 아래 diff 신호 판정용
git log --oneline "$MERGE_BASE"..HEAD       # 커밋 메시지 — PR 제목·본문 대신 변경 의도의 근거
git status --porcelain                       # 미커밋 변경 파일 목록(추적 파일 기준)
git ls-files --others --exclude-standard     # untracked 신규 파일 — 아래 참고
```

**`git diff --name-only`는 untracked 신규 파일을 절대 안 보여준다** — git diff의 기본 동작이고, 실측 확인(방금 이 스킬 자신의 리뷰 대상인 `engines.md`·`merge.md`가 이 명령 출력에서 빠지는 것으로 재현). PR 모드에서는 문제가 안 된다 — PR의 커밋 히스토리에는 신규 파일도 이미 커밋으로 들어가 있어 `gh pr diff`가 전부 잡는다. **로컬 모드만의 문제다.**

**`git status --porcelain`의 `??` 줄로 untracked를 뽑지 않는다** — 신규 디렉터리를 파일 단위가 아니라 디렉터리 한 줄로 뭉갠다(실측 확인: 새 디렉터리 안에 파일 2개를 만들고 비교하면 `git status --porcelain`은 `?? newdir/` 한 줄만 내고, 그 안의 파일 2개는 목록에 안 잡힌다). 대신 `git ls-files --others --exclude-standard`로 뽑는다 — 파일 단위로 나오고, ce-code-review 자신도 `UNTRACKED:` 항목에 이 명령을 쓴다. 이 출력을 `UNTRACKED` 목록으로 저장해 둔다 — Phase 4에서 E3(전문 렌즈)에게 명시로 전달한다.

**중단 조건**:
- `$MERGE_BASE`를 못 구함(베이스 브랜치가 없거나 fetch 실패) → "베이스 브랜치를 찾을 수 없습니다. `base:<ref>`를 직접 지정하거나 원격에 베이스 브랜치가 있는지 확인하세요."
- 커밋된 변경도 미커밋 변경도 전혀 없음 → "베이스 대비 변경사항이 없습니다. 리뷰할 것이 없습니다."
- 변경 파일이 자동생성 파일뿐 → "자동생성 파일만 변경되었습니다."

`baseRefName`·`headRefOid`·`title`·`body` 자리는 이후 단계에서 각각 `$BASE_BRANCH`·`$(git rev-parse HEAD)`·`$CURRENT_BRANCH`·커밋 로그 요약으로 대체한다.

**자동생성 파일**은 이후 모든 단계에서 제외한다: `uv.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Gemfile.lock`, `go.sum`, `poetry.lock`, `Pipfile.lock`, `*.min.js`, `*.min.css`, `*.generated.*`

**diff 신호**를 뽑아 둔다. Phase 3의 조건부 엔진 선택에 쓴다. **판정 기준이 신호마다 다르다** — `workflows`·`tests`는 변경 파일 경로만 보면 되지만, 나머지 넷은 파일 경로로 판단할 수 없어 위에서 파일로 받아 둔 diff 본문을 봐야 한다. 실측 지적 — 이 구분이 없으면 diff 본문을 아예 안 받은 채로 이 표를 적용하게 된다.

**diff 본문은 컨텍스트로 읽지 말고 파일에서 grep으로만 훑는다.** 위에서 diff를 화면 출력이 아니라 파일(`/tmp/review-ensemble-*.diff`)로 받는 이유다 — 수천~수만 줄짜리 diff를 신호 판정 때문에 통째로 읽어들이면 그 자체로 컨텍스트가 넘친다(실측 지적: 이전 버전에 있던 "8000줄 이상이면 /tmp 파일로" 가드가 개편 때 대체 없이 지워졌는데, 본문 신호 추가로 그 위험이 더 커졌다). 본문 신호 4개는 전부 아래 같은 grep 한 번씩으로 판정된다 — 파일을 읽는 게 아니라 개수만 받는다:

```bash
grep -cE '^\+.*(catch|except|rescue|recover)' /tmp/review-ensemble-*.diff              # error-handling
grep -cE '^\+.*(interface |type |class |struct |@dataclass)' /tmp/review-ensemble-*.diff   # new-types — 나머지도 같은 방식
```

| 신호 | 판정 기준 | 켜는 것 (Phase 3) |
|------|-----------|------|
| `workflows` | 변경 파일 경로가 `.github/workflows/*.y*ml`, `action.yml`, `.github/dependabot.yml` | 레포 로컬 워크플로 렌즈 |
| `error-handling` | diff 본문 추가 줄에 `catch`, `except`, `rescue`, `recover`, 폴백 분기 | 조용한 실패 렌즈 |
| `new-types` | diff 본문에 신규 `interface`/`type`/`class`/`struct`/`dataclass` 선언 | 타입 설계 렌즈 |
| `tests` | 변경 파일이 테스트 디렉토리·파일명 규약에 걸림 | 테스트 커버리지 렌즈 |
| `new-logic` | diff 본문에 테스트 파일 밖 신규 함수·메서드 선언 추가 | 테스트 커버리지 렌즈 — `tests` 없이도 켠다. 새 로직에 테스트가 안 따라온 경우가 바로 이 렌즈의 대상이므로, 테스트 파일 변경이 있을 때만 켜면 정작 필요한 때 꺼진다 |
| `comments-heavy` | diff 추가 줄 중 주석·독스트링 줄이 30줄 이상 | 주석 정확성 렌즈 |

마지막 두 신호는 실측 지적으로 추가됐다 — Phase 3 표가 "신규 로직"·"주석 대량 추가"를 조건으로 걸면서 정작 이 표에 판정 기준이 없어, 두 렌즈는 켤 근거를 만들 수 없는 죽은 조건이었다.

---

## Phase 2: 워크트리 준비

**로컬 모드면 이 단계 전체를 건너뛴다.** 이미 그 코드 위에 있으므로 fetch도 워크트리도 필요 없다 — 현재 워킹트리 자체가 리뷰 대상이다. 모든 엔진이 절대경로로 현재 디렉토리를 직접 본다.

PR 모드에서 `quick` 프로파일이거나 `--no-worktree`면 이 단계를 건너뛰고 Phase 3으로 간다.

### 왜 만드는가

두 가지 이유가 있고, 두 번째가 덜 알려져 있다.

1. 코드를 직접 읽는 엔진(전문 렌즈 에이전트, 레포 로컬 렌즈)은 워킹트리가 PR head여야 옳은 파일을 본다
2. **ce-code-review의 Codex 교차 리뷰가 워킹트리 = PR head일 때만 켜진다.** `references/cross-model-review.md`의 게이트 2번: `pr-remote`/`branch-remote`에서는 건너뛴다 — 피어가 로컬 트리를 보는데 그게 PR head가 아니기 때문

### 절차

```bash
# PR head를 체크아웃 없이 가져온다. fork PR도 이 경로로 받아진다.
git fetch --no-tags origin "pull/{PR}/head"
git rev-parse FETCH_HEAD   # headRefOid와 일치하는지 확인
```

워크트리 경로는 `$(git rev-parse --show-toplevel)/.claude/worktrees/review-ensemble-{PR}`.

만들기 전에, 이 경로가 ignore되어 있지 않으면 부모 레포의 `git status`에 워크트리 전체가 untracked로 잡혀 사용자 화면에 노이즈가 생긴다. 추적 파일(`.gitignore`)을 건드리지 않고 로컬 전용 exclude로 막는다:

```bash
git check-ignore -q .claude/worktrees/probe 2>/dev/null \
  || echo ".claude/worktrees/" >> "$(git rev-parse --git-common-dir)/info/exclude"
```

**브랜치 이름을 PR의 `headRefName`과 똑같이 지어야** ce가 `local-aligned`로 판정한다(ce Stage 1의 3개 조건 중 1번이 `git rev-parse --abbrev-ref HEAD` == `headRefName`). `--detach`로 만들면 HEAD가 `HEAD`로 나와 이 조건이 깨진다.

상황별로 다음 표대로 만든다. **기존 로컬 브랜치를 절대 덮어쓰지 않는다** — 사용자의 미푸시 작업이 날아간다.

| 상황 | 명령 | 정렬 |
|------|------|------|
| fork PR (`isCrossRepository: true`) | `git worktree add --detach <WT> FETCH_HEAD` | ❌ |
| 로컬에 `<headRefName>` 브랜치 없음 | `git worktree add <WT> -b <headRefName> FETCH_HEAD` | ✅ |
| 브랜치 있고 PR head와 동일 + 다른 곳에 체크아웃 안 됨 | `git worktree add <WT> <headRefName>` | ✅ |
| 브랜치가 PR head와 다름, 또는 이미 다른 워크트리에 체크아웃됨 | `git worktree add --detach <WT> FETCH_HEAD` | ❌ |

체크아웃 여부는 `git worktree list`로 확인한다.

정렬 결과를 `ALIGNED` 값으로 기억한다. ❌여도 리뷰는 정상 진행되며, ce가 스스로 원격 모드로 떨어진다. 다만 Codex 교차 리뷰는 꺼지므로 Phase 7 리포트의 커버리지에 그 사실을 적는다.

**둘째 행(`-b`로 새 브랜치 생성)이었는지를 `BRANCH_CREATED` 값으로 따로 기억한다.** 실측 지적 — 둘째 행(신규 생성)과 셋째 행(사용자의 기존 브랜치 재사용)이 똑같이 정렬 ✅라서, `ALIGNED`만 들고 Phase 10에 가면 "이 브랜치를 지워도 되는가"를 구분할 수 없다. 셋째 행에서 지우면 사용자 브랜치가 강제 삭제된다 — 이 문서가 절대 일어나면 안 된다고 적어둔 바로 그 결과다.

### 세션 진입

**전제: 이 스킬은 대상 PR의 레포 안에서 실행해야 한다.** 다른 레포에서 실행하면 `EnterWorktree`가 거부한다 — 그 도구는 워크트리가 **현재 세션 레포에 등록된 것**인지 확인하고, 남의 레포 워크트리는 받지 않는다.

Phase 1에서 이미 얻은 `owner/repo`를 현재 위치와 대조한다. **remote URL 문자열을 직접 비교하지 않는다** — 같은 레포도 SSH(`git@github.com:owner/repo.git`)와 HTTPS(`https://github.com/owner/repo`) 형식이 다르고, SSH 별칭 호스트(`github.com-personal`)까지 섞이면 문자열 비교는 틀린 답을 낸다. URL 파싱을 직접 짜지도 않는다(플랫폼마다 `sed` 정규식 방언이 갈린다). `gh`가 정규화해 준 값을 쓴다:

```bash
gh repo view --json nameWithOwner -q .nameWithOwner   # 현재 위치의 owner/repo
```

이 값이 Phase 1의 대상 `owner/repo`와 같을 때만 진입한다. 다르면 **진입을 시도하지 말고** 그 사실을 사용자에게 먼저 알린 뒤 아래 갈림표대로 진행한다 — 거부 오류를 맞고 나서 알아내는 것보다, 미리 알리는 편이 사용자가 "대상 레포에서 다시 실행"을 선택할 여지를 준다.

일치할 때만 진입한다:

```
EnterWorktree(path: "<WT 절대경로>")
```

이 스킬이 워크트리 사용을 명시적으로 지시하므로 EnterWorktree의 사용 조건을 충족한다. 진입 이후 모든 Skill·Agent 호출은 워크트리 안에서 동작한다.

**진입에 실패하면 (레포 불일치·권한 등) 리뷰를 중단하지 않는다.** 워크트리 자체는 이미 만들어져 있으므로 다음으로 나눠 계속한다:

| 엔진 유형 | 진입 실패 시 |
|---|---|
| Agent로 부르는 렌즈 | **정상 동작.** 프롬프트에 워크트리 절대경로를 넣어 보내므로 세션 위치와 무관하다 |
| Skill로 부르는 엔진 | 워크트리를 못 쓴다 ([engines.md](engines.md) E2의 경로 전달 한계 참조). 각 엔진이 알아서 PR을 가져오므로 리뷰는 되지만, 로컬 근거가 낡을 수 있다는 사실을 커버리지에 적는다 |

이 갈림을 리포트 커버리지에 명시한다 — 어느 관점이 어떤 트리를 봤는지가 근거의 신선도를 좌우한다.

---

## Phase 3: 엔진 선택

[engines.md](engines.md)를 읽고 프로파일과 diff 신호에 맞는 엔진을 고른다.

| 엔진 | quick | standard | deep |
|------|:-----:|:--------:|:----:|
| ce-code-review | — | ✅ | ✅ |
| 내장 code-review | ✅ medium | ✅ high | ✅ high |
| 조용한 실패 렌즈 | — | — | `error-handling` 신호 |
| 테스트 커버리지 렌즈 | — | — | `tests` 또는 `new-logic` 신호 |
| 타입 설계 렌즈 | — | — | `new-types` 신호 |
| 주석 정확성 렌즈 | — | — | `comments-heavy` 신호 |
| 레포 로컬 워크플로 렌즈 | — | — | `workflows` 신호 + 레포에 스킬 존재 |

**로컬 모드는 이 제외 규칙이 아예 적용되지 않는다.** 현재 디렉터리 자체가 리뷰 대상이므로 "워킹트리가 PR head와 다를 위험"이 원천적으로 없다 — 전문 렌즈·레포 로컬 렌즈 모두 현재 디렉터리 절대경로를 그대로 받아 정상 동작한다.

PR 모드에서 **워크트리 디렉터리 자체가 없는 경우**(`quick`·`--no-worktree`, 또는 Phase 2의 `git worktree add`가 실패)만 전문 렌즈와 레포 로컬 렌즈를 전부 제외한다. 이들은 로컬 파일을 읽어야 동작하는데 워킹트리가 PR head가 아니면 엉뚱한 파일을 리뷰한다.

**세션 진입(`EnterWorktree`)만 실패한 경우는 다르다** — 디렉터리는 PR head로 이미 만들어져 있다. Phase 2의 구분표대로:
- 전문 렌즈(Agent로 부름) — 프롬프트에 절대경로를 직접 실어 보내므로 세션 위치와 무관하게 정상 실행한다. **제외하지 않는다.**
- 레포 로컬 렌즈(Skill로 부름, E4) — 경로를 못 넘기므로 제외한다.

이 둘을 같은 조건으로 묶으면 `deep` 프로파일이 세션 진입 실패 한 번에 `standard`와 사실상 같아져, 사용자가 고른 프로파일의 의미가 사라진다.

내장 code-review는 diff를 `gh pr diff`로 받아오므로 워크트리 없이도 동작한다. 다만 medium 이상 레벨은 주변 함수·호출자를 로컬 트리에서 읽으므로, 워크트리 없이 돌 때 로컬 HEAD가 PR head와 다르면 그 근거가 낡았을 수 있다 — Phase 7 커버리지에 명시한다 (근거: [engines.md](engines.md) E2의 체크아웃 확인 절).

선택 결과를 사용자에게 한 줄로 알린다. 어떤 관점이 들어갔는지가 알릴 내용이고, 내부 배선은 알릴 내용이 아니다.

---

## Phase 4: 엔진 실행

[engines.md](engines.md)의 호출 규격대로 띄우되, 호출 방식에 따라 순서가 다르다.

**전문 렌즈를 디스패치하기 전에 merge-base SHA를 계산한다** — [engines.md](engines.md) E3의 디스패치 프롬프트 틀이 이 값을 쓴다. **로컬 모드는 이미 Phase 1에서 `$MERGE_BASE`를 구해뒀으므로 그대로 재사용한다** — 다시 계산할 필요 없다.

PR 모드:
```bash
git fetch --no-tags origin {baseRefName}   # Phase 1에서 얻은 base 브랜치
MERGE_BASE=$(git merge-base FETCH_HEAD {headRefOid})   # Phase 1에서 얻은 PR head SHA
```

**E1(ce)·E2(내장 code-review) 호출 인자도 모드에 따라 다르다:**

| 엔진 | PR 모드 | 로컬 모드 |
|---|---|---|
| E1 (ce-code-review) | `mode:agent {PR번호}` | `mode:agent base:{$MERGE_BASE}` — ce 자신의 "명시적 base" 빠른 경로. 인자 없이 부르면 ce가 자체적으로 base를 다시 탐지해 이번 Phase 1의 탐지와 갈릴 수 있으므로, 이미 구한 값을 명시로 넘긴다 |
| E2 (내장 code-review) | `high {PR번호}` (`quick`이면 `medium`) | `high` (`quick`이면 `medium`) — **PR 인자 없이 부른다.** 내장 엔진 자신이 인자 없으면 현재 브랜치의 커밋된+미커밋 변경 전체를 스스로 진단해 diff로 잡는다(실측 확인: `git diff @{upstream}...HEAD; git diff HEAD`) |

**Agent 기반 렌즈(전문 렌즈)를 먼저, 한 메시지에 모아 병렬로 디스패치한다.** Agent 호출은 백그라운드에서 돌므로 이후 작업과 겹쳐 실행된다.

**Skill 기반 엔진(ce → 내장 code-review → 레포 로컬 렌즈)은 순차로 실행한다.** Skill 호출은 지시문이 이 컨텍스트에 로드되어 실행되는 방식이라, 인라인 파이프라인 두 개를 동시에 굴릴 수 없다. 순차여도 벽시계 손해는 작다 — ce가 도는 동안 Agent 렌즈들이 백그라운드에서 함께 돌고 있다.

Agent 렌즈 결과는 마지막에 수거한다.

모든 엔진에 공통으로 강제하는 세 가지:
1. **게시 금지** — `--comment`, `gh pr comment`, `gh api ... /reviews` 등 GitHub에 쓰는 동작 일체
2. **수정 금지** — 워크트리 파일을 고치지 않는다. 이 스킬은 리뷰만 한다
3. **출력 계약** — [merge.md](merge.md)의 통합 스키마로 반환

엔진 하나가 실패해도 나머지로 계속한다. 실패한 엔진은 Phase 7 커버리지에 실패 사실과 한 줄 이유를 적는다. 엔진이 전부 실패하면 중단하고 그 사실을 알린다.

**실패 사유가 "스킬/플러그인을 찾을 수 없음"이면** [references/prerequisites.md](references/prerequisites.md)를 읽어 어느 플러그인이 빠졌는지, 설치 명령이 무엇인지를 Phase 7 커버리지와 사용자 안내에 반영한다 — "E1 실패"로만 알리면 사용자가 원인을 다시 찾아야 한다.

---

## Phase 5: 정규화 · 병합 · 교차확인 계수

[merge.md](merge.md)를 읽고 그대로 적용한다. 요약:

1. 엔진별 원본 등급을 **P0~P3 + 확신도(0/25/50/75/100)**로 정규화. 구조화 출력이 없어 산문으로 온 결과도 버리지 않고 옮긴다
1b. **자동생성 파일에 대한 발견을 여기서 걸러낸다.** Phase 1의 자동생성 파일 목록과 `file`이 일치하는 발견은 버린다. ce·내장 code-review는 `gh pr diff` 전체를 스스로 가져오므로 Phase 1의 필터가 이 둘에는 안 걸린다 — 그래서 병합 단계가 유일한 실제 관문이다. 전문 렌즈는 애초에 워크트리에서 대상 diff만 보므로 대개 해당 없다
2. 중복 제거를 **두 경로로** 돌린다 — 같은 위치(경로 A)와, 파일이 달라도 같은 결함인 경우(경로 B). 경로 B를 빠뜨리면 교차확인이 사라지고 같은 문제가 두 번 게시된다
3. **모순 발견을 골라낸다** — 같은 자리에 동시 적용 불가능한 처방 두 개가 걸린 경우. 합치지도, 일반 발견으로 내보내지도 않고 "결정 필요"로 승격
4. 남은 발견마다 두 숫자를 계산:
   - `engine_count` — 이 발견을 지적한 서로 다른 엔진 수 (소프트 버킷 언급은 세지 않고 주석으로만)
   - `covering_engines` — 그 **파일을 실제로 본** 엔진 수
5. 억제 규칙 적용 (P2·P3 단독 저확신 발견 폐기, `pre_existing`은 인라인에서 제외)

> ⚠️ ce-code-review는 내부에서 페르소나 13종을 이미 병합하므로 **엔진 1개로 센다.** 페르소나 수를 세면 ce 혼자 교차확인 기준을 채워버려 계수가 무의미해진다.

---

## Phase 6: 논쟁 발견사항 검증

교차확인 계수가 이 판단을 추측에서 숫자로 바꿔준다.

**호출 조건** — 다음을 모두 만족하는 발견마다 아래 검증을 돌린다:
- 등급이 P0 또는 P1
- `engine_count == 1` (한 엔진만 지적)
- `covering_engines >= 2` (그 파일을 본 엔진이 둘 이상인데 나머지는 지적하지 않음)

세 번째 조건이 핵심이다. 그 파일을 본 엔진이 하나뿐이면 애초에 교차검증이 불가능하므로 논쟁이 아니다.

조건에 맞는 발견이 없으면 이 단계를 건너뛴다.

### `/rl-verify`가 아니라 이 스킬 자체 내장 반박 검증자 페르소나를 쓴다

> **왜 `/rl-verify`가 아닌가 (실측 근거)**: `/rl-verify`를 실제로 호출해 확인한 결과, 이 스킬은 단건 판정용이 아니었다. Tier 1~3 분류 후 CONTRARIAN·ARCHITECT·RESEARCHER·SIMPLIFIER·EVALUATOR 팀을 꾸리고, **시작 전 `AskUserQuestion`으로 사용자 동의를 요구**하며(자동 판정을 막음), `docs/demiurge/rl-verify/{slug}/`에 plan.md·report.md를 **영구 생성**한다. 이 경로에 `demiurge`가 고정으로 박혀 있어, review-ensemble이 워크트리(대상 레포) 안에서 이걸 부르면 **남의 레포에 관계없는 폴더가 생긴다.** 발견 1건 판정에 5-역할 팀 + 수렴 루프는 무게도 안 맞는다.

> **외부 에이전트 대신 review-ensemble 자신의 파일을 쓰는 이유**: 초기 버전은 `product/.claude/agents/counter-reviewer.md`(demiurge 레포에만 있는 커스텀 에이전트)를 참조했다. review-ensemble **대상 레포**(tax-agent 등) 안에서 실행될 때 그 경로가 안 열려, `~/.claude/agents/counter-reviewer.md`(전역 심링크)로 대체하는 폴백까지 필요했다 — 즉 review-ensemble을 쓰려면 demiurge를 clone해서 `just link`까지 해둬야만 Phase 6 표1이 동작했다. **이 의존성을 끊었다** — 같은 반박 방법론을 review-ensemble 자신의 디렉터리 안(`counter-reviewer.md`)에 옮겨 담아, engines.md·merge.md처럼 review-ensemble과 함께 배포되는 파일로 만들었다. 이제 review-ensemble 폴더를 어디에 두든(다른 레포, 다른 머신, demiurge 없이 이 폴더만 복사해도) 외부 경로 탐색 없이 항상 열린다.

발견마다 **독립적인 검증 표 2개를 병렬로** 받는다(1개면 그 반박이 맞는지 확인할 길이 없고, 3개 이상은 이 규모의 판정에 과하다). 두 표는 **서로 다른 모델 패밀리**로 낸다 — 같은 모델·같은 페르소나·같은 프롬프트로 두 번 물으면 같은 맹점을 똑같이 반복할 수 있고, 그러면 "2/2 REFUTED"가 실은 하나의 편향이 두 번 나온 것일 수 있다(실측 지적: 이전 버전은 opus 기반 반박 페르소나를 그대로 두 번 불렀다).

**표1 — 반박 검증자 페르소나 (Claude, opus)**

`[counter-reviewer.md](counter-reviewer.md)`(review-ensemble과 같은 디렉터리) 내용을 통째로 읽어 `general-purpose` 에이전트 프롬프트에 심는다 — ce-code-review가 페르소나를 다루는 것과 같은 방식이다. 이 페르소나는 커스텀 `subagent_type`으로 등록된 것이 아니라 순수 텍스트 파일이므로, `Agent(subagent_type: "counter-reviewer")`처럼 이름으로 직접 부르면 실패한다("Agent type 'counter-reviewer' not found" — 실측 확인) — 반드시 파일을 읽어 `general-purpose`에 프롬프트로 심는 방식을 쓴다:

```
Agent(subagent_type: "general-purpose", model: "opus")

프롬프트 서두: counter-reviewer.md 전체 내용을 그대로 붙여넣는다
             ("아래는 당신의 페르소나입니다. 이 페르소나를 그대로 따르세요." + 파일 전문)

파일을 못 읽으면 표1을 건너뛰고 커버리지에 실패 사실을 남긴다 — 발견 없이 조용히 넘어가지 않는다.

`model: "opus"`를 명시로 넣는다 — 페르소나를 텍스트로 복사해 옮기는 이 방식에서는 frontmatter의 model 지정이 살아남지 않는다. 명시하지 않으면 세션 기본 모델로 조용히 실행된다.

이어서 아래 공통 검증 요청(두 표 공통)을 붙인다.
```

**표2 — Codex CLI (별도 모델 패밀리, 별도 프로세스)**

ce-code-review의 자체 교차 리뷰가 쓰는 것과 같은 패턴이다(그 스킬의 `references/cross-model-review.md`에서 가져옴) — 셸아웃이라 Agent 서브에이전트 동시성 예산을 안 쓴다.

```bash
codex --version >/dev/null 2>&1 && CODEX_AVAILABLE=1 || CODEX_AVAILABLE=0
if [ "$CODEX_AVAILABLE" = "1" ]; then
  cat > <프롬프트파일> <<'EOF'
{페르소나 지시 + 아래 공통 검증 요청}
EOF
  if codex exec - -s read-only -o <출력파일> < <프롬프트파일> && [ -s <출력파일> ]; then
    cat <출력파일>   # 여기서 반드시 읽는다 — 안 읽으면 판정이 파일에만 남고 유실된다
  else
    CODEX_AVAILABLE=0   # 런타임 실패 — 아래 폴백 경로로 넘어간다
  fi
fi
```

**`codex --version` 성공이 `codex exec` 성공을 보장하지 않는다** — 실측 지적: 버전 확인은 통과했는데 실제 실행이 만료된 인증·레이트리밋·네트워크 오류로 실패하면, 이전 버전은 폴백이 발화할 코드 경로 자체가 없어 Phase 6 판정표가 존재하지 않는 두 번째 의견을 소비했다. 그래서 `codex exec`의 종료 코드와 출력 파일이 비어 있지 않은지(`-s`)를 함께 확인하고, 실패면 `CODEX_AVAILABLE=0`으로 되돌려 폴백을 태운다. **행(hang) 방지**: 이 명령을 실행하는 Bash 도구 호출에 timeout을 600000ms(10분)로 명시한다 — Codex 프로세스가 멈추면 도구 타임아웃이 강제 종료하고, 그 종료도 위와 같은 실패 경로로 처리한다(ce의 교차 리뷰 스크립트가 자체 워치독으로 하는 일을 여기서는 도구 타임아웃이 대신한다).

**`echo "..." | codex exec`가 아니라 파일로 넘긴다** — 실측 지적: 발견의 근거·인용문에는 코드 줄이 그대로 담기고, 그 안에 큰따옴표가 섞이기 마련이다(예: `"session.py:88 return ..."`). `echo "..."`에 그런 문자열을 넣으면 셸이 그 자리에서 깨진다. 따옴표 없는 heredoc(`<<'EOF'`)은 `$`·백틱 확장도 막아 코드 인용문을 안전하게 통째로 옮긴다 — ce 자신의 교차 리뷰 스크립트가 쓰는 것과 같은 방식이다. 마지막 줄(`cat <출력파일>`)도 실측 지적이다 — 이전 버전은 파일에 쓰기만 하고 다시 읽는 단계가 없어, Codex가 정상적으로 답해도 그 판정이 조용히 버려질 수 있었다.

**Codex CLI가 없거나 실패하면(`CODEX_AVAILABLE=0` 또는 명령 오류) 표2를 표1과 같은 방식(general-purpose)으로 대체하되 `model: "sonnet"`을 쓴다** — 페르소나 텍스트는 같아 완전히 독립적이진 않지만, 최소한 모델 가중치가 달라져 이전보다는 상관관계가 줄어든다. 이 경우 판정표 처리 뒤 리포트에 "표2가 폴백 경로였다(Codex 미가용)"를 반드시 남긴다 — 독립성이 약한 판정임을 숨기지 않는다.

**두 표 공통 검증 요청**:

```
- GitHub에 아무것도 게시하지 마세요. gh pr comment, gh api .../reviews, --comment 플래그 모두 금지입니다.
- 파일을 수정하지 마세요. 이 작업은 검증만 합니다.

{발견의 제목·등급·확신도}
파일: {file}:{line}
주장: {why_it_matters}
근거: {evidence}
지적한 엔진: {engine}
같은 파일을 봤지만 이 지점을 지적하지 않은 엔진: {나머지 covering 엔진 목록}

이 코드를 직접 읽고 반박을 시도하라 — 원 조사관의 인용이 맥락에서 벗어나지 않았는지,
같은 증거로 다른 결론이 가능한지, 위반이 다른 곳에서 이미 방지되고 있는지 확인하라.

스코프: {로컬 모드면 항상 현재 워킹트리 절대경로를 Read/Grep으로 직접(git show 쓰지 않음 — 로컬 모드의 존재 이유가 미커밋 변경이므로, git show는 커밋된 것만 보여줘 정반대 결과를 낸다) / PR 모드에서 워크트리 디렉터리 자체가 있으면(Phase 2에서 생성 성공 — ALIGNED 여부와 무관. detached worktree도 FETCH_HEAD 콘텐츠는 정확하다) 워크트리 절대경로를 Read/Grep으로 직접 / 워크트리 자체가 없으면(quick·--no-worktree, 또는 Phase 2의 생성 자체가 실패) git show <head-ref>:<path> 로만}

반드시 하나만 반환하라: {"verdict": "UPHELD"|"WEAKENED"|"REFUTED"|"INCONCLUSIVE", "reasoning": "한두 문장"}
```

앞의 두 줄이 빠졌던 것은 실측 지적이다 — 이 스킬의 다른 모든 엔진 호출은 게시·수정 금지를 강제하는데, 표1(counter-reviewer)은 `general-purpose`에 도구 제한이 없는 채로 열려 있어(Bash 포함) 이론상 검증 도중 `gh pr comment`를 스스로 실행할 수 있었다.

`WEAKENED`를 강제로 빼지 않는다. 표1(counter-reviewer 페르소나)의 판정 체계가 UPHELD·WEAKENED·REFUTED 셋이다 — "부분적 약점은 있으나 결론은 유지"라는 뜻으로, UPHELD(무결함)와도 REFUTED(반박됨)와도 다른 실제 상태다. 표2(Codex)에도 같은 4값 계약을 그대로 요구해 두 표가 같은 자를 쓰게 한다. `INCONCLUSIVE`는 "코드 자체를 확인할 수 없는 경우"(예: 워크트리가 없고, `git show`로 읽을 head 참조도 fetch돼 있지 않은 경우)를 위한 값이다.

### 2표 판정표

| 결과 | 처리 |
|------|------|
| UPHELD 2/2 | 등급 유지 |
| UPHELD/WEAKENED 조합(REFUTED 없음) | 등급 유지 + "일부 약점 지적됨" 주석 |
| REFUTED가 하나 + (UPHELD 또는 WEAKENED) 하나 | 한 단계 강등 + 리포트·코멘트에 논쟁 사실 명시 |
| REFUTED 2/2 | 인라인 게시에서 제외. 리포트 접힌 섹션에 "반박됨"으로 기록 — 조용히 지우지 않는다 |
| INCONCLUSIVE가 하나라도 있고 REFUTED가 없음 | P2로 강등 + "검증 불가" 표시. 판정을 지어내지 않고 불확실성을 그대로 노출한다 |
| INCONCLUSIVE + REFUTED 조합 | REFUTED 쪽에 실질적 반박 근거가 있다는 뜻이므로, "REFUTED 하나 + UPHELD/WEAKENED 하나"와 같은 처리(한 단계 강등) |

REFUTED 폐기는 merge.md의 "P0/P1 자동 폐기 금지"와 충돌하지 않는다 — 그 규칙이 막는 것은 검증 **없이** 지우는 것이고, 여기는 독립 재검증을 통과한 뒤다.

---

## Phase 7: 종합 리포트

대화에 출력한다. 여기는 사용자가 디버깅용으로 보는 화면이므로 엔진 이름을 그대로 쓴다.

**PR 모드**:
```markdown
## PR Review Complete

**PR #{번호}:** {제목}
**브랜치:** {headRefName} → {baseRefName}
**프로파일:** {quick|standard|deep}
```

**로컬 모드** — 위 세 줄 대신:
```markdown
## 로컬 검증 완료

**브랜치:** {CURRENT_BRANCH} → {BASE_BRANCH} (아직 PR 없음)
**프로파일:** {quick|standard|deep}
```

이어서 두 모드 공통:
```markdown

### 커버리지
- 실행한 관점: {목록}
- 워크트리: {경로, 또는 "사용 안 함"} / PR head 정렬: {예|아니오} / 세션 진입: {성공|실패 — 어느 엔진이 어떤 트리를 봤는지}
- Codex 교차 리뷰: {실행됨|건너뜀 — 사유}
- 실패한 엔진: {목록과 사유, 없으면 "없음"}
- 산문 반환을 매핑한 엔진: {목록, 없으면 생략}
- 제외한 파일: {자동생성 파일 목록}

### 발견사항 요약
- 🔴 P0: {n}건 — 머지 차단
- 🟠 P1: {n}건 — 수정 필요
- 🟡 P2: {n}건 — 수정 권장
- 🔵 P3: {n}건 — 개선 제안
- ⚔️ 결정 필요: {n}건 — 처방이 갈려 사람이 정해야 함

교차확인 {n}건 · 단독 지적 {n}건 · 검증으로 강등 {n}건

### 🔴 P0
1. **{제목}** — `{file}:{line}` {배지 — merge.md 배지표의 "터미널 리포트" 열 그대로: 교차확인 / ⚠️ 단독 지적 / 배지 없음(그 파일을 본 엔진이 하나뿐일 때 — quick 프로파일은 전부 여기 해당하므로 "단독 지적"으로 잘못 달지 않는다) 중 하나}
   {왜 문제인지}
   {수정 제안이 있으면}
   {also_at 이 있으면: 발현 위치도 함께}

### 🟠 P1
...

### ⚔️ 결정 필요
1. **{무엇을 정해야 하는가}** — `{file}:{line}` (등급 {P#})

   | 관점 | 진단 | 처방 |
   |---|---|---|
   | {A} | {사실 판단} | {수정안 A} |
   | {B} | {사실 판단} | {수정안 B} |

   갈리는 지점: {무엇을 정하면 어느 쪽으로 결정되는지}
```

**결정 필요 항목은 등급 순 목록 뒤에 따로 둔다.** 등급 목록에 섞으면 "고치면 되는 일"로 읽혀, 정해야 할 것이 정해지지 않은 채 한쪽이 적용된다.

접힌 별도 섹션에 두는 것 — 인라인 게시 대상이 아니지만 버리지도 않는다:

| 섹션 | 담기는 것 |
|---|---|
| 기존 코드의 문제 | `pre_existing: true` 발견 |
| 억제된 발견 | 억제 규칙에 걸려 폐기·접힌 것 (사유 포함) |
| 반박된 발견 | Phase 6에서 `REFUTED` 판정을 받은 것 |
| **낮은 강도의 언급** | **어떤 엔진도 정식 발견으로 올리지 않은 소프트 버킷 항목 중, 다른 발견과 매칭되지 않은 것** |

마지막 행이 없으면 갈 곳 없는 항목이 조용히 사라진다 — 소프트 버킷 규칙은 "발견에 주석으로 붙인다"까지만 정하므로, 붙일 발견이 없는 항목은 규칙의 사각지대다. 리포트에서 사라지면 다음 사람이 그 관찰을 다시 하게 된다.

---

## Phase 8: 게시 범위 확인

**로컬 모드면 이 Phase와 Phase 9를 통째로 건너뛰고 Phase 10으로 간다.** 게시할 PR 자체가 없다 — Phase 7의 리포트가 곧 최종 산출물이다. 사용자에게 확인을 묻지도 않는다, 물을 대상(게시 여부)이 없기 때문이다.

PR 모드에서 `-f`가 있으면 전체 게시로 바로 Phase 9로 간다.

그 외에는 AskUserQuestion으로 묻는다. 질문 카드는 카드만 읽고 결정할 수 있어야 하므로, PR 번호·제목·등급별 건수·교차확인 건수를 카드 안에 담는다.

선택지: 전체 게시 / P0+P1+P2 / P0+P1만 / 게시하지 않음

**결정 필요(모순) 항목도 이 등급 기준을 그대로 탄다.** merge.md의 "모순 발견"에서 등급을 이미 부여받았으므로(두 발견 중 높은 쪽), 별도 취급 없이 같은 필터를 적용한다 — "P0+P1만"을 고르면 P0/P1 등급의 결정 필요 항목만 포함되고, P2 등급인 것은 빠진다.

"게시하지 않음"을 고르면 Phase 10으로 간다.

---

## Phase 9: 게시 (PR 모드 전용)

로컬 모드에서는 Phase 8이 이 단계를 건너뛰므로 여기 도달하지 않는다.

[comment-format.md](comment-format.md)를 읽고 페이로드를 만들어 게시한다.

PR 코멘트는 **팀원이 읽는 문서**다. 엔진 이름·프로파일·내부 워크플로 용어를 코멘트 본문에 노출하지 않는다. 교차확인은 개수와 성격으로만 표현한다 — "3개 리뷰 중 2개가 같은 지적" 은 되고, "ce-code-review + 내장 code-review" 는 안 된다.

라인 유효성 검증을 거쳐, diff 범위 밖의 발견은 인라인에서 빼고 리뷰 본문의 "추가 발견사항"에 넣는다.

```bash
gh api repos/{owner}/{repo}/pulls/{PR}/reviews --input /tmp/pr-review-{PR}.json
```

> `gh api`에 인라인 JSON을 넘기면 셸 glob 문제(`no matches found`)가 난다. 반드시 `--input` 파일을 쓴다.

게시 직후, 응답으로 받은 `review_id`로 실제 코멘트가 줄에 제대로 앵커됐는지 확인한다. **이번 리뷰의 코멘트로 반드시 좁힌다** — 실측 지적: 좁히지 않으면 (a) 이전 리뷰 라운드의 낡은 코멘트가 오탐을 내고, (b) `--paginate` 없이는 기본 첫 페이지(30건, 오래된 순)만 와서 방금 게시한 코멘트가 목록에 아예 안 들어올 수 있다 — 진짜 `side` 누락이 있어도 0이 나와 통과해버린다:

```bash
gh api "repos/{owner}/{repo}/pulls/{PR}/comments" --paginate \
  --jq '[.[] | select(.pull_request_review_id == {review_id} and .line == null)] | length'
```

`gh api`가 오류 없이 리뷰를 만들었다고 해서 코멘트가 정확한 줄에 달렸다는 뜻은 아니다 — `comments[].side`가 빠지면 API가 에러 없이 받되 레거시 방식으로 저장하고, 위 명령이 0이 아닌 값을 낸다([comment-format.md](comment-format.md) 참조). 0이 아니면 페이로드를 다시 점검한다.

게시 성공 시 리뷰 URL을 출력한다.

---

## Phase 10: 정리

**로컬 모드는 이 단계가 사실상 no-op다.** 워크트리도 fetch도 안 만들었으므로 치울 것이 없다 — Phase 7의 리포트가 이미 최종 산출물이었다. 세션을 그대로 종료한다.

PR 모드에서 워크트리를 만들었으면 치운다.

**Phase 2의 세션 진입(`EnterWorktree`)이 성공했던 경우에만** 먼저 빠져나온다. 진입이 실패·생략된 실행(레포 불일치 등 — Phase 2가 정상 결과로 문서화한 경우다)에서는 세션이 워크트리에 들어간 적이 없으므로, `ExitWorktree`를 부르지 않고 바로 아래 "삭제 전 확인"으로 간다 — 실측 지적: 이 분기 없이 무조건 부르면 진입한 적 없는 상태에서 진입을 되돌리는 도구를 호출하는 셈이다.

```
ExitWorktree(action: "keep")   # Phase 2 세션 진입에 성공했던 경우에만
```

`EnterWorktree`에 `path`로 진입한 워크트리는 `ExitWorktree`가 지우지 않으므로 `keep`으로 원래 디렉토리에 돌아온 뒤 직접 제거한다.

**삭제 전 확인 — `git status`만으로는 부족하고, 어디를 확인하는지도 명시해야 한다.** `git worktree remove --force`는 미커밋 변경에 대한 git의 기본 보호를 우회하고, `git branch -D`(대문자)는 병합 안 된 커밋이 있어도 강제로 지운다. 엔진이 "수정 금지"를 어기고 **커밋까지** 했다면 `git status`는 깨끗하게 나오지만 그 커밋들은 `-D`에 그대로 날아간다(reflog로만 겨우 복구 가능). 그래서 미커밋 변경과 별개로 HEAD가 움직였는지도 확인한다.

**반드시 `-C "<WT>"`로 워크트리 경로를 명시한다.** 바로 위에서 `ExitWorktree(keep)`으로 원래 디렉토리에 이미 돌아온 뒤이므로, 경로 없이 `git status`/`git rev-parse HEAD`를 그냥 실행하면 **워크트리가 아니라 원래 디렉토리를 검사한다** — 실측 지적: 원래 디렉토리가 우연히 깨끗한 상태면 워크트리 안의 미커밋 변경·새 커밋을 하나도 못 잡은 채 다음 단계로 넘어간다.

```bash
git -C "<WT>" status --porcelain                                    # 미커밋 변경
[ "$(git -C "<WT>" rev-parse HEAD)" = "<Phase 2에서 fetch한 headRefOid>" ]   # 커밋 추가 여부
```

둘 다 깨끗할 때만 제거한다:

```bash
git worktree remove "<WT>" --force
[ "$BRANCH_CREATED" = "yes" ] && git branch -D "<headRefName>"   # Phase 2에서 -b로 새로 만든 경우에만
```

**기존에 있던 브랜치는 지우지 않는다.** 판단 기준은 Phase 2에서 기억해 둔 `BRANCH_CREATED`이지 `ALIGNED`가 아니다 — `ALIGNED` ✅인 행이 둘(신규 생성·기존 재사용)이라 그 값으로는 구분할 수 없고, 재사용 케이스에서 지우면 사용자의 브랜치와 미병합 커밋이 함께 날아간다.

미커밋 변경이 있거나 HEAD가 원래 fetch한 SHA와 다르면 제거하지 말고 경로를 알린 뒤 사용자 판단에 맡긴다. 엔진들이 수정 금지 규칙을 어겼다는 신호이므로 그 사실도 함께 알린다.
