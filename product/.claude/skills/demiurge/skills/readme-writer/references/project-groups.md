# Project Groups

이 파일은 readme-writer 스킬 Phase 1(자동 탐지)와 Phase 2(그룹 확정)에서 참조한다.

## 자동 탐지 시그널 매트릭스

작업 디렉토리에서 다음 파일/필드를 스캔하여 그룹 후보를 도출한다. 다중 매칭 허용.

| # | 시그널 (파일/필드) | 후보 그룹 | 우선순위 |
|---|--------------------|----------|---------|
| 1 | `package.json` + `bin` 필드 | Package (CLI) | 1 |
| 2 | `package.json` + `main`/`exports` 필드 | Package (Library) | 1 |
| 3 | `pyproject.toml` 또는 `setup.py` | Package (PyPI) | 1 |
| 4 | `Cargo.toml` | Package (Crate) | 1 |
| 5 | `go.mod` | Package (Go) | 1 |
| 6 | `Gemfile` + `*.gemspec` | Package (Gem) | 1 |
| 7 | `pnpm-workspace.yaml` / `lerna.json` / `turbo.json` / `nx.json` | Application (Monorepo) | 2 |
| 8 | `Dockerfile` + (Next.js/Vite/Django 등 웹 프레임워크) | Application (Web) | 2 |
| 9 | 기존 README YAML에 `pipeline_tag` | AI Asset (HF Model) | 3 |
| 10 | `dataset_info.json` | AI Asset (HF Dataset) | 3 |
| 11 | 기존 README에 `awesome` 헤더 + TOC + 카테고리 리스트 | Curated List | 4 |
| 12 | `Chart.yaml` + `values.yaml` | Metadata-bound (Helm) | 5 |
| 13 | `action.yml` | Metadata-bound (GitHub Action) | 5 |
| 14 | `*.tf` + `variables.tf` | Metadata-bound (Terraform) | 5 |

## 5-그룹 정의

### Group 1: Package (Library + CLI)

자동 식별: `package.json`(bin → CLI / main → Library), `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`

필수 섹션:
- Installation (`<package_manager> install <name>`)
- Usage (코드 블록 1개 이상)
- License

권장 섹션:
- API (Library)
- Synopsis + Options + Exit Status (CLI, man-page 스타일)
- Examples
- Configuration
- Contributing

### Group 2: Application (Web App + Monorepo)

자동 식별: 웹 프레임워크 시그널 (Next.js/Vite/Django/Rails), Monorepo 도구

필수 섹션:
- Description (한 줄 핵심 가치)
- Demo (스크린샷 또는 라이브 링크)
- Tech Stack (뱃지)
- Getting Started

권장 섹션:
- Architecture diagram
- Packages Table (Monorepo만)
- Roadmap
- Contributing

### Group 3: AI Asset (Model + Dataset)

자동 식별: 기존 README YAML의 `pipeline_tag`, `dataset_info.json`, `transformers`/`diffusers` import

필수: YAML frontmatter (platform-metadata.md의 HF 섹션 참조), Intended Use, Limitations/Bias
권장: Training Data, Evaluation, CO2 Emissions, Citation, License

### Group 4: Curated List (Awesome + 연구 데이터)

자동 식별: 기존 README의 awesome 헤더 + TOC

필수: Description (단일 scope), Contents (TOC), Categories, Contributing, License (CC0 권장)
권장: Awesome 뱃지, 통일된 항목 형식 (제목 + 한 줄 설명)

### Group 5: Metadata-bound (Helm + Action + Terraform)

자동 식별: `Chart.yaml`, `action.yml`, `*.tf`

필수: Description, Configuration 표 (메타데이터 동기화), Usage, Inputs/Outputs
권장: 자동 생성 도구 안내 (helm-docs, terraform-docs)

## 다중 매칭 처리

여러 그룹이 동시에 매칭되면 (예: `package.json` + `turbo.json` → Package(npm) + Application(Monorepo)) Phase 2에서 AskUserQuestion `multiSelect: true`로 사용자가 적용할 그룹을 선택한다.

## 매칭 0건 처리

시그널 파일이 없으면 (예: Markdown 문서 저장소) Phase 2에서 AskUserQuestion으로 그룹 직접 선택.
