# demi plugin-stats 리포트

- 생성: 2026-06-01T01:00:09.111311+00:00
- 윈도우: 2025-11-30 ~ 2026-06-01 (183일)

## 요약 (유형별 등급)
| 유형 | total | active | live | dead |
|---|---:|---:|---:|---:|
| agent | 92 | 37 | 0 | 55 |
| command | 1 | 1 | 0 | 0 |
| mcp_server | 4 | 2 | 0 | 2 |
| plugin | 10 | 1 | 0 | 9 |
| skill | 135 | 43 | 17 | 75 |

## 사용 빈도 그래프 (Top 15)

### 통합 (skill + agent + command)
```
  general-purpose                                        ██████████████████████████████  395
  compound-engineering:ce-adversarial-document-reviewer  ██████░░░░░░░░░░░░░░░░░░░░░░░░  83
  rl-verify                                              ████░░░░░░░░░░░░░░░░░░░░░░░░░░  54
  commit                                                 ████░░░░░░░░░░░░░░░░░░░░░░░░░░  50
  claude-code-guide                                      ████░░░░░░░░░░░░░░░░░░░░░░░░░░  47
  Explore                                                ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  42
  compound-engineering:ce-web-researcher                 ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  40
  compound-engineering:ce-correctness-reviewer           ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  39
  deep-research                                          ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  37
  compound-engineering:ce-feasibility-reviewer           ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  34
  compound-engineering:ce-best-practices-researcher      ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  33
  compound-engineering:ce-testing-reviewer               ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░  29
  compound-engineering:ce-coherence-reviewer             ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░  28
  compound-engineering:ce-architecture-strategist        ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░  26
  organize                                               ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░  24
```

### skills
```
  rl-verify                                ██████████████████████████████  54
  commit                                   ████████████████████████████░░  50
  deep-research                            █████████████████████░░░░░░░░░  37
  organize                                 █████████████░░░░░░░░░░░░░░░░░  24
  compound-engineering:ce-doc-review       ████████████░░░░░░░░░░░░░░░░░░  22
  superpowers:writing-plans                ████████████░░░░░░░░░░░░░░░░░░  22
  compound-engineering:ce-code-review      ███████████░░░░░░░░░░░░░░░░░░░  20
  superpowers:subagent-driven-development  ███████████░░░░░░░░░░░░░░░░░░░  20
  qa                                       ███████░░░░░░░░░░░░░░░░░░░░░░░  12
  ouroboros:qa                             ███████░░░░░░░░░░░░░░░░░░░░░░░  12
  concept-explainer                        ██████░░░░░░░░░░░░░░░░░░░░░░░░  11
  vercel-react-best-practices              ██████░░░░░░░░░░░░░░░░░░░░░░░░  11
  superpowers:writing-skills               █████░░░░░░░░░░░░░░░░░░░░░░░░░  9
  debug                                    ████░░░░░░░░░░░░░░░░░░░░░░░░░░  8
  vercel-composition-patterns              ████░░░░░░░░░░░░░░░░░░░░░░░░░░  7
```

### agents
```
  general-purpose                                        ██████████████████████████████  395
  compound-engineering:ce-adversarial-document-reviewer  ██████░░░░░░░░░░░░░░░░░░░░░░░░  83
  claude-code-guide                                      ████░░░░░░░░░░░░░░░░░░░░░░░░░░  47
  Explore                                                ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  42
  compound-engineering:ce-web-researcher                 ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  40
  compound-engineering:ce-correctness-reviewer           ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  39
  compound-engineering:ce-feasibility-reviewer           ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  34
  compound-engineering:ce-best-practices-researcher      ███░░░░░░░░░░░░░░░░░░░░░░░░░░░  33
  compound-engineering:ce-testing-reviewer               ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░  29
  compound-engineering:ce-coherence-reviewer             ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░  28
  compound-engineering:ce-architecture-strategist        ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░  26
  compound-engineering:ce-scope-guardian-reviewer        ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░  22
  compound-engineering:ce-maintainability-reviewer       ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░  20
  compound-engineering:ce-security-lens-reviewer         █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  18
  compound-engineering:ce-project-standards-reviewer     █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  17
```

### commands
```
  save_obsi  ██████████████████████████████  18
```

