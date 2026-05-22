---
paths:
  - "**/agents/**/*.md"
---

# Agent (Subagent) 작성 규칙

Claude Code subagent를 생성·수정할 때 적용. **skill과 본질적으로 다른 컨셉**이므로 [[skills]] rule과 별도로 관리. 공식 docs: [sub-agents.md](https://code.claude.com/docs/en/sub-agents.md).

## 1. Agent vs Skill 본질적 차이 (가장 중요)

| 항목 | Agent | Skill |
|---|---|---|
| 컨텍스트 | **Fresh context** — 새 window, 부모 대화사 없음 | 부모 세션 context 상속 |
| 호출 방식 | Task tool의 `subagent_type` 또는 자동 위임 | Skill tool의 `skill` 또는 자동 로드 |
| `model` 동작 | **그 subagent 수명 내내 적용** (skill의 "rest of current turn"과 다름) | turn 끝나면 세션 모델 복귀 |
| 자동 호출 차단 | `disable-model-invocation` 같은 필드 **없음**. `.claude/settings.json` permissions.deny로만 차단 | `disable-model-invocation: true` |
| 사용 시점 | context overflow 방지 + 독립 권한·모델 필요 | 재사용 프롬프트, 부모 context 참조 필요 |

### 선택 기준

- **Agent 선택**: 작업이 무겁고 부모 context를 오염시키지 말아야 할 때 (예: 코드 전체 조사, 적대적 검토, 병렬 검증), 다른 권한·모델을 강제해야 할 때
- **Skill 선택**: 부모 대화의 context가 필요할 때, 한두 번의 tool 호출로 끝나는 워크플로우, frontmatter로 model override만 필요할 때

## 2. Frontmatter 필드 (총 16개)

### 필수
| 필드 | 형식 | 비고 |
|---|---|---|
| `name` | kebab-case (lowercase letters/digits/hyphens), 컨벤션상 최대 64자 | 파일명과 달라도 됨 |
| `description` | 자연어 1~2문장 | Claude가 자동 위임 판단에 사용. 트리거 조건 명시 |

### 권장 (대부분의 agent에 명시 권장)
| 필드 | 가능 값 | 비고 |
|---|---|---|
| `tools` | `Read, Grep, Glob` 같은 쉼표 list 또는 YAML list | skill의 `allowed-tools`와 **다른 키 이름**. 생략 시 부모 권한 상속 |
| `model` | `inherit`(기본), `sonnet`, `opus`, `haiku`, full ID | **agent 수명 내내 적용** — 명시 시 부모가 opus여도 그 agent는 명시된 모델로 실행 |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` | 권한 프롬프트 처리 방식. read-only 조사 agent는 `default`, 자동 수정 agent는 `acceptEdits` 권장 |

### 선택
| 필드 | 비고 |
|---|---|
| `disallowedTools` | tools allowlist 적용 후 차단할 도구 |
| `effort` | `low`/`medium`/`high`/`xhigh`/`max` — 세션 설정 상속이 기본 |
| `skills` | 시작 시 프리로드할 skill 목록 (reference가 아닌 content 주입) — fresh context에서도 특정 skill을 무조건 사용해야 할 때 |
| `mcpServers` | inline 정의 또는 이름 참조 — 이 agent만 접근하는 MCP 서버 |
| `hooks` | PreToolUse, PostToolUse, Stop 지원 |
| `memory` | `user`, `project`, `local` — agent별 persistent memory |
| `background` | `true`/`false` — 항상 background로 실행할지 |
| `isolation` | `worktree` — git worktree 격리 실행 |
| `color` | UI 표시색 (red/blue/green/yellow/purple/orange/pink/cyan) |
| `maxTurns` | 정수 — agentic turn 수 제한 |
| `initialPrompt` | 자연어 — 첫 turn 자동 제출 |

## 3. `model` 필드 결정 원칙 (skill과 다름!)

skill의 model 결정 원칙([[skills]] rule 1번 참조)을 그대로 적용하면 **안 됨**. agent는 fresh context에서 시작부터 끝까지 명시된 모델로 실행되므로 trade-off가 다르다.

| 케이스 | 권장 model | 근거 |
|---|---|---|
| 단순 정보 추출 agent (Explore, log-investigator 등) | `haiku` 또는 명시 | 분량이 많아도 작업이 mechanical |
| 균형 잡힌 조사·분석 agent | `inherit` (기본) 또는 `sonnet` | 부모 세션의 품질을 그대로 유지하거나 일관성 위해 sonnet |
| 깊은 추론·전략적 판단 agent (architect 류) | `inherit` 또는 `opus` | 사용자가 opus 세션이면 그대로, 또는 명시적으로 opus |
| 적대적/창의적 검토 (ce-adversarial-document-reviewer 류) | `inherit` 또는 `opus` | 의외성 필요, downgrade 시 손실 큼 |

> **원칙**: 부모 모델보다 작업 자체의 요구가 더 중요. agent는 fresh context라 부모와 분리되므로, 작업 복잡도에 맞춰 명시.

## 4. Plugin Agent 제약

플러그인이 제공하는 agent는 다음 필드가 **무시됨**:
- `hooks`, `mcpServers`, `permissionMode`

이 필드들을 활용해야 한다면 정의를 `product/.claude/agents/`로 복사하여 override.

## 5. 자동 호출 차단

skill처럼 `disable-model-invocation` 필드가 **없다**. agent를 명시 호출만 받게 하려면:

```json
// .claude/settings.json
{
  "permissions": {
    "deny": ["Agent(특정-agent-name)"]
  }
}
```

위 설정으로 Claude가 해당 agent를 자동 위임하지 못하게 차단.

## 6. demiurge 컨벤션

현재 demiurge에는 21개 agent가 `product/.claude/agents/`에 정의. 공통 패턴:
- `architect` 계열 (12개): T2-T3 tier로 도메인별 아키텍처 자문
- `investigation` 계열 (5개): 코드/로그/히스토리 조사 (Explore 패턴)
- `convergence-evaluator`, `contrarian` 등: rl-verify, 적대적 검토 등 메타 워크플로우 지원

신규 agent 추가 시 `product/.claude/agents/{name}.md` 생성 → `just link` → AID 컨벤션({Tier}-{Role}-R{Round}) 따르기.
