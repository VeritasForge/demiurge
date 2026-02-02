# RAG 파이프라인 구현 — Step by Step

```
┌─────────────────────────────────────────────────────────────┐
│              학습 로드맵 (8 Steps)                            │
│                                                              │
│  Step 0: 환경 세팅 + 샘플 데이터 준비            [완료]      │
│  Step 1: 문서 로딩 (Document Loading)            [완료]      │
│  Step 2: 청킹 (Text Splitting)                   [완료]      │
│  Step 3: 임베딩 (Embedding)                      [완료]      │
│  Step 4: 벡터 DB 저장 (Vector Store)              [완료]      │
│  Step 5: 검색 (Retrieval)                                    │
│  Step 6: 답변 생성 (Generation)                              │
│  Step 7: 전체 파이프라인 통합                                 │
│                                                              │
│  전략: 순수 Python + OpenAI API로 먼저 구현 (원리 이해)      │
│        → 이후 프레임워크(LlamaIndex/LangChain)로 전환        │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 0: 환경 세팅 + 샘플 데이터 준비

### 1. 무엇을 다루는가? 무엇을 배울 수 있는가?

프로젝트 뼈대를 세우는 단계다.
코드를 한 줄도 쓰기 전에 **개발 환경, 디렉토리 구조, 샘플 데이터**를 먼저 준비한다.

- `uv`를 사용한 Python 패키지 관리
- `pyproject.toml` 기반 프로젝트 설정 (빌드, lint, test 통합)
- RAG에서 다룰 샘플 `.txt` 문서 3개 준비 (약품 정보)

```
practice/type-a-rag/
├── pyproject.toml          # 프로젝트 설정 (의존성, 빌드, lint, test)
├── src/rag/                # 소스 코드
│   ├── __init__.py
│   └── cli.py              # CLI 엔트리포인트
├── tests/                  # 테스트 코드
│   └── __init__.py
└── data/                   # 샘플 데이터
    ├── metformin_overview.txt
    ├── aspirin_clinical_review.txt
    └── drug_interactions_guide.txt
```

### 2. 주의깊게 봐둬야 하는 부분

- **`pyproject.toml`의 `[tool.hatch.build.targets.wheel]`**: `packages = ["src/rag"]`로 설정해야 `from rag.xxx import yyy` 형태로 import 가능
- **`[tool.pytest.ini_options]`**: `testpaths = ["tests"]`로 테스트 디렉토리 지정
- **`[tool.ruff]`**: `src = ["src"]`로 import 정렬 기준 디렉토리 지정

### 3. 아키텍처와 동작 원리

```
pyproject.toml이 하는 일:

┌─ 의존성 관리 ─── uv가 읽어서 .venv에 패키지 설치
├─ 빌드 설정 ───── hatchling이 읽어서 wheel 생성
├─ lint 설정 ───── ruff가 읽어서 코드 검사
└─ test 설정 ───── pytest가 읽어서 테스트 실행

하나의 파일로 4가지 도구를 모두 설정한다 (설정 파일 분산 방지).
```

### 4. 개발자로서 알아둬야 할 것들

- **`uv` vs `pip`**: `uv`는 Rust로 작성된 패키지 매니저로, `pip`보다 훨씬 빠르다. `uv run pytest`처럼 가상환경 활성화 없이 바로 실행 가능
- **src layout**: `src/rag/` 구조를 쓰면 개발 중에도 설치된 패키지처럼 `from rag.xxx`로 import할 수 있다. 루트에 바로 `rag/`를 두면 설치 없이 import되어 테스트가 오염될 수 있음
- **샘플 데이터는 실제와 유사하게**: RAG 파이프라인에서 chunking, embedding 품질은 데이터 특성에 크게 좌우됨. 실제 도메인 문서를 쓰는 것이 좋다

### 5. 더 알아야 할 것

- `pyproject.toml`의 PEP 표준들: PEP 517 (빌드), PEP 621 (메타데이터), PEP 735 (dependency groups)
- `uv`의 lockfile (`uv.lock`): 재현 가능한 빌드를 위해 정확한 버전을 고정

---

## Step 1: 문서 로딩 (Document Loading)

### 1. 무엇을 다루는가? 무엇을 배울 수 있는가?

RAG 파이프라인의 첫 번째 단계 — **파일을 읽어서 프로그램이 다룰 수 있는 데이터 구조로 변환**하는 것을 배운다.

- `dataclass`로 도메인 모델(`Document`) 설계
- 파일 I/O (`Path.read_text()`, `Path.stat()`)
- TDD 사이클 (Red → Green → Refactor)
- 에러 처리 패턴 (검증 → 실패 빠르게)

```
파일 시스템                          프로그램 내부
┌──────────────┐    load_file()    ┌──────────────────────┐
│ .txt 파일     │ ───────────────▶ │ Document              │
│ (바이트 덩어리)│                  │   content: str        │
└──────────────┘                   │   metadata: dict      │
                                   └──────────────────────┘
```

### 2. 주의깊게 봐둬야 하는 부분

- **`Document.metadata`를 `dict`로 설계한 이유**: LangChain의 `Document`, LlamaIndex의 `TextNode` 모두 metadata를 dict로 관리한다. 나중에 프레임워크로 전환할 때 호환성을 위해 동일한 패턴을 사용
- **`load_file`의 검증 순서**: 확장자 검증 → 파일 읽기 → 빈 파일 검증. "비싼 연산(I/O) 전에 싼 검증(suffix 체크)을 먼저" 하는 Fail-Fast 원칙
- **`load_directory`에서 `sorted()`를 쓰는 이유**: `glob()`의 반환 순서는 OS/파일시스템에 따라 다르다. 정렬해야 테스트가 결정적(deterministic)

### 3. 아키텍처와 동작 원리

```
load_file(path) 동작 흐름:

  path (str|Path)
    │
    ▼
  Path(path)  ─── suffix != ".txt" ──▶ ValueError
    │
    ▼
  read_text(encoding="utf-8")  ─── FileNotFoundError (자동)
    │
    ▼
  strip() 후 빈 문자열?  ─── Yes ──▶ ValueError("empty")
    │ No
    ▼
  stat() → file_size 추출
    │
    ▼
  Document(content, metadata) 반환