## 시간 추이 (호출량)

### 월별 (chronological)
```
  2026-04  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  22
  2026-05  ██████████████████████████████  2674
  2026-06  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  7
```

### 주별 — 최근 20주
```
  2026-W17  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  11
  2026-W18  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░  44
  2026-W19  ████████░░░░░░░░░░░░░░░░░░░░░░  228
  2026-W20  ██████████████████████████████  866
  2026-W21  █████████████████████████████░  834
  2026-W22  █████████████████████████░░░░░  713
  2026-W23  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  7
```

## 자산별 시간 추이 (카테고리별 Top 10, sparkline)

### skills — 월별
```
                                           2026-04 → 2026-06  (span=3)
  rl-verify                                ▁█▁  total=54 last=0
  commit                                   ▁█▁  total=50 last=0
  deep-research                            ▁█▁  total=37 last=0
  organize                                 ▁█▁  total=24 last=0
  compound-engineering:ce-doc-review       ▁█▁  total=22 last=0
  superpowers:writing-plans                ▁█▁  total=22 last=0
  compound-engineering:ce-code-review      ▁█▁  total=20 last=0
  superpowers:subagent-driven-development  ▁█▁  total=20 last=0
  qa                                       ▁█▁  total=12 last=0
  ouroboros:qa                             ▁█▁  total=12 last=0
```

### skills — 주별 (최근 20주)
```
                                           2026-W17 → 2026-W23  (span=7)
  rl-verify                                ▁▂▃▅█▆▁  total=54 last=0
  commit                                   ▁▂▆▅█▆▁  total=50 last=0
  deep-research                            ▁▂▂█▆▇▁  total=37 last=0
  organize                                 ▁▁▆██▆▁  total=24 last=0
  compound-engineering:ce-doc-review       ▁▁▂▂▅█▁  total=22 last=0
  superpowers:writing-plans                ▁▁▁▂▅█▁  total=22 last=0
  compound-engineering:ce-code-review      ▁▁▁▁█▃▁  total=20 last=0
  superpowers:subagent-driven-development  ▁▁▁▃██▁  total=20 last=0
  qa                                       ▁▄█▅▂▂▁  total=12 last=0
  ouroboros:qa                             ▁▄█▅▂▂▁  total=12 last=0
```

### agents — 월별
```
                                                         2026-04 → 2026-06  (span=3)
  general-purpose                                        ▁█▁  total=395 last=0
  compound-engineering:ce-adversarial-document-reviewer  ▁█▁  total=83 last=0
  claude-code-guide                                      ▂█▁  total=47 last=0
  Explore                                                ▁█▁  total=42 last=0
  compound-engineering:ce-web-researcher                 ▁█▁  total=40 last=1
  compound-engineering:ce-correctness-reviewer           ▁█▁  total=39 last=0
  compound-engineering:ce-feasibility-reviewer           ▁█▁  total=34 last=0
  compound-engineering:ce-best-practices-researcher      ▁█▁  total=33 last=0
  compound-engineering:ce-testing-reviewer               ▁█▁  total=29 last=0
  compound-engineering:ce-coherence-reviewer             ▁█▁  total=28 last=0
```

### agents — 주별 (최근 20주)
```
                                                         2026-W17 → 2026-W23  (span=7)
  general-purpose                                        ▁▁▁▆██▁  total=395 last=0
  compound-engineering:ce-adversarial-document-reviewer  ▁▁▃▅██▁  total=83 last=0
  claude-code-guide                                      ▁▂▁█▅▄▁  total=47 last=0
  Explore                                                ▂▁▂█▆▃▁  total=42 last=0
  compound-engineering:ce-web-researcher                 ▁▁▂▆█▆▁  total=40 last=1
  compound-engineering:ce-correctness-reviewer           ▁▁▁▃█▂▁  total=39 last=0
  compound-engineering:ce-feasibility-reviewer           ▁▁▁▂▅█▁  total=34 last=0
  compound-engineering:ce-best-practices-researcher      ▁▁▃▇█▅▁  total=33 last=0
  compound-engineering:ce-testing-reviewer               ▁▁▁▂█▂▁  total=29 last=0
  compound-engineering:ce-coherence-reviewer             ▁▁▁▂▅█▁  total=28 last=0
```

