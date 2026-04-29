---
name: auto-model-routing
category: mlops
description: Automatically select the best LLM model for a given task based on task characteristics using lightweight rules-based routing.
triggers:
  - before any non-trivial task when model hasn't been specified by user
  - when user asks for help without specifying a specific model
  - when a task could benefit from cost-effective model selection
version: 1.0.0
---

# Auto Model Routing Skill

## Purpose

Automatically select the best model for a given task based on task characteristics. Uses a lightweight rules-based router — **no LLM needed for routing decisions**.

## Trigger Conditions

Activate this skill when:
- User submits a task without specifying a model
- Task complexity is unclear and you need to choose an appropriate model
- You want to optimize for cost-performance balance

## Routing Logic

### Task Classification Flow

```
Task Text → Keyword Analysis → Category Detection → Model Selection
```

### Model Categories

| Category | Keywords | Selected Model | Provider |
|----------|----------|----------------|----------|
| **reasoning/heavy** | debug, architect, design, analyze, complex, system | claude-sonnet-4-20250514 | anthropic |
| **fast/light** | quick, simple, one-liner, small, easy, fix typo | MiniMax-M2.7-highspeed | minimax |
| **creative** | write, story, creative, song, poem, narrative | MiniMax-M2.7-highspeed | minimax |
| **research** | research, find, investigate, explore, search | deep-research-iterative | perplexity |
| **coding** | code, implement, refactor, program, build, function | claude-sonnet-4-20250514 | anthropic |

## Output Format

```json
{
  "selected": "model-name",
  "provider": "provider-name",
  "confidence": 0.85,
  "reason": "Matched category 'coding' via keyword 'code'"
}
```

## Override Rules

1. **User-specified model always wins** — If user explicitly names a model, use that model regardless of routing rules
2. **Context-aware** — Consider task complexity even without explicit keywords
3. **Cost awareness** — Don't route trivial tasks to expensive models

## Confidence Levels

| Level | Score | Criteria |
|-------|-------|----------|
| High | 0.8-1.0 | Explicit keyword match |
| Medium | 0.5-0.79 | Partial match or context inference |
| Low | 0.3-0.49 | Ambiguous, using fallback |

## Fallback

If no rule matches: return `MiniMax-M2.7-highspeed` with `confidence: 0.3`

## Usage

### CLI

```bash
python scripts/router.py "debug my Python code"
```

### Integration

```python
from router import route_task

result = route_task("analyze this architecture")
print(result)
```

## Files

- `scripts/router.py` — Main routing engine
- `references/rules.md` — Detailed routing rules and model mappings