load_directory(path) 동작 흐름:

  path
    │
    ▼
  glob("*.txt")  →  sorted()  →  [load_file(f) for f in files]
    │
    ▼
  list[Document] 반환
```

**파일 구조:**

| 파일 | 역할 |
|------|------|
| `src/rag/loader.py` | `Document` dataclass + `load_file()` + `load_directory()` |
| `tests/test_loader.py` | 11개 테스트 (모델, 단일파일, 디렉토리, 에러) |

### 4. 개발자로서 알아둬야 할 것들

- **`dataclass` vs `NamedTuple` vs `TypedDict`**: `dataclass`는 mutable하고 `__eq__`/`__repr__`이 자동 생성된다. `NamedTuple`은 immutable tuple 기반. `TypedDict`는 순수 dict에 타입 힌트만 추가. 여기서는 metadata를 나중에 추가할 수 있어야 하므로 mutable한 `dataclass`가 적합
- **`field(default_factory=dict)`**: mutable 기본값(dict, list)은 `default_factory`로 감싸야 한다. 안 그러면 모든 인스턴스가 같은 dict 객체를 공유하는 버그 발생
- **테스트 데이터 전략**: happy path는 `data/` 실제 파일로, edge case는 `tmp_path`(pytest 빌트인 fixture)로 격리

### 5. 더 알아야 할 것

- Python 3.15에서 기본 인코딩이 UTF-8로 변경 예정 (PEP 686). 현재 3.12에서는 `encoding="utf-8"` 명시가 안전
- `Path.read_text()` 대신 `open()`을 쓰는 경우: 대용량 파일을 줄 단위로 스트리밍해야 할 때. `read_text()`는 전체 내용을 메모리에 올림

### Q&A

**Q: `path.read_text(encoding="utf-8")`에서 왜 `utf-8`을 명시하는가?**

`encoding`을 생략하면 Python은 `locale.getpreferredencoding()`을 호출해서 OS 로캘의 기본 인코딩을 사용한다.

| 환경 | 기본 인코딩 |
|------|------------|
| macOS / Linux | 보통 UTF-8 |
| Windows (한국어) | cp949 |
| Windows (영어) | cp1252 |

같은 코드가 Windows에서는 cp949로 읽어서 글자가 깨지거나 `UnicodeDecodeError`가 발생할 수 있다. `encoding="utf-8"`을 명시하면 어떤 OS에서든 동일하게 동작한다.

비유하면: 도서관에서 "이 책은 한국어판으로 읽어줘"라고 명시하는 것. 생략하면 도서관의 기본 언어로 해석하는데, 한국 도서관이면 한국어, 일본 도서관이면 일본어로 해석해버린다.

---

## Step 2: 청킹 (Text Splitting)

### 1. 무엇을 다루는가? 무엇을 배울 수 있는가?

RAG 파이프라인의 두 번째 단계 — **긴 문서를 작은 조각(chunk)으로 나누는 것**을 배운다.

왜 나눠야 하는가?
- LLM의 context window에는 한계가 있다 (토큰 수 제한)
- 임베딩 모델은 짧은 텍스트에서 더 정확한 벡터를 생성한다
- 검색 시 문서 전체가 아니라 **관련 부분만** 가져와야 정확도가 올라간다

비유하면: 백과사전 전체를 통째로 건네주는 것보다, 질문과 관련된 **페이지만 찢어서** 건네주는 것이 더 도움이 된다.

```
원본 Document (6000자)
│
│  split_document(chunk_size=500, chunk_overlap=50)
▼
┌────────┐ ┌────────┐ ┌────────┐     ┌────────┐
│chunk 0 │ │chunk 1 │ │chunk 2 │ ... │chunk N │
│ 500자  │ │ 500자  │ │ 500자  │     │ ≤500자 │
└────────┘ └────────┘ └────────┘     └────────┘
       ◄──50──▶
       overlap
```

### 2. 주의깊게 봐둬야 하는 부분

- **Overlap의 역할**: chunk 경계에서 문맥이 끊기는 것을 방지한다. 이전 chunk의 마지막 50자를 다음 chunk 시작에 포함시켜서 연결 고리를 만든다. overlap이 없으면 "metformin은"에서 잘린 뒤 다음 chunk가 "당뇨 치료에 사용된다"로 시작해 맥락을 잃는다
- **chunk_size와 overlap의 관계**: overlap >= chunk_size이면 무한루프에 빠진다. 반드시 overlap < chunk_size여야 한다
- **metadata 전파**: 원본 Document의 metadata를 chunk에 상속해야 나중에 "이 chunk가 어떤 파일에서 왔는지" 추적 가능

### 3. 아키텍처와 동작 원리

```
split_document(doc, chunk_size=500, chunk_overlap=50) 동작 흐름:

  doc.content (6000자)
    │
    ▼
  검증: content 비어있음? chunk_size ≤ 0? overlap ≥ chunk_size?
    │
    ▼
  슬라이싱 루프:
    start = 0
    ┌─────────────────────────────────┐
    │ chunk = content[start:start+500]│
    │ start += (500 - 50) = 450       │──▶ 반복
    │ chunks.append(chunk)            │
    └─────────────────────────────────┘
    │
    ▼
  각 chunk에 metadata 부여:
    원본 metadata + {chunk_index, chunk_count, chunk_char_count}
    │
    ▼
  list[Document] 반환


step 간의 위치 (step 이동 시 stride = chunk_size - overlap):

  content: [==========================================================]
  chunk 0: [=========]                         stride = 500 - 50 = 450
  chunk 1:      [=========]
  chunk 2:           [=========]
  ...
  chunk N:                                [====]  (마지막, 짧을 수 있음)
