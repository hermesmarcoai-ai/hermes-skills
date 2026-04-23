---
name: hermes-context-maintenance
description: Automatic context window maintenance for Hermes Agent — compresses old conversation history, archives sessions, and prevents context overflow.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [context, memory, compression, session, maintenance]
    category: devops
---

# Hermes Context Maintenance

Automatic context window management. Compresses old conversation history, archives sessions, and prevents context overflow.

## When to Use

- "My context is getting full"
- "Archive old conversations"
- "Compress session history"
- "Optimize context usage"

## How It Works

```
Context usage > 80%
       ↓
Identify oldest/summarizable messages
       ↓
Compress via summarization (keep key facts)
       ↓
Or archive (move to long-term storage)
       ↓
Verify context still coherent
```

## Compression Strategies

| Strategy | When to Use | Tokens Saved |
|----------|------------|--------------|
| Summarize | Same topic, long thread | 60-80% |
| Prune | Off-topic sidebar | 40-60% |
| Archive | Session complete | 100% |

## Session Archival

```
Completed sessions → Obsidian daily note
  • Key decisions
  • Action items
  • References used
  • Links to files created
```

## Usage

### Manual context check

```
User: "How much context am I using?"
→ Report:
  Current: 45,230 / 200,000 tokens (22.6%)
  Sessions: 3 active
  Oldest: Apr 20 (3 days ago)

  Recommendations:
  • Archive session from Apr 20
  • Compress #general thread (saving ~8k tokens)
```

### Archive old session

```
User: "Archive sessions older than a week"
→ Find sessions with last_message > 7 days
→ Extract key facts for each
→ Write summary to Obsidian
→ Delete old messages
→ Report: "Archived 12 sessions, saved ~45k tokens"
```

### Cron auto-maintenance

```bash
# Run context maintenance daily at 02:00
hermes cron create \
  --name "Context maintenance" \
  --prompt "Run hermes-context-maintenance: compress sessions >80% full, archive sessions >7 days old, log stats" \
  --schedule "0 2 * * *"
```

## Memory Bank Structure

Archived sessions go to Obsidian:
```
memory/
  sessions/
    2026-04/
      20-01-general.md   (archived Apr 20)
      20-02-vps-setup.md
      ...
```

Each archived session note contains:
- Date range
- Participants
- Key decisions
- Action items created
- Files referenced
