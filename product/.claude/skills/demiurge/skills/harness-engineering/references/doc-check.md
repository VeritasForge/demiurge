# 공식 문서 확인 절차

하니스 파일(CLAUDE.md·AGENTS.md·rules·skill·agent·hook·settings)을 작성·수정하기 전에
공식 문서와 기존 기준을 대조하는 절차다. 학습 데이터와 이 스킬의 references는 낡을 수
있으므로, 바꾸는 규칙과 관련된 공식 문서를 확인한 뒤에 확신을 갖고 반영한다.

## 언제 확인하는가

- **작업 하나당 한 번**: 사용자 요청 하나에 해당하는 수정 묶음의 시작에서 확인한다.
  파일마다, Edit마다, 같은 작업 안의 후속 문구 수정마다 다시 확인하지 않는다.
- **관련 문서만**: 아래 표에서 바꾸는 대상에 해당하는 문서만 본다.
- **확인하지 않는 경우**: 오타·문법처럼 동작이 바뀌지 않는 수정, 같은 세션에서 이미 확인한
  페이지(결과 재사용), 일반 소프트웨어 공학 원칙(ADR, docs-as-code 등 잘 안 바뀌는 것).
- **추가로 확인하는 경우**: 대조에서 충돌이 나온 부분만 다시 확인한다.

| 바꾸는 것 | Claude 쪽 문서 | Codex 쪽 문서 |
|---|---|---|
| CLAUDE.md·AGENTS.md 행동 규칙 | memory, best-practices, 프롬프팅 best practices | AGENTS.md 문서, Codex best practices, 모델 프롬프팅 가이드 |
| rules | memory의 rules 절 | 해당 없음 |
| skill | skills | Codex `skill-creator` 스킬 |
| subagent | sub-agents | 해당 없음 |
| hook·settings | hooks, settings | `codex-self-knowledge.md`의 배치 기준, config 문서 |

## 확인 도구

| 대상 | 기본 도구 | 대체 수단 |
|---|---|---|
| Claude 쪽 | Agent 도구 `subagent_type="claude-code-guide"`. 확인할 문서 URL을 직접 짚어 전달한다 | 아래 "Claude 쪽 대체 페르소나" |
| Codex 쪽 | codex 플러그인으로 Codex를 **읽기 전용** 실행하고 요청에 `$openai-docs`를 명시한다 | 아래 "Codex 쪽 대체 수단" |

URL을 짚는 이유: URL 없이 "확인해 줘"라고만 시키면 에이전트가 문서 지도에서 다른 페이지를
골라 열고 "확인 불가"라고 답할 수 있다(2026-08-27 실측: URL 없이 물은 4개 항목이 모두
"확인 불가"였으나, URL을 짚어 다시 물으니 전부 원문 그대로 확인됨). "확인 불가"는 "없다"가
아니라 "이번에 연 페이지에서 못 찾았다"일 수 있다.

Codex 쪽 실행 예시(플러그인 버전 폴더는 설치본에 맞춘다):

```bash
node ~/.claude/plugins/cache/openai-codex/codex/<버전>/scripts/codex-companion.mjs task --fresh \
  "\$openai-docs 스킬을 사용해서 답하라. 질문: ... 반드시 보고하라: 읽은 스킬 파일 절대 경로, 열어 본 공식 URL, 각 주장의 원문 인용(영어 그대로). 공식 자료에 없으면 '언급 없음'이라고 써라. 파일은 수정하지 마라."
```

- `--write`를 붙이지 않는다. 붙이지 않으면 읽기 전용 샌드박스로 실행된다.
- `/codex:rescue` 명령은 기본으로 `--write`를 붙이므로, 쓰려면 요청에 읽기 전용을 명시한다.
- 읽은 스킬 파일 경로를 보고하게 해야 Codex가 스킬을 실제로 썼는지 기억으로 답했는지 구분된다.

## 실패 처리

재시도는 첫 시도 실패 후 **2회까지**다. 대체 수단은 **1회만** 실행하고, 대체 수단도 실패하면
판정 불가로 끝낸다.

| 실패 유형 | 판별 | 처리 |
|---|---|---|
| A. 도구 없음 | Agent 도구가 `Agent type 'claude-code-guide' not found` 오류를 낸다(2026-11-24 실측, Claude Code v2.1.331). codex 쪽은 플러그인 스크립트가 없거나 Codex 미설치·미인증을 보고한다 | **반드시 경고**한 뒤 대체 수단 1회 |
| B. 실행 오류 | 타임아웃·네트워크 오류 등으로 결과가 오지 않는다 | 같은 요청으로 2회 재시도 → 모두 실패하면 대체 수단 1회. 대체 결과를 썼다고 알린다 |
| C. 확인 불가 | 결과는 왔지만 "확인 불가"·"찾지 못함"이다 | 재시도 1: 지난번에 연 페이지를 묻고 맞는 URL을 지정한다. 재시도 2: 다른 후보 URL이나 문서 지도를 지정한다. 그래도 없으면 "공식 문서에서 확인 못 함"으로 표시하고 판정 불가로 둔다. 대체 수단은 같은 문서를 읽으므로 쓰지 않는다 |