```

**파일 구조:**

| 파일 | 역할 |
|------|------|
| `src/rag/splitter.py` | `split_document()` + `split_documents()` |
| `tests/test_splitter.py` | 10개 테스트 (기본 분할, overlap/metadata, 일괄처리, 에러) |

**Chunking 전략 비교:**

| 전략 | 동작 방식 | 장점 | 단점 |
|------|-----------|------|------|
| **Fixed-size + Overlap** (이번 구현) | 문자 수 기준으로 자른다 | 단순, 예측 가능 | 문장 중간에서 잘릴 수 있음 |
| Recursive (separator 기반) | `\n\n` → `\n` → `. ` → ` ` 순서로 시도 | 문단/문장 경계 존중 | 로직 복잡 |
| Semantic (의미 단위) | 임베딩 유사도로 의미 경계 판단 | 의미 보존 최상 | 외부 모델 필요, 느림 |

### 4. 개발자로서 알아둬야 할 것들

- **chunk_size의 단위**: 여기서는 "문자 수(char)"를 사용하지만, 실무에서는 "토큰 수"로 관리하는 경우가 많다. OpenAI의 `text-embedding-3-small`은 최대 8191 토큰. 토큰과 문자는 1:1이 아니다 (영어: ~1토큰=4자, 한국어: ~1토큰=1~2자)
- **chunk_size 튜닝**: 너무 작으면 문맥 손실, 너무 크면 검색 정확도 저하. 일반적으로 256~1024자(또는 100~500토큰) 사이에서 시작
- **LangChain과의 비교**: 이 구현은 LangChain의 `CharacterTextSplitter(chunk_size=500, chunk_overlap=50)`와 동일한 개념. 원리를 이해한 뒤 프레임워크로 전환하면 블랙박스가 아니게 된다

### 5. 더 알아야 할 것

- **Recursive Character Splitter**: 문단(`\n\n`) → 줄바꿈(`\n`) → 문장(`. `) → 공백(` `) 순서로 분할을 시도하여 의미 경계를 존중하는 방식. Step 2의 개선 버전으로 구현 가능
- **Parent Document Retriever**: chunk로 검색하되, 실제로 LLM에 전달할 때는 원본의 더 넓은 범위를 가져오는 기법
- **Late Chunking**: 임베딩을 먼저 생성한 뒤에 chunking하는 최신 기법. 토큰 임베딩에 전체 문서의 문맥이 이미 반영되어 있어 품질이 높다

---

## Step 3: 임베딩 (Embedding)

### 1. 무엇을 다루는가? 무엇을 배울 수 있는가?

RAG 파이프라인의 세 번째 단계 — **텍스트를 숫자 벡터로 변환**하는 것을 배운다.

왜 벡터로 변환하는가?
- 컴퓨터는 "metformin"과 "당뇨 치료제"가 비슷한 의미라는 것을 모른다
- 텍스트를 벡터(숫자 배열)로 변환하면 **의미적 유사도를 수학적으로 계산**할 수 있다
- 이것이 "키워드 검색"이 아닌 "의미 검색"을 가능하게 하는 핵심

비유하면: 도서관에서 책을 찾을 때 제목의 글자가 같은 책이 아니라, **내용이 비슷한 책**을 찾아주는 사서를 고용하는 것. 임베딩 모델이 그 사서 역할을 한다.

```
Step 2 출력                              Step 3 (이번)
┌────────────────┐                     ┌──────────────────────────┐
│ list[Document] │    embed_documents  │ list[EmbeddedDocument]   │
│  (~40 chunks)  │ ─────────────────▶  │  각 chunk + 384차원 벡터  │
└────────────────┘                     └──────────────────────────┘

"metformin treats diabetes" → [0.12, -0.34, 0.56, ..., 0.08]  (384개 숫자)
```

### 2. 주의깊게 봐둬야 하는 부분

- **Lazy Loading 패턴**: 모델은 최초 호출 시에만 로드하고 이후 재사용한다 (singleton). `all-MiniLM-L6-v2`는 ~80MB로 매 호출마다 로드하면 비효율적
- **배치 인코딩**: `model.encode(texts)` — 리스트를 한 번에 넘기면 GPU/CPU 병렬 처리로 하나씩 인코딩하는 것보다 훨씬 빠르다
- **embed_query vs embed_documents 분리**: 검색 시에는 쿼리 1개만 임베딩하면 되고, 인덱싱 시에는 수백 개 chunk를 배치 임베딩해야 한다. 용도가 다르므로 분리

### 3. 아키텍처와 동작 원리

```
embed_documents(docs) 동작 흐름:

  list[Document]
    │
    ▼
  검증: 빈 리스트? → [] 반환
  검증: content가 빈 Document? → ValueError
    │
    ▼
  _get_model() ─── 첫 호출: SentenceTransformer("all-MiniLM-L6-v2") 로드
    │              이후 호출: 캐시된 모델 반환
    ▼
  texts = [doc.content for doc in docs]
    │
    ▼
  model.encode(texts) ─── 배치 인코딩 (내부적으로 토크나이즈 → Transformer → Pooling)
    │
    ▼
  zip(docs, vectors) ─── 원본 Document와 벡터를 1:1 매핑
    │
    ▼
  list[EmbeddedDocument] 반환


embed_query(text) 동작 흐름:

  str
    │
    ▼
  _get_model()
    │
    ▼
  model.encode(text) → list[float] (384차원)
```

**파일 구조:**

| 파일 | 역할 |
|------|------|
| `src/rag/embedder.py` | `EmbeddedDocument` dataclass + `embed_documents()` + `embed_query()` |
| `tests/test_embedder.py` | 10개 테스트 (기본, 순서/metadata/유사도, 에러, 통합) |

**sentence-transformers 내부 파이프라인:**

```
입력 텍스트
    │
    ▼
Tokenizer ─── 텍스트 → 토큰 ID 배열 (BPE/WordPiece)
    │
    ▼
Transformer (MiniLM) ─── 토큰별 임베딩 생성 (6 레이어)
    │
    ▼
Pooling (Mean) ─── 토큰 임베딩 → 문장 벡터 1개 (384차원)
    │
    ▼
