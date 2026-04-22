---
name: deep-research
description: Trigger deep research mode using Perplexity Sonar Deep Research model via OpenRouter when user explicitly requests "deep research"
triggers:
  - deep research
  - "deep research"
  - do deep research
  - perform deep research
---

# Deep Research Mode

## Overview

When the user explicitly mentions **"deep research"**, switch to the `perplexity/sonar-deep-research` model for web extraction and analysis tasks. This model provides more comprehensive, in-depth research capabilities compared to the standard `perplexity/sonar-pro`.

## Trigger Phrases

Any of the following should activate deep research mode:
- "deep research"
- "do deep research on..."
- "perform deep research"
- "I need deep research"

## Implementation

### Method 1: Environment Variable Override (Recommended)

When the user triggers deep research mode, set the environment variable before calling web tools:

```python
import os

# Check for deep research trigger
def should_use_deep_research(user_input: str) -> bool:
    """Check if user is requesting deep research mode."""
    triggers = [
        "deep research",
        "sonar-deep-research",
    ]
    user_lower = user_input.lower()
    return any(trigger in user_lower for trigger in triggers)

# If deep research detected, override the model
if should_use_deep_research(user_message):
    os.environ["AUXILIARY_WEB_EXTRACT_MODEL"] = "perplexity/sonar-deep-research"
    os.environ["AUXILIARY_WEB_EXTRACT_PROVIDER"] = "openrouter"
    os.environ["AUXILIARY_WEB_EXTRACT_BASE_URL"] = "https://openrouter.ai/api/v1"
```

### Method 2: Tool-Level Override

When calling web_extract in deep research mode, explicitly use the deep research model.

## Model Details

| Mode | Model | Provider | Use Case |
|------|-------|----------|----------|
| Standard | `perplexity/sonar-pro` | OpenRouter | Normal web extraction and summarization |
| Deep Research | `perplexity/sonar-deep-research` | OpenRouter | When user explicitly requests "deep research" |

## Important Notes

- **Do NOT** use deep research model for normal web search - it consumes more tokens and is slower
- Only activate when user explicitly says "deep research" or similar phrases
- Standard `web_search` uses Firecrawl/Parallel backend, only `web_extract` uses LLM processing
- Reset environment variables after the deep research task to return to normal mode

## Pitfalls

**Don't modify config.yaml permanently for temporary mode switches.** The config file should keep `perplexity/sonar-pro` as the default. Use environment variable overrides at runtime to activate deep research mode temporarily. This follows "configure once, override dynamically" pattern - config.yaml for defaults, env vars for session-specific overrides.

## Example Workflow

```yaml
User: "Do deep research on quantum computing breakthroughs in 2026"

Action:
  1. Detect "deep research" trigger
  2. Set AUXILIARY_WEB_EXTRACT_MODEL=perplexity/sonar-deep-research
  3. Perform web search to find sources
  4. Use web_extract with deep research model for comprehensive analysis
  5. Reset to normal model after completion
```
