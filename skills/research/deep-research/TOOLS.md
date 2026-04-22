# Deep Research Tools Configuration

## Web Tools Integration

### Auxiliary Configuration Reference

Located in `~/.hermes/config.yaml`:

```yaml
auxiliary:
  web_extract:
    provider: openrouter
    model: perplexity/sonar-pro          # Standard model for normal requests
    base_url: https://openrouter.ai/api/v1
    api_key: ''                          # Uses OPENROUTER_API_KEY from .env
    timeout: 30
```

### Deep Research Override

When triggered by user saying "deep research", temporarily override with:

```yaml
auxiliary:
  web_extract:
    provider: openrouter
    model: perplexity/sonar-deep-research  # Deep research model
    base_url: https://openrouter.ai/api/v1
    api_key: ''
    timeout: 60                           # Increase timeout for deeper processing
```

## Environment Variable Overrides

The web tools check for these environment variables at runtime:

| Variable | Standard Value | Deep Research Value |
|----------|----------------|---------------------|
| `AUXILIARY_WEB_EXTRACT_PROVIDER` | `openrouter` | `openrouter` |
| `AUXILIARY_WEB_EXTRACT_MODEL` | `perplexity/sonar-pro` | `perplexity/sonar-deep-research` |
| `AUXILIARY_WEB_EXTRACT_BASE_URL` | `https://openrouter.ai/api/v1` | `https://openrouter.ai/api/v1` |
| `AUXILIARY_WEB_EXTRACT_TIMEOUT` | `30` | `60` |

## Code Implementation

### web_tools.py Integration

The model selection happens in `~/.hermes/hermes-agent/tools/web_tools.py`:

```python
# Line 249
DEFAULT_SUMMARIZER_MODEL = os.getenv("AUXILIARY_WEB_EXTRACT_MODEL", "").strip() or None

# This is used in process_content_with_llm() at line 258
async def process_content_with_llm(
    content: str, 
    url: str = "", 
    title: str = "",
    model: str = DEFAULT_SUMMARIZER_MODEL,  # Uses env var if set
    min_length: int = DEFAULT_MIN_LENGTH_FOR_SUMMARIZATION
) -> Optional[str]:
```

### Usage Pattern

```python
# Before deep research task
import os
original_model = os.environ.get("AUXILIARY_WEB_EXTRACT_MODEL", "perplexity/sonar-pro")
os.environ["AUXILIARY_WEB_EXTRACT_MODEL"] = "perplexity/sonar-deep-research"
os.environ["AUXILIARY_WEB_EXTRACT_TIMEOUT"] = "60"

# Perform web extract
try:
    result = await web_extract_tool(urls=[...])
finally:
    # Restore normal settings
    os.environ["AUXILIARY_WEB_EXTRACT_MODEL"] = original_model
    os.environ["AUXILIARY_WEB_EXTRACT_TIMEOUT"] = "30"
```

## API Endpoint Details

### OpenRouter Configuration
- **Base URL**: `https://openrouter.ai/api/v1`
- **Models**: 
  - `perplexity/sonar-pro` (standard)
  - `perplexity/sonar-deep-research` (deep research)
- **API Key**: Read from `OPENROUTER_API_KEY` environment variable

### Request Format

```bash
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "perplexity/sonar-deep-research",
    "messages": [
      {"role": "system", "content": "Extract and analyze web content"},
      {"role": "user", "content": "Summarize: <content>"}
    ]
  }'
```
