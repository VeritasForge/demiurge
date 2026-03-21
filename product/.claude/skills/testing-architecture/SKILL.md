---
description: Test Pyramid, Contract Testing, TDD/BDD, LLM Evaluation, LLM-as-Judge
user-invocable: false
---

# Testing Architecture Skill

테스트 피라미드, Contract Testing, TDD/BDD 패턴, LLM Evaluation을 담당합니다.

## 핵심 역량

### Test Pyramid (Martin Fowler)

```
                    ┌───────┐
                   /   E2E   \         느림, 비용 높음
                  /───────────\        실제 사용자 시나리오
                 /─────────────\
                / Integration   \      중간 속도
               /─────────────────\     서비스 간 연동
              /───────────────────\
             /      Unit Tests     \   빠름, 비용 낮음
            /───────────────────────\  비즈니스 로직 검증
           └─────────────────────────┘

권장 비율: Unit(70%) : Integration(20%) : E2E(10%)
```

### Test Types

| 유형 | 범위 | 속도 | 목적 |
|------|------|------|------|
| **Unit** | 함수/클래스 | ms | 비즈니스 로직 |
| **Integration** | 모듈/서비스 간 | 초 | 연동 검증 |
| **E2E** | 전체 시스템 | 분 | 사용자 시나리오 |
| **Contract** | API 경계 | ms | 계약 준수 |
| **Performance** | 시스템 | 분~시간 | 성능 한계 |

### Contract Testing

```
┌─────────────────────────────────────────────────────────┐
│                Consumer-Driven Contracts                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Consumer                        Provider               │
│  ┌────────────┐                 ┌────────────┐          │
│  │ Consumer A │──┐              │            │          │
│  └────────────┘  │   Contract   │  Provider  │          │
│  ┌────────────┐  ├───Broker────>│   Service  │          │
│  │ Consumer B │──┘              │            │          │
│  └────────────┘                 └────────────┘          │
│                                                          │
│  Flow:                                                  │
│  1. Consumer writes contract (expected request/response) │
│  2. Contract stored in broker (Pact, Spring Cloud)      │
│  3. Provider verifies contract in CI                    │
│  4. Breaking changes detected before deployment         │
└─────────────────────────────────────────────────────────┘
```

### Test Double Types

| 유형 | 설명 | 사용 시점 |
|------|------|-----------|
| **Dummy** | 전달만, 사용 안함 | 파라미터 채우기 |
| **Stub** | 고정된 응답 반환 | 의존성 대체 |
| **Spy** | 호출 기록 | 호출 검증 |
| **Mock** | 기대값 검증 | 행동 검증 |
| **Fake** | 간단한 구현체 | In-memory DB |

### TDD Cycle

```
    ┌─────────────────────────────────────┐
    │                                      │
    ▼                                      │
┌───────┐     ┌───────┐     ┌───────────┐ │
│  RED  │────>│ GREEN │────>│ REFACTOR  │─┘
└───────┘     └───────┘     └───────────┘
 실패하는      통과하는       코드 개선
 테스트        테스트          (중복 제거)
  작성          작성

Outside-In TDD:
E2E → Integration → Unit (Acceptance Test 먼저)

Inside-Out TDD:
Unit → Integration → E2E (단위 테스트 먼저)
```

### BDD (Behavior-Driven Development)

```gherkin
Feature: 환자 조회
  Scenario: 존재하는 환자 조회
    Given 환자 ID "P001"이 시스템에 등록되어 있다
    When 환자 ID "P001"로 조회한다
    Then 환자 정보가 반환된다
    And 상태 코드는 200이다

  Scenario: 존재하지 않는 환자 조회
    Given 환자 ID "P999"가 시스템에 없다
    When 환자 ID "P999"로 조회한다
    Then 404 에러가 반환된다
```

