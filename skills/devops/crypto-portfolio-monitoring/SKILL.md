---
name: cron-job-recovery
description: Automatic recovery and restart for failed cron jobs — detects failures, implements backoff, and escalates persistent failures to human notification.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [cron, recovery, failure, restart, automation]
    category: devops
---

# Cron Job Recovery

Automatic recovery system for failed cron jobs. Detects failures, applies exponential backoff, and escalates persistent failures.

## When to Use

- "My cron job failed — try again automatically"
- "Don't spam me with the same failure"
- "Restart the gateway if it crashes"
- "Escalate if something keeps failing"

## Recovery Flow

```
Failure detected
       ↓
Check: Is this a transient error?
  → Network timeout, rate limit → Retry with backoff
  → Auth error, config error → DO NOT retry → Escalate
       ↓
Retry 1: wait 5 min
       ↓
Retry 2: wait 15 min
       ↓
Retry 3: wait 60 min
       ↓
Still failing? → Escalate to human
```

## Backoff Schedule

| Attempt | Wait Time | Total Elapsed |
|---------|-----------|---------------|
| 1 | 5 min | 5 min |
| 2 | 15 min | 20 min |
| 3 | 60 min | 80 min |
| 4+ | 4 hours | Escalate |

## Error Classification

### Retry-Ready (transient)
- Network timeout / DNS failure
- Rate limiting (429)
- Temporary service unavailability
- Resource exhaustion (temp)

### Non-Retry (permanent)
- Authentication failure (401, 403)
- Invalid configuration
- Missing files/permissions
- Code errors (500 from our services)

## Setup

```bash
# Enable auto-recovery for a cron job
hermes cron update <job_id> --recovery=auto

# Set max retries
hermes cron update <job_id> --max-retries=3

# Disable recovery for a specific job
hermes cron update <job_id> --recovery=none
```

## Integration with hermes-gateway-troubleshooting

When the gateway itself fails, this skill coordinates:
1. Detect gateway down (via health check)
2. Attempt PM2 restart
3. If that fails, restart the service
4. If still failing, page human

## Log Format

```
[RECOVERY] hermes-auto-update @ 14:23
  → git pull failed (network timeout)
  → Retry 1/3 in 5 min
  → SUCCESS at 14:28
```
