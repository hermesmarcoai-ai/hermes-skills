---
name: cron-alert-noise-reduction
description: Reduce alert fatigue from cron jobs — intelligent deduplication, batching, and severity filtering to prevent notification spam.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [cron, alerts, noise-reduction, monitoring, notifications]
    category: devops
---

# Cron Alert Noise Reduction

Intelligent deduplication, batching, and severity filtering for cron job alerts. Prevents notification spam while ensuring critical alerts still get through.

## When to Use

- "I'm getting too many cron notifications"
- "Only alert me if it's really broken"
- "Batch similar alerts together"
- "Set up escalation for persistent issues"

## Alert Severity Levels

| Level | Definition | Action |
|-------|-----------|--------|
| CRITICAL | Gateway down, data loss | Immediate push |
| WARNING | Degraded, recoverable | Batched (1h window) |
| INFO | Routine, expected | Daily digest |
| DEBUG | Verbose, dev only | Never notify |

## Deduplication Rules

```
Rule: Same error, same skill, within 1 hour → suppress
Rule: Same error, different skill → group into batch
Rule: New error type → always notify (once)
Rule: Recovery from error → notify once ("resolved")
```

## Batching Strategy

```
WARNINGS → Batch for 1 hour
  • 5+ warnings in 1h → single notification: "5 issues in monitoring"
  • Include: issue list, severity trend

INFO → Daily digest at 18:00
  • All routine events from the day
  • Format: "Daily digest: 3 skills updated, 2 cron jobs ran"

CRITICAL → Instant (no batching)
```

## Configuration

```yaml
# ~/.hermes/config.yaml
alert_filter:
  severity_threshold: WARNING  # Ignore INFO below this
  dedup_window_minutes: 60
  batch_window_minutes: 60
  max_batched_alerts: 10
  digest_time: "18:00"
  channels:
    telegram:
      critical: instant
      warning: batched
      info: daily_digest
    discord:
      critical: instant
      warning: batched
      info: daily_digest
```

## Setup

```bash
# Apply to all existing cron jobs
hermes cron list --format=json | jq '.[] | .id' | xargs -I{} \
  hermes cron update {} --alert-level=warning

# Set per-cron override
hermes cron update <job_id> --alert-level=critical
```

## Notification Format

### Batched warning

```
⚠️  CRON ALERTS (5 in last hour)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. hermes-gateway: 3x "connection timeout"
2. hermes-health-check: 2x "disk > 80%"
3. hermes-auto-update: "git pull failed"
→ Most likely cause: network blip
```

### Resolved notification

```
✅ RECOVERED: hermes-gateway
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Was: "connection timeout" (3 occurrences)
Now: Gateway responding normally
Duration: 12 minutes
```
