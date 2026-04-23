---
name: cos-chief-of-staff
description: Chief of Staff skill for Hermes Agent — coordinates the executive assistant suite, manages priorities, delegates to specialist skills, and ensures nothing falls through the cracks.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [chief-of-staff, coordination, executive, productivity, scheduling]
    category: productivity
---

# Chief of Staff

Executive coordination layer for Hermes Agent. Acts as the Chief of Staff that:
- Filters and prioritizes incoming requests
- Delegates to specialist skills (COS sub-agents)
- Tracks outstanding items and follows up
- Manages the daily/weekly operating rhythm

## When to Use

- User has multiple requests or competing priorities
- A request spans multiple domains (needs COS sub-agents)
- Regular check-in: "any updates on outstanding items?"
- Setting weekly/daily priorities

## COS Sub-Agents

| Sub-Agent | Handles |
|-----------|---------|
| `cos-daily-task-manager` | Daily task tracking, standup, priorities |
| `cos-overnight-logger` | Overnight monitoring, incident logging |
| `cos-proactive-reporting` | Scheduled reports, briefings |
| `cos-relationship-manager` | Contact updates, relationship tracking |
| `cos-executive-assistant` | Calendar, email, scheduling |
| `cos-bootstrap` | New project setup, onboarding |

## Operating Rhythm

```
Morning (08:00)  → cos-daily-task-manager: priorities + standup
Throughout day   → Route requests to specialist COS
Evening (18:00)  → cos-overnight-logger: end-of-day summary
Weekly (Mon)     → cos-proactive-reporting: weekly brief
Weekly (Fri)     → cos-relationship-manager: contact check-in
```

## How to Use

### Report to COS

```
User: "I have a lot going on this week — can you help me prioritize?"
→ Load this skill, review all outstanding items, propose priority matrix
```

### Delegate a project

```
User: "I need to launch the new website by Friday"
→ Load cos-bootstrap, create project skeleton, delegate sub-tasks
```

### Get a briefing

```
User: "What's on my plate today?"
→ Load cos-daily-task-manager, summarize today's priorities
```

## Coordination Flow

```
Incoming request
       ↓
  Is it actionable? → No → Acknowledge + defer
       ↓ Yes
  Which skill handles it?
       ↓
  Delegate to COS sub-agent
       ↓
  Track outcome
       ↓
  Follow up if needed
```

## Integration

Works with: Linear (tasks), Obsidian (notes), Cron jobs (scheduling), Telegram/Discord (notifications)
