---
name: cos-daily-task-manager
description: Daily task management for the Chief of Staff suite — tracks priorities, runs standups, manages the daily operating rhythm.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [tasks, standup, daily, priorities, cos]
    category: productivity
---

# COS Daily Task Manager

Manages daily task execution, standup, and priority tracking for the Chief of Staff operating loop.

## When to Use

- Morning standup: "What are today's priorities?"
- Adding, completing, or reprioritizing tasks
- Weekly review: "What did we accomplish?"
- Checking if something fell through the cracks

## Setup

Tasks are stored in Obsidian or Linear. The skill detects which is available.

```bash
# If using Linear for task storage
export LINEAR_API_KEY=your_key

# If using Obsidian
export OBSIDIAN_VAULT_PATH=~/Obsidian/vault
```

## Usage

### Add a task

```
User: "Add 'Review Q2 budget' to today's list"
→ Create task with today() deadline, priority=high
```

### Standup format

```
Today's Focus:
  1. [HIGH] Review Q2 budget — by 10am
  2. [MED]  Follow up with Marco about VPS — by noon
  3. [LOW]  Clean up old skills — evening

Blockers:
  - Waiting on: VPS specs from host
```

### Priority Matrix

| Priority | Definition | Action |
|----------|-----------|--------|
| HIGH | Must do today | Block other work if needed |
| MED | Should do today | Do if time permits |
| LOW | Nice to have | Do if everything else done |

## Cron Integration

Run automatically each morning at 08:00:

```bash
hermes cron create \
  --name "Morning standup" \
  --prompt "Run cos-daily-task-manager standup and post priorities to Telegram" \
  --schedule "0 8 * * *" \
  --deliver telegram
```
