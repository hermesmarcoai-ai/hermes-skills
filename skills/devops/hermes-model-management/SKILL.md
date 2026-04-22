---
name: hermes-model-management
description: Manage Hermes agent model configuration — change default model, monitor free model pricing changes, configure auxiliary models (vision/web_extract)
triggers:
  - change hermes model
  - change default model
  - hermes using which model
  - update hermes config
  - auxiliary model configuration
  - configure vision model
  - model pricing change
---

# Hermes Model Management

How to change, monitor, and manage model configuration for the Hermes Agent.

## Changing the Default Model

1. Read current config:
```bash
grep -n "default:" ~/.hermes/config.yaml | head -1
```

2. Patch the model in `~/.hermes/config.yaml`:
```python
# Using the patch tool:
path: ~/.hermes/config.yaml
old_string: "default: deepseek/deepseek-v3.2"
new_string: "default: qwen/qwen3.6-plus:free"
```

3. Restart the gateway to apply:
```bash
pm2 restart hermes-gateway --update-env
```

## Key Config Locations

| Setting | Path in config.yaml | Purpose |
|---------|--------------------|---------|
| Default model | `model.default` | Main agent responses |
| Provider | `model.provider` | API provider (e.g., openrouter) |
| Vision model | `auxiliary.vision.model` | Image analysis |
| Web extract model | `auxiliary.web_extract.model` | Web page summarization |

## Auxiliary Models — Critical Configuration

**IMPORTANT:** Auxiliary models MUST NOT set `api_key: ''` (empty string) — this explicitly overrides the credential pool fallback and causes 401 "Missing Authentication header" errors.

To use credential pool auto-resolution (from `~/.hermes/.env`), simply omit the `api_key` field:

```yaml
auxiliary:
  vision:
    provider: openrouter
    model: qwen/qwen-2.5-vl-72b-instruct:free
    base_url: https://openrouter.ai/api/v1
    timeout: 30
    download_timeout: 30
    # NO api_key field here — uses env cred pool
  web_extract:
    provider: openrouter
    model: perplexity/sonar-pro
    base_url: https://openrouter.ai/api/v1
    timeout: 30
    # NO api_key field
```

**If you see 401 errors in vision:** Check that `api_key: ''` is NOT present in config.yaml for the auxiliary model.

## Free Model Recommendations (OpenRouter)

| Use Case | Model | Notes |
|----------|-------|-------|
| Main chat | `qwen/qwen3.6-plus:free` | Good quality, free tier |
| Vision analysis | `qwen/qwen-2.5-vl-72b-instruct:free` | Best free vision model |
| Web extract | `perplexity/sonar-pro` | Already configured, costs from OpenRouter credits |

## Monitoring Free Model Pricing

If using a `:free` model, monitor for price changes via cron:
```python
# Create a cron job to check every 6 hours
cronjob(action='create',
    name='Monitor {model} Pricing',
    prompt="Check if model '{model}' on OpenRouter is still free...",
    schedule='every 6h',
    model='openai/gpt-4o-mini',
    deliver='origin')
```

## Daily Auto-Update Cron

To keep Hermes updated automatically:
```python
cronjob(action='create',
    name='Daily Hermes Agent Update',
    prompt="Execute a daily update check for the Hermes Agent...\n1. cd /root/.hermes/hermes-agent && git fetch origin\n2. Compare LOCAL vs REMOTE...\n3. If updates: backup config, git stash, pull, npm install, uv pip install -e ., pm2 restart --update-env",
    schedule='0 4 * * *',
    model='openai/gpt-4o-mini',
    deliver='local')
```

## Common Issues

### "Missing Authentication header" 401 on vision calls
- **Cause:** `api_key: ''` present in auxiliary config section
- **Fix:** Remove the `api_key: ''` line from the auxiliary model config

### Model change not taking effect
- **Cause:** Gateway needs restart with `--update-env` flag
- **Fix:** `pm2 restart hermes-gateway --update-env`

### Telegram timeout errors after model change
- **Cause:** Unrelated to model change — Telegram uses fallback IPs
- **Fix:** Gateway reconnects automatically; check `pm2 logs hermes-gateway`

## Free Model Recommendations (2026 Verified via OpenRouter API)

| Use Case | Model | Avg cost/M | Context | Notes |
|----------|-------|-----------|---------|-------|
| Main chat | `qwen/qwen3.6-plus:free` | FREE | 1M tokens | Best free model (SWE-bench 78.8) |
| Vision analysis | `qwen/qwen-2.5-vl-72b-instruct:free` | FREE | Good for photo analysis |
| Fallback main | `deepseek/deepseek-v3.2` | $0.32 avg | 164K tokens | Cheapest top-tier — $0.26 in + $0.38 out |
| Fallback lite | `google/gemini-2.5-flash-lite` | $0.25 avg | 1M tokens | Multimodal, excellent research |
| Fallback long context | `x-ai/grok-4-fast` | $0.35 avg | 2M tokens | Longest context on market |

