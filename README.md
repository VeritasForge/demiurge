# Demiurge

**Shaping Claude Code into an omnipotent architect-creator.**

---

## The Name: Demiurge (데미우르고스)

In Plato's *Timaeus*, the **Demiurge** (δημιουργός) is the divine craftsman who gazes upon eternal Forms and shapes the raw, chaotic material of the cosmos into an ordered universe. Not a god who creates from nothing, but an artisan who *molds* what already exists into something purposeful.

In the Gnostic tradition, the Demiurge is the creator who fashions the entire physical world — the bridge between abstract intention and concrete reality.

This project carries that name deliberately. Claude Code is powerful raw material — a general-purpose AI coding assistant. **Demiurge** is the configuration that molds it into an all-capable architect and builder. Just as the mythic Demiurge shapes cosmos from chaos, this project shapes Claude Code from a blank slate into a structured, governed, multi-specialist system that can reason about any software architecture challenge.

## Philosophy (철학)

Demiurge is built on a single conviction: **the right structure of knowledge and governance can make Claude Code omnipotent for software engineering.**

This repository contains no source code. It is a **meta-configuration** — a carefully designed system of agents, rules, skills, and orchestration protocols. The belief is that:

- A well-defined cast of specialist architects, each with deep domain knowledge, can collectively reason about any system design problem.
- Governance rules automatically applied at the right boundaries enforce quality without manual oversight.
- An orchestration protocol with tiered review, parallel evaluation, and consensus voting produces decisions superior to any single perspective.
- Knowledge, not code, is the lever. The right patterns, principles, and frameworks — structured for retrieval — make Claude Code an expert in any architectural domain.

Demiurge doesn't build software. It makes Claude Code capable of building *anything*.

## What This Is

A **multi-agent architecture governance template** for Claude Code:

- **16 agents** — 12 specialist architects + 4 investigation agents
- **18 skill cards** — architecture patterns, investigation orchestration, deep research, job analysis, and more
- **8 governance rules** — auto-applied based on file paths
- **2 orchestration systems** — architect review (consensus protocol) + investigation (evidence-based judgment)

No application code. No runtime dependencies. Pure `.claude/` configuration.

## How It Works

### Orchestration Flow

```
[Requirement] → [Analysis & Routing] → [Tier 1: Strategic] → [Tier 2: Design] → [Tier 3: Quality] → [Consensus] → [Result]
                                         (Sequential)          (Parallel)         (Parallel)          (Round-based voting)
```

### Agent Tiers

| Tier | Agents | Execution |
|------|--------|-----------|
| **1 Strategic** (required) | Solution Architect, Domain Architect | Sequential |
| **2 Design** (conditional) | Application, Data, Integration, Healthcare Informatics | Parallel |
| **3 Quality** (conditional) | Security, SRE, Cloud-Native | Parallel |
| **4 Enabling** (on-demand) | EDA Specialist, ML Platform, Concurrency | On-demand |
| **Investigation** (on-demand) | Code, Log, History Investigators + Counter-Reviewer | Parallel |

### Consensus Protocol

- **Threshold**: 2/3 agreement (67%)
- **Veto power**: Tier 1 architects
- **Max rounds**: 5
- **Minority opinions**: always recorded

## Usage

### Multi-agent orchestration (complex, cross-cutting decisions)

```
/architect-orchestration 스킬을 실행하여 요구사항 분석 및 다중 아키텍트 리뷰 수행
```

### Individual agent review (focused analysis)

```
domain-architect: 도메인 모델 및 Bounded Context 검토
security-architect: 보안 위협 분석 및 암호화 검증
solution-architect: 전체 시스템 아키텍처 설계
```

### Skill reference (quick pattern lookup)

```
.claude/skills/domain-driven-design/SKILL.md
.claude/skills/eda/SKILL.md
.claude/skills/cloud-native/SKILL.md
```

### Codebase investigation (bug, performance, structure analysis)

```
/investigation-orchestration 코드베이스 조사 (버그, 성능, 구조 분석 등)
```

### Documentation sync

```
/wrap          # Analyze + detect drift + update CLAUDE.md
/wrap --check  # Analyze + detect drift only (no changes)
```

## Structure

```
demiurge/
├── CLAUDE.md                          # Project instructions (single source of truth)
├── README.md                          # This file
├── .claude/
│   ├── agents/                        # 16 agent definitions
│   │   ├── solution-architect.md      #   12 architect agents
│   │   ├── domain-architect.md
│   │   ├── application-architect.md
│   │   ├── data-architect.md
│   │   ├── integration-architect.md
│   │   ├── security-architect.md
│   │   ├── sre-architect.md
│   │   ├── cloud-native-architect.md
│   │   ├── eda-specialist.md
│   │   ├── concurrency-architect.md
│   │   ├── ml-platform-architect.md
│   │   ├── healthcare-informatics-architect.md
│   │   ├── code-investigator.md       #   4 investigation agents
│   │   ├── log-investigator.md
│   │   ├── history-investigator.md
│   │   └── counter-reviewer.md
│   ├── rules/                         # 8 governance rules (auto-applied by glob)
│   │   ├── architecture-principles.md
│   │   ├── security-requirements.md
│   │   ├── ddd-patterns.md
│   │   ├── api-design.md
│   │   ├── cloud-native.md
│   │   ├── messaging-patterns.md
│   │   ├── healthcare-compliance.md
│   │   └── architect-review.md
│   ├── skills/                        # 18 skill cards
│   │   ├── architect-orchestration/
│   │   ├── investigation-orchestration/
│   │   ├── deep-research/
│   │   ├── job-analysis/
│   │   ├── solution-architecture/
│   │   ├── domain-driven-design/
│   │   ├── application-architecture/
│   │   ├── eda/
│   │   ├── concurrency-patterns/
│   │   ├── cloud-native/
│   │   ├── api-design/
│   │   ├── testing-architecture/
│   │   ├── data-architecture/
│   │   ├── integration/
│   │   ├── security/
│   │   ├── sre/
│   │   ├── ml-platform/
│   │   └── healthcare-informatics/
│   └── commands/                      # Slash commands
│       ├── commit.md
│       ├── rl.md
│       ├── wrap.md
│       └── save_obsi.md
├── docs/                              # Design documentation
│   ├── investigation-orchestration-system.md       # Deep research (기반 연구)
│   └── investigation-orchestration-implementation.md # 설계/구현 문서
└── adr_1.md
```

## License

This project is a configuration template. Use it however you see fit.
