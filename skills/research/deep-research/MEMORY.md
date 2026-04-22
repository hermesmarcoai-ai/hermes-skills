# Deep Research Memory / Implementation Notes

## Current Configuration (as of 2026-04-02)

### Standard Web Extract Model
- **Model**: `perplexity/sonar-pro`
- **Provider**: OpenRouter
- **Purpose**: Normal web page extraction and summarization

### Deep Research Model
- **Model**: `perplexity/sonar-deep-research`
- **Provider**: OpenRouter  
- **Purpose**: Only used when user explicitly says "deep research"
- **Characteristics**: More comprehensive analysis, higher token usage, slower

## Trigger Detection

### Active Triggers
- "deep research" (case insensitive)
- "sonar-deep-research"
- "do deep research"
- "perform deep research"

### Examples of Trigger Phrases
✅ **Should activate deep research:**
- "Do deep research on quantum computing"
- "I need a deep research report on climate change"
- "Can you perform deep research on crypto markets?"

❌ **Should NOT activate deep research (use standard sonar-pro):**
- "Search for information about quantum computing"
- "Find me articles on climate change"
- "Look up crypto market data"

## Implementation Approach

Since Hermes doesn't have a built-in "deep research" mode switch, we use environment variable overrides:

1. **Before** calling `web_extract_tool()`, check user input for trigger phrases
2. If triggered, set `AUXILIARY_WEB_EXTRACT_MODEL=perplexity/sonar-deep-research`
3. Proceed with web extraction
4. (Optional) Restore original model after task

## File Locations

- Main config: `~/.hermes/config.yaml`
- Web tools code: `~/.hermes/hermes-agent/tools/web_tools.py`
- Auxiliary client: `~/.hermes/hermes-agent/agent/auxiliary_client.py`
- Environment file: `~/.hermes/.env`

## Model Comparison

| Aspect | Sonar Pro | Sonar Deep Research |
|--------|-----------|---------------------|
| Speed | Fast | Slower |
| Depth | Standard | More thorough |
| Cost | Lower | Higher |
| Use for | Quick summaries, simple extraction | Complex analysis, comprehensive reports |
| Trigger | Default | "Deep research" phrase only |

## Testing

To verify deep research mode is active:
1. Check logs for model being used
2. Verify response depth and quality
3. Monitor token usage

## Notes

- The `web_search` tool (finding URLs) uses Firecrawl/Parallel and doesn't use LLM
- Only `web_extract` (content processing) uses the Perplexity models
- The environment variable override affects only the current process/session
- For persistent change, modify `config.yaml` (not recommended for this use case)
