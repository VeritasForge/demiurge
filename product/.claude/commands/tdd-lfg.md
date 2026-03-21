---
name: tdd-lfg
description: "TDD-LFG: CE compound-knowledge planning + SP TDD execution pipeline"
argument-hint: "[feature description] [--fast|--full]"
disable-model-invocation: true
---

Parse $ARGUMENTS: extract mode flag (--fast|--full) and feature description.

Modes:
- --fast: steps 2, 4, 5 only
- --full: all steps 1-6
- no flag: ask user (Full/Fast)

Run applicable steps in order. Do not stop between steps.

1. (full only) /compound-engineering:workflows:brainstorm $FEATURE_DESCRIPTION
2. /compound-engineering:workflows:plan $FEATURE_DESCRIPTION
3. (full only) /compound-engineering:deepen-plan
4. Invoke superpowers:writing-plans skill — use the CE plan file from step 2 as the spec/requirements input. Do not present execution handoff choice.
5. Invoke superpowers:subagent-driven-development skill — use the TDD plan from step 4.
6. (full only) /compound-engineering:workflows:compound

Required steps (2, 4, 5): stop pipeline on failure.
Optional steps (1, 3, 6): warn and continue on failure.

Start now.