A의 경고 문구(도구 이름은 실제로 사라진 것으로 바꾼다):

```
⚠️ claude-code-guide 에이전트를 찾을 수 없습니다. Claude Code 업데이트로 사라졌거나 이름이
바뀌었을 수 있습니다. 이 에이전트를 참조하는 스킬·에이전트를 수정해야 합니다:
<demiurge 레포의 product/·.claude/에서 grep -rn "claude-code-guide" 한 결과>
이번 확인은 대체 페르소나로 진행합니다.
```

B가 자주 반복되면 일시 오류가 아니라 에이전트 정의가 망가진 상태일 수 있다. 이때는 A처럼
다룬다.

## Claude 쪽 대체 페르소나

Agent 도구 `subagent_type="general-purpose"`에 아래 지시문과 확인할 질문·URL을 붙여 실행한다.
claude-code-guide의 조회 방식(문서 지도 → 페이지 선택 → 원문 인용)을 따르게 하되,
general-purpose에는 "기억으로 답하지 말라"는 규칙이 없으므로 명시한다.

```
당신은 Claude 공식 문서 확인 담당이다. 질문 영역에 맞는 문서 지도를 먼저 가져와서
관련 페이지를 고른 뒤, 그 페이지를 직접 가져와 답한다.
- Claude Code·Agent SDK: https://code.claude.com/docs/en/claude_code_docs_map.md
- Claude API·프롬프팅: https://platform.claude.com/llms.txt
- Claude Tag(Slack): https://claude.com/docs/llms.txt
URL이 지정된 질문은 그 페이지부터 가져온다.
규칙:
- 모든 주장에 원문 인용(영어 그대로)과 URL을 붙인다. 인용할 수 없는 주장은 쓰지 않는다.
- 문서에서 찾지 못하면 "언급 없음"이라고 쓰고, 열어 본 페이지 URL을 함께 적는다.
- 문서에 접근하지 못하면 그 사실을 밝힌다. 학습 데이터(기억)로 답을 채우지 않는다.
```

## Codex 쪽 대체 수단

Codex를 쓸 수 없으면 Codex가 설치한 참조 파일을 직접 읽고, 공식 웹 문서를 WebFetch로 연다.

- `~/.codex/skills/.system/openai-docs/SKILL.md`
- `~/.codex/skills/.system/openai-docs/references/codex-self-knowledge.md` — 설정을 어디에 둘지 고르는 기준
- `~/.codex/skills/.system/openai-docs/references/prompting-guide.md` — 모델 프롬프팅 권고의
  **로컬 사본**. 파일 첫머리에 적힌 웹 정본 URL을 먼저 연다
- AGENTS.md 문서: https://learn.chatgpt.com/docs/agent-configuration/agents-md
- Codex best practices: https://learn.chatgpt.com/guides/best-practices

`.system` 폴더는 Codex가 관리하므로 읽기만 하고 고치지 않는다.

## 대조와 반영

1. 확인 결과를 이 스킬, CLAUDE.md, AGENTS.md, rules의 기존 기준과 대조한다.
   공식 문서가 정한 **동작·제약**과 선택 가능한 **작성 권고**를 구분한다. 표현 차이를
   충돌로 취급하지 않기 위해서다.
2. **일치하면** 그대로 반영한다.
3. **충돌하면** 반영을 멈추고 차이를 사용자에게 보여 검토한다. 결론에 따라 반영한다.
   - 기존 기준이 낡았거나 틀림 → 기준 문서를 고치고, references라면 최종 검증일을 갱신한다.
   - 공식 권고와 다르지만 의도적으로 유지함 → 기준은 두고 다르게 유지하는 이유를 그 옆에
     적는다. 적지 않으면 다음 확인 때 같은 차이가 다시 충돌로 올라온다.

## 출처

- Claude Code 서브에이전트 목록(claude-code-guide 포함) — https://code.claude.com/docs/en/sub-agents
- claude-code-guide의 문서 지도와 조회 순서 — Claude Code v2.1.331 실행 파일에 포함된 에이전트 지시문(2026-11-24 확인)
- Codex AGENTS.md — https://learn.chatgpt.com/docs/agent-configuration/agents-md
- Codex `openai-docs` 시스템 스킬 — `~/.codex/skills/.system/openai-docs/` (codex-cli 0.171.0)
