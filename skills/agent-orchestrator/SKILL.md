---
name: agent-orchestrator
description: |
  Multi-agent coordination. Delegates tasks, monitors progress, handles failures.
trigger: "orchestrate,multi-agent,delegate,team"
---

# Agent Orchestrator

## Architecture
```
Orchestrator
├── Research Agent
├── Analysis Agent
├── Execution Agent
└── Review Agent
```

## Delegation Pattern
1. Decompose into 3-6 tasks
2. Spawn workers with delegate_task
3. Monitor checkpoints
4. Aggregate results

## Failure Handling
- Timeout → retry with simpler scope
- 3 retries → mark failed, continue
- Always log failures