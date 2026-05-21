# Standards Comparison

readme-writer Phase 2 (표준 선택) 및 Phase 3 (초안 생성)에서 참조한다.

## 6종 표준 비교 매트릭스

| 표준 | 섹션 수 | 순서 강제 | 라이선스 위치 | 적합 그룹 |
|------|--------|----------|--------------|----------|
| Standard Readme | 16 | ✅ 엄격 | 마지막 강제 | Package (라이브러리) |
| Make a README | 12 | ❌ 유연 | 자유 | 일반 OSS, Application |
| Best-README-Template | 12 | 🟡 권장 | 끝부분 | Application (웹 앱) |
| Ankane (Ruby) | 7-8 | ✅ 엄격 | 마지막 | Package (Ruby Gem만) |
| HF Model Card | YAML+본문 | YAML 필수 | YAML + LICENSE | AI Asset |
| Awesome Manifesto | TOC+카테고리 | 카테고리만 | CC0 권장 | Curated List |

## 그룹별 기본 표준 추천

| 그룹 | 1순위 표준 | 2순위 |
|------|----------|------|
| Package | Standard Readme | Make a README |
| Application | Make a README | Best-README-Template |
| AI Asset | HF Model Card (필수) | - |
| Curated List | Awesome Manifesto | - |
| Metadata-bound | Make a README + Configuration 표 | - |

사용자가 명시(--standard)하지 않으면 1순위를 채택.

## 각 표준의 핵심 규칙

### Standard Readme (Package 라이브러리)

> "Sections must appear in order given below. Optional sections may be omitted."

16개 섹션 순서 (선택 제외):
1. **Title** — 저장소·폴더·패키지 매니저명과 일치, 불일치 시 Long Description에 사유 명기
2. **Banner** — 선택
3. **Badges** — 자체 title 없음, newline 구분
4. **Short Description** — 120자 미만, `>` 기호로 시작 금지
5. **Long Description** — 선택
6. **Table of Contents** — 100줄 미만 README는 선택, 그 외 필수
7. **Security** — 보안 관련 시만
8. **Background** — 선택
9. **Install**
10. **Usage**
11. **Extra Sections** — 자유 추가
12. **API** — 라이브러리만
13. **Maintainers** — 선택
14. **Thanks** — 선택
15. **Contributing**
16. **License** — 반드시 마지막, 저장소 라이선스와 일치

핵심: 순서가 엄격하고, License는 반드시 마지막에 위치해야 한다.

### Make a README (일반 OSS)

> "The sections used in the template are suggestions for most open source projects."
> "Too long is better than too short."

12개 섹션 권장 순서 (유연):
1. **Name**
2. **Description**
3. **Badges**
4. **Visuals** — 스크린샷/데모
5. **Installation**
6. **Usage**
7. **Support**
8. **Roadmap**
9. **Contributing**
10. **Authors/Acknowledgment**
11. **License**
12. **Project Status**

핵심: 순서는 권장이며 조정 가능. 길어도 상관없음 ("Too long is better than too short").

### Best-README-Template (Application 웹 앱)

뱃지 6개 (Contributors/Forks/Stargazers/Issues/License/LinkedIn) 상단 고정, "back to top" 링크, contrib.rocks 이미지.

섹션 순서:
1. **Badges** (상단 6개 고정)
2. **Logo + Title**
3. **Table of Contents**
4. **About The Project** (스크린샷)
5. **Built With** — 기술 스택
6. **Getting Started** (Prerequisites + Installation)
7. **Usage**
8. **Roadmap** (체크박스)
9. **Contributing**
10. **License**
11. **Contact**
12. **Acknowledgments**

핵심: 시각적 요소(뱃지, 로고, 스크린샷) 강조, "back to top" 링크 상시 제공.

### Ankane (Ruby Gem 개인 컨벤션)

> ⚠️ 단일 개인 큐레이터(Andrew Kane) 사이트. Ruby 커뮤니티 표준 아님.
> Ruby Gem 자동 탐지 시에만 Phase 2 옵션에 추가.

순서:
1. **Header** — 제목 + 간단 설명
2. **Installation** — Gemfile/gem install
3. **Quick Start** — 가장 간단한 사용법
4. **Usage** — 자세한 사용 설명
5. **Options** — 필요 시 (많은 옵션이 있을 때)
6. **Upgrading** — 메이저 버전 변경 시
7. **Contributing**
8. **License**

핵심: 간결함, Ruby Gem 특화, "Quick Start" 강조.

### HF Model Card (AI Asset 필수)

YAML frontmatter + Markdown 본문 구조:

**YAML frontmatter 예**:
```yaml
---
language: ko
license: cc-by-4.0
datasets:
  - custom_dataset_name
model_id: "user/model-name"
tags:
  - transformers
  - pytorch
---
```

**본문 권장 섹션** (순서는 자유):
- **모델 설명** — 아키텍처, 학습 방식
- **의도된 사용처 및 한계** — 적용 도메인, 편향·윤리 주의사항
- **학습 파라미터** — 하이퍼파라미터, 학습 데이터 크기
- **데이터셋** — 출처, 전처리
- **평가 결과** — 벤치마크 성능

지원 기능:
- KaTeX 수식: `$$ ... $$`
- 다크/라이트 모드 이미지: `#hf-light-mode-only`, `#hf-dark-mode-only`

YAML 필드는 `platform-metadata.md`의 HF 섹션 참조.

### Awesome Manifesto (Curated List)

차별점: **CC0** (Creative Commons Zero) 권장 — 코드 라이선스(MIT/BSD/GPL) 비권장.

필수 요소:
1. **Awesome 뱃지** — 상단 필수
2. **간결한 description** — 범위 명확히
3. **단일 scope** — 광범위한 주제 X, 특정 도메인에 집중
4. **Table of Contents** — 카테고리 링크
5. **카테고리** — 논리적 그룹핑
6. **통일된 항목 형식** — 모든 항목이 동일 구조
7. **Contribution Guidelines** — PR·이슈 기준 명기

핵심 철학: **"Only awesome is awesome"** — curation (정성적 선별), not collection (무분별 수집).

## 표준 임의 조합

사용자가 표준을 임의 조합 요청 (예: Standard Readme 16-섹션 + HF YAML frontmatter)하면 허용한다.

골격(Standard Readme의 섹션 구조)과 메타데이터(YAML frontmatter)는 직교(orthogonal)한다. YAML은 spec 외부 요소이므로 파일 첫 행에 frontmatter를 추가할 수 있다.

예시:
```yaml
---
language: en
license: MIT
---
# Title
...
(Standard Readme 16-섹션 이어짐)
```

이 경우 검증 시 Standard Readme의 순서 + HF의 YAML 메타데이터 모두 확인한다.
