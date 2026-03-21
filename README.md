# Demiurge

**Claude Code를 전지전능한 아키텍트-창조자로 빚어내다.**

---

## 이름: Demiurge (데미우르고스)

플라톤의 *티마이오스*에서 **데미우르고스**(δημιουργός)는 영원한 형상(Forms)을 응시하며 혼돈의 질료를 질서 있는 우주로 빚어내는 신적 장인이다. 무에서 창조하는 신이 아니라, 이미 있는 것을 목적에 맞게 *형상화*하는 존재다.

이 프로젝트는 그 이름을 의도적으로 빌려왔다. Claude Code는 강력한 원재료다. **Demiurge**는 이 원재료를 구조화된 다중 전문가 시스템으로 빚어내는 메타-설정(meta-configuration)이다. 신화의 데미우르고스가 혼돈에서 코스모스를 빚듯, 이 프로젝트는 Claude Code를 빈 캔버스에서 어떤 소프트웨어 아키텍처 문제든 추론할 수 있는 거버넌스 시스템으로 변환한다.

## 철학

Demiurge는 하나의 확신 위에 세워졌다: **올바른 지식 구조와 거버넌스가 Claude Code를 소프트웨어 엔지니어링에서 전지전능하게 만들 수 있다.**

이 저장소에는 소스 코드가 없다. 에이전트, 규칙, 스킬, 오케스트레이션 프로토콜로 이루어진 **순수한 메타-설정**이다.

- 각 분야의 전문 아키텍트들이 어떤 시스템 설계 문제든 집단적으로 추론한다.
- 거버넌스 규칙이 적절한 경계에서 자동 적용되어 품질을 보장한다.
- 계층적 리뷰, 병렬 평가, 합의 투표로 단일 관점보다 우수한 의사결정을 도출한다.
- 코드가 아닌 **지식이 지렛대**다. 올바른 패턴, 원칙, 프레임워크가 Claude Code를 모든 아키텍처 도메인의 전문가로 만든다.

## Components at a Glance

| Component | Count | Description |
|-----------|-------|-------------|
| **Agents** | 20 | 15 architect + 5 investigation |
| **Skills** | 31 | Architecture, AI Backend, Business, Investigation, Utility |
| **Rules** | 8 | 파일 경로 기반 자동 적용 거버넌스 (DDD, Security, API 등) |
| **Commands** | 6 | 5 global + 1 project-local |

소스 코드 없음. 런타임 의존성 없음. 순수 `.claude/` 설정.

## Quick Start

```bash
git clone <repo> ~/lab/demiurge
cd ~/lab/demiurge
./bootstrap.sh          # stow + just 설치, ~/.claude/ 심링크 생성
```

> **Prerequisites:** macOS + Homebrew

이제 아무 프로젝트에서:

```
/architect-orchestration <요구사항>     # 다중 아키텍트 합의 리뷰
/deep-research <주제>                   # 3단계 심층 조사
/investigation-orchestration <조사>     # 코드베이스 조사
```

## How It Works

### Orchestration Flow

```
[요구사항] → [분석 & 라우팅] → [Tier 1: Strategic] → [Tier 2: Design] → [Tier 3: Quality] → [합의] → [결과]
                                  (Sequential)          (Parallel)         (Parallel)          (라운드 기반 투표)
```

### Agent Tiers

| Tier | Agents | Execution |
|------|--------|-----------|
| **1 Strategic** | Solution Architect, Domain Architect | Sequential |
| **2 Design** | Application, Data, Integration, Healthcare, LLM, RAG | Parallel |
| **3 Quality** | Security, SRE, Cloud-Native, AI Safety | Parallel |
| **4 Enabling** | EDA, ML Platform, Concurrency | On-demand |
| **Investigation** | Code, Log, History, Counter-Reviewer, Release | Parallel |

### Consensus Protocol

- **임계값**: 2/3 합의 (67%)
- **거부권**: Tier 1 아키텍트
- **최대 라운드**: 5
- **소수 의견**: 항상 기록

## Usage

### 다중 에이전트 오케스트레이션 (복잡한, 횡단적 의사결정)

```
/architect-orchestration 요구사항 분석 및 다중 아키텍트 리뷰 수행
```

### 개별 에이전트 리뷰 (집중 분석)

```
domain-architect: 도메인 모델 및 Bounded Context 검토
security-architect: 보안 위협 분석 및 암호화 검증
solution-architect: 전체 시스템 아키텍처 설계
```

### 스킬 참조 (패턴 빠른 조회)

```
domain-driven-design, eda, cloud-native, rag-architecture, ai-agent, prompt-engineering ...
```

### 코드베이스 조사 (버그, 성능, 구조 분석)

```
/investigation-orchestration 코드베이스 조사 실행
```

### 문서 동기화

```
/wrap          # CLAUDE.md 분석 + 드리프트 감지 + 업데이트
/wrap --check  # 분석 + 드리프트 감지만 (변경 없음)
```

### Stow 관리

```bash
just status    # 심링크 상태 확인
just link      # 심링크 생성/갱신
just unlink    # 심링크 해제
```

## Structure

```
demiurge/
├── product/.claude/          # 전역 배포 (GNU Stow 경유 → ~/.claude/)
│   ├── skills/ (31)
│   ├── agents/ (20)
│   └── commands/ (5)
├── .claude/                  # 프로젝트 로컬
│   ├── rules/ (8)
│   └── commands/wrap.md
├── justfile                  # Task runner
├── bootstrap.sh              # 최초 설정
├── CLAUDE.md                 # Single source of truth
└── README.md
```

개별 에이전트·스킬·규칙 목록은 `CLAUDE.md` 참조.

## Extending

```bash
just new-skill <name>       # 스킬 템플릿 생성 + 자동 심링크
just new-command <name>     # 커맨드 템플릿 생성 + 자동 심링크
```

## License

이 프로젝트는 설정 템플릿입니다. 자유롭게 사용하세요.