### commands — 월별
```
             2026-04 → 2026-06  (span=3)
  save_obsi  ▁█▁  total=18 last=0
```

### commands — 주별 (최근 20주)
```
             2026-W17 → 2026-W23  (span=7)
  save_obsi  ▁▁▅▆▇█▁  total=18 last=0
```

## 활성 자산 (active)
- 🟢 `Explore` (agent, builtin, calls=42)
- 🟢 `Plan` (agent, builtin, calls=5)
- 🟢 `claude-code-guide` (agent, builtin, calls=47)
- 🟢 `codex:codex-rescue` (agent, plugin:codex, calls=3)
- 🟢 `compound-engineering:ce-adversarial-document-reviewer` (agent, plugin:compound-engineering, calls=83)
- 🟢 `compound-engineering:ce-adversarial-reviewer` (agent, plugin:compound-engineering, calls=9)
- 🟢 `compound-engineering:ce-agent-native-reviewer` (agent, plugin:compound-engineering, calls=9)
- 🟢 `compound-engineering:ce-api-contract-reviewer` (agent, plugin:compound-engineering, calls=4)
- 🟢 `compound-engineering:ce-architecture-strategist` (agent, plugin:compound-engineering, calls=26)
- 🟢 `compound-engineering:ce-best-practices-researcher` (agent, plugin:compound-engineering, calls=33)
- 🟢 `compound-engineering:ce-code-simplicity-reviewer` (agent, plugin:compound-engineering, calls=12)
- 🟢 `compound-engineering:ce-coherence-reviewer` (agent, plugin:compound-engineering, calls=28)
- 🟢 `compound-engineering:ce-correctness-reviewer` (agent, plugin:compound-engineering, calls=39)
- 🟢 `compound-engineering:ce-data-integrity-guardian` (agent, plugin:compound-engineering, calls=6)
- 🟢 `compound-engineering:ce-data-migration-reviewer` (agent, plugin:compound-engineering, calls=1)
- 🟢 `compound-engineering:ce-design-lens-reviewer` (agent, plugin:compound-engineering, calls=10)
- 🟢 `compound-engineering:ce-feasibility-reviewer` (agent, plugin:compound-engineering, calls=34)
- 🟢 `compound-engineering:ce-framework-docs-researcher` (agent, plugin:compound-engineering, calls=7)
- 🟢 `compound-engineering:ce-julik-frontend-races-reviewer` (agent, plugin:compound-engineering, calls=6)
- 🟢 `compound-engineering:ce-learnings-researcher` (agent, plugin:compound-engineering, calls=13)
- 🟢 `compound-engineering:ce-maintainability-reviewer` (agent, plugin:compound-engineering, calls=20)
- 🟢 `compound-engineering:ce-performance-oracle` (agent, plugin:compound-engineering, calls=1)
- 🟢 `compound-engineering:ce-performance-reviewer` (agent, plugin:compound-engineering, calls=6)
- 🟢 `compound-engineering:ce-product-lens-reviewer` (agent, plugin:compound-engineering, calls=11)
- 🟢 `compound-engineering:ce-project-standards-reviewer` (agent, plugin:compound-engineering, calls=17)
- 🟢 `compound-engineering:ce-reliability-reviewer` (agent, plugin:compound-engineering, calls=8)
- 🟢 `compound-engineering:ce-repo-research-analyst` (agent, plugin:compound-engineering, calls=10)
- 🟢 `compound-engineering:ce-scope-guardian-reviewer` (agent, plugin:compound-engineering, calls=22)
- 🟢 `compound-engineering:ce-security-lens-reviewer` (agent, plugin:compound-engineering, calls=18)
- 🟢 `compound-engineering:ce-security-reviewer` (agent, plugin:compound-engineering, calls=11)
- 🟢 `compound-engineering:ce-security-sentinel` (agent, plugin:compound-engineering, calls=7)
- 🟢 `compound-engineering:ce-testing-reviewer` (agent, plugin:compound-engineering, calls=29)
- 🟢 `compound-engineering:ce-web-researcher` (agent, plugin:compound-engineering, calls=40)
- 🟢 `convergence-evaluator` (agent, global, calls=3)
- 🟢 `data-architect` (agent, global, calls=1)
- 🟢 `general-purpose` (agent, builtin, calls=395)
- 🟢 `solution-architect` (agent, global, calls=1)
- 🟢 `save_obsi` (command, global, calls=18)
- 🟢 `mcp-atlassian` (mcp_server, mcp, calls=463)
- 🟢 `playwright` (mcp_server, mcp, calls=2)
- 🟢 `context7` (plugin, plugin:context7, calls=30)
- 🟢 `architect-orchestration` (skill, global, calls=1)
- 🟢 `autopilot` (skill, global, calls=2)
- 🟢 `codex:codex-cli-runtime` (skill, plugin:codex, calls=3)
- 🟢 `codex:gpt-5-4-prompting` (skill, plugin:codex, calls=3)
- 🟢 `commit` (skill, global, calls=50)
- 🟢 `compound-engineering:ce-brainstorm` (skill, plugin:compound-engineering, calls=1)
- 🟢 `compound-engineering:ce-code-review` (skill, plugin:compound-engineering, calls=20)
- 🟢 `compound-engineering:ce-debug` (skill, plugin:compound-engineering, calls=5)
- 🟢 `compound-engineering:ce-doc-review` (skill, plugin:compound-engineering, calls=22)
- 🟢 `compound-engineering:ce-frontend-design` (skill, plugin:compound-engineering, calls=2)
- 🟢 `compound-engineering:ce-optimize` (skill, plugin:compound-engineering, calls=1)
- 🟢 `concept-explainer` (skill, global, calls=11)
- 🟢 `debug` (skill, global, calls=8)
- 🟢 `deep-research` (skill, global, calls=37)
- 🟢 `humanize-writing` (skill, global, calls=1)
- 🟢 `humanize-writing-portable` (skill, global, calls=1)
- 🟢 `interview-prep` (skill, global, calls=2)
- 🟢 `job-analysis` (skill, global, calls=3)
- 🟢 `md-to-html` (skill, global, calls=4)
- 🟢 `organize` (skill, global, calls=24)
- 🟢 `ouroboros:qa` (skill, plugin:ouroboros, calls=12)
- 🟢 `ouroboros:run` (skill, plugin:ouroboros, calls=1)
- 🟢 `qa` (skill, global, calls=12)
- 🟢 `ralph-loop-guide` (skill, global, calls=1)
- 🟢 `readme-writer` (skill, global, calls=2)
- 🟢 `resume-optimizer` (skill, global, calls=1)
- 🟢 `retrospective` (skill, global, calls=5)
- 🟢 `review-pr` (skill, global, calls=5)
- 🟢 `rl` (skill, global, calls=1)
- 🟢 `rl-verify` (skill, global, calls=54)
- 🟢 `session-handoff` (skill, global, calls=1)
- 🟢 `superpowers:brainstorming` (skill, plugin:superpowers, calls=1)
- 🟢 `superpowers:executing-plans` (skill, plugin:superpowers, calls=3)
- 🟢 `superpowers:finishing-a-development-branch` (skill, plugin:superpowers, calls=3)
- 🟢 `superpowers:subagent-driven-development` (skill, plugin:superpowers, calls=20)
- 🟢 `superpowers:systematic-debugging` (skill, plugin:superpowers, calls=3)
- 🟢 `superpowers:test-driven-development` (skill, plugin:superpowers, calls=1)
- 🟢 `superpowers:using-git-worktrees` (skill, plugin:superpowers, calls=3)
- 🟢 `superpowers:writing-plans` (skill, plugin:superpowers, calls=22)
- 🟢 `superpowers:writing-skills` (skill, plugin:superpowers, calls=9)
- 🟢 `testing-architecture` (skill, global, calls=3)
- 🟢 `vercel-composition-patterns` (skill, global, calls=7)
- 🟢 `vercel-react-best-practices` (skill, global, calls=11)

