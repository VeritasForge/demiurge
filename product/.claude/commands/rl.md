---
description: Ralph Loop Runner - sequential-thinking MCP 기반 반복 실행
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch, Edit, Write, Task
---

# Ralph Loop Runner

Execute the ralph-loop skill with sequential-thinking MCP enabled.

**Usage:** `/ralph-loop <prompt>` or `/ralph-loop <prompt> --max-iterations <number>`

```
Parse the user's input from: $ARGUMENTS

Extract:
1. The prompt text (everything before --max-iterations, or the entire input if --max-iterations is not specified)
2. The max-iterations value (number after --max-iterations flag, default: 20)

Then invoke the ralph-loop:ralph-loop skill with the following format:

/ralph-loop:ralph-loop {prompt} mcp sequential-thinking use --max-iterations {max-iterations} --completion-promise COMPLETE

Where:
- {prompt} = the extracted prompt text
- {max-iterations} = the extracted max-iterations value or 20 if not specified
```
