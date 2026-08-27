# Platform Metadata Hooks

readme-writer Phase 3(Layer 3 플랫폼 메타데이터) 및 Phase 6(외부 도구 안내)에서 참조한다.

## GitHub

- 자동 인식 우선순위: `.github/README.md` → 루트 `README.md` → `docs/README.md`
- 파일 크기 제한: **500 KiB** 초과 시 잘림 → `docs/`로 분리 안내
- Profile README: 사용자명과 동일한 public repo의 루트에 README 배치 시 프로필에 자동 표시
- 자동 기능: 헤딩 기반 TOC ("Outline" 메뉴), 헤딩 hover anchor, 상대 경로 자동 변환

Phase 6 안내: README가 500 KiB 초과 시 콘솔에 경고 + "긴 콘텐츠는 `docs/` 디렉토리로 분리하세요" 권고.

## npm (package.json sync)

- 렌더링: GitHub Flavored Markdown (GFM)
- ⚠️ 중요 제약: **"The README.md file will only be updated on the package page when you publish a new version of your package."**

Phase 6 안내 (Package + package.json 탐지 시):
```bash
npm version patch
npm publish
```
설명: "README 변경을 npmjs.com 페이지에 반영하려면 새 버전을 publish하세요."

## PyPI (setup.py / pyproject.toml)

setup.py 패턴:
```python
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='package_name',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
```

지원 Content-Type:
| 형식 | Content-Type |
|---|---|
| Plain text | `text/plain` |
| reStructuredText (Sphinx 확장 제외) | `text/x-rst` |
| Markdown (GFM/CommonMark) | `text/markdown` |

⚠️ 금지: Sphinx role (`:py:func:` 등) 사용 시 "will result in error messages"

버전 요구: setuptools ≥ 38.6.0, wheel ≥ 0.31.0, twine ≥ 1.11.0

Phase 6 안내 (Package + pyproject.toml 탐지 시):
```bash
pip install --upgrade setuptools wheel twine
python -m build
twine check dist/*
```

## Cargo (crates.io)

- `Cargo.toml`의 `package.readme` 필드 (기본값 `README.md` 자동 인식)
- crates.io 패키지 페이지에 README 표시
- ⚠️ 이중 관리: `docs.rs`는 `lib.rs`의 `//!` doc-comment를 우선 렌더링

권장 패턴 (Phase 6 안내):
```rust
#![doc = include_str!("../README.md")]
```
설명: "README와 docs.rs를 동기화하려면 lib.rs에 이 매크로 추가"

## Hugging Face Model Card (YAML frontmatter)

AI Asset 그룹 필수. README.md 첫 부분에 `---`로 둘러싸인 YAML 블록.

```yaml
---
language:
  - en
  - ko
license: apache-2.0
# 또는 커스텀: license_name + license_link
tags:
  - text-generation
datasets:
  - stanfordnlp/imdb
library_name: transformers  # 2024.8 이후 명시 필수
pipeline_tag: text-generation
base_model: meta-llama/Llama-3-8B
base_model_relation: finetune
# 가능 값: adapter | merge | quantized | finetune
new_version: org/model-v2  # 신버전 있을 때
model-index:
  - name: my-model
    results:
      - task:
          type: text-generation
        dataset:
          name: ai2_arc
          type: ai2_arc
        metrics:
          - name: ARC
            value: 64.59
        source:
          name: Open LLM Leaderboard
          url: https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard
---
```

특별 기능:
- KaTeX 수식: `$$ ... $$` (display), `\\(... \\)` (inline)
- 다크/라이트 이미지: `![alt](url#hf-light-mode-only)`, `![alt](url#hf-dark-mode-only)`

Phase 6 안내 (AI Asset 탐지 시):
"YAML frontmatter는 huggingface.co/{org}/{model} 페이지의 metadata UI에서 확인하세요."

## Metadata-bound (Helm/Terraform/Action)

### Helm
Phase 6 안내:
```bash
# Configuration 표 자동 생성/갱신
helm-docs --chart-search-root=.
```
미설치 시:
```bash
brew install norwoodj/tap/helm-docs
# 또는
go install github.com/norwoodj/helm-docs/cmd/helm-docs@latest
```

### Terraform
Phase 6 안내:
```bash
terraform-docs markdown table . > README.md
```
미설치 시:
```bash
brew install terraform-docs
```

### GitHub Action
Phase 6 안내:
"action.yml의 name/description/inputs/outputs가 README Usage 예제와 일치하는지 수동 확인 필수. 자동 도구 없음."