[0.12, -0.34, 0.56, ..., 0.08]
```

### 4. 개발자로서 알아둬야 할 것들

- **모델 선택 기준**: `all-MiniLM-L6-v2`는 384차원, ~80MB로 로컬 CPU에서도 충분히 빠르다. 프로덕션에서는 `text-embedding-3-small` (OpenAI, 1536차원)이나 `bge-large-en-v1.5` (1024차원) 등을 사용
- **차원 수의 의미**: 384차원 = 텍스트의 의미를 384개의 축으로 표현. 차원이 높을수록 표현력이 좋지만 저장/계산 비용 증가. 실무에서는 768~1536차원이 일반적
- **cosine similarity**: 두 벡터의 방향이 얼마나 비슷한지 측정 (-1 ~ 1). 의미가 비슷한 텍스트는 cosine similarity가 높다. 이것이 Step 5(검색)에서 핵심 역할
- **벡터 정규화**: `all-MiniLM-L6-v2`는 출력 벡터를 자동으로 정규화(norm=1)하므로 cosine similarity = dot product로 계산 가능

**임베딩 모델 비교:**

| 모델 | 차원 | 크기 | API 키 | 속도 | 용도 |
|------|------|------|--------|------|------|
| `all-MiniLM-L6-v2` (이번 구현) | 384 | ~80MB | 불필요 | 빠름 (CPU) | 학습/프로토타입 |
| `text-embedding-3-small` (OpenAI) | 1536 | API | 필요 | API 호출 | 프로덕션 |
| `text-embedding-3-large` (OpenAI) | 3072 | API | 필요 | API 호출 | 고정밀도 |
| `bge-large-en-v1.5` | 1024 | ~1.3GB | 불필요 | 보통 (GPU 권장) | 오프라인 프로덕션 |

### 5. 더 알아야 할 것

- **Matryoshka Representation Learning (MRL)**: 하나의 모델이 여러 차원(64, 128, 256, ..., 768)의 벡터를 동시에 학습하는 기법. 저장 비용을 줄이면서도 품질을 유지할 수 있다
- **Cross-Encoder vs Bi-Encoder**: Bi-Encoder(이번 구현)는 문서와 쿼리를 독립적으로 임베딩. Cross-Encoder는 쿼리-문서 쌍을 함께 인코딩하여 정확도가 높지만 느리다. 실무에서는 Bi-Encoder로 후보를 추린 뒤 Cross-Encoder로 재정렬하는 2단계 방식을 사용
- **Instruction-tuned Embeddings**: 최근 모델(`intfloat/e5-mistral-7b-instruct` 등)은 쿼리 앞에 "query: " 또는 "passage: " 프리픽스를 붙여서 쿼리/문서 임베딩을 구분한다

### Q&A

**Q: embed_query와 embed_documents를 왜 분리하는가? 내부적으로 같은 모델을 쓰는데?**

지금은 같은 모델이지만, 분리해두면 나중에 달라질 수 있다.

1. **프리픽스가 다를 수 있다**: E5 같은 모델은 쿼리에 "query: ", 문서에 "passage: "를 붙인다
2. **배치 최적화**: documents는 수백~수천 개를 한 번에 처리해야 하므로 배치 인코딩이 중요. query는 항상 1개
3. **프레임워크 호환**: LangChain의 `Embeddings` 인터페이스도 `embed_query()`와 `embed_documents()`를 분리한다

비유하면: 식당에서 "1인분 주문"과 "단체 주문"은 같은 메뉴를 쓰지만, 단체 주문은 대량 조리 프로세스로 처리하는 것이 효율적이다.

**Q: 왜 모델을 lazy loading (singleton)으로 관리하는가?**

`SentenceTransformer("all-MiniLM-L6-v2")`를 호출하면:
1. 디스크에서 ~80MB 모델 파일을 읽음
2. 메모리에 Transformer 가중치를 올림
3. 토크나이저를 초기화

이 과정이 첫 호출에 수 초가 걸린다. 매번 새로 로드하면 10개 chunk 임베딩에 수십 초가 소요된다.

```
❌ 매번 로드:
  embed_query() → 3초 (모델 로드) + 0.01초 (인코딩)
  embed_query() → 3초 (모델 로드) + 0.01초 (인코딩)
  총: 6.02초

✅ Singleton:
  embed_query() → 3초 (모델 로드) + 0.01초 (인코딩)
  embed_query() → 0.01초 (인코딩)
  총: 3.02초
```

**Q: 384차원 벡터가 실제로 뭘 나타내는가?**

각 차원은 텍스트의 의미적 특성을 나타낸다. 예를 들어 (실제로는 이렇게 해석 가능하지 않지만 비유적으로):

- 차원 42: "의학 관련도" (metformin → 높음, 날씨 → 낮음)
- 차원 100: "긍정/부정" (치료 → 양수, 부작용 → 음수)
- 차원 200: "시간성" (최신 → 양수, 과거 → 음수)

384개의 축으로 텍스트의 의미를 공간상의 한 점으로 표현한다. 비슷한 의미의 텍스트는 이 공간에서 가까이 위치한다.

비유하면: 지도에서 서울과 부산의 위치를 (위도, 경도) 2차원으로 표현하듯, 텍스트의 "의미 위치"를 384차원으로 표현하는 것. 차원이 많을수록 더 섬세하게 구분할 수 있다.

**Q: chunk와 embedding은 결국 하나의 단위인가?**

맞다. **chunk가 RAG 파이프라인 전체를 관통하는 원자 단위(atomic unit)**다. Step 2에서 chunk가 쪼개지는 순간, 이후 모든 단계의 "단위"가 결정된다.

```
파이프라인에서 chunk의 여정:

  Step 1        Step 2          Step 3           Step 4          Step 5         Step 6
  문서 1개  →  chunk N개  →  chunk+벡터 N개  →  DB에 N행 저장  →  검색: K개 반환  →  LLM에 전달
  Document    Document      EmbeddedDocument    (id, vec, text)   top-K chunks     prompt에 삽입

              ──────────────────────────────────────────────────────────────────
              chunk가 쪼개지는 순간, 이후 모든 단계의 "단위"가 결정된다
```

그래서 **Step 2의 chunk_size 결정이 생각보다 무겁다**. chunk는 단순히 "텍스트를 자르는 크기"가 아니라 파이프라인 전체의 품질을 좌우하는 설계 결정이다.

| chunk가 결정하는 것 | 영향 |
|---|---|
| 임베딩 품질 | 너무 길면 의미가 희석, 너무 짧으면 문맥 부족 |
| 저장 비용 | chunk 수 × 384차원 × 4바이트 = 벡터 DB 크기 |
| 검색 정밀도 | 큰 chunk → 관련 없는 내용도 포함, 작은 chunk → 핵심만 |
| LLM 토큰 소비 | top-K × chunk_size = context에 들어가는 양 |

비유하면: **레고 블록의 크기를 정하는 것**. 블록을 한번 만들면 조립(저장)하고, 찾고(검색), 설명서에 붙이는(LLM 전달) 모든 과정이 그 크기에 맞춰 돌아간다.

이 1:1 관계가 반드시 고정은 아니다. 실무에서 이를 의도적으로 깨는 패턴도 존재한다:

```
일반적인 RAG (지금 구현):
  검색 단위 = chunk = LLM 전달 단위     ← 단순하고 직관적

