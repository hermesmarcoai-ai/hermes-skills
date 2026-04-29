---
name: semantic-skill-routing
description: Automatically route tasks to the most relevant skills using lightweight semantic matching (TF-IDF). Always run before selecting a skill for any non-trivial task.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [routing, skill-selection, tfidf, semantic-match, automation]
    trigger: always_run_before_skill_selection
---

# Semantic Skill Routing

Automatically find the most relevant skill(s) for a given task using lightweight semantic matching — no LLM required.

## Trigger

**Always run before selecting a skill for any non-trivial task** (complex queries, multi-step tasks, or tasks where the optimal skill is unclear).

Do NOT run when:
- User explicitly names a skill (e.g., "use the github-code-review skill")
- Task is trivial (simple question, greeting)
- Query is about the router itself

## Algorithm

1. **Parse all skills**: Load every `~/.hermes/skills/*/SKILL.md`, extract `name` and `description` from frontmatter + body text.
2. **Build TF-IDF corpus**: Use `scripts/skill_router.py` which creates a TF-IDF vectorizer from all skill names + descriptions.
3. **Score input query**: Transform query into TF-IDF vector, compute cosine similarity against all skills.
4. **Return top-k matches**: Return top 3 matches with scores > threshold (default 0.1).

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `threshold` | 0.1 | Minimum score to suggest a skill |
| `top_k` | 3 | Number of matches to return |
| `skills_dir` | `~/.hermes/skills/` | Where skills are located |

## Output Format

```json
[
  {
    "skill": "github-code-review",
    "score": 0.847,
    "reason": "Query contains 'code review' which strongly matches skill name and description"
  },
  {
    "skill": "github-pr-workflow",
    "score": 0.623,
    "reason": "Query contains 'pull request' related terms"
  }
]
```

## Pitfalls

1. **User override**: If user explicitly names a skill, do NOT run the router or override their choice.
2. **Low score suppression**: If top match score < threshold, return empty suggestions and let the agent decide.
3. **Exact skill names**: If query contains an exact skill name, boost that skill's score.
4. **Performance**: Full scan must complete in < 500ms. TF-IDF is fast; avoid any LLM calls.
5. **Missing SKILL.md**: Skills without SKILL.md are skipped silently.
6. **Category matching**: Query "productivity" should boost skills in the productivity category.

## Reference Implementation

```bash
# Run the router from command line
python ~/.hermes/skills/productivity/semantic-skill-routing/scripts/skill_router.py "review my code changes"

# Python API
from skill_router import SkillRouter
router = SkillRouter()
results = router.route("write a test for this function")
print(results)
```

## Example Queries

| Query | Top Match | Score |
|-------|-----------|-------|
| "review my pull request" | github-code-review | 0.85 |
| "schedule a meeting" | google-workspace | 0.72 |
| "analyze this dataset" | jupyter-live-kernel | 0.68 |
| "deploy to production" | docker-management | 0.61 |
| "make a diagram" | architecture-diagram | 0.55 |

## Files

- `SKILL.md` — This file
- `scripts/skill_router.py` — Core routing engine
- `references/routing_rules.md` — Manual override rules
