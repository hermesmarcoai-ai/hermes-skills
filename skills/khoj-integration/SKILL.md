---
name: khoj-integration
description: |
  Khoj AI second brain integration. Provides deep research, semantic search,
  document Q&A, and automated research workflows. Self-hosted or cloud options.
  34k+ stars, Python-based, Obsidian native.
trigger: "khoj,research,brain,second brain,deep search,semantic,knowledge base"
---

# Khoj AI Second Brain Integration

[Khoj](https://khoj.dev) — Your AI second brain. Self-hostable, supports Obsidian, chat with any LLM.

## Setup Options

### Cloud (Quick Start)
```bash
# Just use https://app.khoj.dev — no setup required
# API endpoint: https://app.khoj.dev/api
```

### Self-Hosted Docker
```bash
# Pull official image
docker pull ghcr.io/khoj-ai/khoj

# Run with Obsidian vault
docker run -v /path/to/obsidian:/kb \
  -p 8000:8000 \
  -e OBSIDIAN_VAULT_DIR=/kb \
  ghcr.io/khoj-ai/khoj
```

### Self-Hosted Python
```bash
pip install khoj --break-system-packages
khoj --help
```

## Features

- **Chat with docs**: PDF, Markdown, Obsidian, Notion, Word
- **Semantic search**: Find info using natural language
- **Research agent**: Automated deep research pipelines
- **Custom agents**: Create agents with specific knowledge/persona
- **Web search**: Query internet + your docs simultaneously
- **Image generation**: Integrate with Stable Diffusion
- **Audio**: Text-to-speech, voice messages

## API Integration

```python
import requests

# Chat with Khoj
def khoj_chat(query, conversation_id=None):
    response = requests.post(
        "https://app.khoj.dev/api/chat",
        json={
            "q": query,
            "conversationId": conversation_id,
            "stream": False
        },
        headers={"Authorization": "Bearer YOUR_API_KEY"}
    )
    return response.json()

# Search docs
def khoj_search(query):
    response = requests.get(
        f"https://app.khoj.dev/api/search?q={query}",
        headers={"Authorization": "Bearer YOUR_API_KEY"}
    )
    return response.json()
```

## Hermes Integration Pattern

```python
# Use Khoj for deep research in Hermes
def deep_research(query):
    # 1. Query Khoj for relevant context
    context = khoj_search(query)
    
    # 2. Use context + web search for comprehensive answer
    # 3. Save findings to Obsidian
    
    return summary

# Cron job: Morning research digest
CRON: "0 6 * * *"
PROMPT: "Use khoj_search to find top 5 relevant items from your knowledge base.
Save to ~/Obsidian-Vault/daily-research/YYYY-MM-DD.md"
```

## Khoj Agents for Hermes

Create specialized agents:

1. **Research Agent** → Uses Khoj to find relevant past work
2. **Writing Agent** → Queries knowledge base for context
3. **Trading Agent** → Searches financial docs, market analysis
4. **Coding Agent** → Finds relevant code patterns from docs

## Obsidian Integration

Khoj natively supports Obsidian. Enable in Khoj settings:
- Vault path: `/home/Obsidian-Vault`
- Index markdown, create semantic search over notes
- Chat with your notes using natural language

## Configuration

```yaml
# ~/.hermes/config/khoj.yaml
khoj:
  api_url: https://app.khoj.dev/api
  api_key: ${KHOJ_API_KEY}  # From environment
  vault_path: /home/Obsidian-Vault
  default_model: claude-3.5-sonnet
  
  agents:
    research:
      system: "Use Khoj to find relevant information from your knowledge base."
    trading:
      system: "Search financial documents, market analysis, trading logs."
```

## Troubleshooting

```bash
# Check Khoj status
curl https://app.khoj.dev/api/health

# Re-index Obsidian vault
# In Khoj settings → Re-index all files

# Clear cache
# Settings → Clear embedding cache
```