## 정리 후보 (dead)
- 🔴 `ai-safety-architect` (agent, global)
- 🔴 `application-architect` (agent, global)
- 🔴 `claude` (agent, builtin)
- 🔴 `cloud-native-architect` (agent, global)
- 🔴 `code-investigator` (agent, global)
- 🔴 `compound-engineering:ce-ankane-readme-writer` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-deployment-verification-agent` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-design-implementation-reviewer` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-design-iterator` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-figma-design-sync` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-git-history-analyzer` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-issue-intelligence-analyst` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-pattern-recognition-specialist` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-pr-comment-resolver` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-previous-comments-reviewer` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-session-historian` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-slack-researcher` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-spec-flow-analyzer` (agent, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-swift-ios-reviewer` (agent, plugin:compound-engineering)
- 🔴 `concurrency-architect` (agent, global)
- 🔴 `counter-reviewer` (agent, global)
- 🔴 `domain-architect` (agent, global)
- 🔴 `eda-specialist` (agent, global)
- 🔴 `healthcare-informatics-architect` (agent, global)
- 🔴 `history-investigator` (agent, global)
- 🔴 `integration-architect` (agent, global)
- 🔴 `llm-architect` (agent, global)
- 🔴 `log-investigator` (agent, global)
- 🔴 `ml-platform-architect` (agent, global)
- 🔴 `ouroboros:advocate` (agent, plugin:ouroboros)
- 🔴 `ouroboros:analysis-agent` (agent, plugin:ouroboros)
- 🔴 `ouroboros:architect` (agent, plugin:ouroboros)
- 🔴 `ouroboros:breadth-keeper` (agent, plugin:ouroboros)
- 🔴 `ouroboros:code-executor` (agent, plugin:ouroboros)
- 🔴 `ouroboros:codebase-explorer` (agent, plugin:ouroboros)
- 🔴 `ouroboros:consensus-reviewer` (agent, plugin:ouroboros)
- 🔴 `ouroboros:contrarian` (agent, plugin:ouroboros)
- 🔴 `ouroboros:evaluator` (agent, plugin:ouroboros)
- 🔴 `ouroboros:hacker` (agent, plugin:ouroboros)
- 🔴 `ouroboros:judge` (agent, plugin:ouroboros)
- 🔴 `ouroboros:ontologist` (agent, plugin:ouroboros)
- 🔴 `ouroboros:ontology-analyst` (agent, plugin:ouroboros)
- 🔴 `ouroboros:qa-judge` (agent, plugin:ouroboros)
- 🔴 `ouroboros:research-agent` (agent, plugin:ouroboros)
- 🔴 `ouroboros:researcher` (agent, plugin:ouroboros)
- 🔴 `ouroboros:seed-architect` (agent, plugin:ouroboros)
- 🔴 `ouroboros:seed-closer` (agent, plugin:ouroboros)
- 🔴 `ouroboros:semantic-evaluator` (agent, plugin:ouroboros)
- 🔴 `ouroboros:simplifier` (agent, plugin:ouroboros)
- 🔴 `ouroboros:socratic-interviewer` (agent, plugin:ouroboros)
- 🔴 `rag-architect` (agent, global)
- 🔴 `release-investigator` (agent, global)
- 🔴 `security-architect` (agent, global)
- 🔴 `sre-architect` (agent, global)
- 🔴 `statusline-setup` (agent, builtin)
- 🔴 `notion` (mcp_server, mcp)
- 🔴 `ouroboros` (mcp_server, mcp)
- 🔴 `Notion` (plugin, plugin:Notion)
- 🔴 `codex` (plugin, plugin:codex)
- 🔴 `compound-engineering` (plugin, plugin:compound-engineering)
- 🔴 `frontend-design` (plugin, plugin:frontend-design)
- 🔴 `notion-workspace-plugin` (plugin, plugin:notion-workspace-plugin)
- 🔴 `ouroboros` (plugin, plugin:ouroboros)
- 🔴 `ralph-loop` (plugin, plugin:ralph-loop)
- 🔴 `superpowers` (plugin, plugin:superpowers)
- 🔴 `typescript-lsp` (plugin, plugin:typescript-lsp)
- 🔴 `Notion:knowledge-capture` (skill, plugin:Notion)
- 🔴 `Notion:meeting-intelligence` (skill, plugin:Notion)
- 🔴 `Notion:research-documentation` (skill, plugin:Notion)
- 🔴 `Notion:spec-to-implementation` (skill, plugin:Notion)
- 🔴 `api-design` (skill, global)
- 🔴 `codex:codex-result-handling` (skill, plugin:codex)
- 🔴 `compound-engineering:ce-agent-native-architecture` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-agent-native-audit` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-clean-gone-branches` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-commit` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-commit-push-pr` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-compound` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-compound-refresh` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-demo-reel` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-dhh-rails-style` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-dogfood-beta` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-gemini-imagegen` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-ideate` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-plan` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-polish-beta` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-product-pulse` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-proof` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-release-notes` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-report-bug` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-resolve-pr-feedback` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-riffrec-feedback-analysis` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-sessions` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-setup` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-simplify-code` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-slack-research` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-strategy` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-test-browser` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-test-xcode` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-update` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-work` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-work-beta` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:ce-worktree` (skill, plugin:compound-engineering)
- 🔴 `compound-engineering:lfg` (skill, plugin:compound-engineering)
- 🔴 `frontend-design:frontend-design` (skill, plugin:frontend-design)
- 🔴 `group-job-analysis` (skill, global)
- 🔴 `investigation-orchestration` (skill, global)
- 🔴 `notion-workspace-plugin:knowledge-capture` (skill, plugin:notion-workspace-plugin)
- 🔴 `notion-workspace-plugin:meeting-intelligence` (skill, plugin:notion-workspace-plugin)
- 🔴 `notion-workspace-plugin:research-documentation` (skill, plugin:notion-workspace-plugin)
- 🔴 `notion-workspace-plugin:spec-to-implementation` (skill, plugin:notion-workspace-plugin)
- 🔴 `ouroboros:auto` (skill, plugin:ouroboros)
- 🔴 `ouroboros:brownfield` (skill, plugin:ouroboros)
- 🔴 `ouroboros:cancel` (skill, plugin:ouroboros)
- 🔴 `ouroboros:evaluate` (skill, plugin:ouroboros)
- 🔴 `ouroboros:evolve` (skill, plugin:ouroboros)
- 🔴 `ouroboros:help` (skill, plugin:ouroboros)
- 🔴 `ouroboros:interview` (skill, plugin:ouroboros)
- 🔴 `ouroboros:pm` (skill, plugin:ouroboros)
- 🔴 `ouroboros:publish` (skill, plugin:ouroboros)
- 🔴 `ouroboros:ralph` (skill, plugin:ouroboros)
- 🔴 `ouroboros:resume-session` (skill, plugin:ouroboros)
- 🔴 `ouroboros:seed` (skill, plugin:ouroboros)
- 🔴 `ouroboros:setup` (skill, plugin:ouroboros)
- 🔴 `ouroboros:status` (skill, plugin:ouroboros)
- 🔴 `ouroboros:tutorial` (skill, plugin:ouroboros)
- 🔴 `ouroboros:unstuck` (skill, plugin:ouroboros)
- 🔴 `ouroboros:update` (skill, plugin:ouroboros)
- 🔴 `ouroboros:welcome` (skill, plugin:ouroboros)
- 🔴 `release-handoff` (skill, global)
- 🔴 `rl-fresh` (skill, global)
- 🔴 `save-confluence` (skill, global)
- 🔴 `skill-routing-learner` (skill, global)
- 🔴 `superpowers:dispatching-parallel-agents` (skill, plugin:superpowers)
- 🔴 `superpowers:receiving-code-review` (skill, plugin:superpowers)
- 🔴 `superpowers:requesting-code-review` (skill, plugin:superpowers)
- 🔴 `superpowers:using-superpowers` (skill, plugin:superpowers)
- 🔴 `superpowers:verification-before-completion` (skill, plugin:superpowers)
- 🔴 `tdd-lfg` (skill, global)
- 🔴 `vercel-react-native-skills` (skill, global)
- 🔴 `web-design-guidelines` (skill, global)

## 추세 (이전 스냅샷 대비)
- 신규 dead: notion, ouroboros, ouroboros:evolve, ouroboros:help, ouroboros:interview, ouroboros:seed