Parent Document Retriever:
  검색 단위 = 작은 chunk (정밀 검색)
  LLM 전달 = 큰 parent chunk (풍부한 문맥)   ← 검색과 전달을 분리

Late Chunking:
  임베딩 = 문서 전체 (문맥 보존)
  저장 = 이후에 잘라서 저장                   ← 임베딩과 chunking 순서를 뒤집음
```

지금 단계에서는 chunk = 임베딩 = 저장 = 검색 단위로 가는 것이 원리를 이해하기에 적합하고, 이 기본을 알고 있으면 나중에 변형 패턴을 만났을 때 "왜 분리하는지"가 바로 보인다.

**Q: embed_query와 embed_documents는 왜 다른 시점에 쓰이는가?**

두 함수는 입력 타입만 다른 게 아니라, **RAG 파이프라인에서 사용되는 시점과 목적 자체가 다르다.**

- `embed_documents` → **인덱싱 시점** (데이터를 벡터 DB에 넣을 때, 1회)
- `embed_query` → **검색 시점** (사용자가 질문할 때마다 실행)

```
전체 흐름:

═══ 인덱싱 (데이터 준비, 1회) ═══

  문서 → chunk → embed_documents() → 벡터 DB에 저장
                  [0.12, -0.34, ...]    (chunk + 벡터 쌍으로 저장)


═══ 검색 (사용자 질문, 매번) ═══

  "metformin 부작용은?"
         │
         ▼
    embed_query()           ← 질문을 벡터로 변환
    [0.15, -0.30, ...]
         │
         ▼
    벡터 DB에서 유사도 검색   ← 질문 벡터와 가장 가까운 chunk 벡터를 찾음
         │
         ▼
    top-K chunks 반환        ← "이 chunk들이 질문과 가장 관련 있습니다"
         │
         ▼
    LLM에 전달 → 답변 생성
```

벡터 DB 입장에서 보면, 저장된 chunk 벡터들과 질문 벡터 사이의 **cosine similarity를 계산**해서 가장 가까운 것들을 돌려주는 것이다. 같은 모델로 벡터화했기 때문에 의미가 비슷하면 벡터도 가까운 위치에 놓이고, 그래서 "키워드가 같은 문서"가 아니라 "의미가 비슷한 문서"를 찾을 수 있다.

비유하면: 도서관에 책을 꽂아두는 과정(embed_documents)과, 나중에 "이런 내용의 책 찾아주세요"라고 요청하는 과정(embed_query)은 별개다. 단, 같은 분류 체계(같은 임베딩 모델)를 써야 책을 꽂은 위치와 찾는 위치가 일치한다.

---

## Step 4: 벡터 DB 저장 (Vector Store)

### 1. 무엇을 다루는가? 무엇을 배울 수 있는가?

RAG 파이프라인의 네 번째 단계 — **임베딩된 문서를 벡터 DB에 저장하고, 유사도 검색을 수행**하는 것을 배운다.

왜 벡터 DB가 필요한가?
- Step 3에서 만든 임베딩 벡터를 메모리에만 들고 있으면 프로그램 종료 시 사라진다
- 수천~수백만 개의 벡터에서 "가장 비슷한 K개"를 빠르게 찾으려면 전용 인덱싱이 필요하다
- 일반 DB(MySQL, PostgreSQL)는 384차원 벡터의 cosine similarity 검색에 최적화되어 있지 않다

비유하면: Step 3에서 모든 책에 좌표(벡터)를 붙였다면, Step 4는 **그 책들을 서가에 정리하는 것**이다. 서가(벡터 DB)에 넣어야 나중에 "이 좌표 근처의 책 3권 가져와"라고 할 수 있다.

```
Step 3 출력                               Step 4 (이번)
┌──────────────────────┐               ┌────────────────────────────┐
│ list[EmbeddedDocument]│  VectorStore │  ChromaDB Collection        │
│  각 chunk + 384차원   │ ──────────▶  │  (id, embedding, text, meta)│
└──────────────────────┘  add_documents│  + cosine similarity 검색   │
                                       └────────────────────────────┘
                          search()
  query vector ──────────────────────▶  list[SearchResult]
  [0.15, -0.30, ...]                    (document + score) × top_k
```

### 2. 주의깊게 봐둬야 하는 부분

- **Class vs 함수 설계 전환**: Step 1~3은 순수 함수였지만, Step 4부터는 Class(`VectorStore`)를 사용한다. DB client와 collection이라는 **상태**를 관리해야 하기 때문. 상태가 없으면 함수, 상태가 있으면 클래스 — 이 판단 기준이 중요하다
- **cosine distance → score 변환**: ChromaDB는 `distance`를 반환하는데(0이면 동일), 우리가 원하는 건 `similarity`(1이면 동일). `score = 1.0 - distance`로 변환한다
- **결정적 ID 생성**: `"metformin.txt::chunk-3"` 형태의 ID를 만들면 같은 문서를 다시 넣을 때 upsert로 덮어쓴다. UUID를 쓰면 매번 중복 행이 생긴다
- **upsert vs insert**: `upsert`를 사용하면 같은 ID의 문서가 이미 있으면 업데이트, 없으면 삽입. 데이터 파이프라인을 반복 실행해도 안전하다 (멱등성)

### 3. 아키텍처와 동작 원리

```
VectorStore 내부 구조:

  ┌─────────────────────────────────────────────────┐
  │ VectorStore                                     │
  │                                                 │
  │  _client: chromadb.Client (in-memory)           │
  │           또는 PersistentClient (디스크)         │
  │                                                 │
  │  _collection: Collection                        │
  │    ├── name: "rag"                              │
  │    ├── metadata: {"hnsw:space": "cosine"}       │
  │    └── HNSW index (내부 자동 생성)              │
  │                                                 │
  │  add_documents(docs) ─┐                         │
  │    _make_id() ──────────▶ upsert(ids, vecs, ..) │
  │                                                 │
  │  search(query_vec) ───▶ query() ───▶ distance   │
  │                         score = 1 - distance    │
  │                         list[SearchResult]       │
  └─────────────────────────────────────────────────┘


