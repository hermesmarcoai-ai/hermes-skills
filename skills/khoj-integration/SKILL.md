---
name: khoj-integration
description: |
  Khoj AI second brain. 34k+ stars. Semantic search, chat with docs,
  research agents, Obsidian integration.
trigger: "khoj,research,brain,knowledge base,semantic search"
---

# Khoj Integration

## Cloud (No Setup)
```
https://app.khoj.dev
API: https://app.khoj.dev/api
```

## Docker Self-Host
```bash
docker pull ghcr.io/khoj-ai/khoj
docker run -v /path/to/vault:/kb -p 8000:8000 ghcr.io/khoj-ai/khoj
```

## Features
- Chat with PDFs, Markdown, Obsidian, Notion
- Semantic search
- Custom agents
- Web + docs simultaneous search

## API Usage
```python
requests.post("https://app.khoj.dev/api/chat",
  json={"q": "query", "stream": False})
```

## Hermes Integration
```python
# Cron: Morning research
khoj_search(query) → save to Obsidian
```