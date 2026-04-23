---
name: setup-shell-automation
description: Shell automation utilities for common VPS tasks — cron-based scripts, background jobs, log rotation, and system maintenance.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [shell, automation, cron, scripts, maintenance]
    category: devops
---

# Setup Shell Automation

Shell scripts and automation utilities for common VPS maintenance tasks.

## When to Use

- "Automate this repetitive task"
- "Set up log rotation"
- "Create a background job"
- "Write a shell script for my VPS"

## Common Scripts

### Log Rotation

```bash
#!/bin/bash
# /usr/local/bin/rotate-logs.sh

LOG_DIR="/var/log/hermes"
MAX_SIZE_MB=100
MAX_DAYS=7

find $LOG_DIR -type f -name "*.log" -size +${MAX_SIZE_MB}M | while read log; do
  mv "$log" "$log.$(date +%Y%m%d-%H%M%S)"
  gzip "$log".*
  # Keep only last $MAX_DAYS
  find $LOG_DIR -name "*.log.*.gz" -mtime +$MAX_DAYS -delete
done
```

### Health Check Script

```bash
#!/bin/bash
# /usr/local/bin/hermes-health.sh

# Check gateway
if ! pgrep -f "tui_gateway.entry" > /dev/null; then
  echo "Gateway down, restarting..."
  cd /root/.hermes && python -m tui_gateway.entry &
fi

# Check disk
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
  echo "⚠️  Disk at ${DISK_USAGE}%" | send_telegram_alert
fi
```

### Automatic Updates

```bash
#!/bin/bash
# /usr/local/bin/hermes-auto-update.sh

cd /root/.hermes
git pull
pip install -e . -q
pm2 restart hermes-gateway
```

### Disk Space Monitor

```bash
#!/bin/bash
# /usr/local/bin/disk-check.sh

df -h | grep -vE '^Filesystem|tmpfs|loop'
du -sh /root/.hermes/* 2>/dev/null | sort -h | tail -10
```

## Cron Setup

```bash
# Add to crontab
crontab -e

# Health check every 5 minutes
*/5 * * * * /usr/local/bin/hermes-health.sh >> /var/log/hermes/health.log 2>&1

# Log rotation daily at 02:00
0 2 * * * /usr/local/bin/rotate-logs.sh >> /var/log/hermes/rotate.log 2>&1

# Auto-update every Sunday at 03:00
0 3 * * 0 /usr/local/bin/hermes-auto-update.sh >> /var/log/hermes/update.log 2>&1
```

## Background Jobs with PM2

```bash
# Long-running scripts with auto-restart
pm2 start /usr/local/bin/hermes-health.sh --name health-check --cron-restart "*/5 * * * *"

# Script that never exits (monitoring)
pm2 start /usr/local/bin/monitor.sh --name monitor

# Save and restart on boot
pm2 save
pm2 startup
```

## Useful One-Liners

```bash
# Watch logs in real-time
tail -f /var/log/hermes/gateway.log | grep -i error

# Kill all processes for a user
pkill -u username

# Find largest directories
du -ah / | sort -rh | head -20

# Monitor CPU usage
watch -n 1 "ps aux --sort=-%cpu | head -11"

# Find files modified in last 24h
find /root -mtime 0 -ls

# Background process that survives logout
nohup ./script.sh > output.log 2>&1 &
```

## Script Templates

### Basic daemon script

```bash
#!/bin/bash
# /usr/local/bin/my-daemon.sh

while true; do
  # Do the thing
  python3 /root/.hermes/scripts/do_thing.py
  
  # Wait before next run
  sleep 60
done
```

### Exit on error

```bash
#!/bin/bash
set -euo pipefail

# Your script here
echo "Starting..."
```

## Tips

- Always use `set -euo pipefail` in scripts
- Log to `/var/log/<app>/` for system logs
- Use `nohup` for background jobs that should survive logout
- Set `SHELL=/bin/bash` in crontab for full features
