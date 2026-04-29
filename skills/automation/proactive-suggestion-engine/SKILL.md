---
name: proactive-suggestion-engine
description: Proactive failure pattern detection — monitors cron jobs, subagent failures, and repeated errors; offers investigations before user notices
triggers:
  - after any failed cron job or subagent task
  - periodic health check intervals
  - when session history shows same error 3+ times
  - during morning brief generation
steps:
  - "1. Scan recent failure logs: ~/.hermes/logs/, cron output, subagent traces"
  - "2. Count occurrences of each unique error pattern"
  - "3. If any pattern appears 3+ times → flag as recurring"
  - "4. Generate suggestion: specific investigation offer with root cause hypothesis"
  - "5. Present to user only if confidence is high (≥ 3 occurrences OR explicit failure signal)"
detection_targets:
  - cron job failures (exit code != 0)
  - subagent task failures (exit_reason: failed/max_iterations)
  - repeated API errors (same endpoint same error 3+ times)
  - skill execution failures (skill produces unexpected output)
suggestion_format: |
  ⚠️ Pattern detected: [short description]
  
  Seen: X times in recent logs
  Last seen: Y ago
  Hypothesis: [likely root cause]
  
  Want me to investigate?
confidence_levels:
  low: "1-2 occurrences — mention in passing"
  medium: "3 occurrences — offer investigation"
  high: "5+ occurrences — strongly recommend investigation"
integration_points:
  - Run after every failed subagent task
  - Run during morning brief (automatic)
  - Run on demand: "check for problems", "anything broken?"
pitfalls:
  - don't spam user with low-confidence suggestions
  - don't suggest investigation if user just fixed the issue
  - distinguish "same error different cause" from "same error same cause"
  - never block on this — it's always async/non-blocking
  - avoid keyword-only patterns — "Gateway.*down" catches SIGTERM shutdown messages, not actual crashes. Use more specific anchors like "gateway.*restart.*signal|crash|panic"
  - order matters: more specific patterns must come before general ones in the PATTERNS list
---

## Proactive Suggestion Engine

### How It Works

```
Failure Event → Error Parser → Pattern Counter → Confidence Score
                                                      ↓
                           Suggestion Generator ← Pattern Match (≥ 3x)
                                  ↓
                           User Notification (only if confidence ≥ medium)
```

### Error Pattern Types

| Type | Source | Detection Method |
|------|--------|------------------|
| Cron failure | cron output logs | exit code != 0 |
| Subagent failure | task traces | exit_reason in [failed, max_iterations] |
| API error | logs/agent.log | repeated same error string |
| Skill failure | skill execution output | unexpected output format |
| Network error | logs | ETIMEDOUT, ConnectionRefused |

### Suggestion Examples

**Low confidence (mention in passing):**
> "Noticed a couple of API timeouts in the logs lately — likely transient, let me know if it happens again."

**Medium confidence (offer investigation):**
> "⚠️ The cron-wrapper.sh has failed 3 times with predicate errors. Last time: `shell:"false"` exit code 1. Want me to investigate the predicate evaluation logic?"

**High confidence (recommend investigation):**
> "🔴 VPS gateway has failed 5 times in 24h — all with ETIMEDOUT on Telegram. This looks like a network-level issue. Recommend running `openclaw-telegram-etimedout-fix`. Want me to apply it now?"

### Integration

Run proactively:
```bash
python3 ~/.hermes/skills/automation/proactive-suggestion-engine/scripts/detector.py
```

Or import the detector into any skill/post-processing step.
