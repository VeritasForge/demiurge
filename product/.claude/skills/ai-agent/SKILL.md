---
description: AI Agent 아키텍처, ReAct, Multi-Agent, Workflow Orchestration, MCP, State Management
user-invocable: false
---

# AI Agent Skill

AI Agent 아키텍처 패턴, Multi-Agent 시스템, Workflow Orchestration, Tool Use를 설계합니다.

## 핵심 역량

### Agent 패턴 계보

```
Simple Chain ──> ReAct ──> Plan-and-Execute ──> Multi-Agent
  (2022)        (2023)      (2024)              (2026)

추세: 2026년 엔터프라이즈 앱 40%에 Agent 탑재 예측 (Gartner)
```

### Agent 아키텍처 패턴

| 패턴 | 핵심 아이디어 | 복잡도 | 적합 시나리오 |
|------|-------------|--------|-------------|
| **ReAct** | Thought→Action→Observation 루프 | 낮음 | 단일 도구, 간단한 태스크 |
| **ReWOO** | 계획을 먼저 수립 후 실행 | 낮음 | 토큰 절약 필요 시 |
| **Plan-and-Execute** | 별도 Planner + Executor | 중간 | 복잡한 다단계 태스크 |
| **LATS** | Tree Search + Self-reflection | 높음 | 탐색 공간 큰 문제 |
| **Reflexion** | 실패 시 자기 반성 후 재시도 | 중간 | 학습 필요한 태스크 |

### ReAct 루프

```
┌──────────────────────────────────────┐
│  Thought: "가격을 알아봐야 한다"      │
│     ↓                                │
│  Action: search_product("iPhone 16") │
│     ↓                                │
│  Observation: "₩1,390,000"           │
│     ↓                                │
│  Thought: "가격을 알았으니 비교하자"  │
│     ↓                                │
│  ... (루프 반복)                     │
│     ↓                                │
│  Final Answer: "..."                 │
└──────────────────────────────────────┘
```

### Multi-Agent 패턴

```
┌─── Supervisor Pattern ────────────────┐
│                                        │
│      ┌────────────┐                   │
│      │ Supervisor │ ← 태스크 분배     │
│      └─────┬──────┘                   │
│       ┌────┼────┐                     │
│       ▼    ▼    ▼                     │
│     Agent Agent Agent                 │
│       A    B    C                     │
└────────────────────────────────────────┘

┌─── Hierarchical Pattern ──────────────┐
│                                        │
│      ┌──────────────┐                 │
│      │   Manager    │                 │
│      └──────┬───────┘                 │
│        ┌────┴────┐                    │
│        ▼         ▼                    │
│   ┌────────┐ ┌────────┐              │
│   │ Team A │ │ Team B │              │
│   │Lead    │ │Lead    │              │
│   └──┬──┬──┘ └──┬──┬──┘              │
│      ▼  ▼       ▼  ▼                 │
│     W1 W2      W3 W4   Workers      │
└────────────────────────────────────────┘

┌─── Handoff Pattern ───────────────────┐
│                                        │
│  Agent A ──handoff──> Agent B         │
│     │                    │             │
│     └──<──handoff──<─────┘             │
│  (전문 영역에 따라 위임)               │
└────────────────────────────────────────┘
```

### State Management

| 유형 | 범위 | 지속성 | 예시 |
|------|------|--------|------|
| **Working Memory** | 현재 턴 | 휘발 | 현재 추론 컨텍스트 |
| **Short-term** | 세션 | 세션 종료 시 소멸 | 대화 히스토리 |
| **Long-term** | 영구 | 영구 저장 | 사용자 선호도 |
| **Episodic** | 에피소드 | 선택적 | 과거 성공/실패 경험 |

**체크포인팅 권장사항**:
- 각 Agent Step 후 상태 저장
- 직렬화 가능한 상태 설계 (JSON/Protobuf)
- 실패 시 마지막 체크포인트에서 재개

### Tool Use & MCP (Model Context Protocol)

```
┌─── MCP 아키텍처 ──────────────────────┐
│                                        │
│  Agent ──MCP Client──> MCP Server     │
│                          │             │
│                    ┌─────┴─────┐       │
│                    │  Tools    │       │
│                    │  Resources│       │
│                    │  Prompts  │       │
│                    └───────────┘       │
│                                        │
│  "AI의 USB-C" — 표준화된 도구 연결    │
└────────────────────────────────────────┘
```

### Workflow Orchestration

| 엔진 | 유형 | 강점 | 적합 시나리오 |
|------|------|------|-------------|
| **LangGraph** | Graph-based | 토큰 효율, 유연한 흐름 제어 | 복잡한 조건 분기 |
| **Temporal** | Durable Execution | 장기 실행, 복구, 타이머 | 미션 크리티컬 |
| **CrewAI** | Role-based | 빠른 프로토타이핑 | 역할 분담 명확할 때 |

### 프레임워크 비교

| Framework | 진입장벽 | 유연성 | 프로덕션 | 적합 |
|-----------|---------|--------|---------|------|
| **LangGraph** | 중간 | 높음 | 높음 | 복잡한 워크플로우 |
| **CrewAI** | 낮음 | 중간 | 중간 | 빠른 프로토타입 |
| **AutoGen** | 중간 | 높음 | 중간 | 연구/실험 |
| **OpenAI Agents SDK** | 낮음 | 낮음 | 높음 | OpenAI 생태계 |
| **Semantic Kernel** | 중간 | 중간 | 높음 | .NET/Azure 환경 |

## 의사결정 매트릭스

```
        ┌──────────────┐
        │ 태스크 복잡도? │
        └──────┬───────┘
        단순   │   복잡
    ┌──────────┴───────────┐
    ▼                       ▼
Simple Chain/       ┌───────────────┐
ReAct              │ 도구 수?       │
                   └──────┬────────┘
                  1-3개   │   4개+
              ┌───────────┴────────────┐
              ▼                         ▼
        Plan-and-Execute          Multi-Agent
                                  (Supervisor)
```

## 프로덕션 체크리스트
- [ ] Agent 행동 범위 제한 (action limits)
- [ ] Human-in-the-Loop 승인 게이트
- [ ] Tool 실행 샌드박싱
- [ ] 비용 제어 (max tokens, max steps)
- [ ] 타임아웃 설정 (agent 무한 루프 방지)
- [ ] 관찰 가능성 (각 step 트레이싱)

## 사용 시점
- AI Agent 시스템 설계
- Multi-Agent 아키텍처 설계
- Workflow/Orchestration 엔진 선택
- Tool Use / MCP 통합 설계
- Agent Safety & Control 설계

## 참고 조사
- 상세 조사: [research/ai-backend/agent-orchestration.md](../../../research/ai-backend/agent-orchestration.md)
