---
name: md-to-html
description: Use when turning one or more markdown files (or the last conversation output, or a vault doc) into a polished, shareable HTML page — especially when plain/pandoc conversion looks "too markdown-y", or you need ONE self-contained file to send people that opens offline. Triggers — "이 문서 HTML로", "공유용 웹페이지로 만들어", "md들 하나의 html로 합쳐", "render markdown as a shareable self-contained webpage".
argument-hint: "[a.md b.md ...] | [@경로] | (없으면 직전 대화)"
---

# md-to-html — 마크다운 → 공유용 HTML

## Overview

마크다운을 **콘텐츠 적응형 · 완전 자기완결(단일 파일, 외부참조 0) · 시스템폰트 전용** HTML로 변환한다.

**핵심 원칙**: CSS는 재작성하지 않는다 — 검증된 `assets/theme.css`/`assets/theme.js`를 **그대로 인라인**하고, 적응은 *어떤 콘텐츠를 어떤 컴포넌트로·어떤 순서로·히어로 카피를 무엇으로* 결정하는 **구성 레벨**에서만 한다. 디자인 품질의 정체성은 폰트가 아니라 레이아웃·스케일·컬러·계층에서 나온다.

## When to Use

- 마크다운 문서(들)를 사람에게 **공유**하려는데 보기 좋게 만들고 싶다
- 기본/pandoc 변환이 "마크다운 티가 난다"
- 메신저·메일로 보낼 **단일 파일**이 필요하다(오프라인에서도 동일하게 열림)
- 여러 `.md`(a.md b.md c.md)를 **하나의 HTML로 결합**해야 한다

NOT: 라이브 웹앱/React 컴포넌트 제작(→ frontend-design), 원본 md 편집(→ organize).

## Workflow

1. **입력 해석** — 인자 파일(들) | 직전 대화 출력 | vault 경로. 여러 파일이면 인자 순서대로 결합(→ `references/merge.md`).
2. **콘텐츠 분석** — 유형(리포트/가이드/노트/README)·구조·표·코드·콜아웃 후보·확신도/등급 신호 식별. 제목·frontmatter(tags/created) 추출.
3. **구성 계획** — 히어로, 섹션→컴포넌트 매핑, TOC, 서사 순서를 콘텐츠에 맞게 결정(→ `references/components.md`).
4. **빌드** — 단일 HTML 생성:
   - `assets/theme.css` 전체를 `<style>`로, `assets/theme.js` 전체를 `<script>`로 **인라인**.
   - 시맨틱 HTML(`nav/main/section/article`) + 컴포넌트 클래스로 콘텐츠를 **적응적으로** 구성.
   - 웹폰트·CDN·외부 이미지 링크 **금지**(이미지는 data URI 또는 생략).
5. **검증** — `agent-browser`로 라이트+다크(+모바일 1컷) 스크린샷 → litmus 점검 → glaring 이슈 1패스 수정. (부재 시 mental review + 명시) → `references/verify.md` 없음, 아래 체크 사용.
6. **자기완결 확인** (필수, 출력 직후):
   ```bash
   grep -ic 'fonts.googleapis\|@font-face\|@import\|cdn\.' OUT.html        # → 0
   grep -ioE '(src|href)=["'"'"']https?://[^"'"'"']*\.(css|js|woff2?|ttf)' OUT.html  # 외부 리소스 → 0 (콘텐츠 <a href> 링크는 무관)
   ```
7. **출력** — `<원본명>.html`을 원본 옆(또는 지정 경로)에 저장 → 경로·크기·자기완결 확인 보고 → `open`(선택).

## Quick Reference

| 입력 | 처리 |
|------|------|
| `md-to-html a.md` | 단일 변환 |
| `md-to-html a.md b.md c.md` | 인자 순서로 1개 HTML 결합(파트 그룹 + 통합 TOC) |
| `md-to-html`(인자 없음) | 직전 대화 substantive 출력 |
| `md-to-html wiki/x.md` | vault/경로 |

컴포넌트 카탈로그·매핑 규칙 → `references/components.md` · 다중 파일 병합 → `references/merge.md`.

## Common Mistakes (← 실제 baseline 실패)

| 실패 | 교정 |
|------|------|
| "마크다운 티" 나는 평면 변환(raw 표/리스트 나열) | theme 컴포넌트로 매핑(히어로·콜아웃·비교표·배지·매트릭스·스텝퍼). 단 **과장 금지**(아래) |
| **웹폰트(Google Fonts/@font-face) 사용** | 시스템폰트만. theme.css 폰트 스택 유지, `<link>`/`@font-face` 추가 금지 |
| **다크모드 강조면 눈부심**(밝은 그라데이션 카드) | theme.css에 박제된 `[data-theme=dark] .rec-hero` deep-muted 규칙 유지 — 새 강조면 만들면 다크 대비 직접 확인 |
| 외부 이미지/CDN 링크로 자기완결 깨짐 | data URI 또는 생략. Step 6 grep로 검증 |
| **평범한 산문에 비교카드·매트릭스 강요**(AI slop) | 콘텐츠가 진짜 비교/단계/평결일 때만 해당 컴포넌트. 산문은 산문답게 |
| 진짜 표 데이터를 카드로 쪼갬 | 표는 `table.cmp`로 유지 |
| CSS를 매번 새로 작성 | `assets/theme.css` 인라인 재사용(확장은 허용, 재작성 금지) |

## Red Flags — STOP

- `<link href="...fonts.googleapis">` 또는 `@font-face`를 쓰려 함 → 시스템폰트만
- 출력에 `src="http...` 외부 리소스가 남음 → 자기완결 위반
- 다크모드에서 안 보고 라이트만 확인 → 양쪽 다 스크린샷
- 모든 섹션을 카드로 → 카드는 상호작용/비교/평결일 때만

## 배포 (전역 스킬)

이 스킬은 `product/.claude/skills/md-to-html/`에 위치. 변경 후 `cd <product-repo> && just link`로 stow 재배포.
