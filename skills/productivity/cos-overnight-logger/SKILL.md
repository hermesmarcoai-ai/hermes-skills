---
name: cos-overnight-logger
description: Overnight monitoring and logging for the Chief of Staff suite — tracks overnight events, incidents, and important notifications for morning review.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [monitoring, overnight, logging, incidents, cos]
    category: productivity
---

# COS Overnight Logger

Tracks overnight events, system incidents, and important notifications for morning review. Part of the Chief of Staff operating loop.

## When to Use

- Evening check-in: "Log today's progress before shutdown"
- Morning review: "What happened overnight?"
- Incident detection: "Something went wrong with the VPS"
- Setting up overnight monitoring alerts

## Setup

```bash
# Ensure cron jobs are set up for overnight monitoring
# See: hermes-auto-update-cron, hermes-gateway-troubleshooting
```

## Usage

### End-of-day log

```
User: "End-of-day summary"
→ Collect:
  - Tasks completed today
  - Outstanding items for tomorrow
  - Any incidents or blockers
→ Write to Obsidian daily note
→ Post summary to Telegram if configured
```

### Overnight monitoring

Monitors and logs:
- Hermes gateway uptime (via health-check cron)
- System resources (disk, memory, CPU)
- Any cron job failures
- Discord/Telegram message volume (anomaly detection)

### Morning review format

```
🌅 OVERNIGHT REPORT
━━━━━━━━━━━━━━━━━━━━
Gateway: ✅ Online (uptime: 18h)
Disk: ⚠️  72% full (VPS)
Memory: ✅  58% used
Cron failures: 1 (hermes-auto-update — network timeout)

📬 TALKED BETWEEN US
━━━━━━━━━━━━━━━━━━━━
Discord: 0 new messages
Telegram: 2 new messages

📋 READY FOR TODAY
━━━━━━━━━━━━━━━━━━━━
1. Follow up with Marco about VPS specs
2. Review PR #47 (pending since Tue)
```

## Cron Integration

```bash
hermes cron create \
  --name "Overnight monitoring" \
  --prompt "Run cos-overnight-logger health check, log results to Obsidian daily note, alert if gateway down" \
  --schedule "0 23 * * *" \
  --deliver local
```
