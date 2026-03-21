---
name: save_confluence
description: 직전 대화 출력 결과를 Confluence에 업로드합니다. 새 페이지 생성 또는 기존 페이지에 내용 삽입을 지원합니다.
triggers:
  - save_confluence
  - confluence에 올려
  - confluence 저장
  - 컨플루언스에 올려
  - 컨플루언스 저장
user_invocable: true
---

# save_confluence 스킬

직전 assistant 응답 내용을 Confluence에 업로드하는 스킬입니다.

## 사용법

```
# 새 페이지 생성
/save_confluence <space_key>
/save_confluence <space_key>, <parent_page_id>
/save_confluence <space_key>, <parent_page_id>, <title>

# 기존 페이지에 삽입
/save_confluence <page_id>, --append
/save_confluence <page_id>, --after "헤딩 텍스트"
```

## 실행 절차

### Step 1: 인자 파싱

사용자가 전달한 인자를 분석하여 모드를 결정합니다.

- `--append` 또는 `--after` 플래그가 있으면 **기존 페이지 삽입 모드**
- 그 외에는 **새 페이지 생성 모드**

인자 파싱 규칙:
- 쉼표(`,`)로 구분된 인자를 파싱
- 앞뒤 공백 트림
- `--append`: 페이지 끝에 추가
- `--after "텍스트"`: 해당 헤딩 뒤에 삽입

### Step 2: 직전 대화 내용 수집

이 스킬이 호출되기 직전의 assistant 응답 내용을 수집합니다.
- 대화 컨텍스트에서 가장 최근 assistant 메시지의 텍스트 내용을 가져옵니다.
- tool call 결과가 아닌, 사용자에게 보여진 텍스트 출력만 수집합니다.

### Step 3: Confluence Storage Format 변환

수집한 마크다운 내용을 Confluence storage format (XHTML)으로 변환합니다.

**변환 규칙:**

1. **헤딩**: `# H1` → `<h1>H1</h1>`, `## H2` → `<h2>H2</h2>`, ... `###### H6` → `<h6>H6</h6>`

2. **코드 블록**:
````
```python
code here
```
````
→
```xml
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">python</ac:parameter>
  <ac:plain-text-body><![CDATA[code here]]></ac:plain-text-body>
</ac:structured-macro>
```

3. **테이블**:
```
| Header1 | Header2 |
|---------|---------|
| Cell1   | Cell2   |
```
→
```xml
<table>
  <thead>
    <tr><th>Header1</th><th>Header2</th></tr>
  </thead>
  <tbody>
    <tr><td>Cell1</td><td>Cell2</td></tr>
  </tbody>
</table>
```

4. **인라인 서식**:
   - `**bold**` → `<strong>bold</strong>`
   - `*italic*` → `<em>italic</em>`
   - `` `code` `` → `<code>code</code>`
   - `[text](url)` → `<a href="url">text</a>`

5. **리스트**:
   - 순서 없는 리스트 (`- item`) → `<ul><li>item</li></ul>`
   - 순서 있는 리스트 (`1. item`) → `<ol><li>item</li></ol>`
   - 중첩 리스트도 지원

6. **단락**: 빈 줄로 구분된 텍스트 → `<p>텍스트</p>`

7. **수평선**: `---` → `<hr />`

8. **특수 처리**:
   - HTML 엔티티 이스케이프 (코드 블록 내부의 `<`, `>`, `&`)
   - CDATA 섹션 내부는 이스케이프하지 않음

### Step 4A: 새 페이지 생성 (Mode 1)

새 페이지 생성 모드일 때:

1. **제목 결정**:
   - 인자로 제목이 주어졌으면 그대로 사용
   - 없으면 내용의 첫 번째 헤딩을 제목으로 사용
   - 헤딩도 없으면 내용 첫 줄에서 50자 이내로 자르고 Title Case 적용

2. **페이지 생성**:
   - `confluence_create_page` MCP 도구 사용
   - `space_key`: 사용자 지정 space key
   - `title`: 결정된 제목
   - `content`: Step 3에서 변환한 storage format HTML
   - `content_format`: `"storage"`
   - `parent_id`: 지정된 경우에만 포함

3. **결과 보고**:
   - 생성된 페이지 제목과 URL 출력
   - 오류 시 에러 메시지 출력

### Step 4B: 기존 페이지에 삽입 (Mode 2)

기존 페이지 삽입 모드일 때:

1. **기존 페이지 내용 가져오기**:
   - `confluence_get_page` MCP 도구로 현재 내용 조회
   - `page_id`: 사용자 지정 페이지 ID
   - `convert_to_markdown`: `false` (raw HTML 유지)
   - `include_metadata`: `true`

2. **삽입 위치 결정 및 내용 합성**:
   - `--append`: 기존 HTML 끝에 변환된 내용 추가
   - `--after "헤딩 텍스트"`: 기존 HTML에서 해당 헤딩 태그(`<h1>`~`<h6>`)를 찾고, 그 헤딩이 속한 섹션 끝(다음 동일 레벨 이상 헤딩 앞 또는 문서 끝)에 삽입

3. **페이지 업데이트**:
   - `confluence_update_page` MCP 도구 사용
   - `page_id`: 대상 페이지 ID
   - `title`: 기존 페이지 제목 유지
   - `content`: 합성된 storage format HTML
   - `content_format`: `"storage"`

4. **결과 보고**:
   - 업데이트된 페이지 제목과 URL 출력
   - 오류 시 에러 메시지 출력

### 에러 처리

- space_key나 page_id가 없으면 사용자에게 요청
- Confluence API 오류 시 에러 메시지를 사용자에게 보고
- 변환 실패 시 원본 마크다운을 `content_format: "markdown"`으로 폴백
