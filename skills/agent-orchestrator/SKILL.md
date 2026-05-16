---
name: agent-orchestrator
description: |
  Multi-agent orchestration skill. Coordinates multiple autonomous agents,
  manages task delegation, monitors progress, handles failures. Use with
  workspace-dispatch for complex missions.
trigger: "orchestrate,multi-agent,delegate,coordinator,team of agents"
---

# Agent Orchestrator

Coordina team di agent autonomi per completare missioni complesse.

## Architecture

```
Orchestrator (you)
├── Research Agent → gather data
├── Analysis Agent → process info
├── Execution Agent → perform tasks
└── Review Agent → verify results
```

## Delegation Pattern

### 1. Decompose Mission
```
Break into 3-6 independent tasks.
Each task = one worker, one clear goal.
```

### 2. Spawn Workers
```bash
# Use delegate_task for parallel execution
delegate_task(
  goal="Research [topic]. Output to /tmp/research.md",
  toolsets=["web", "terminal"],
  context="Deadline: [time]"
)
```

### 3. Monitor Progress
- Set clear checkpoints
- Expect status updates
- Handle timeouts gracefully

### 4. Aggregate Results
- Merge worker outputs
- Resolve conflicts
- Synthesize final report

## Task Types

| Type | Worker Role | Verify |
|------|-------------|--------|
| research | Gather & document | File with content |
| coding | Write & test code | Tests pass |
| review | Audit & validate | Pass verdict |
| execute | Run operations | Completion signal |

## Failure Handling

- Worker timeout → retry with simpler scope
- Exit criteria fail → retry with error context
- 3 retries exhausted → mark failed, continue next
- Always log failures for review

## Example Mission

```
Mission: Generate trading strategy report

Tasks:
1. Research Agent → Collect market data → /tmp/market.md
2. Analysis Agent → Identify patterns → /tmp/patterns.md  
3. Strategy Agent → Draft strategy → /tmp/strategy.md
4. Review Agent → Validate → /tmp/review.md

Orchestrator: Aggregate all → Final report
```