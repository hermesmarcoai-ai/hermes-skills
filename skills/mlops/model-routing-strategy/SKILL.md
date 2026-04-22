---
name: model-routing-strategy
category: mlops
description: Cost-optimized model routing strategy for Hermes Agent — selects the best model per task based on cost, quality, and context needs.
---

# Model Routing Strategy for Hermes Agent

## Principle
Maximize useful output per euro. Free first, then cheapest viable, then premium only when ROI justifies it.

## Current Landscape (OpenRouter, Apr 2026)

### Tier 1: FREE Models (use as defaults)
| Model | Context | Best For |
|---|---|---|
| `qwen/qwen3.6-plus:free` | 1M | **Primary default** — general reasoning, coding, conversation |
| `deepseek/deepseek-v3.2` | 164K | $0.26/M in, $0.38/M out — cheapest strong model |
| `qwen/qwen3-coder:free` | 262K | Coding-specific tasks |
| `qwen/qwen3-next-80b-a3b-instruct:free` | 262K | Strong reasoning, free |
| `meta-llama/llama-3.3-70b-instruct:free` | 65K | High-quality free fallback |
| `google/gemma-3-27b-it:free` | 131K | Multilingual, creative tasks |
| `google/gemini-2.0-flash-lite` | 1M | $0.075/M in, $0.30/M out — cheapest large-context paid |

### Tier 2: Ultra-Cheap (<$1/M tokens total)
| Model | In/M | Out/M | Context | Best For |
|---|---|---|---|---|
| `deepseek/deepseek-v3.2` | $0.26 | $0.38 | 164K | Best value reasoning |
| `mistralai/mistral-small-3.1-24b-instruct` | $0.03 | $0.11 | 131K | Fast, cheap responses |
| `qwen/qwen3-235b-a22b-thinking-2507` | $0.15 | $1.50 | 131K | Complex reasoning (thinking mode) |
| `qwen/qwen3-coder` | $0.22 | $1.00 | 262K | Heavy coding tasks |
| `google/gemini-2.5-flash-lite` | $0.10 | $0.40 | 1M | Long context, cheap |

### Tier 3: Mid-Range ($1-5/M tokens)
| Model | In/M | Out/M | Context | Best For |
|---|---|---|---|---|
| `qwen/qwen3-max-thinking` | $0.78 | $3.90 | 262K | Complex reasoning |
| `google/gemini-2.5-flash` | $0.30 | $2.50 | 1M | Vision, long context |
| `mistralai/mistral-large-2512` | $0.50 | $1.50 | 262K | Strong general-purpose |
| `deepseek/deepseek-r1` | $0.70 | $2.50 | 64K | Reasoning (R1 architecture) |

### Tier 4: Premium (use sparingly)
| Model | In/M | Out/M | Context | Best For |
|---|---|---|---|---|
| `anthropic/claude-sonnet-4.6` | $3.00 | $15.00 | ? | Best instruction following |
| `anthropic/claude-opus-4.6` | $5.00 | $25.00 | ? | Hardest reasoning problems |
| `google/gemini-2.5-pro` | $1.25 | $10.00 | 1M | Heavy reasoning, vision |

## Routing Rules

### Rule 1: Default = Free
Always start with `qwen/qwen3.6-plus:free`. It handles 90%+ of tasks well enough.

### Rule 2: Coding = Qwen3 Coder Free
Use `qwen/qwen3-coder:free` for code-heavy tasks.

### Rule 3: Complex Reasoning = DeepSeek V3.2
When free models struggle with logic/math/analysis, switch to `deepseek/deepseek-v3.2` ($0.38/M output = extremely cheap).

### Rule 4: Long Documents = Gemini Flash Lite
For 100K+ token contexts, use `google/gemini-2.5-flash-lite` ($0.10/M in, $0.40/M out).

### Rule 5: Vision = Qwen3-VL Free or Gemini
Use `qwen/qwen3-vl-8b-instruct` for $0.08/M input, or free alternatives.

### Rule 6: Premium Only When Justified
Anthropic/GPT-5 class models only when:
- Task quality directly monetizable
- User explicitly requests
- Budget allows (€8/mo cap)

## Cost Estimates (Monthly, typical usage)
- **Light** (~50 messages/day, avg 2K tokens each): ~$0-2/month
- **Medium** (~200 messages/day, avg 4K tokens): ~$2-5/month  
- **Heavy** (~500 messages/day, avg 10K tokens, some reasoning): ~$5-15/month

## Fallback Chain
1. qwen/qwen3.6-plus:free
2. qwen/qwen3-coder:free
3. meta-llama/llama-3.3-70b-instruct:free
4. deepseek/deepseek-v3.2
5. qwen/qwen3-235b-a22b-thinking-2507
6. qwen/qwen3-max-thinking

## VPS Local Considerations
- VPS specs matter for local inference. Check RAM/GPU before considering ollama/vllm local.
- 7B models → 8GB RAM minimum
- 70B models → 40GB+ VRAM or CPU (slow)
- MoE models (Qwen3 30B-A3B) → efficient, 16GB RAM may suffice
- API is almost always cheaper unless you have a GPU-equipped VPS

## Updates
Re-evaluate this file quarterly or when:
- OpenRouter adds new free models
- Qwen 3.6 free is removed/limited
- A new model offers 2x+ better price/performance
