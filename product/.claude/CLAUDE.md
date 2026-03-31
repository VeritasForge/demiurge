# 응답 가이드라인

답변 시 반드시 다음 원칙을 준수할 것:

1. 항상 맥락을 고려할 것
2. 다양한 관점에서 바라볼 것
3. 나의 성장을 고려할 것
4. 단계별로 설명할 것
5. 예를 들어 설명할 것
6. 대안이나 추가로 확인해야 하는 부분도 제시할 것
7. 내가 12살이라고 가정하고, 현실 세계의 사물에 비유해서 설명할 것
8. 답변을 도출해내는 논리와 과정을 보여줄 것. 왜 이러한 답변인지 기준을 제시할 것
9. 이해가 안 되는 부분이 있으면 반드시 물어볼 것
10. Step by step으로 sequential thinking을 할 것 (sequentialthinking MCP 도구 활용)

# 플랜 작성 템플릿

플랜을 작성할 때 (plan mode, superpowers, compound-engineering, ouroboros 등 도구 무관) 반드시 아래 필수 섹션을 포함할 것. 기존 스킬의 템플릿 구조는 유지하되, 아래 섹션이 누락되지 않도록 보완할 것.

## 필수 섹션 (반드시 포함, 내용을 채울 수 없으면 AskUserQuestion으로 사용자에게 질문할 것)

### 1. 완료조건 (Completion Criteria)
- 측정 가능한 성공 기준
- 검증 명령어 또는 테스트 포함

### 2. 금지사항 (Don'ts)
- 명시적으로 하지 말아야 할 것을 핵심 위주로 간결하게
- "~대신 ~해라" 대조 형식으로 작성

### 3. 고려사항 (Considerations)
- 엣지 케이스, 성능, 보안, 아키텍처 관련 사항

### 4. 제약사항 (Constraints)
- 기술적 제한, 외부 의존성, 리소스 제약

### 5. 스킬 검색 (Skill Discovery)
- Memory에서 이전 매핑 테이블 확인 (있으면 참고, 없으면 fresh 검색)
- ~/.claude 하위 skills, agents, 전역 plugins 실제 검색
- Memory 매핑과 현재 검색 결과 교차 비교:
  - Memory에 있고 + 현재 존재 → 채택
  - Memory에 있고 + 현재 없음 → 제외 + Memory에서 삭제
  - Memory에 없고 + 새로 발견 → 후보로 추가
- 스킬 매핑 테이블 작성: 각 스킬/agent의 용도와 적용 Task를 테이블로 정리
- 플랜 완료 후 AskUserQuestion으로 사용자에게 매핑 테이블 Memory 저장 여부 확인

### 6. Task List
- 작업 순서대로 나열
- 각 Task에 반드시 포함:
  - **완료조건**: 이 Task의 측정 가능한 성공 기준
  - **스킬 매핑**: 5번 매핑 테이블에서 이 Task에 해당하는 스킬/agent 참조
  - 금지사항, 고려사항, 제약사항은 필요시 추가

## 실행 및 검증 프로세스

### Task 등록 (필수)
플랜 실행 시작 전에 반드시 플랜의 Task List 전체를 TaskCreate로 등록할 것. 플랜 문서만으로 실행하지 말 것.

### Task 실행 순서
Task는 반드시 순차 실행한다 (병렬 실행 금지). /rl이 .claude/ralph-loop.local.md 단일 상태 파일을 사용하므로 병렬 실행 시 파일 충돌이 발생한다.

### Task별 검증
각 Task 완료 후 /rl을 실행하여 검증한다.
- /rl 프롬프트에는 해당 Task의 완료조건을 포함할 것
- /rl 실행 중 발견한 새로운 사실이나 오류가 있으면 해당 Task를 수정하여 재수행

### 플랜 최종 검증
모든 Task 완료 후 /rl을 실행하여 플랜 단위 완료조건을 최종 검증한다.
- /rl 프롬프트에 플랜의 완료조건 항목을 모두 포함할 것
- 미충족 항목 발견 시:
  1. 미충족 원인을 분석
  2. 보완 Task를 Task List 끝에 추가 (6번 Task 규격 동일 적용: 완료조건, 스킬 매핑 필수)
  3. 보완 Task 수행 → /rl로 Task별 검증
  4. 플랜 완료조건 재검증

## 선택 섹션 (필요시 추가)
- 기타 플랜 맥락에 필요한 섹션 자유 추가

## 플랜 검증 (2단계)

### Step 1: document-review (문서 품질)
플랜 작성 완료 후 compound-engineering:document-review 스킬을 실행하여 명확성, 완전성, 구체성, YAGNI를 검증할 것.

### Step 2: rl-verify (기술적 정확성)
document-review 완료 후 /rl-verify를 실행하여 기술적 사실 여부, 실현 가능성, 기술적 타당성을 검증할 것. 검증 결과를 플랜에 반영하여 최종 플랜을 출력할 것.

# 스킬/에이전트 개발 규칙
- 스킬/에이전트 파일은 `product/.claude/skills/` 또는 `product/.claude/agents/` 하위에 생성한다 (`~/.claude/` 직접 생성 금지)
- 파일 생성 후 `just link`를 실행하여 stow로 전역 심링크를 배포한다
- subagent에게 스킬 생성을 위임할 때도 이 경로를 명시적으로 전달한다

# Skills/Agents 호출 규칙
- Claude Code 내부 동작/기능/설정 확인 시 → claude-code-guide 에이전트 사용
- 여러 출처를 교차 검증하는 조사가 필요한 경우 → /deep-research 스킬 사용 (WebSearch/WebFetch를 직접 여러 번 쓰지 말고)
- 이력서/문서에서 AI 톤을 제거할 때 → /humanize-writing 스킬 사용
- 새 스킬이나 에이전트를 생성할 때 → /superpowers:writing-skills 스킬 사용
- 구현 전 아이디어를 정리하고 설계할 때 → /superpowers:brainstorming 스킬 사용
- 플랜이나 문서의 품질을 검증할 때 → /compound-engineering:document-review 스킬 사용
- AI 협업 세션 회고/교훈 추출 시 → /retrospective 스킬 사용
