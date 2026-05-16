---
name: khoj-research-agent
description: |
  Automated research agent using Khoj. Searches knowledge base + web,
  synthesizes reports, creates research briefs. Integrates with daily
  cron jobs for morning briefings.
trigger: "research,khoj,deep research,investigate,knowledge base,research brief"
---

# Khoj Research Agent

Automated research using Khoj's AI second brain + web search capabilities.

## Research Pipeline

```
1. Query Khoj (local knowledge)
   ↓
2. Query Web (internet search)
   ↓
3. Synthesize Findings
   ↓
4. Save to Obsidian
   ↓
5. Generate Summary
```

## Usage

### Basic Research Query
```bash
# Direct API call to Khoj cloud
curl -X POST "https://app.khoj.dev/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"q": "What are the latest developments in crypto trading?", "stream": false}'
```

### Python Research Function
```python
import requests
from datetime import datetime

def khoj_research(query, save_to_vault=True):
    """
    Perform research using Khoj AI second brain.
    """
    # 1. Query Khoj
    response = requests.post(
        "https://app.khoj.dev/api/chat",
        json={"q": f"Research: {query}", "stream": False}
    )
    khoj_results = response.json()
    
    # 2. Search web for additional context
    web_results = duckduckgo_search(query, limit=10)
    
    # 3. Synthesize
    summary = f"""# Research: {query}
Date: {datetime.now().strftime('%Y-%m-%d')}

## Key Findings
{khoj_results.get('response', 'No response')}

## Web Sources
{chr(10).join([f"- {r['title']}: {r['link']}" for r in web_results[:5]])}

## Confidence
Based on {len(web_results)} sources from web + Khoj knowledge base.
"""
    
    # 4. Save to Obsidian
    if save_to_vault:
        date = datetime.now().strftime('%Y-%m-%d')
        path = f"/home/Obsidian-Vault/research/{date}-{query[:30]}.md"
        with open(path, 'w') as f:
            f.write(summary)
    
    return summary
```

## Cron Job: Morning Research

```json
{
  "name": "Morning Research Digest",
  "prompt": "Use khoj_research to find top 5 relevant items from your knowledge base. Check for new trading signals, market analysis, or interesting articles. Save to ~/Obsidian-Vault/daily-research/YYYY-MM-DD.md",
  "schedule": "0 6 * * *",
  "deliver": "telegram"
}
```

## Research Templates

### Trading Research
```
Topic: {crypto/stock} + {specific query}
Output: ~/Obsidian-Vault/Trading/research/{date}-{ticker}.md

Sections:
- Current price action
- Key levels to watch
- Sentiment analysis
- Source links
```

### Technical Research
```
Topic: {technology trend}
Output: ~/Obsidian-Vault/Research/{date}-{topic}.md

Sections:
- Overview
- Key players
- Market impact
- Future predictions
```

## Khoj API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Chat with Khoj |
| `/api/search` | GET | Semantic search |
| `/api/files` | GET | List indexed files |
| `/api/conversation` | GET | Conversation history |

## Authentication

```bash
# Get API key from https://app.khoj.dev/settings
export KHOJ_API_KEY="your-key-here"

# Use in requests
curl -H "Authorization: Bearer $KHOJ_API_KEY" \
  "https://app.khoj.dev/api/chat"
```