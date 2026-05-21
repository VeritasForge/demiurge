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

`references/project-groups.md` 참조. 작업 디렉토리에서 다음 13가지 시그널 파일을 스캔한다.

```bash
# 스캔 대상 파일 (스킬은 Glob/Read 도구로 확인)
- package.json (bin / main / exports 필드 확인)
- pyproject.toml | setup.py
- Cargo.toml
- go.mod
- Gemfile + *.gemspec
- pnpm-workspace.yaml | lerna.json | turbo.json | nx.json
- Dockerfile (+ 웹 프레임워크 시그널: next.config.* / vite.config.* / manage.py 등)
- 기존 README.md의 YAML frontmatter (pipeline_tag)
- dataset_info.json
- 기존 README.md (awesome 헤더 + TOC + 카테고리)
- Chart.yaml + values.yaml
- action.yml
- *.tf + variables.tf
```

탐지 결과는 콘솔에 출력:
```
🔍 자동 탐지 결과
- Group: Package (CLI), Package (Library)  ← package.json + bin + main 모두 존재
- Platform: GitHub, npm
- 현재 README.md: 없음 (신규 모드)
- 언어 옵션: ko (기본)
```

다중 매칭 또는 0건 매칭 시 Phase 2로 진행.

## Phase 2: 그룹·표준·플랫폼·언어·뱃지 확정

자동 탐지 결과 중 모호한 항목만 AskUserQuestion으로 사용자 확인. `references/standards-comparison.md`의 그룹별 추천 표를 1순위로 적용.

### 2-1. 그룹 확정

다중 매칭 시 (예: Package(CLI) + Package(Library) + Application(Monorepo)):
```yaml
AskUserQuestion:
  question: "여러 그룹이 탐지되었습니다. 적용할 그룹을 모두 선택하세요."
  multiSelect: true
  options:
    - "Package (CLI)"
    - "Package (Library)"
    - "Application (Monorepo)"
```

0건 매칭 시:
```yaml
AskUserQuestion:
  question: "시그널 파일이 탐지되지 않았습니다. 프로젝트 유형을 선택하세요."
  multiSelect: false
  options: [Package, Application, AI Asset, Curated List, Metadata-bound]
```

### 2-2. 표준 확정

`--standard` 옵션 미지정 + 자동 추천 후보가 2개 이상이면 AskUserQuestion:
```yaml
AskUserQuestion:
  question: "사용할 README 표준을 선택하세요."
  multiSelect: false
  options:
    - Standard Readme (recommended for Library)
    - Make a README
    - Best-README-Template
    - HF Model Card (recommended for AI Asset)
    - Awesome Manifesto (recommended for Curated List)
  # Ankane은 Ruby Gem 자동 탐지 시에만 옵션에 추가
```

### 2-3. 언어 확정

`--lang` 옵션 미지정 시:
```yaml
AskUserQuestion:
  question: "README 언어를 선택하세요."
  multiSelect: false
  options:
    - ko (한국어, 기본)
    - en (영어)
    - both (한국어 메인 + README.en.md 보조 + 상단 스위처)
```

### 2-4. 뱃지 프리셋 확정

`--badges` 옵션 미지정 시:
```yaml
AskUserQuestion:
  question: "뱃지 프리셋을 선택하세요."
  multiSelect: false
  options:
    - minimal (2개: version, license)
    - standard (4개: build, version, license, coverage) ← 기본
    - extensive (6-7개: contributors/forks/stars/issues/license/version + optional LinkedIn)
```

### 2-5. AskUserQuestion 4 질문 제약

위 4개(그룹/표준/언어/뱃지)는 1 메시지에 동시 질문 가능 (multiSelect 혼합). 추가 질문 필요 시 별도 메시지로 분할.

## Phase 3: 초안 생성

(Task 7에서 채움)

## Phase 4: 인라인 검증

(Task 7에서 채움)

## Phase 5: 통합 호출 (humanize-writing + rl-verify)

(Task 8에서 채움)

## Phase 6: 출력 + 외부 도구 안내

(Task 8에서 채움)