add_documents(docs) 동작 흐름:

  list[EmbeddedDocument]
    │
    ▼
  빈 리스트? → [] 반환 (early return)
    │
    ▼
  각 doc에서 추출:
    ids        = [_make_id(doc) for doc]     ← "file.txt::chunk-0"
    embeddings = [doc.embedding for doc]     ← 384차원 벡터
    documents  = [doc.document.content]      ← 원본 텍스트
    metadatas  = [doc.document.metadata]     ← filename, chunk_index 등
    │
    ▼
  collection.upsert(ids, embeddings, documents, metadatas)
    │
    ▼
  ids 반환


search(query_embedding, top_k) 동작 흐름:

  query_embedding (384차원)
    │
    ▼
  count() == 0? → [] 반환 (early return)
    │
    ▼
  collection.query(
    query_embeddings=[query_vec],
    n_results=min(top_k, count()),
    include=["documents", "metadatas", "distances"]
  )
    │
    ▼
  각 결과에 대해:
    score = 1.0 - distance
    Document(content, metadata) 재구성
    │
    ▼
  list[SearchResult] 반환 (score 내림차순, 유사한 것이 앞)


_make_id(doc) 로직:

  metadata에 filename + chunk_index가 있으면:
    → "metformin.txt::chunk-0"  (결정적, upsert 안전)

  없으면:
    → UUID4  (비결정적, 매번 새 행)
```

**파일 구조:**

| 파일 | 역할 |
|------|------|
| `src/rag/store.py` | `SearchResult` dataclass + `VectorStore` class |
| `tests/test_store.py` | 10개 테스트 (기본 동작, 검색 품질, 에러 처리, 통합) |

**Step별 설계 비교:**

| Step | 모듈 | 상태 | 설계 | 이유 |
|------|------|------|------|------|
| 1 | loader.py | 없음 | 순수 함수 | 파일 읽기는 입력→출력 매핑 |
| 2 | splitter.py | 없음 | 순수 함수 | 텍스트 분할은 입력→출력 매핑 |
| 3 | embedder.py | 모델 (숨겨진 singleton) | 순수 함수 | 모델 로딩은 내부에서 캐싱, 외부는 무상태로 보임 |
| **4** | **store.py** | **DB client + collection** | **Class** | **사용자가 어떤 DB, 어떤 collection을 쓸지 제어해야 함** |

### 4. 개발자로서 알아둬야 할 것들

- **ChromaDB의 내부 인덱스**: HNSW (Hierarchical Navigable Small World) 알고리즘을 사용한다. 모든 벡터 쌍을 비교하는 brute-force(O(n))가 아니라, 그래프 기반 근사 검색(ANN)으로 O(log n)에 가까운 속도를 낸다. 정확도를 약간 희생하고 속도를 얻는 트레이드오프
- **in-memory vs persistent**: `persist_directory=None`이면 메모리에만 존재 (테스트용). 경로를 지정하면 디스크에 저장되어 프로그램 재시작 후에도 유지
- **distance function 선택**: `"cosine"`, `"l2"` (유클리드), `"ip"` (내적) 중 선택. 정규화된 벡터(`all-MiniLM-L6-v2`의 경우)에서는 세 가지가 수학적으로 동일한 순서를 만들지만, cosine이 가장 직관적
- **metadata 타입 제한**: ChromaDB는 metadata 값으로 `str`, `int`, `float`, `bool`만 허용한다. dict나 list는 저장 불가. 복잡한 메타데이터는 JSON 문자열로 직렬화해야 한다

**벡터 DB 비교:**

| DB | 특징 | 적합한 규모 | 비고 |
|------|------|------------|------|
| **ChromaDB** (이번 구현) | 임베디드, Python 네이티브 | ~100만 | 프로토타입, 학습용 |
| Pinecone | 관리형 SaaS | 수억 | 서버리스, 비용 발생 |
| Weaviate | 셀프호스팅/클라우드 | 수억 | GraphQL API, 모듈 시스템 |
| Qdrant | 셀프호스팅/클라우드 | 수억 | Rust 기반, 고성능 필터링 |
| pgvector | PostgreSQL 확장 | ~수백만 | 기존 PostgreSQL 인프라 활용 |
| FAISS (Meta) | 라이브러리 (DB 아님) | 수십억 | GPU 지원, 인덱스만 제공 |

### 5. 더 알아야 할 것

- **HNSW 파라미터 튜닝**: `ef_construction` (인덱스 빌드 품질), `ef_search` (검색 품질), `M` (연결 수). 높을수록 정확하지만 느리고 메모리를 많이 쓴다
- **Hybrid Search**: 벡터 유사도 + 키워드 매칭(BM25)을 결합하는 방식. "metformin"이라는 정확한 키워드가 중요한 경우 벡터만으로는 놓칠 수 있다
- **Namespace/Multi-tenancy**: 하나의 벡터 DB에서 사용자별, 프로젝트별로 데이터를 격리하는 패턴. ChromaDB에서는 collection을 나누거나 metadata 필터링으로 구현
- **Vector DB vs 전통 DB**: 전통 DB는 정확한 매칭(WHERE id = 123)에 최적화, 벡터 DB는 근사 매칭(이 벡터와 가장 비슷한 K개)에 최적화. 용도가 근본적으로 다르다

### Q&A

**Q: 왜 Class로 설계했는가? Step 3처럼 함수로 할 수 없나?**

할 수는 있지만, 매 호출마다 DB client를 생성하고 collection을 열어야 한다. 이것은 비효율적이고, "어떤 collection에 저장하고 어떤 collection에서 검색하는지"를 사용자가 제어할 수 없게 된다.

```
❌ 함수 방식:
  add_documents(docs, collection_name="rag")   # 매번 client 생성?
  search(vec, collection_name="rag")            # 또 client 생성?

✅ Class 방식:
  store = VectorStore("rag")                    # 1회 생성
  store.add_documents(docs)                     # 같은 collection 재사용
  store.search(vec)                             # 같은 collection 재사용
