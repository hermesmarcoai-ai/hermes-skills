# web-search-plus — Hermes Plugin

Multi-provider web search with intelligent auto-routing for the [Hermes AI agent](https://github.com/robbyczgw-cla).

> Ported from [robbyczgw-cla/web-search-plus-plugin](https://github.com/robbyczgw-cla/web-search-plus-plugin) (OpenClaw) to the Hermes Plugin API.

---

## Features

- **Intelligent auto-routing** — picks the best provider automatically based on query intent
- **7 providers** — Serper, Tavily, Exa, Querit, Perplexity, You.com, SearXNG
- **Exa Deep Research** — `depth=deep` for multi-source synthesis, `depth=deep-reasoning` for cross-document analysis
- **Time filtering** — `time_range=day/week/month/year`
- **Domain filtering** — whitelist or blacklist specific domains
- **Local caching** — avoids duplicate API calls
- **Graceful fallback** — skips unavailable providers

---

## Routing Logic

| Provider | Best for | Free tier |
|----------|----------|-----------|
| Serper (Google) | News, shopping, facts, local queries | 2,500/mo |
| Tavily | Research, deep content, academic topics | 1,000/mo |
| Exa | Semantic discovery, "alternatives to X", "companies like Y", arxiv | 1,000/mo |
| Querit | Multilingual, real-time queries | 1,000/mo |
| Perplexity | Direct AI-synthesized answers | Via API key |
| You.com | LLM-ready real-time snippets | Limited |
| SearXNG | Privacy, self-hosted, no API key needed | Free |

Auto-routing scores each provider based on query signals (keywords, intent, patterns) and picks the highest match. Override anytime with `provider=...`.

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/robbyczgw-cla/hermes-web-search-plus.git \
  ~/.hermes/plugins/web-search-plus
```

### 2. Install Python dependencies

The plugin calls `search.py` as a subprocess. Dependencies:

```bash
cd ~/.hermes/plugins/web-search-plus
pip install requests
```

> Python 3.8+ required. No other dependencies needed for basic usage.
> For Exa deep research: `pip install httpx` (optional, falls back to requests)

### 3. Set API keys

Copy the template and fill in at least one key:

```bash
cp ~/.hermes/plugins/web-search-plus/.env.template \
   ~/.hermes/plugins/web-search-plus/.env
```

Edit `.env`:

```bash
# Required (at least one)
SERPER_API_KEY=your-serper-key        # https://serper.dev — 2,500 free/mo
TAVILY_API_KEY=your-tavily-key        # https://tavily.com — 1,000 free/mo
EXA_API_KEY=your-exa-key              # https://exa.ai — 1,000 free/mo

# Optional
QUERIT_API_KEY=your-querit-key        # https://querit.ai
PERPLEXITY_API_KEY=your-perplexity-key  # https://www.perplexity.ai/settings/api
KILOCODE_API_KEY=your-kilocode-key    # fallback for Perplexity via Kilo Gateway
YOU_API_KEY=your-you-key              # https://api.you.com
SEARXNG_INSTANCE_URL=https://your-instance.example.com  # self-hosted
```

### 4. Verify the plugin loads

Start a Hermes session and check that `web_search_plus` appears in available tools. Test with:

```
Search for: Graz weather today
```

You should see `[Provider: serper | auto-routed | ...]` in the response.

---

## Tool: `web_search_plus`

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | **required** | The search query |
| `provider` | string | `"auto"` | Force a provider: `serper`, `tavily`, `exa`, `querit`, `perplexity`, `you`, `searxng`, or `auto` |
| `depth` | string | `"normal"` | Exa depth: `normal`, `deep` (4-12s synthesis), `deep-reasoning` (12-50s cross-doc analysis) |
| `count` | integer | `5` | Number of results (1–20) |
| `time_range` | string | — | Recency filter: `day`, `week`, `month`, `year` |
| `include_domains` | array | — | Whitelist domains, e.g. `["arxiv.org", "github.com"]` |
| `exclude_domains` | array | — | Blacklist domains, e.g. `["reddit.com"]` |

### Examples

```python
# Auto-routing (default)
web_search_plus(query="Graz weather today")
# → routed to Serper

# Force Exa for semantic discovery
web_search_plus(query="alternatives to Notion for note taking", provider="exa")

# Exa deep synthesis
web_search_plus(query="impact of LLMs on software development", provider="exa", depth="deep")

# Exa deep reasoning for complex analysis
web_search_plus(
    query="reconcile conflicting claims about transformer scaling laws",
    provider="exa",
    depth="deep-reasoning"
)

# News from last 24h
web_search_plus(query="OpenAI latest news", provider="serper", time_range="day")

# Only arxiv results
web_search_plus(query="LoRA fine-tuning survey", include_domains=["arxiv.org"])

# Exclude Reddit
web_search_plus(query="best Python async libraries", exclude_domains=["reddit.com"])
```

### Direct CLI testing

```bash
python3 ~/.hermes/plugins/web-search-plus/search.py \
  --query "test query" \
  --provider auto \
  --max-results 5 \
  --compact
```

---

## Architecture

```
__init__.py      — Hermes plugin entry point, tool schema, handler, registration
search.py        — Core search engine (~2600 lines): all providers, routing logic, caching
plugin.yaml      — Plugin manifest (name, version, toolsets)
.env.template    — API key reference
CHANGELOG.md     — Version history
```

The plugin calls `search.py` as a subprocess, passing query params as CLI args and forwarding all env vars. Timeout is **75 seconds** to support Exa deep-reasoning queries.

### Hermes Plugin API note

The Hermes tool registry calls handlers with the full input dict as the **first positional argument**, not as `**kwargs`. The handler unpacks it with `isinstance(args_or_query, dict)`.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

## Feature parity

| Feature | OpenClaw plugin | Hermes plugin |
|---------|:-:|:-:|
| Auto-routing | ✅ | ✅ |
| Serper / Tavily / Exa / Querit | ✅ | ✅ |
| Perplexity / You.com / SearXNG | ✅ | ✅ |
| `depth` (Exa deep/deep-reasoning) | ✅ | ✅ |
| `time_range` | ✅ | ✅ |
| `include_domains` / `exclude_domains` | ✅ | ✅ |
| Timeout 75s | ✅ | ✅ |
| Local caching | ✅ | ✅ |

---

## Related

- [OpenClaw plugin](https://github.com/robbyczgw-cla/web-search-plus-plugin) — original TypeScript version for OpenClaw
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — the agent this plugin runs on