### Testing Hexagonal Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Test Strategy                        │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Unit Tests (Domain):                                  │
│  • Entity 비즈니스 로직                                │
│  • Value Object 불변성                                 │
│  • Domain Service                                      │
│                                                         │
│  Integration Tests (Ports):                            │
│  • Input Port + Use Case                               │
│  • Use Case + Output Port (with Fake)                  │
│                                                         │
│  Adapter Tests:                                        │
│  • REST Controller (MockMvc)                           │
│  • Repository (@DataJpaTest)                           │
│  • Message Consumer                                    │
│                                                         │
│  E2E Tests:                                            │
│  • 전체 흐름 (TestContainers)                          │
└────────────────────────────────────────────────────────┘
```

### Test Data Management

| 전략 | 설명 | 적합한 테스트 |
|------|------|---------------|
| **Builder Pattern** | 테스트 객체 생성 | Unit |
| **Object Mother** | 공통 테스트 객체 | Unit, Integration |
| **Test Fixtures** | 사전 정의된 데이터 | Integration |
| **TestContainers** | 실제 DB/MQ 컨테이너 | Integration, E2E |

### Code Coverage Guidelines

| 레이어 | 권장 커버리지 | 설명 |
|--------|---------------|------|
| Domain | 90%+ | 핵심 비즈니스 로직 |
| Application | 80%+ | Use Case |
| Infrastructure | 70%+ | 외부 연동 |
| UI/Controller | 60%+ | 얇은 레이어 |

## 평가 체크리스트

- [ ] Test Pyramid 비율 준수?
- [ ] Contract Test 구현? (MSA)
- [ ] 핵심 도메인 로직 테스트 충분?
- [ ] 테스트 격리 (독립 실행)?
- [ ] CI에서 자동 실행?
- [ ] 테스트 데이터 관리 전략?

## LLM Evaluation

### LLM Test Pyramid

```
                  ┌─────────┐
                 / Red Team  \         수동, 비용 높음
                /─────────────\        보안 + 엣지 케이스
               / Human Eval   \       전문가 평가
              /─────────────────\
             / LLM-as-Judge     \     자동, 유연
            /─────────────────────\    GPT-4: 85% human agreement
           / RAGAS + Unit Eval    \   자동, 빠름
          /─────────────────────────\  Faithfulness, Relevancy
         └───────────────────────────┘
```

### RAGAS 핵심 메트릭

| 메트릭 | 측정 대상 | 공식 |
|--------|----------|------|
| **Faithfulness** | 답변이 컨텍스트 기반인가 | 지지되는 문장 / 전체 문장 |
| **Answer Relevancy** | 답변이 질문에 적합한가 | 역생성 질문 유사도 |
| **Context Precision** | 검색 결과 정밀도 | 관련 문서 순위 기반 |
| **Context Recall** | 검색 결과 재현율 | Ground Truth 대비 |

### LLM-as-Judge 패턴

```python
# Pointwise Evaluation
judge_prompt = """
Rate the following response on a scale of 1-5:
- Accuracy: {criteria}
- Response: {response}
- Reference: {reference}
Score:
"""

# Pairwise Comparison
compare_prompt = """
Which response is better? A or B?
- Question: {question}
- Response A: {response_a}
- Response B: {response_b}
Winner:
"""
```

**주의**: Position Bias (~40%) → 순서 교체 후 평균

### Regression Testing for LLM

```yaml
# CI/CD 통합 (promptfoo)
on:
  push:
    paths: ['prompts/**', 'config/**']

jobs:
  eval:
    steps:
      - run: promptfoo eval -c eval_config.yaml
      - run: |
          if [ "$SCORE" -lt "$THRESHOLD" ]; then
            echo "Regression detected!" && exit 1
          fi
```

**발견**: 58.8% 프롬프트+모델 조합에서 API 업데이트 시 정확도 하락 발생

### Eval Framework 비교

| Framework | 특화 | CI/CD | 가격 |
|-----------|------|-------|------|
| **RAGAS** | RAG 메트릭 | ✅ | OSS |
| **DeepEval** | 종합 메트릭 | ✅ | OSS |
| **Promptfoo** | 프롬프트 반복 | ✅ | OSS |
| **Braintrust** | Eval + Observability | ✅ | SaaS |

## 사용 시점
- 테스트 전략 수립
- Contract Testing 도입
- TDD/BDD 적용
- 테스트 커버리지 개선
- 테스트 인프라 설계
- LLM Evaluation 파이프라인 설계
- RAG 품질 평가 (RAGAS)
- LLM Regression Testing 구축
- Red Teaming 전략 수립

## 참고 조사
- LLM Evaluation 상세: [research/ai-backend/evaluation.md](../../../research/ai-backend/evaluation.md)
