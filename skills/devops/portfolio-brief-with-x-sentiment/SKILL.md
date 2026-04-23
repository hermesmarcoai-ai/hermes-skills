---
name: hermes-permanent-agent-team
description: Spawn a permanent team of specialized AI agents that work together 24/7 — each agent has a specific role and expertise.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [multi-agent, team, delegation, autonomous, permanent]
    category: autonomous-ai-agents
---

# Permanent Agent Team

Spawn and manage a permanent team of specialized AI agents that work together 24/7. Each agent has a defined role and collaborates with others.

## When to Use

- "Set up a team of agents"
- "I need specialized agents for different domains"
- "Run multiple agents that share context"
- "Create an autonomous team that works while I sleep"

## Team Structure

```
Hermes (Team Lead)
├── Researcher  → Web search, fact-checking, arxiv
├── Coder       → Code review, PRs, implementation
├── Monitor     → Health checks, alerting, incidents
└── Writer      → Emails, docs, reports
```

## Roles

| Agent | Specialty | Tools |
|-------|-----------|-------|
| Team Lead (this) | Coordination, delegation, human interface | All |
| Researcher | Web search, arxiv, blogwatcher | web, search, arxiv |
| Coder | GitHub, code review, PR workflow | github, terminal |
| Monitor | Health checks, cron, alerting | cron, health-check |
| Writer | Emails, docs, briefs | email, obsidian |

## Spawning the Team

```python
from hermes_tools import delegate_task

# Spawn Researcher
researcher = delegate_task(
    goal="You are Researcher on Marco's team. Your job: web search, arxiv, fact-check claims, summarize articles. Report findings to Team Lead.",
    context="Team Lead will assign you tasks. Always report back with sources.",
    role="leaf"
)

# Spawn Coder
coder = delegate_task(
    goal="You are Coder on Marco's team. Your job: code review, PR checks, GitHub issues. Report to Team Lead.",
    context="Use github-pr-workflow and code-review skills. Report findings to Team Lead.",
    role="leaf"
)
```

## Team Communication

```
Human → Team Lead → Sub-agents → Report back
              ↓
         Team Lead summarizes
              ↓
         Response to Human
```

## Shared Context

Team members share context via:
- Obsidian (shared notes)
- Cron output (scheduled reports)
- Session history (last N messages)

## Operating Loop

```bash
# Morning: All agents check in
# 08:00 → Researcher: overnight news summary
# 08:00 → Monitor: health check + gateway status
# 08:00 → Writer: prepare daily brief

# Throughout day: Team Lead delegates
# User request → Team Lead → appropriate agent → report

# Evening: EOD reports
# 18:00 → Each agent reports progress
# 18:00 → Team Lead compiles summary
```

## Tips

- Keep agents focused (one role each)
- Team Lead should summarize, not do all work
- Use shared Obsidian for cross-agent memory
- Set clear escalation: "if blocked, report to Team Lead"
