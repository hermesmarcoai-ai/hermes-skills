---
name: morning-brief-cronjob
description: Morning brief cron job — automated scheduler that triggers the morning brief workflow each weekday at 8am.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [morning, briefing, cron, automation, scheduled]
    category: productivity
---

# Morning Brief Cron Job

Automated scheduler for morning briefings. Triggers the full morning brief workflow each weekday at 8am.

## When to Use

- Setting up automated morning briefings
- "I want a brief every morning at 8am"
- Adjusting the briefing schedule

## Setup

```bash
# Create the cron job
hermes cron create \
  --name "Morning Brief" \
  --prompt "Run full morning brief: check calendar, open tasks, priorities, overnight events. Format as structured text and deliver to Telegram." \
  --schedule "0 8 * * 1-5" \
  --deliver telegram

# Options:
#   --deliver telegram  → Send to Marco's Telegram
#   --deliver discord   → Send to Discord #general
#   --deliver origin   → Post in current thread
```

## What Gets Included

```
🌅 MORNING BRIEF — [DATE]
━━━━━━━━━━━━━━━━━━━━━━━━

📅 TODAY'S SCHEDULE
  • 09:00 — Q2 Budget Review (with Sarah)
  • 14:00 — Team Standup
  • 16:00 — 1:1 with Marco

⚡ TOP PRIORITIES (High)
  1. Review Q2 budget — Sarah needs answer by 10am
  2. Follow up on VPS specs — waiting on email
  3. Review PR #47 — pending since Tuesday

📋 OPEN TASKS
  • 8 total (3 high, 4 med, 1 low)
  • Overdue: 1 (hermes-auto-update cron — network timeout)

🌙 OVERNIGHT
  • Gateway: ✅ Online (99.9% uptime)
  • VPS Disk: ⚠️ 72% full (15GB free of 75GB)
  • No incidents

💬 LAST CONVERSATIONS
  • Sarah (Telegram) — re: budget numbers
  • GitHub — PR #47 needs your review

☀️ AOSTA WEATHER (if available)
  • 12°C, partly cloudy, 5°C low
```

## Cron Schedule Options

| Schedule | Description |
|----------|-------------|
| `0 8 * * 1-5` | Every weekday at 8am |
| `0 7 * * 1-5` | Every weekday at 7am |
| `0 9 * * *` | Every day at 9am |
| `0 8 * * 1` | Every Monday at 8am only |

## Managing the Cron

```bash
# List all cron jobs
hermes cron list

# Pause the morning brief
hermes cron pause --name "Morning Brief"

# Resume
hermes cron resume --name "Morning Brief"

# Delete
hermes cron remove --name "Morning Brief"
```
