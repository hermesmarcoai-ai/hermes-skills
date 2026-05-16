---
name: khoj-research-agent
description: |
  Automated research using Khoj. Searches knowledge base + web,
  synthesizes reports, morning briefings.
trigger: "research,khoj,investigate,briefing"
---

# Khoj Research Agent

## Pipeline
```
1. Khoj (local knowledge)
2. Web (internet)
3. Synthesize
4. Save to Obsidian
5. Summary
```

## Usage
```bash
python3 ~/.hermes/scripts/khoj-research.py "query" --save
```

## Cron: Morning Research
```json
{
  "name": "Morning Research",
  "prompt": "khoj research top 5 items, save to Obsidian",
  "schedule": "0 6 * * *"
}
```

## API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Chat |
| `/api/search` | GET | Semantic search |