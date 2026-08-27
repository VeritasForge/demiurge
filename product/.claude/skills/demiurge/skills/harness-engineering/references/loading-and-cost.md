# 로딩 메커니즘 · 우선순위 · 비용

"이걸 추가하면 얼마나 비싼가", "양쪽에 같은 이름이 있으면 누가 이기나"를 판단할 때 읽는다.

## 컨텍스트 3계층

매 요청은 앞부분(캐시되는 prefix)부터 세 계층으로 구성된다:

```
1) 시스템 프롬프트   핵심 지침·도구 정의          하드 지침
2) 프로젝트 컨텍스트 CLAUDE.md, auto memory,      권고(advisory) — 강제하려면 훅
                     paths 없는 rules
3) 대화             메시지·응답·도구 결과         매 턴 늘어남
```

CLAUDE.md는 2계층이다 — "YOU MUST"라고 써도 권고이며, 반드시 지킬 것은 훅·CI·permissions로
강제한다.

## 요소별 로딩 시점 (= 상시 비용 여부)

| 요소 | 언제 로드 | 상시 비용 |
|---|---|---|
| CLAUDE.md (실행 경로+조상) | 세션 시작 | O |
| 하위 디렉토리 CLAUDE.md | 그 폴더 파일 읽을 때 | X |
| rules (`paths:` 있음) | 매칭 파일 읽을 때 | X |
| rules (`paths:` 없음) | 세션 시작 | O |
| Skill | description만 세션 시작, 본문은 호출 시 | description만 |
| Subagent | 위임 시 (별도 컨텍스트) | X |
| MCP | 도구 이름은 세션 시작, 전체 스키마는 필요 시 | 이름만 |
| Hook | 이벤트 발생 시 실행 (출력만 컨텍스트에 들어감) | X |
| settings.json | 컨텍스트에 안 실림 (클라이언트가 강제) | X |

→ 관리 부담과 비용을 줄이는 배치: **상시 로딩(CLAUDE.md)은 최소로, 나머지는 온디맨드로.**

## 컨텍스트를 채우는 최대 요인은 파일 읽기다

공식 context-window 문서: "File reads dominate context usage." CLAUDE.md 다이어트만큼,
구체적 프롬프트로 읽는 파일을 줄이고 조사를 서브에이전트로 격리하는 것이 중요하다.
noise가 쌓일수록 성능이 저하된다(context-rot). 대화 누적은 작업(PR) 단위 `/clear`,
작업 경계에서 `/compact`로 관리한다.

## 캐싱 경제학 — 상시 로딩 비용의 실제 크기

- CLAUDE.md 등 prefix는 프롬프트 캐시에 올라간다. 캐시 읽기는 기본 입력 요율의 약 10%,
  수명은 최대 1시간.
- 캐시가 깨지는 경우: 세션 도중 **모델 변경**(모델별 캐시 분리), **추론 강도(effort) 변경**
  (effort가 캐시 키에 포함), 캐시 수명을 넘긴 휴식. 그래서 모델·effort는 세션 시작에 정하고
  도중에 바꾸지 않는다.
- `/compact`는 대화 계층만 요약하고 시스템 프롬프트 층 캐시를 재사용한다 — 단
  **CLAUDE.md·memory가 세션 시작 이후 불변일 때만** 캐시 히트한다.
- 캐싱은 요금을 낮출 뿐 없애지 않는다. 남는 비용: ① 컨텍스트 윈도우 점유·주의 분산
  (돈이 아니라 성능 비용) ② cache-miss 시 전액 재처리.

## 우선순위 — 같은 이름이 여러 레벨에 있을 때 (공식 features-overview·settings)

| 요소 | 규칙 (높음 → 낮음) |
|---|---|
| CLAUDE.md | 가산 — 모든 레벨이 동시에 로드됨 (오버라이드 없음) |
| rules | project > user (user·project 레벨만 존재) |
| Skills | managed > **user > project** |
| Subagents | managed > CLI > **project > user** > plugin |
| Hooks | 병합 — 등록된 훅 전부 실행 |
| MCP | local > project > user |
| settings.json | managed > CLI > local(settings.local.json) > project(settings.json) > user |
| Plugins | 담긴 구성요소별 규칙. 플러그인 스킬은 네임스페이스(`plugin:skill`)로 충돌 회피 |

주의: Skills(user가 project를 이김)와 Subagents(project가 user를 이김)는 **반대 방향**이다.

## 근거·출처

공식 문서 (code.claude.com/docs/en/):
memory, best-practices, skills, sub-agents, hooks, mcp, plugins, features-overview,
large-codebases, context-window, costs, prompt-caching, settings, monitoring-usage.

연구·1차 자료:
- ETH Zurich/LogicStar, "Evaluating AGENTS.md" (arXiv 2602.11988) — 컨텍스트 파일이 성공률을
  안정적으로 올리지 못함(LLM 생성 −0.5~−2%p, 개발자 작성 +2.4%p·p=0.21), 비용 +20%,
  저장소 개요는 무용, 명시적 지침은 준수됨, 기존 문서가 없는 저장소에서만 도움(+2.7%p).
- Chroma Research, "Context Rot" — 입력이 길수록 성능 저하.
- METR 무작위 대조 실험 (arXiv 2507.09089) — 숙련 개발자가 잘 아는 코드베이스에선 AI 사용이
  19% 느렸는데 본인들은 빠르다고 믿음 → 체감이 아니라 처리량을 측정하라.
- DORA — 문서 품질은 측정 가능한 성능 동인, 효과는 도구보다 주변 시스템(정책·측정)에서 나온다.
