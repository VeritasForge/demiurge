# Components Catalog & Block→Component Mapping

`assets/theme.css`/`assets/theme.js`에 정의된 컴포넌트와, **마크다운 블록을 어떤 컴포넌트로 매핑할지**의 규칙. CSS는 재작성하지 말고 이 클래스들을 사용한다.

## Page Skeleton (이 골격을 채운다)

```html
<!DOCTYPE html>
<html lang="ko" data-theme="light">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>제목</title>
<style>/* ← assets/theme.css 전체 인라인 */</style>
</head>
<body>
<button class="theme-toggle" id="themeBtn" aria-label="테마 전환">🌙</button>

<header class="hero"><div class="hero-inner">
  <div class="eyebrow">Eyebrow · 날짜 · 메타</div>
  <h1>제목 <em>강조어</em></h1>
  <p class="hero-thesis">한두 문장 핵심 결론. <b>강조</b>.</p>
  <div class="hero-meta"><span><span class="dot"></span>메타1</span><span>메타2</span></div>
  <div class="tags"><span class="tag">#tag1</span><span class="tag">#tag2</span></div>
</div></header>

<div class="shell">
  <nav class="toc" aria-label="목차"><div class="toc-title">Contents</div>
    <ol>
      <li><a href="#s1"><span class="n">01</span>섹션1</a></li>
      <!-- ... 섹션마다 -->
    </ol>
  </nav>
  <main>
    <section id="s1" class="reveal">
      <div class="sec-head"><span class="sec-num">01</span><h2 class="sec-title">섹션 제목</h2></div>
      <!-- 본문: 아래 컴포넌트로 구성 -->
    </section>
    <!-- ... -->
    <footer>푸터 메타</footer>
  </main>
</div>
<script>/* ← assets/theme.js 전체 인라인 */</script>
</body></html>
```

- 모든 `<section>`에 고유 `id` + `class="reveal"`, TOC 링크는 `#id`로. 스크롤스파이가 자동 하이라이트.
- 섹션 번호는 `01,02,...` 권장(없어도 됨).

## Block → Component 매핑

| 마크다운 입력 | → 컴포넌트 | 클래스 |
|------|------|------|
| 문서 제목/부제 | 히어로 | `.hero` (제목 H1, 핵심결론 `.hero-thesis`) |
| TL;DR / 핵심 요약 목록 | 평결 카드 | `.verdict` (번호 목록) |
| 일반 문단/설명 | 그대로 산문 | `<p>`, `.lead`(인트로 문단) |
| 팁/주의/핵심 인용구(`> 💡`/`> ⚠️`) | 콜아웃 | `.callout.tip` / `.callout.warn` / `.callout.key` |
| 판정·상태가 붙은 항목(✅/🟡/⚪/❓/🔄) | 평결 행 + 배지 | `.vrow.ok|warn|bad` + `.badge.b-*` |
| 2×N 개념 지형/분류 매트릭스 | 매트릭스 그리드 | `.matrix` (열 수는 inline `style="grid-template-columns:..."`) |
| 다열 비교 표(도구/옵션 비교) | 스타일 표 | `.table-wrap > table.cmp` (상태 `.dot.d-*`) |
| 등급/리스크 순위 목록 | 리스크 행 | `.risk.low|mid|high` |
| 최우선 추천/결론 강조 | 추천 히어로 카드 | `.rec-hero` + `.rec-grid .cell`; 대안은 `.alt-cards .alt` |
| 순서가 중요한 단계/액션 플랜 | 스텝퍼 | `.steps`(중요 단계 `li.hot`) |
| 변경/정정 이력(before→after) | 정정 카드 | `.corr`(`.was`/`.arr`/`.now`/`.stage`) |
| 의사결정 트리/분기 | 트리 박스 | `.tree`(`.q`/`.yes`/`.no`/`.pick`) |
| 출처/링크 목록 | 칩 링크 | `.src-group > .src-list a` |

### 배지 의미색 (고정)
✅ Confirmed → `.b-ok` · 🟡 Likely → `.b-warn` · ⚪ Refuted → `.b-bad` · ❓ Uncertain → `.b-neutral` · 🔄 Synthesized → `.b-synth`

### 매트릭스 열 수 지정 예
```html
<div class="matrix" style="grid-template-columns:auto 1fr 1fr 1fr">
  <div class="mh"></div><div class="mh">열A</div><div class="mh">열B</div><div class="mh">열C</div>
  <div class="rh">행1</div><div><span class="tool">…</span></div><div>…</div><div>…</div>
</div>
```

## 적응 원칙 (over-decoration 금지)

- **콘텐츠가 그 컴포넌트의 의미일 때만** 사용한다. 비교가 아니면 비교표 금지, 단계가 아니면 스텝퍼 금지, 평결이 아니면 verdict 금지.
- 평범한 산문/노트/README → 히어로 + 깔끔한 `<p>`/리스트/콜아웃 정도로 **절제**. 억지 카드화는 AI slop.
- **진짜 표 데이터는 `table.cmp`로 유지**(카드로 쪼개지 말 것).
- 카드는 "상호작용/비교/평결/추천"처럼 카드일 이유가 있을 때만.
- 히어로 카피는 콘텐츠에서 가장 중요한 한 문장(결론/주제)을 뽑아 쓴다. 프롬프트·메타 발화 금지.

## 산문 base 스타일 (평범한 문서)

theme.css는 `code`/`pre`/일반 `ul·ol·li`/`blockquote`/`img`/`hr`의 **base 산문 스타일을 이미 포함**한다(테마 변수 기반). 따라서 README·노트는 컴포넌트 없이도 깔끔하게 렌더된다 — 코드블록·리스트를 위해 별도 CSS를 추가할 필요 없음.

## 다크모드/자기완결 주의

- 새 강조면(밝은 배경 카드)을 만들면 **다크모드 대비를 반드시 확인**. `.rec-hero`처럼 `[data-theme="dark"]` 오버라이드로 deep-muted 처리(theme.css에 예시 박제).
- **확장 스타일을 추가할 때는 반드시 테마 변수(`var(--ink)`,`var(--surface)`,`var(--line)`,`var(--code-bg)` 등)만 사용** → 다크모드 자동 대응(별도 다크 규칙 불필요).
- 웹폰트·외부 이미지·CDN 절대 추가 금지. 이미지가 꼭 필요하면 data URI.
