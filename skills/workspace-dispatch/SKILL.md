---
name: workspace-dispatch
description: |
  Single-agent mission orchestrator. Decomposes mission into tasks,
  spawns workers, verifies exit criteria, chains tasks.
trigger: "dispatch,mission,tasks,worker"
---

# Workspace Dispatch

## Flow
1. Decompose into 2-6 tasks with exit criteria
2. Spawn worker per task
3. Verify output
4. Chain to next
5. Report summary

## Exit Criteria Examples
- `test -f /path` — file exists
- `grep -q "keyword" /path` — contains expected
- `wc -c < /path | awk '$1 > 100'` — has content

## Dispatch Loop
```
For each task:
  1. Spawn worker
  2. sessions_yield()
  3. Verify exit criteria
  4. Pass or retry (max 3)
```

## Completion
```
✅ Mission complete: {goal}
Tasks:
- ✅ {title} — verified
Output: {project_path}
```