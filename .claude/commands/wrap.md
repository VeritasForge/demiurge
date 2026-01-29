# /wrap — CLAUDE.md 문서 동기화 검증 및 업데이트

이 커맨드는 CLAUDE.md가 실제 프로젝트 구조(agents, skills, rules, commands)와 일치하는지 검증하고, 불일치 발견 시 CLAUDE.md를 업데이트합니다.

## 모드

- `/wrap` — 분석 + 불일치 감지 + CLAUDE.md 자동 업데이트
- `/wrap --check` — 분석 + 불일치 감지만 (수정 없음)

인자: $ARGUMENTS

---

## 실행 절차

### Step 1: 실제 파일 스캔

다음 경로의 파일을 스캔하여 현재 상태를 수집합니다:

1. **Agents**: `.claude/agents/*.md` 파일 목록 (파일명에서 `.md` 제거 = agent 이름)
2. **Skills**: `.claude/skills/*/SKILL.md` 파일 목록 (상위 디렉터리명 = skill 이름)
3. **Rules**: `.claude/rules/*.md` 파일 목록 (파일명에서 `.md` 제거 = rule 이름). 각 rule 파일의 frontmatter에서 `globs` 필드 추출
4. **Commands**: `.claude/commands/*.md` 파일 목록 (파일명에서 `.md` 제거 = command 이름)
5. **Tier 배정**: `.claude/skills/architect-orchestration/architect-registry.md` 파일에서 각 agent의 `tier` 필드 확인

### Step 2: CLAUDE.md 파싱

CLAUDE.md에서 다음 정보를 추출합니다:

1. **Repository Structure** 섹션의 agent/skill/rule/command 수
2. **Agents** 섹션의 agent 이름 목록
3. **Skills** 섹션의 skill 이름 목록
4. **Rules Auto-Application** 섹션의 rule 이름 및 trigger paths
5. **Agent Tiers** 테이블의 tier 배정
6. **Coverage Matrix** 테이블

### Step 3: 불일치 감지

다음 항목을 비교하여 불일치를 감지합니다:

| # | 검사 항목 | 비교 방법 |
|---|-----------|-----------|
| 1 | Agent 수 | Step 1 agent 파일 수 vs Repository Structure의 "12 architect agent definitions" |
| 2 | Skill 수 | Step 1 skill 파일 수 vs Repository Structure의 "15 quick-reference skill cards" |
| 3 | Rule 수 | Step 1 rule 파일 수 vs Rules 섹션 제목의 "(8개)" |
| 4 | Command 수 | Step 1 command 파일 수 vs Repository Structure의 commands 목록 |
| 5 | Agent 이름 | Step 1 agent 파일명 vs Agents 테이블의 agent 이름 |
| 6 | Skill 이름 | Step 1 skill 디렉터리명 vs Skills 테이블의 skill 이름 |
| 7 | Rule 이름 | Step 1 rule 파일명 vs Rules 테이블의 rule 이름 |
| 8 | Rule globs | 각 rule 파일의 globs vs Rules 테이블의 Trigger Paths |
| 9 | Tier 배정 | architect-registry.md의 tier vs Agent Tiers 테이블 |

### Step 4: 결과 보고

불일치 감지 결과를 다음 형식으로 출력합니다:

```
## /wrap 검증 결과

### 현재 상태
- Agents: {n}개 (CLAUDE.md: {m}개) {✅ | ⚠️ 불일치}
- Skills: {n}개 (CLAUDE.md: {m}개) {✅ | ⚠️ 불일치}
- Rules: {n}개 (CLAUDE.md: {m}개) {✅ | ⚠️ 불일치}
- Commands: {n}개 (CLAUDE.md: {m}개) {✅ | ⚠️ 불일치}

### 불일치 목록
| # | 유형 | 항목 | 실제 | CLAUDE.md | 조치 |
|---|------|------|------|-----------|------|
| 1 | ... | ... | ... | ... | ... |

### 요약
- 총 {n}건의 불일치 감지
- {조치 요약}
```

### Step 5: CLAUDE.md 업데이트 (기본 모드)

`$ARGUMENTS`에 `--check`가 **포함되지 않은** 경우에만 실행합니다.

불일치가 감지되면 CLAUDE.md를 업데이트합니다:

1. **Repository Structure**: 실제 파일 수로 업데이트
2. **Agents 테이블**: 누락된 agent 추가, 삭제된 agent 제거
3. **Skills 테이블**: 누락된 skill 추가, 삭제된 skill 제거
4. **Rules 테이블**: 누락된 rule 추가, 삭제된 rule 제거, glob 업데이트
5. **Agent Tiers**: architect-registry.md 기준으로 tier 업데이트
6. **Version**: patch 버전 bump (예: 3.0 → 3.1)
7. **Changelog**: 변경 내용 추가

새로 추가된 agent/skill의 경우, 해당 파일을 읽어서 역할과 핵심 지식을 파악한 후 테이블에 추가합니다.

### Step 5 (대체): --check 모드

`$ARGUMENTS`에 `--check`가 **포함된** 경우:

- 불일치 목록만 출력하고 종료
- "CLAUDE.md 업데이트가 필요합니다. `/wrap`을 실행하세요." 메시지 출력
- 불일치가 없으면 "CLAUDE.md가 최신 상태입니다." 출력
