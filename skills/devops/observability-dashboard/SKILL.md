---
name: observability-dashboard
description: Single command system health overview — active fronts, cron jobs, gateway, disk/memory, recent failures
triggers:
  - "how is everything running?"
  - "system health"
  - "dashboard"
  - "status check"
  - "observability"
  - "health overview"
category: devops
---

# Observability Dashboard

Single command to get a text-mode health overview of the Hermes Agent system.

## Usage

```
dashboard
```

Or run the script directly:

```bash
python3 ~/.hermes/skills/devops/observability-dashboard/scripts/dashboard.py
```

## Output Sections

| Section | Source | Indicators |
|---------|--------|------------|
| Active Fronts | `~/.hermes/.active-fronts.md` | ✅ OK / ⚠️ WARNING / 🔴 CRITICAL |
| Cron Jobs | `cronjob list` | ✅ OK / ⚠️ WARNING / 🔴 CRITICAL |
| Gateway Status | PM2 process list | ✅ OK / ⚠️ WARNING / 🔴 CRITICAL |
| Disk/Memory | `df`, `free` | ✅ OK / ⚠️ WARNING / 🔴 CRITICAL |
| Recent Failures | System logs | 🔴 CRITICAL |

## Exit Codes

- `0` — All systems OK
- `1` — One or more WARNING
- `2` — One or more CRITICAL

## Color Indicators

- ✅ OK — Green, all healthy
- ⚠️ WARNING — Yellow, attention needed
- 🔴 CRITICAL — Red, immediate action required

## Dependencies

No external dependencies. Uses only standard tools:
- `df` — Disk usage
- `free` — Memory usage
- `ps` — Process status
- `crontab` / `cronjob` — Cron job listing
- `pm2` — Process management (if available)