```

비유하면: 서랍장을 쓸 때 매번 "서랍장을 새로 사서 물건을 넣고 버리는" 것(함수)과, "서랍장 하나를 두고 계속 쓰는" 것(클래스)의 차이. 서랍장이라는 상태를 유지해야 의미가 있다.

**Q: `score = 1.0 - distance`가 정확한가?**

ChromaDB의 cosine distance는 `1 - cosine_similarity`로 정의된다. 따라서:

| cosine similarity | cosine distance | score (1 - distance) |
|---|---|---|
| 1.0 (동일) | 0.0 | 1.0 |
| 0.5 (약간 유사) | 0.5 | 0.5 |
| 0.0 (무관) | 1.0 | 0.0 |
| -1.0 (반대) | 2.0 | -1.0 |

즉 `score = 1.0 - distance = cosine_similarity`가 된다. 수학적으로 정확하다.

**Q: upsert가 왜 insert보다 안전한가?**

데이터 파이프라인은 반복 실행될 수 있다. 에러로 중단된 후 재실행하거나, 문서를 업데이트한 후 다시 인덱싱할 수 있다.

```
insert를 쓰면:
  1차 실행: chunk-0, chunk-1, chunk-2 삽입 ✅
  2차 실행: chunk-0 중복! → 에러 or 중복 행 생성 ❌

upsert를 쓰면:
  1차 실행: chunk-0, chunk-1, chunk-2 삽입 ✅
  2차 실행: chunk-0 이미 있음 → 덮어쓰기 ✅ (항상 최신 상태)
```

이것이 바로 **멱등성(idempotency)** — 같은 연산을 여러 번 실행해도 결과가 같다. 데이터 파이프라인에서 매우 중요한 성질이다.

**Q: 검색 결과에서 원본 Document가 아니라 새 Document를 만드는 이유는?**

ChromaDB에 저장할 때 Document 객체 자체를 저장하는 것이 아니라, content(str)와 metadata(dict)를 분해해서 저장한다. 검색할 때 ChromaDB가 돌려주는 것도 문자열과 딕셔너리이므로, 이것을 다시 Document로 조립해야 한다.

```
저장 시:  EmbeddedDocument.document → 분해 → content, metadata로 저장
검색 시:  ChromaDB 결과 → content, metadata → 새 Document 조립

원본 객체 ≠ 검색 결과 객체 (내용은 동일)
```

비유하면: 택배를 보낼 때 상자를 분해해서 납작하게 보내고(저장), 받는 쪽에서 다시 조립하는 것(검색). 내용물은 같지만 상자 자체는 다르다.

**Q: `get_or_create_collection`은 무슨 역할인가?**

ChromaDB client의 메서드로, **collection이 있으면 가져오고, 없으면 새로 만드는** 함수다.

```
get_or_create_collection("rag")

  "rag" collection이 이미 존재?
    │
    ├── Yes → 기존 collection 반환 (데이터 유지)
    │
    └── No  → 새 collection 생성 후 반환 (빈 상태)
```

ChromaDB에는 비슷한 함수가 3개 있다:

| 메서드 | 있을 때 | 없을 때 |
|--------|---------|---------|
| `create_collection` | **에러 발생** | 새로 생성 |
| `get_collection` | 기존 반환 | **에러 발생** |
| `get_or_create_collection` | 기존 반환 | 새로 생성 |

`get_or_create_collection`은 **어떤 상황에서든 에러가 나지 않는다**. 처음 실행하든, 두 번째 실행하든 안전하게 동작한다.

비유하면: 도서관에 가서 "한국사 코너 있으면 안내해주고, 없으면 새로 만들어주세요"라고 하는 것. `create_collection`은 "한국사 코너를 만들어주세요"인데, 이미 있으면 "이미 있잖아요!" 하고 거절당하는 것이고, `get_collection`은 "한국사 코너 어디예요?"인데 없으면 "그런 코너 없어요!" 하는 것.

이 패턴 덕분에 `VectorStore("rag")`를 여러 번 인스턴스화해도 기존 데이터가 날아가지 않는다. DB의 `CREATE TABLE IF NOT EXISTS`와 같은 개념이다.

**Q: Collection을 여러 개 만들 수 있는가? metadata 설정 기준은?**

먼저 `metadata={"hnsw:space": "cosine"}`는 일반적인 key-value metadata가 아니라, ChromaDB가 인식하는 **예약된 설정값**이다.

```
metadata={"hnsw:space": "cosine"}
          ──────────── ────────
          HNSW 인덱스    거리 함수
          설정 네임스페이스
```

설정 가능한 거리 함수:

| 값 | 수식 | 의미 | 언제 쓰는가 |
|------|------|------|------------|
| `cosine` | 1 - cos(A,B) | 방향(의미) 비교 | **텍스트 임베딩 (가장 일반적)** |
| `l2` | 유클리드 거리 | 절대 위치 비교 | 이미지, 수치 데이터 |
| `ip` | 내적 (dot product) | 정규화된 벡터에서 cosine과 동일 | 이미 정규화된 벡터 |

비유하면: 서가를 만들 때 "이 서가는 **주제별**로 정리합니다(cosine)" vs "이 서가는 **페이지 수**로 정리합니다(l2)"를 결정하는 것. 한번 서가를 만들면 정리 방식은 바꿀 수 없다 (collection 재생성 필요).

그리고 collection은 여러 개 만들 수 있다:

```python
# 업무 A, B, C 각각 독립된 collection
store_a = VectorStore(collection_name="business-a")
store_b = VectorStore(collection_name="business-b")
store_c = VectorStore(collection_name="business-c")

# A 업무 문서는 A에만 저장
store_a.add_documents(business_a_docs)

# B 업무에서 검색하면 B 문서만 나옴
store_b.search(query_vec)  # → business-b 문서만 검색됨
```

```
ChromaDB Client
├── collection: "business-a"   ← A 업무 문서만
│   ├── chunk-0: "A 프로젝트 요구사항..."
│   ├── chunk-1: "A 프로젝트 일정..."
│   └── chunk-2: "A 프로젝트 예산..."
│
├── collection: "business-b"   ← B 업무 문서만
│   ├── chunk-0: "B 계약서 1조..."
│   └── chunk-1: "B 계약서 2조..."
│
└── collection: "business-c"   ← C 업무 문서만
    ├── chunk-0: "C 보고서 개요..."
    └── chunk-1: "C 보고서 결론..."
