---
name: cos-proactive-reporting
description: Proactive reporting for the Chief of Staff suite — scheduled briefings, weekly summaries, and automated status reports.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [reporting, briefings, weekly, summaries, cos]
    category: productivity
---

# COS Proactive Reporting

Scheduled briefings, weekly summaries, and automated status reports. Part of the Chief of Staff operating loop.

## When to Use

- Weekly review: "Give me a weekly summary"
- Morning briefing: "What's the status?"
- Custom report: "Generate a status report for project X"
- Setting up scheduled reports

## Report Types

### Morning Brief

Daily at 08:00:
```
🌅 GOOD MORNING
━━━━━━━━━━━━━━━━
📅 TODAY: 3 meetings, 2 deadlines
⚡ PRIORITY: Review Q2 budget (by 10am)
📋 TASKS: 8 open (3 high, 4 med, 1 low)
💬 ACTION: Reply to Sarah's email
```

### Weekly Summary

Every Monday:
```
📊 WEEKLY SUMMARY (Apr 14–20)
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ COMPLETED: 12 tasks
⏳ IN PROGRESS: 5 tasks
📈 TOP COMPLETION: Hermes skills migration

💬 COMMUNICATIONS
  • Discord: 47 messages (↑ 12%)
  • Telegram: 23 messages (↓ 5%)

🔧 TECHNICAL
  • VPS uptime: 99.8%
  • Gateway restarts: 2 (auto-recovered)
  • New skills installed: 4

📅 THIS WEEK
  • Mon: Q2 budget review
  • Wed: Team sync
  • Fri: Sprint retrospective
```

### Custom Status Report

```
/report project:hermes-vps-migration
```

## Cron Setup

```bash
# Morning brief
hermes cron create \
  --name "Morning brief" \
  --prompt "Run cos-proactive-reporting morning brief, deliver to Telegram" \
  --schedule "0 8 * * *"

# Weekly summary
hermes cron create \
  --name "Weekly summary" \
  --prompt "Run cos-proactive-reporting weekly summary, deliver to Telegram" \
  --schedule "0 9 * * 1"
```

## Data Sources

- Obsidian daily notes (tasks, accomplishments)
- Linear (open/closed issues)
- Hermes session history (communications)
- System health checks (gateway, VPS)
- Cron job logs (failures, completions)
