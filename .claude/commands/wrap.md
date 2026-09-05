---
description: 문서가 참조하는 스킬·규칙이 실제로 존재하는지 검증하고 개수를 맞춘다
allowed-tools: Read, Grep, Glob, Bash, Edit
---

# /wrap — 문서와 실제 파일의 불일치 검증

demiurge 문서(`README.md`, `product/.claude/CLAUDE.md`, 스킬 본문)가 참조하는 스킬·규칙이 실제로 존재하는지 확인하고, 개수 표기가 실제와 같은지 검증한다. 불일치를 발견하면 문서를 고친다.

## 왜 필요한가

스킬을 지우거나 이름을 바꿔도 그것을 부르던 문서는 그대로 남는다. 그 문서를 읽은 AI가 없는 스킬을 호출하면 그 단계가 조용히 실패한다. 실제 사례로 `readme-writer`가 `humanize-writing-portable`을 호출하도록 적혀 있었는데 그 스킬은 이미 삭제되어 있었고, 아무도 알아채지 못한 채 남아 있었다.

## 모드

- `/wrap` — 검증 후 발견한 불일치를 문서에 반영
- `/wrap --check` — 검증 결과만 출력하고 수정하지 않음

인자: `$ARGUMENTS`

## Step 1: 실제 인벤토리 수집

```bash
# 스킬 (배포 이름은 demiurge:<디렉터리명>)
ls product/.claude/skills/demiurge/skills

# 에이전트 (현재는 비어 있거나 디렉터리 자체가 없음)
ls product/.claude/skills/demiurge/agents 2>/dev/null

# 전역 규칙 + 프로젝트 로컬 규칙
ls product/.claude/rules .claude/rules

# 활성 플러그인 수
python3 -c "import json,os;d=json.load(open(os.path.expanduser('~/.claude/settings.json')));print(sum(1 for v in d.get('enabledPlugins',{}).values() if v))"
```

스킬 디렉터리마다 `SKILL.md`의 frontmatter에서 `name`을 읽는다. 디렉터리명과 `name`이 다르면 그 자체가 불일치다. Claude Code는 디렉터리명으로 호출하기 때문이다.

## Step 2: 문서가 참조하는 이름 수집

세 곳에서 스킬·에이전트 이름을 뽑는다.

1. **`product/.claude/CLAUDE.md`의 "Skills/Agents 호출 규칙" 표** — `/plugin:skill` 또는 `/skill` 형태로 적힌 호출 대상
2. **`README.md`** — 사용법 절의 호출 예시와 개수 표기
3. **demiurge 스킬 본문** — `Skill("...")`, `/demiurge:...`, `subagent_type: "..."` 형태로 다른 자산을 부르는 부분

```bash
grep -rn -oE 'Skill\("[^"]+"|subagent_type: *"[^"]+"|/[a-z0-9-]+:[a-z0-9-]+' \
  product/.claude/skills/demiurge/skills product/.claude/CLAUDE.md README.md
```

## Step 3: 이름 해석 (존재 여부 판정)

수집한 이름마다 다음 순서로 실제 존재를 확인한다.

| 형태 | 확인 방법 |
|------|----------|
| `demiurge:<name>` 또는 접두어 없는 자체 스킬 | `product/.claude/skills/demiurge/skills/<name>/SKILL.md` 존재 |
| `<plugin>:<name>` | 그 플러그인이 활성이고 `installPath` 아래에 해당 SKILL.md가 있는지 |
| `subagent_type: "<name>"` | 빌트인 목록(general-purpose, Explore, Plan, claude, claude-code-guide, statusline-setup) 또는 활성 플러그인이 제공하는 에이전트에 있는지 |
| MCP 도구 이름 | 해당 MCP 서버가 설정되어 있는지 |

플러그인 캐시 경로에는 버전 번호가 들어가므로 경로를 문서에 적지 말고, 존재 확인에만 쓴다.

**죽은 참조로 세지 않는 것** (실측으로 확인된 오탐 유형):

- 템플릿 자리표시자 — `subagent_type="{이름}"`처럼 실행 시 채워지는 값
- 반례 설명 — "이 페르소나는 `subagent_type`으로 등록된 것이 아니므로 이름으로 부르면 안 된다" 같이, 부르지 말라고 적은 문장 안의 이름
- 스킬 자기 폴더 안의 참조 파일 — `rl-verify/convergence-evaluator.md`처럼 파일을 직접 읽어 프롬프트에 주입하는 방식은 등록 자산이 아니어도 정상이다. 파일이 실제로 있는지만 확인한다.

## Step 4: 불일치 판정

| # | 검사 항목 | 판정 기준 |
|---|-----------|----------|
| 1 | 스킬 개수 | Step 1 실제 수 vs README "구성 요소" 표와 "구조" 절의 표기 |
| 2 | 규칙 개수 | Step 1 실제 수 vs README 표기 |
| 3 | 활성 플러그인 수 | Step 1 실제 수 vs README 표기 |
| 4 | 죽은 참조 | Step 2에서 뽑은 이름 중 Step 3에서 해석되지 않는 것 |
| 5 | 이름 불일치 | 스킬 디렉터리명과 frontmatter `name`이 다른 것 |
| 6 | 사라진 경로 | 문서가 링크한 파일·디렉터리 경로 중 존재하지 않는 것 |

판정 불가 항목은 비워 두고 그 이유를 적는다. 모든 행을 채우려고 추측하지 않는다.

## Step 5: 결과 보고

```
## /wrap 검증 결과

### 개수 대조
| 항목 | 실제 | 문서 | 판정 |
|------|-----:|-----:|------|
| 스킬 | {n} | {m} | ✅ 일치 / ⚠️ 불일치 |
| 규칙 | {n} | {m} | |
| 활성 플러그인 | {n} | {m} | |

### 죽은 참조
| # | 참조한 파일 | 부르는 이름 | 상태 |
|---|------------|-----------|------|

### 요약
- 불일치 {n}건
- 조치: {수정 내역 또는 "--check 모드이므로 수정 없음"}
```

## Step 6: 문서 수정 (`--check` 없을 때만)

- **개수 불일치** — README의 해당 숫자를 실제 값으로 고친다.
- **죽은 참조** — 부르는 쪽 문서를 고친다. 대체할 자산이 있으면 그 이름으로 바꾸고, 없으면 그 호출 단계를 제거한다. **삭제된 자산을 되살리지 않는다.**
- **이름 불일치** — frontmatter `name`을 디렉터리명에 맞춘다. 반대 방향(디렉터리 이름 변경)은 배포 심링크가 얽혀 있으므로 `.claude/rules/stow-deployment.md`의 순서를 따라 별도로 진행한다.

수정 후 무엇을 왜 고쳤는지 한 줄씩 보고한다.

## 하지 말 것

- 죽은 참조를 발견했다고 그 스킬을 새로 만들지 마라. 보고만 하고 사용자가 판단한다.
- 플러그인 캐시의 버전 포함 경로를 문서에 적지 마라. 플러그인이 갱신되면 깨진다.
- 개수만 맞추고 죽은 참조를 넘어가지 마라. 숫자보다 죽은 참조가 실제 고장이다.
