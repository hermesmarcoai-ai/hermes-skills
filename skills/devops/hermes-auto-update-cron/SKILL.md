---
name: hermes-auto-update-cron
description: Setup cron job for automatic Hermes Agent code updates — git pull + dependency install + gateway restart, with Discord notification.
category: devops
---

## Overview

Automatically checks for and applies Hermes Agent updates on a scheduled basis. Prevents the agent from falling behind on upstream commits.

## Setup

```bash
hermes cron add "Auto-update Hermes" --schedule "0 */6 * * *" --script /root/hermes-backup/auto-update.sh
```

## Script: auto-update.sh

```bash
#!/bin/bash
set -euo pipefail

cd /root/hermes-agent

# Fetch and check for updates
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "$(date): Already up to date"
    exit 0
fi

echo "$(date): New commits detected ($LOCAL → $REMOTE)"

# Pull updates
git pull origin main

# Install dependencies if changed
if git diff --name-only HEAD@{1} HEAD | grep -qE '(requirements|pyproject|setup)'; then
    cd /root/hermes-agent
    source venv/bin/activate
    pip install -r requirements.txt -q
fi

# Restart gateway
pkill -9 -f hermes_gateway
sleep 3
systemctl start hermes-gateway.service

echo "$(date): Updated and gateway restarted ($REMOTE)"
```

## Verification

- `hermes cron list` — check job is active
- `hermes cron logs <job-id>` — review last run output
- Check Discord for update notification

## Known Pitfalls

- Same Discord token conflict as manual restarts — the script uses `pkill -9` + `systemctl start` (proven fix pattern)
- Kills active Telegram session too (unavoidable shared-process issue)
- Only notifies on actual updates; silent when already current