## Anthropic OAuth Tokens (Claude Subscription)

Anthropic offers two credential types:
| Credential | Prefix | Billing |
|------------|--------|---------|
| OAuth Token | `sk-ant-oat01-...` | Uses Claude.ai Pro/Max subscription quota |
| API Key | `sk-ant-api03-...` | Separate pay-per-token billing |

The OAuth token (`sk-ant-oat01-...`) is generated from Claude.ai account settings and **consumes your Pro/Max subscription quota** — no additional API charges. It's designed for personal tools, prototypes, and single-user apps.

To generate one:
1. Install Claude Code CLI: `npm install -g @anthropic-ai/claude-code`
2. Log in with your Anthropic account on a machine with interactive terminal
3. Run `claude setup-token` and copy the generated token
4. The token can be used with any API client (Anthropic Python SDK, curl, etc.)

**Limitations:**
- Tied to subscription tier — rate limits apply
- NOT for multi-user/SaaS products (against ToS)
- Key rotation is complex (tied to account session)
- Only useful for personal tools, dev prototypes

**Hermes Support:** Hermes natively supports standard API keys via OpenRouter or direct Anthropic API. For direct OAuth token usage, configure the token via `~/.hermes/.env` with `OPENROUTER_API_KEY=sk-ant-oat01-...` or test compatibility with direct Anthropic endpoint.

## Troubleshooting Gateway Startup After Update

When updating Hermes, PM2 restart may fail with exit code 1. This is normal — the process still restarts. Verify with:
```bash
pm2 list  # Check status is "online"
pm2 logs hermes-gateway --lines 20 --nostream  # Check for errors
```

## Cron Job — Price Monitoring Best Practices (Verified 2026)

**CRITICAL: Avoid false alarms in price-monitoring cron jobs.**
The OpenRouter API returns pricing as strings (e.g., `"0"` for free models). A cron prompt that checks `price != "0"` or compares as string can generate false alerts even when price is $0.

Use precise numeric comparison with epsilon threshold:
```
If BOTH prompt < 0.0000001 AND completion < 0.0000001 → exit silently (NO output)
If EITHER > 0.0000001 → report price change
If model NOT FOUND in API response → report removal
```

## OpenRouter Model Landscape (Verified Live API — April 2026)

Scanned 350 models via `https://openrouter.ai/api/v1/models`. Key findings:

### Best Free Models (prompt: "0", completion: "0")
| Model | Context | Notes |
|-------|---------|-------|
| `qwen/qwen3.6-plus:free` | 1M | Best free model on OpenRouter (SWE-bench 78.8) |
| `nousresearch/hermes-3-llama-3.1-405b:free` | 131K | Hermes 3 405B — powerful reasoning |
| `meta-llama/llama-3.3-70b-instruct:free` | 65K | Solid reasoning, 70B params |
| `google/gemma-3-27b-it:free` | 131K | Best free Google model, multimodal |
| `minimax/minimax-m2.5:free` | 197K | Good general purpose |

### Best Paid Budget Options (avg $/M token)
| Model | In $/M | Out $/M | Avg | Context | Notes |
|-------|--------|---------|-----|---------|-------|
| `google/gemini-2.5-flash-lite` | 0.10 | 0.40 | 0.25 | 1M | Best value paid model |
| `deepseek/deepseek-v3.2` | 0.26 | 0.38 | 0.32 | 164K | Proven, stable, cheapest top-tier |
| `x-ai/grok-4-fast` | 0.20 | 0.50 | 0.35 | 2M | Longest context on market |
| `google/gemini-2.5-flash` | 0.30 | 2.50 | 1.40 | 1M | Full Gemini 2.5 Flash |

### Premium (AVOID for autonomous agent — overpriced)
| Model | In $/M | Out $/M | Avg $/M |
|-------|--------|---------|---------|
| `openai/gpt-5-chat` | 1.25 | 10.00 | 5.62 |
| `claude-sonnet-4.6` | 3.00 | 15.00 | 9.00 |
| `claude-opus-4.6` | 5.00 | 25.00 | 15.00 |
| `openai/gpt-5-pro` | 15.00 | 120.00 | 67.50 |

**Cost per session estimate** (typical 2h/day agent use, ~50K tokens/session):
- Free model: €0
- Deepseek-V3.2: €0.02/session → ~€4-8/month
- Claude Sonnet: €0.54/session → ~€100+/month
