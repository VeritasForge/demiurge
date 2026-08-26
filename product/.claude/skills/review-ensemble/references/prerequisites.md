# 필요 조건 — 별도 설치가 필요한 것

SKILL.md 본문에서 읽는 게 아니라, **엔진이 플러그인 부재로 실패했을 때** 또는 **사용자가 설치 여부를 물었을 때만** 읽는다. 매 실행마다 필요한 정보가 아니므로 본문에는 안 둔다(SKILL.md의 인트로에 이 파일로 가는 포인터만 있다).

Claude Code에 기본 내장된 게 아니라 **별도 설치해야 하는 것**이 세 가지 있다. 설치 안 해도 리뷰 자체가 죽지는 않는다 — Phase 4의 "엔진 하나가 실패해도 나머지로 계속한다" 규칙대로 그 관점만 빠진 채 나머지로 진행된다.

| 대상 | 필요한 이유 | 설치 명령 | 설치 안 하면 |
|---|---|---|---|
| `compound-engineering` 플러그인 | E1(주력 엔진) | `/plugin marketplace add EveryInc/compound-engineering-plugin`<br>`/plugin install compound-engineering@compound-engineering-plugin` | E1 전체가 빠진다 — 리뷰 품질에 가장 큰 영향. `quick` 프로파일 외엔 사실상 필수 |
| `pr-review-toolkit` 플러그인 | E3(전문 렌즈 4종, `deep` 프로파일 전용) | `/plugin marketplace add anthropics/claude-plugins-official`<br>`/plugin install pr-review-toolkit@claude-plugins-official` | `standard` 이하 프로파일은 애초에 영향 없음. `deep`을 써도 E3만 빠지고 나머지는 정상 진행 |
| Codex CLI(`codex` 명령) | Phase 6 표2(반박 검증 두 번째 표 — 별도 모델 패밀리로 독립성 확보) | `brew install codex` 등(OpenAI 공식 설치 방법 참고, 별도 로그인 필요) | 표2가 자동으로 Claude(sonnet) 폴백으로 대체된다 — Phase 6 자체가 꺼지지는 않지만 두 표의 독립성이 약해진다는 사실을 리포트에 남긴다 |

플러그인 설치 후 `/reload-plugins`가 필요할 수 있다. 이미 설치돼 있는지는 `/plugin list --enabled`로 확인한다.

**설치가 필요 없는 것들** (혼동하기 쉬워 명시한다):
- **E2(내장 `code-review`)** — Claude Code 자체에 내장돼 있다. 아무것도 안 해도 된다
- **E4(레포 로컬 워크플로 렌즈)** — 사용자가 설치하는 게 아니라 **리뷰 대상 레포 안에** `.claude/skills/github-actions-review/`가 있을 때만 켜지는 조건부 스킬이다. 없으면 조용히 건너뛴다
- **Phase 6 표1(반박 검증 페르소나)** — `[counter-reviewer.md](../counter-reviewer.md)`가 review-ensemble 자기 디렉터리 안에 함께 있어 별도 설치·외부 의존성이 없다

## 근거

마켓플레이스 이름·레포 경로는 `~/.claude/plugins/known_marketplaces.json`·`installed_plugins.json`에서 실제 값을 확인했다(추측 아님) — `compound-engineering@compound-engineering-plugin` ← `EveryInc/compound-engineering-plugin`, `pr-review-toolkit@claude-plugins-official` ← `anthropics/claude-plugins-official`. Codex는 `brew list --formula`로 이 시스템의 실제 설치 방식을 확인했다.
