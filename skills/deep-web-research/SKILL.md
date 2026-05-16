---
name: deep-web-research
description: |
  Autonomous deep research agent that searches the web, analyzes sources,
  and synthesizes comprehensive reports. Uses multiple search engines
  and evaluates source quality.
trigger: "research,deep search,web analysis,investigate,find information,search"
---

# Deep Web Research Agent

Autonomous agent that performs comprehensive web research with source verification.

## Research Flow

1. **Query Analysis** → Break down question into search components
2. **Parallel Search** → Search multiple engines/sources simultaneously
3. **Source Evaluation** → Assess credibility and relevance
4. **Information Synthesis** → Combine findings into coherent report
5. **Citation** → Provide source links for all claims

## Search Commands

```bash
# DuckDuckGo search
duckduckgo-search "your query here" --limit 10

# YouTube transcript extraction
yt-dlp --write-auto-sub --skip-download "VIDEO_URL"

# Wikipedia research
wikipedia-search "topic"

# Academic papers (if arxiv skill loaded)
arxiv search "keywords"
```

## Output Format

```
# Research Report: [Topic]

## Executive Summary
[2-3 sentence overview]

## Key Findings
1. [Finding with source]
2. [Finding with source]
...

## Sources
- [Source 1](url)
- [Source 2](url)
...

## Confidence Level
[High/Medium/Low based on source quality]
```

## Quality Rules

- Cross-reference facts across 3+ sources
- Prefer official sources over secondary
- Note conflicting information
- Flag unverified claims
- Include publication dates