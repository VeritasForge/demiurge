---
paths:
  - "**/SKILL.md"
  - "**/skills/**/*.md"
---

# Skill / Command 작성 규칙

Claude Code skill 또는 command를 생성·수정할 때 적용. 공식 입장: "Custom commands have been merged into skills" — command와 skill은 동일한 frontmatter/동작을 공유. agent는 별개 컨셉이므로 agents 규칙(`rules/agents.md`)을 참조.

공식 docs 근거: [custom-skills.md](https://code.claude.com/docs/en/custom-skills.md), [model-config.md](https://code.claude.com/docs/en/model-config.md).

## 1. `model` frontmatter 결정 원칙

### 공식 동작
> "`model`: ... The override applies for **the rest of the current turn** and is not saved to settings; the session model resumes on your next prompt."

즉 skill이 활성화되면, **skill body가 끝난 후 같은 turn 안에서 일어나는 모든 후속 작업**(첫 iteration, chain된 skill·tool 호출, 추가 메시지)이 override된 모델로 실행된다. 다음 사용자 입력(새 turn)부터 세션 모델로 자동 복귀.

### 결정 원칙

> **Rule**: skill이 곧 turn 전체 작업이면 model 명시. skill이 사용자 후속 작업의 진입점에 불과하면 model 미명시(세션 모델 상속).

| 패턴 | model 명시? | 예시 |
|---|---|---|
| skill 본문에서 시작→종료까지 완결되는 작업 | ✅ 명시 가능 | `/commit` (git status→메시지→commit→push 4단계가 한 turn 안에서 끝남) |
| skill body 직후 같은 turn에서 사용자 task가 시작되는 작업 | ❌ 미명시 (세션 모델 상속) | `/rl` (skill 후 첫 iteration 시작), `/rl-fresh` (요구사항 분해 → 디스패처) |
| 같은 turn 안에서 다른 skill을 chain 호출하는 작업 | ❌ 미명시 | `/tdd-lfg` (workflows:plan → writing-plans → subagent-driven-development) |

### 위반 시 결과 (실측 사례)
사용자가 opus 세션에서 `/rl "어려운 task"`를 호출할 때, skill frontmatter에 `model: claude-sonnet-4-6`이 있으면 **첫 iteration이 sonnet으로 silently downgrade**된다. 첫 iteration은 보통 방향·설계·테스트 골격 결정이 일어나는 시점이라 회복이 어렵다.

### 비대칭이 의도된 경우 주석 명시
한 그룹의 skill 중 일부만 model을 명시하면 미래 개발자가 "왜 일관성이 없지?"라고 잘못된 통일 리팩토링을 시도할 수 있다. frontmatter 직후 `<!-- model intentionally omitted — see ... -->` 또는 `<!-- model: X — turn 전체가 ... 작업이므로 명시 -->` 같은 한 줄 주석으로 결정 근거를 영구 기록한다.

## 2. Frontmatter 표준 (Claude Code spec)

| 필드 | 제약 | 비고 |
|---|---|---|
| `name` | lowercase letters/digits/hyphens만, 최대 64자 | underscore 금지 (`new_rl` ❌ → `rl-fresh` ✅) |
| `description` | `description` + `when_to_use` 합쳐 최대 1536자 (listing에서 truncate) | "Use when..." 트리거 명시, workflow 요약 금지 |
| `allowed-tools` | 본문에서 실제 사용하는 tool만 | grep으로 본문 vs frontmatter 일치 검증 |
| `argument-hint` | 인자 받는 skill만 | 예: `"<prompt> [--max-iterations N]"` |
| `disable-model-invocation` | `true` 시 사용자 명시 호출만 가능 (자동 미감지) | `/tdd-lfg` 같이 의도 명확한 명령형에 적합 (/commit은 frontmatter `model` 고정으로 충분하여 미사용) |
| `model` | 위 1번 원칙대로 | Anthropic API: `claude-haiku-4-5`, `claude-sonnet-4-6`, `claude-opus-4-7` 형식 |

## 3. Skill takes precedence over command

공식 docs: skill과 command가 같은 이름이면 **skill takes precedence**. 마이그레이션·롤백·실험 중 둘이 공존해도 호출은 skill로 라우팅됨. 롤백 시 신규 skill 디렉토리만 삭제하면 기존 command로 복귀 (배포·심링크 재적용 절차는 CLAUDE.md '스킬/에이전트 개발 규칙' 참조 — demiurge 레포에선 `stow-deployment` 규칙이 상세 주 출처).

## 4. Description 작성 객관 기준

- 첫 문장에 "use when..." 또는 "~할 때 사용" 형태 포함
- 구체적 사용 상황/증상 명시 (예: "변경사항을 git에 커밋할 때", "Ralph Loop가 필요할 때")
- 절차 나열(Step 1/2/3) 금지 — Claude가 본문 안 읽고 description만 따라가는 함정 발생
- 200자 이내 권장 (listing 가독성)

## 5. Provider 호환성

`claude-haiku-4-5`, `claude-sonnet-4-6` 등 full model ID는 Anthropic API 정식 식별자. Bedrock/Vertex/Foundry에서는 alias(`haiku`, `sonnet`)가 다른 버전으로 resolve될 수 있으므로 그 환경에서 재사용 시 ID 재확인 필요.