```

왜 나누는가?

| 전략 | 장점 | 단점 |
|------|------|------|
| **collection 분리** (A, B, C 따로) | 검색 범위가 좁아서 빠르고 정확, 데이터 격리 | collection 간 교차 검색 불가 |
| **하나의 collection + metadata 필터** | 교차 검색 가능, 관리 단순 | 검색 범위가 넓어서 노이즈 가능 |

metadata 필터 방식은 이렇게 생겼다:

```python
# 하나의 collection에 전부 넣되, business 필드로 구분
store = VectorStore(collection_name="all-business")

# 검색 시 필터링 (ChromaDB의 where 파라미터)
collection.query(
    query_embeddings=[query_vec],
    where={"business": "A"},   # A 업무 문서만 검색
)
```

실무에서의 선택 기준:

```
질문: "A 업무 검색할 때 B, C 문서가 섞여 나와도 되나?"

  Yes → 하나의 collection + metadata 필터
        (예: 전사 지식 검색, FAQ 통합 검색)

  No  → collection 분리
        (예: 고객사별 데이터 격리, 보안 등급이 다른 문서)
```

비유하면: 사무실에서 **캐비닛을 따로 두는 것**(collection 분리) vs **하나의 캐비닛에 폴더 라벨을 붙이는 것**(metadata 필터). 보안이 중요하면 캐비닛을 따로 두고 잠금장치를 달고, 편의성이 중요하면 하나의 캐비닛에서 라벨로 구분하는 것이 낫다.

**Q: HNSW와 ANN은 어떤 관계인가?**

ANN은 **문제의 이름**이고, HNSW는 그 문제를 **푸는 방법(알고리즘) 중 하나**다.

```
ANN (Approximate Nearest Neighbor)
"100만 개 벡터 중에서 쿼리와 가장 비슷한 K개를 빠르게 찾아라"
  │
  ├── HNSW        ← ChromaDB, Qdrant, pgvector
  ├── IVF         ← FAISS, Milvus
  ├── LSH         ← 대규모 중복 탐지
  ├── ANNOY       ← Spotify (추천 시스템)
  ├── ScaNN       ← Google
  └── DiskANN     ← Microsoft (디스크 기반)
```

비유하면: "서울에서 부산까지 빠르게 가라"가 **문제(ANN)**이고, KTX / 비행기 / 자동차가 **풀이법(알고리즘)**이다.

가장 단순한 방법은 **전수 조사(brute-force)** — 100만 개 벡터를 하나씩 전부 비교하는 것이다. 정확하지만 O(n)으로 느리다. ANN은 "정확한 답을 약간 포기하고, 거의 맞는 답을 빠르게 찾자"는 접근이다.

```
Nearest Neighbor 검색
├── Exact NN (정확한 검색)
│     모든 벡터를 전부 비교 → 100% 정확, 느림 (O(n))
│
└── Approximate NN (근사 검색) ← ANN
      일부만 비교하거나 구조를 활용 → ~99% 정확, 빠름 (O(log n))
      ├── HNSW
      ├── IVF
      └── ...
```

HNSW (Hierarchical Navigable Small World)는 벡터들을 **계층적 그래프**로 연결해두고, 위층에서 대략적으로 찾은 뒤 아래층에서 정밀하게 찾는 방식이다.

```
Layer 2 (최상위, 노드 적음)     ●─────────────────●
                                 장거리 점프로 대략적 위치 파악
                                │
Layer 1 (중간)              ●───●───●─────●───●
                                 중거리 이동
                                    │
Layer 0 (최하위, 모든 노드)  ●─●─●─●─●─●─●─●─●─●─●─●─●
                                 근거리 정밀 탐색
```

비유하면 **지도 앱에서 길 찾기**와 같다:

```
Layer 2:  세계 지도에서 "한국" 찾기          ← 대륙 단위 점프
Layer 1:  한국 지도에서 "서울" 찾기          ← 도시 단위 점프
Layer 0:  서울 지도에서 "강남역 2번 출구" 찾기 ← 블록 단위 정밀 탐색
```

주요 ANN 알고리즘 비교:

| | HNSW | IVF | LSH |
|------|------|-----|-----|
| **원리** | 계층 그래프 탐색 | 구역(cluster)으로 나눠서 해당 구역만 탐색 | 비슷한 벡터가 같은 해시 버킷에 들어가도록 설계 |
| **정확도** | 매우 높음 (~99%) | 높음 (~95%) | 보통 (~90%) |
| **검색 속도** | 빠름 | 빠름 | 매우 빠름 |
| **메모리** | 많음 (그래프 저장) | 보통 | 적음 |
| **인덱스 구축** | 느림 | 보통 (클러스터링) | 빠름 |
| **사용처** | ChromaDB, Qdrant, pgvector | FAISS, Milvus | 대규모 중복 탐지 |

비유하면:

```
HNSW  = 지도 앱 (세계→도시→블록 순서로 정밀 탐색)
        장점: 정확함  |  단점: 지도 데이터가 메모리에 필요

IVF   = 도서관 분류 체계 (과학 코너 → 그 안에서만 찾기)
        장점: 단순함  |  단점: 코너 경계에 있는 책을 놓칠 수 있음

LSH   = 색깔별 바구니 (빨간 바구니, 파란 바구니에 대충 분류)
        장점: 엄청 빠름  |  단점: 분류가 부정확할 수 있음
```

ChromaDB가 HNSW를 선택한 이유: RAG에서는 검색 결과가 LLM 답변 품질을 직접 좌우하므로, 속도를 약간 희생하더라도 **정확도가 높은 HNSW가 적합**하다.

```
RAG에서의 우선순위:

  정확도 > 속도 > 메모리

  → HNSW가 최적 (정확도 최상, 속도 충분, 메모리는 감수)
```

"근사"라는 것은 **가끔 진짜 1위가 아니라 2위를 1위로 반환할 수 있다**는 뜻이다. 하지만 RAG에서는 top-5를 가져와서 LLM에 넘기므로, 1위와 2위가 바뀌어도 실질적 영향이 거의 없다. 대규모(수십억 벡터)에서는 HNSW의 메모리 문제가 심각해지므로, FAISS의 IVF+PQ(Product Quantization) 같은 압축 기법을 조합해서 사용하지만, 학습 규모에서는 HNSW가 가장 직관적이고 성능이 좋다.
