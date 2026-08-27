# CLAUDE.md · rules 작성과 유지

CLAUDE.md와 `.claude/rules/`를 새로 쓰거나, 항목을 추가·이관·삭제할 때 읽는다.
배치 판단 자체는 SKILL.md의 결정 트리가 우선이다.

## 넣을 것 / 뺄 것 (공식 memory·best-practices 기준)

줄마다 물어라: "이 줄을 지우면 Claude가 실수하나?" 아니라면 삭제한다.

| 넣을 것 | 뺄 것 |
|---|---|
| 추측 불가능한 빌드·테스트·배포 명령 | 코드로 유추 가능한 것 (디렉토리 트리, 의존성 목록, 파일별 설명) |
| 기본과 다른 코드 스타일 | 모델이 이미 아는 표준 언어·프레임워크 관례 |
| 테스트 러너·저장소 규약 | 상세 API 문서 (링크로 대체) |
| 프로젝트 고유 아키텍처 결정·함정 | 자주 바뀌는 정보, 자명한 상투구 ("깨끗한 코드 짜라") |
| 개발 환경 특이사항 (필수 env var 등) | 긴 설명·튜토리얼 |
| 서비스 간 의존 관계 (코드만 봐선 안 보이는 것) | 시크릿·자격증명 (절대 금지 — 환경변수 참조만) |

- 서비스 간 의존은 "프로젝트 고유 아키텍처"에 해당한다: 이 서비스가 무엇을 호출·의존하고,
  무엇이 이 서비스에 의존하며, 바꾸면 깨지는 하위 의존이 무엇인지를 루트에 짧게 적는다.
- 아키텍처 결정의 **"왜"는 ADR**(Architecture Decision Record, 저장소 내
  `doc/arch/adr-NNN.md`)에 남기고, CLAUDE.md에는 한 줄짜리 운영 규칙 + ADR 참조만 둔다.
  예: "라우트 핸들러에 원시 SQL 금지, Knex만 — ADR-014 참조."
- 뒤집힌 결정은 조용히 지우지 말고 ADR에서 "superseded"로 표시해 이력을 남긴다.
  CLAUDE.md 자체는 토큰 예산을 위해 공격적으로 삭제하고, 이력은 ADR·git에 둔다.

## 처음 만들 때

`/init`이 만든 초안을 **그대로 커밋하지 않는다** — 자동 생성본은 대개 코드에서 유추
가능한 내용(효과 없음, 토큰 낭비)이다. 손으로 얇게 시작한다. 5~15줄이면 충분하다:

```
- 패키지 매니저: pnpm (npm 금지)
- 테스트 pnpm test / 빌드 pnpm build
- 커밋 전 pnpm lint 통과
```

나머지는 SKILL.md의 추가 신호가 관측될 때 그것만 붙인다.

## 로딩 동작 — 알아야 배치가 보인다

- 실행한 폴더에서 **위로 올라가며** 경로상의 CLAUDE.md를 모두 세션 시작 시 로드한다.
  하위 폴더의 CLAUDE.md는 그 폴더 파일을 읽을 때만 온디맨드 로드된다.
  → 상위 폴더 파일은 그 아래 전부에 적용되므로, 무관한 프로젝트를 CLAUDE.md 있는 폴더
  아래 두면 지침이 딸려 들어간다. `/context`(상세는 `/context all`)로 확인하고,
  `claudeMdExcludes` 설정으로 특정 경로를 제외할 수 있다.
- 세션 시작 때 한 번 읽으므로 **도중의 편집·git pull은 즉시 반영되지 않는다**. 단
  `/compact`는 루트 CLAUDE.md를 디스크에서 다시 읽어 재주입하므로, `/clear`나 재시작
  없이도 `/compact` 한 번으로 최신본이 반영된다. 작업(PR) 단위로 세션을 새로 시작하면
  팀원이 올린 최신본이 자연히 반영되고 쌓인 컨텍스트도 비워진다.
- `claudeMdExcludes`로 특정 경로를 제외할 수 있으나, **관리 정책(managed) CLAUDE.md는
  제외 대상에서 뺄 수 없다** — 조직이 강제한 규칙이라 개인이 끌 수 없게 설계됨.
- CLAUDE.md는 `@경로` 임포트로 다른 파일을 끌어올 수 있다(재귀 임포트 가능, 최대 깊이
  4단계). 다이어트로 내용을 다른 파일에 옮기고 CLAUDE.md에서 임포트하는 방식도 가능하나,
  이 스킬은 기본적으로 "이관 후 원본에서 삭제, 필요할 때만 스킬로 읽기"를 권한다 — 임포트는
  매 세션 상시 로드라 이관의 취지(온디맨드화)와 안 맞을 수 있다.

## .claude/rules/ — 주제·경로별 분리

- 파일 하나 = 주제 하나 (`testing.md`, `api-design.md`). 하위 폴더까지 재귀 탐색된다.
- frontmatter `paths:` 글롭이 있으면 **매칭 파일을 읽을 때만** 로드된다(토큰 절약).
  없으면 CLAUDE.md와 같은 비용으로 상시 로드 — 절감이 아니라 큰 CLAUDE.md를 주제별로
  관리하는 용도다.
- 개인 `~/.claude/rules/`는 프로젝트 rules보다 먼저 로드되어 **프로젝트가 우선**한다.
- `/compact` 이후에도 path-scoped rules(`paths:` 있는 것)는 그 경로의 파일을 다시 읽을
  때 재로드된다 — 스킬과 달리 rules는 compact를 건너도 살아남는다(공식 memory 문서
  troubleshooting 절에 명시).

## 다이어트 절차 (200줄 초과 시)

1. 각 섹션을 네 갈래로 태깅한다:
   - **UNIVERSAL** — 매 대화 필요, 코드로 유추 불가 → 유지
   - **TASK-SPECIFIC** — 특정 작업에서만 필요 → Skill로 이관
   - **DEEP-DIVE** — 상세 배경 지식 → 스킬의 references/ 또는 링크로
   - **OBSOLETE** — 낡음·모순·이미 잘함 → 삭제
2. 이관한 섹션은 **원본에서 삭제**한다. 옮기고 안 지우면 중복 로드로 오히려 나빠진다.
3. `/doctor`(v2.1.206+)가 코드로 유추 가능한 내용의 트림을 제안해 준다.
4. 중첩된 CLAUDE.md·rules 간 모순을 정리한다 — 모순되면 Claude가 임의로 하나를 고른다.

## 이 파일이 막는 실패 모드

비대화로 지시가 묻힘 · 낡은 지시가 오도(drift) · 틀린 지시의 매 세션 반복(baked-in) ·
중첩 파일 간 모순 · 시크릿 유출. 각각의 방어가 위 절차들이다.

## 출처

- 공식 memory — https://code.claude.com/docs/en/memory (넣을 것/뺄 것, 200줄, 로딩 규칙)
- 공식 best-practices — https://code.claude.com/docs/en/best-practices (권고 vs 강제, 삭제 기준)
- 공식 large-codebases — https://code.claude.com/docs/en/large-codebases (모노레포 계층, 소유)
- ADR — https://adr.github.io/ · Nygard, Documenting Architecture Decisions
- ETH Zurich, Evaluating AGENTS.md — https://arxiv.org/abs/2602.11988 (개요 무용, 지침은 준수됨)
