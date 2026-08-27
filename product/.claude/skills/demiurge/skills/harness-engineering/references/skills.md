# Skill 설계

스킬을 새로 만들거나 고칠 때 읽는다. 만드는 절차는 skill-creator·writing-skills를 따르고,
여기서는 **무엇을 스킬로 만들지, 어떻게 트리거되게 하고, 어떤 실행 컨텍스트를 고를지**를 다룬다.

## 스킬로 만들 것인가 — 먼저 판별

스킬은 "여러 단계 절차" 또는 "가끔만 필요한 도메인 지식"의 자리다 (SKILL.md 결정 트리).

- 같은 절차를 **반복**하게 됐을 때 만든다. 미리 만들지 않는다.
- 한 줄 사실("pnpm 사용")은 스킬이 아니라 CLAUDE.md다.
- 매번 반드시 강제할 것은 스킬이 아니라 훅이다 — 스킬 지시는 권고일 뿐이다.
- 같은 입력에 항상 같은 출력이 나와야 하는 일(변환·검증·집계)은 산문 지시가 아니라
  `scripts/`의 코드로 만든다. Claude가 번들 스크립트를 실행할 수 있다.

## Progressive disclosure — 3단 로딩 구조

| 층 | 내용 | 로드 시점 |
|---|---|---|
| 1 | name + description | 항상 (매 요청 컨텍스트에 있음) |
| 2 | SKILL.md 본문 | 스킬 호출 시 (500줄 이하 권장) |
| 3 | references/·scripts/·assets/ | 본문이 지시할 때만 |

description은 항상 컨텍스트에 실리므로 스킬 개수 자체가 상시 비용이다. 본문이 길어지면
작업별 상세를 references/로 내리고, 본문에는 "언제 어느 파일을 읽어라"는 포인터를 남긴다.

## description — 자동 호출을 좌우하는 단 하나의 신호

Claude는 description만 보고 스킬 사용 여부를 정한다. 본문이 아무리 좋아도 description이
약하면 안 불린다.

- 첫 문장에 "~할 때 사용(Use when...)"으로 트리거 상황을 명시한다.
- 구체적 사용 상황·증상·사용자 표현을 나열한다. 스킬을 직접 지명하지 않는 요청
  ("이 문서 정리해줘")까지 잡으려면 그런 표현을 description에 미리 넣는다.
- 절차 요약(Step 1/2/3)은 넣지 않는다 — Claude가 본문을 안 읽고 description만 따라가는
  함정이 생긴다.
- 현재 모델은 스킬을 덜 쓰는(undertrigger) 경향이 있으므로 다소 강하게("반드시 참조")
  쓰는 편이 낫다. 단 과대 트리거로 무관한 작업에 끼어들면 near-miss 상황을 description에
  명시해 배제한다.

## Frontmatter 핵심 필드

| 필드 | 언제 쓰나 |
|---|---|
| `disable-model-invocation: true` | 부작용 있는 워크플로(커밋·배포·메시지 발송)를 사용자 수동 호출로만 제한. **다른 스킬·Claude가 못 부르게 되므로 참조형 스킬에는 쓰지 않는다** |
| `user-invocable: false` | 사용자 직접 호출을 막고 Claude 자동 호출만 허용 (내부 참조 전용 지식) |
| `context: fork` | 아래 "실행 컨텍스트" 참조 |
| `model` | 스킬이 turn 전체 작업일 때만 명시. 후속 작업의 진입점이면 미명시(세션 모델 상속) — 명시하면 이후 작업이 그 모델로 조용히 다운그레이드될 수 있다 |
| `allowed-tools` | 본문에서 실제 쓰는 도구만 |

## 실행 컨텍스트 — 기본은 인라인이다

**스킬 본문은 기본적으로 현재 대화에 로드되어 메인 컨텍스트 윈도우를 차지한다**
(공식 features-overview: "Adds to your main window"). 격리가 기본이 아니다.

- `context: fork`를 명시하면 서브에이전트(격리 컨텍스트)에서 실행된다. 이때 스킬 본문이
  서브에이전트를 구동하는 프롬프트가 되고, **앞의 대화 이력은 넘어가지 않는다.**
- 선택 기준: 결과 요약만 필요한 조사·검증형 작업은 fork로 메인 컨텍스트를 아끼고,
  대화 맥락 위에서 이어 가는 작업(코드 수정, 문서 작성)은 인라인으로 둔다.

## 스킬 간 조합 — 세 가지 방식

| 방식 | 어떻게 | 쓰임새 |
|---|---|---|
| ① 호출 | 본문에 "이 단계에서 X 스킬을 호출하라"고 지시 → Claude가 Skill 도구로 실행 | 라우터(상황 판별 후 선택 호출), 체이닝(작성 후 검증 스킬 호출) |
| ② 참조 | 다른 스킬의 references/ 파일을 읽으라고 지시 (`@path` 임포트 또는 Read) | 실행 없이 지식만 재사용. 경로가 머신마다 실존해야 하므로 팀 배포 시 깨지기 쉬움 |
| ③ 프리로드 | 서브에이전트 정의의 `skills:` 필드에 나열 → 실행 시 본문이 통째로 미리 로드 | 커스텀 에이전트에 도메인 지식 주입 |

제약: `disable-model-invocation: true`인 스킬은 ①로 부를 수 없다(사용자 수동 호출만).
라우터·체이닝 패턴 자체는 공식 best-practice로 문서화되지 않은 관행 영역이므로,
호출 대상 스킬 이름을 본문에 명시하고 실제로 불리는지 검증한다.

## 운영

- 사용 추적: `OTEL_LOG_TOOL_DETAILS=1`을 켜면 `tool_result` 이벤트에 `skill_name`,
  비용 카운터에 `skill.name` 속성이 기록된다. 오래 안 쓰인 스킬은 통합·폐기한다.
- 자동 호출이 잘 안 되면: description을 트리거 상황 중심으로 다듬는 것이 1순위.
  CLAUDE.md에 "상황 → 스킬" 매핑 표를 두는 방법도 있으나 동기화 부담이 생긴다.
- 스킬도 하니스 파일이다 — 코드처럼 PR 리뷰, 관측 기반 개선, 낡으면 삭제.

## 출처

- 공식 skills — https://code.claude.com/docs/en/skills (frontmatter, fork, scripts)
- 공식 features-overview — https://code.claude.com/docs/en/features-overview (로딩 층, 조합, 인라인 기본)
- 공식 sub-agents — https://code.claude.com/docs/en/sub-agents (skills 프리로드, Skill 도구)
- 공식 monitoring-usage — https://code.claude.com/docs/en/monitoring-usage (OTEL_LOG_TOOL_DETAILS, skill.name)
