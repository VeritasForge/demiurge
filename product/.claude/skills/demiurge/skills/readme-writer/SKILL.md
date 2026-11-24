---
name: readme-writer
description: README.md 파일을 생성하거나 업데이트하는 스킬. 프로젝트 유형(Package/Application/AI Asset/Curated/Metadata-bound)을 자동 탐지하고, 한국어 기본으로 README를 작성한다. 기존 README가 있으면 README.v2.md로 비파괴 출력. 작성한 사실을 레포 파일과 대조해 검증한다. /readme-writer로 사용자 호출, 또는 신규/기존 OSS 저장소에서 README 작성·갱신 요청 시 사용.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[--lang ko|en|both] [--standard <name>] [--badges minimal|standard|extensive] [--force]"
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
- 적용한 기본값: 언어 ko, 뱃지 standard, 표준 ○○ (바꾸려면 말씀해 주세요)
```

다중 매칭 또는 0건 매칭 시 Phase 2로 진행.

## Phase 2: 그룹·표준·플랫폼·언어·뱃지 확정

기본값을 적용하고, 자동 탐지 결과 중 모호한 항목만 사용자에게 평문으로 확인한다. 적용한 기본값은 Phase 1 탐지 결과 출력에 함께 적어 사용자가 바꿀 수 있게 한다. `references/standards-comparison.md`의 그룹별 추천 표를 1순위로 적용.

### 2-1. 그룹 확정

다중 매칭 시 (예: Package(CLI) + Package(Library) + Application(Monorepo)) 후보 그룹을 글로 나열하고 평문으로 묻는다. 여러 개를 고를 수 있다.
```
여러 그룹이 탐지되었습니다. 적용할 그룹을 모두 알려 주세요.
- Package (CLI)
- Package (Library)
- Application (Monorepo)
```

0건 매칭 시 프로젝트 유형을 평문으로 묻는다.
```
시그널 파일이 탐지되지 않았습니다. 프로젝트 유형을 하나 알려 주세요.
- Package / Application / AI Asset / Curated List / Metadata-bound
```

### 2-2. 표준 확정

`--standard` 옵션 미지정 시 `references/standards-comparison.md`의 그룹별 1순위 표준을 채택한다. 묻지 않는다. 확정한 그룹이 여럿이라 1순위 후보가 같은 순위로 둘 이상 남을 때만 그 후보들을 글로 나열해 평문으로 묻는다.

참고용 표준 목록:
- Standard Readme (Library 1순위)
- Make a README
- Best-README-Template
- HF Model Card (AI Asset 1순위)
- Awesome Manifesto (Curated List 1순위)
- Ankane (Ruby Gem 자동 탐지 시에만 후보)

### 2-3. 언어 확정

묻지 않는다. `--lang` 옵션 미지정 시 `ko`를 쓴다.

참고용 값: `ko` (한국어, 기본) / `en` (영어) / `both` (한국어 메인 + README.en.md 보조 + 상단 스위처)

### 2-4. 뱃지 프리셋 확정

묻지 않는다. `--badges` 옵션 미지정 시 `standard`를 쓴다.

참고용 프리셋 정의:
- minimal (2개: version, license)
- standard (4개: build, version, license, coverage) ← 기본
- extensive (6-7개: contributors/forks/stars/issues/license/version + optional LinkedIn)

## Phase 3: 초안 생성

3-Layer 구조로 README 본문을 생성한다.

### Layer 1: 공통 골격 (모든 그룹 공통)

```
Title → Description → Badges → Installation → Usage → Contributing → License
```

각 섹션 작성 가이드:
- **Title**: 자동 탐지된 프로젝트명 (package.json의 `name`, Cargo.toml의 `[package].name` 등). 모호하면 사용자에게 질문.
- **Description**: 한 줄 핵심 가치. 120자 미만 (Standard Readme 표준). 모호한 표현("A tool for...") 금지 (anti-patterns.md #1).
- **Badges**: Phase 2-4에서 정한 프리셋(기본 standard)에 따라 Shields.io URL 생성.
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

### 4-3. 안티패턴 매칭 (11개)

`anti-patterns.md`의 11개 패턴에 대해:
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
- `library_name` (필수)
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

## Phase 5: 사실 검증 (레포 대조)

> 문장 톤 정리는 별도 스킬로 넘기지 않는다. 한국어 명료성은 Phase 4 안티패턴 #9~#11에서 초안 단계에 함께 걸러진다.

Phase 4를 통과한 초안에서 사실 주장을 뽑아 레포 파일과 직접 대조한다. README의 사실은 대부분 레포 안에 근거가 있다.

| 주장 유형 | 대조할 곳 (예) |
|---|---|
| 설치·실행 명령 | package.json scripts, Makefile·justfile, pyproject.toml, Cargo.toml |
| 버전·런타임 요구사항 | manifest의 version, engines, requires-python |
| 라이선스 | LICENSE 파일, manifest의 license 필드 |
| 파일·디렉터리 경로, 설정 키 | 실제 존재 여부(Glob), 설정 파일 |
| 기능·API 이름 | 소스의 export, CLI 정의 |

레포에서 근거를 찾을 수 없는 주장(외부 서비스 동작, 성능 수치 등)은 지어내지 않는다. 문장을 빼거나 "확인 필요"로 표시한다.

결과 분기:
- 레포와 어긋난 주장이 0건 → Phase 6 진행
- 1건 이상 → 어긋난 항목을 수정 지시로 바꿔 Phase 3에 1회 재진입한다(Phase 3 재작성 → Phase 4 재검증. Phase 5는 다시 돌지 않는다: 무한 루프 방지)
  - 재시도 후에도 남으면 README 상단에 HTML 주석으로 표시:
    `<!-- readme-writer: 레포와 대조되지 않은 항목 N개 — 수동 확인 필요 -->`

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
- 검증: 인라인 PASS, 레포 대조 통과
- 다음 단계: 위 외부 도구 명령을 실행하세요.
```

비파괴 모드 시 추가 안내:
```
ℹ️  비파괴 출력 모드:
README.v2.md를 검토한 뒤 README.md로 옮기려면:
    mv README.md README.bak.md && mv README.v2.md README.md
```
