---
name: hermes-context-maintenance
description: Automatic context window maintenance for Hermes Agent — checkpoints state every 3-5 tool calls to prevent context loss during long sessions.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [context, memory, checkpoint, session, recovery]
    category: devops
---

# Hermes Context Maintenance

Automatic checkpoint system to prevent context loss during long autonomous sessions. Every 3-5 tool calls, state is snapshotted to disk.

## When to Use

- Long-running autonomous tasks (>10 tool calls)
- Complex multi-step implementations
- R&D loops that accumulate state
- Any session where context overflow is a risk

## How It Works

### Checkpoint File Location
```
~/.hermes/memory/Agent-Hermes/checkpoints/
```

### Checkpoint Format (JSON)
```json
{
  "timestamp": "2026-04-26T02:15:00+02:00",
  "session_id": "uuid-here",
  "tool_count": 5,
  "current_task": "Implement memory flush script",
  "state": {
    "files_modified": ["/path/to/file1", "/path/to/file2"],
    "decisions_made": ["decision 1", "decision 2"],
    "pending_work": ["next step 1", "next step 2"],
    "errors_encountered": []
  },
  "memory_snapshot": "brief summary of what's in context"
}
```

### Recovery Process

If session crashes/restarts:

1. Check for most recent checkpoint
2. Read `current_task` and `state`
3. Resume from `pending_work`
4. Restore `files_modified` state if needed

## Usage Patterns

### Pattern 1: Manual Checkpoint (recommended for critical moments)

```
After completing any significant step:
→ write_filecheckpoint (JSON state)
→ Log to daily log
```

### Pattern 2: Automated via execute_code

Use the `checkpoint` helper in execute_code scripts:

```python
from hermes_tools import terminal

def checkpoint(session_id, tool_count, current_task, state):
    """Write checkpoint to disk"""
    # Implementation below
    pass
```

### Pattern 3: Cron-triggered Recovery

Every 30 minutes during active sessions:
- Check if session is still running
- If not, read last checkpoint
- Resume or notify of incomplete work

## Session ID Tracking

Each autonomous session should:
1. Generate unique ID at start: `date +%s`-`uuidgen | head -c 8`
2. Include session_id in all checkpoints
3. Write session marker file: `~/.hermes/memory/Agent-Hermes/active_session`

```
~/.hermes/memory/Agent-Hermes/active_session
```
```
SESSION_ID=2026-04-26-021500-ab12cd34
STARTED=2026-04-26T02:15:00+02:00
LAST_CHECKPOINT=2026-04-26T02:20:00+02:00
CURRENT_TASK=Implement memory flush script
STATUS=active
```

## Integration with Autonomous Employee

The autonomous-employee skill should:

1. **Session Start**: Create active_session marker
2. **Every 3-5 tool calls**: Write checkpoint
3. **Before completing**: Final checkpoint with STATUS=completed
4. **Daily log**: Copy checkpoint summary to daily log

## CLI Commands

```bash
# Check if session is active
cat ~/.hermes/memory/Agent-Hermes/active_session

# Get last checkpoint
ls -t ~/.hermes/memory/Agent-Hermes/checkpoints/ | head -1

# Resume from checkpoint (manual)
cat ~/.hermes/memory/Agent-Hermes/checkpoints/$(ls -t ~/.hermes/memory/Agent-Hermes/checkpoints/ | head -1)
```

## Implementation Checklist

- [ ] Create checkpoints directory
- [ ] Create active_session marker on session start
- [ ] Checkpoint every 3-5 tool calls
- [ ] Recovery process documented
- [ ] Integration with daily logging
