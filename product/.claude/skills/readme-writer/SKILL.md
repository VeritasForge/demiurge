---
name: readme-writer
description: README.md 파일을 생성하거나 업데이트하는 스킬. 프로젝트 유형(Package/Application/AI Asset/Curated/Metadata-bound)을 자동 탐지하고, 한국어 기본으로 README를 작성한다. 기존 README가 있으면 README.v2.md로 비파괴 출력. 생성 후 humanize-writing + rl-verify를 자동 호출한다. /readme-writer로 사용자 호출, 또는 신규/기존 OSS 저장소에서 README 작성·갱신 요청 시 사용.
---

# README Writer

Claude Code 작업 디렉토리의 README.md를 자동 생성하거나 갱신한다.

## Phase 0: 인자 파싱 + 기존 README 감지

옵션 파싱:
- `--lang ko|en|both` (기본: ko)
- `--standard <name>` (Standard Readme | Make | Best-README | Ankane | HF | Awesome)
- `--badges minimal|standard|extensive` (기본: standard)
- `--force` (기존 README.md 덮어쓰기, 위험 명시)

기존 `README.md` 존재 여부 확인:
- 존재 → 비파괴 모드 (출력: `README.v2.md`)
- 부재 → 신규 모드 (출력: `README.md`)
- `--force` 지정 시 → 직접 덮어쓰기 (사용자 확인 후)

## Phase 1: 자동 탐지

(Task 6에서 채움)

## Phase 2: 그룹·표준·플랫폼·언어·뱃지 확정

(Task 6에서 채움)

## Phase 3: 초안 생성

(Task 7에서 채움)

## Phase 4: 인라인 검증

(Task 7에서 채움)

## Phase 5: 통합 호출 (humanize-writing + rl-verify)

(Task 8에서 채움)

## Phase 6: 출력 + 외부 도구 안내

(Task 8에서 채움)
