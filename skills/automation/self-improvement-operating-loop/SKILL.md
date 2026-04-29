---
name: self-improvement-operating-loop
description: Evolutionary self-improvement loop for Hermes Agent using DSPy + GEPA. Evolve skills, prompts, and tool descriptions through reflective genetic search.
version: 1.0
author: NousResearch / Marco
metadata:
  hermes:
    tags: [self-improvement, optimization, dspy, skills, evolution]
    category: automation
    skill_dir: /home/marco/hermes-agent-self-evolution
---

# Self-Improvement Operating Loop

Automated skill and prompt evolution for Hermes Agent using [hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution) (DSPy + GEPA).

## When to Use

- User says "improve this skill", "optimize my agent", or "self-evolve"
- A skill produces sub-optimal results and needs targeted improvement
- After discovering a recurring failure pattern in agent behavior
- Periodic maintenance: run on a schedule to keep skills sharp

## How It Works

```
Read skill/prompt → Generate eval dataset → GEPA mutates
       ↑                                      ↓
Execution traces ←── Evaluate candidates ←── Constraint gates
       ↓
Best variant → PR against skill repo
```

**No GPU needed.** ~$2-10 per optimization run via API calls.

## Setup (One-Time)

```bash
# Clone the evolution engine
git clone https://github.com/NousResearch/hermes-agent-self-evolution.git ~/hermes-agent-self-evolution
cd ~/hermes-agent-self-evolution
pip install -e ".[dev]"

# Point at your hermes-agent/skills repo
export HERMES_AGENT_REPO=~/.hermes/skills
```

## Run Evolution

### Evolve a specific skill

```bash
cd ~/hermes-agent-self-evolution

# With synthetic eval data (fast, no history needed)
python -m evolution.skills.evolve_skill \
    --skill github-code-review \
    --iterations 10 \
    --eval-source synthetic

# With real session history (more accurate, needs sessiondb)
python -m evolution.skills.evolve_skill \
    --skill github-code-review \
    --iterations 10 \
    --eval-source sessiondb
```

### Evolve all skills at once

```bash
python -m evolution.skills.evolve_all \
    --iterations 5 \
    --eval-source synthetic
```

### Check status

```bash
python generate_report.py --latest
ls ~/hermes-agent-self-evolution/reports/
```

## Phase Roadmap

| Phase | Target | Status |
|-------|--------|--------|
| 1 | Skill files (SKILL.md) | ✅ Done |
| 2 | Tool descriptions | 🔲 Soon |
| 3 | System prompt sections | 🔲 Soon |
| 4 | Tool implementation code | 🔲 Soon |
| 5 | Fully automated loop | 🔲 Soon |

## Constraint Gates

Every evolved variant must pass:
- `pytest tests/ -q` — 100% pass
- Skill size ≤ 15KB
- Tool description ≤ 500 chars
- Semantic preservation check
- Human PR review

## Tips

- Run Phase 1 on skills that change frequently or underperform
- Use `sessiondb` source for skills that fail in specific contexts
- Keep `HERMES_AGENT_REPO` pointing to the **skills** directory, not the main agent repo
- Review generated PRs carefully — evolution can drift semantics
- Cost per run: ~$2-10 depending on iterations and eval source

## Skills Added (2026-04-25)

- `cron-conditional-execution` — conditional cron predicates (price/state/time/shell)
- `deep-research-iterative` — iterative research loop with gap analysis
- `multi-modal-output` — video/animation/PDF generation pipeline
- `decision-log` — save reasoning before closing strategic threads
- `context-cross-reference` — multi-front project coordination pattern
