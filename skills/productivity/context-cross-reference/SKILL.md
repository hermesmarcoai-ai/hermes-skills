---
name: context-cross-reference
description: Internal operating pattern for multi-front project coordination — track cross-domain dependencies and avoid context fragmentation
triggers:
  - working on projects spanning code + ops + markets
  - delegating to multiple subagents in parallel
  - switching between different project domains
steps:
  - "Before starting any sub-task, scan active project fronts and tag which ones are involved"
  - "Maintain a lightweight front registry at ~/.hermes/.active-fronts.md listing: project name, domain, last modified, key files"
  - "When delegating in parallel, include cross-front context in each subagent context (not just its own front)"
  - "After completing a sub-task on multi-front project, update the front registry timestamp"
  - "Before closing a multi-front thread, run decision-log skill if strategic decisions were made"
pitfalls:
  - working in isolation — forgetting to check other fronts for relevant context
  - context bleed — subagent knows nothing about sibling fronts state
  - orphan decisions — strategic choices made without logging reasoning
front_registry_template: |
  # Active Project Fronts
  | Project | Domain | Last Active | Key Files | Notes |
  |---------|--------|-------------|-----------|-------|
verification:
  - Front registry exists at ~/.hermes/.active-fronts.md
  - Each subagent task includes relevant cross-front context
  - Multi-front threads trigger decision-log before closing
---

## Context Cross-Reference Pattern

When working on projects that span multiple domains (code + ops + markets), context easily becomes fragmented across subagents and sessions. This pattern keeps everything anchored.

### Front Registry

Maintain `~/.hermes/.active-fronts.md`:

```
| Project | Domain | Last Active | Key Files | Notes |
|---------|--------|-------------|-----------|-------|
| Content Factory | creative | 2026-04-25 | scripts/content-factory/ | Discord pipeline |
| VPS Migration | devops | 2026-04-24 | skills/hermes-vps-migration/ | Phase 2 pending |
| Trading Bot | markets | 2026-04-25 | wundertrading/ | BTC momentum |
```

### Cross-Front Delegation

When delegating to parallel subagents, include this in context:
- What other fronts exist
- What the sibling agents are working on
- Any shared dependencies or files

### When to Trigger

- Any task involving 2+ domains
- Parallel subagent launches
- Thread switching between different project areas
