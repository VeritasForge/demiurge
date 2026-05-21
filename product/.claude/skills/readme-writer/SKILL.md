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

3-Layer 구조로 README 본문을 생성한다.

### Layer 1: 공통 골격 (모든 그룹 공통)

```
Title → Description → Badges → Installation → Usage → Contributing → License
```

각 섹션 작성 가이드:
- **Title**: 자동 탐지된 프로젝트명 (package.json의 `name`, Cargo.toml의 `[package].name` 등). 모호하면 사용자에게 질문.
- **Description**: 한 줄 핵심 가치. 120자 미만 (Standard Readme 표준). 모호한 표현("A tool for...") 금지 (anti-patterns.md #1).
- **Badges**: Phase 2-4에서 선택한 프리셋에 따라 Shields.io URL 생성.
- **Installation**: 자동 탐지된 패키지 매니저로 명령 작성 (npm install / pip install / cargo add 등).
- **Usage**: 실제 코드 예제 (foo/bar/baz 금지, anti-patterns.md #4).
- **Contributing**: 짧으면 인라인, 길면 `CONTRIBUTING.md` 링크.
- **License**: 자동 탐지된 LICENSE 파일과 일치 (없으면 사용자에게 질문).

### Layer 2: 그룹별 추가 섹션

`references/project-groups.md`의 각 그룹 정의 참조.

| 그룹 | 추가 섹션 |
|------|----------|
| Package (Library) | API |
| Package (CLI) | Synopsis, Options, Exit Status, Environment Variables |
| Application (Web) | Demo, Screenshots, Tech Stack, Architecture |
| Application (Monorepo) | Packages Table (자식 패키지 목록 + 링크) |
| AI Asset | Intended Use, Limitations/Bias, Training Data, Evaluation |
| Curated List | Contents (TOC), Categories (통일된 항목 형식) |
| Metadata-bound | Configuration 표 (values.yaml/action.yml/*.tf 동기화) |

### Layer 3: 플랫폼 메타데이터

`references/platform-metadata.md` 참조.

- GitHub: 500 KiB 경고 체크
- npm: package.json의 description/keywords 활용
- PyPI: long_description_content_type 안내 (Phase 6에서)
- Cargo: lib.rs doc-comment sync 패턴 안내 (Phase 6에서)
- HF: YAML frontmatter 자동 채움 (AI Asset 그룹 전용)

### 언어 처리

- `--lang ko` (기본): README.md 한국어로 작성
- `--lang en`: README.md 영어로 작성
- `--lang both`:
  1. README.md 한국어로 작성
  2. README.en.md 영어로 작성 (섹션 구조 동일, 제목·본문만 번역)
  3. 두 파일 상단에 스위처 자동 삽입:
     ```markdown
     > [한국어](README.md) | [English](README.en.md)
     ```

## Phase 4: 인라인 검증

`references/anti-patterns.md` 참조. 4종 인라인 검증 + 자동 수정.

### 4-1. 섹션 순서 검증

선택한 표준(`references/standards-comparison.md`)의 순서와 일치하는지 LLM이 직접 확인. 위반 시 재배치.

예: Standard Readme 선택 시 — License가 마지막 위치인지 확인.

### 4-2. Short Description 120자 검증

```python
# 의사 코드
short_desc = extract_section(readme, "Description")
if len(short_desc) >= 120:
    short_desc = compress_to_under_120(short_desc)  # LLM이 직접 압축
```

Standard Readme + Make a README 모두 권장. HF Model Card는 별도 제약 없음.

### 4-3. 안티패턴 매칭 (8개)

`anti-patterns.md`의 8개 패턴에 대해:
1. 탐지 신호로 매칭 시도
2. 매칭 시 → 처방 적용 (LLM 자동 수정)
3. 적용 제외 그룹이면 → 경고만 출력, 수정 안 함
4. 수정 후 재검증 1회 (수정이 다른 패턴 유발했는지)
5. 재검증 후에도 위반 남으면 → README 상단 HTML 주석으로 표시:
   ```html
   <!-- readme-writer: 수동 검토 필요 — 안티패턴 #N (이유) -->
   ```

### 4-4. YAML frontmatter 필드 검증 (AI Asset 그룹만)

`platform-metadata.md`의 HF 섹션 필수 필드 체크:
- `library_name` (2024.8 이후 명시 필수)
- `pipeline_tag`
- `license` 또는 (`license_name` + `license_link`)
- `tags` 1개 이상

누락 시 placeholder + 콘솔 안내:
```yaml
library_name: transformers  # TODO: 실제 라이브러리로 교체
```

### Phase 4 출력

검증 결과 콘솔 요약:
```
✅ Phase 4 인라인 검증
- 섹션 순서: PASS (Standard Readme 16-섹션 준수)
- Short Description: PASS (98자)
- 안티패턴: 1건 자동 수정 (#1 모호한 설명)
- YAML frontmatter: N/A (Package 그룹)
```

## Phase 5: 통합 호출 (humanize-writing + rl-verify)

Phase 4 검증을 통과한 초안에 대해 두 스킬을 순차 자동 호출한다.

### 5-A: humanize-writing 호출

```
Skill("humanize-writing", initial_draft)
→ 출력: AI 톤 제거된 초안
```

실패 시:
- 콘솔 경고: "humanize-writing 호출 실패. 원본 초안으로 진행합니다."
- 사용자 안내: "수동으로 `/humanize-writing README.md` 실행을 권장합니다."
- 원본 초안 유지하고 Phase 5-B로 계속.

### 5-B: rl-verify 호출

```
Skill("rl-verify", "다음 README의 사실 정확성을 Tier 1로 검증하라: <humanized_draft>")
→ 출력: PASS / PARTIAL / FAIL 리포트
```

Tier 1 (경량) — 단일 문서, 영향 범위 제한.

결과 분기:
- **PASS** → Phase 6 진행
- **PARTIAL** 또는 **FAIL** → Phase 3 재진입 (1회만):
  - rl-verify의 FAIL/PARTIAL 항목을 수정 지시로 변환
  - Phase 3 Layer 1-3 재작성 (수정 지시 반영)
  - Phase 4 인라인 검증 재실행
  - Phase 5 재진입 안 함 (무한 루프 방지)
  - 재시도 후에도 FAIL 항목 있으면 → README 상단 HTML 주석으로 표시:
    ```html
    <!-- readme-writer: rl-verify FAIL 항목 N개 — 수동 확인 필요 -->
    ```

rl-verify 호출 자체가 실패하면:
- 콘솔 경고: "rl-verify 호출 실패. 검증을 건너뜁니다."
- 사용자 안내: "수동으로 `/rl-verify README.md` 실행을 권장합니다."
- 검증 스킵하고 Phase 6 진행.

## Phase 6: 출력 + 외부 도구 안내

### 6-A: 파일 출력

```
모드 결정:
  --force 옵션 + 기존 README.md 존재 → README.md 덮어쓰기 (사용자 확인 후)
  기존 README.md 부재 → README.md 생성 (신규 모드)
  기존 README.md 존재 (--force 없음) → README.v2.md 생성 (비파괴 모드)

언어 처리:
  --lang ko (기본): README.md (또는 README.v2.md) 1개
  --lang en: 동일, 영어
  --lang both: README.md + README.en.md (또는 .v2.md + .en.v2.md) 2개 + 스위처
```

비파괴 모드일 때 diff 요약 콘솔 출력:
```
📋 비파괴 출력: README.v2.md 생성 완료
- 추가된 섹션: Installation, Configuration (2개)
- 수정된 섹션: Description (한 줄 압축)
- 보존된 섹션: About, Acknowledgments (사용자 손작성)
```

### 6-B: 외부 도구 명령 안내

선택한 그룹/플랫폼에 따라 콘솔에 복사-붙여넣기 가능한 명령 안내. `references/platform-metadata.md` 참조.

```
🛠️  추천 외부 검증 도구

# 마크다운 일반 (모든 그룹)
markdownlint README.md
lychee README.md

# PyPI (Package 그룹 + pyproject.toml 탐지 시)
twine check dist/*

# Helm (Metadata-bound + Chart.yaml 탐지 시)
helm-docs --chart-search-root=.
```

미설치 도구 자동 감지 + 설치 명령 함께 출력:
```bash
# 의사 코드
for tool in [markdownlint, lychee, twine, helm-docs]:
    if not command_exists(tool):
        print(f"# {tool} 미설치. 설치 명령:")
        print(install_command_for(tool))
```

설치 명령 예시:
```bash
# markdownlint
npm install -g markdownlint-cli

# lychee
brew install lychee

# twine
pip install --upgrade twine

# helm-docs
brew install norwoodj/tap/helm-docs
```

### 6-C: 최종 종료 메시지

```
✅ README 생성 완료
- 파일: README.md (또는 README.v2.md)
- 표준: Standard Readme
- 그룹: Package (Library)
- 언어: ko
- 검증: 인라인 PASS, humanize PASS, rl-verify PASS
- 다음 단계: 위 외부 도구 명령을 실행하세요.
```

비파괴 모드 시 추가 안내:
```
ℹ️  비파괴 출력 모드:
README.v2.md를 검토한 뒤 README.md로 옮기려면:
    mv README.md README.bak.md && mv README.v2.md README.md
```
