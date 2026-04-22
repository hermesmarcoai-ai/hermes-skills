---
name: hermes-gateway-troubleshooting
description: Diagnose and fix Hermes messaging gateway connectivity issues (Telegram/Discord down, stale locks, PM2 problems)
triggers:
  - telegram gateway not working
  - discord gateway not working
  - hermes gateway down
  - "Another local Hermes gateway is already using"
  - gateway connection error
  - pm2 gateway stopped
  - telegram bot token lock
  - hermes gateway locked
---

# Hermes Gateway Troubleshooting

Common connectivity issues and solutions for Hermes messaging gateway.

## Quick Diagnostics

Check gateway status:
```bash
~/.hermes/node/bin/pm2 status
```

View recent logs:
```bash
~/.hermes/node/bin/pm2 logs hermes-gateway --lines 50
tail -50 /root/.pm2/logs/hermes-gateway-error-0.log
tail -50 /root/.pm2/logs/hermes-gateway-out-0.log
```

## Issue 1: "Another local Hermes gateway is already using this token"

**Symptoms:**
- Error in logs: `ERROR gateway.platforms.telegram: [Telegram] Another local Hermes gateway is already using this Telegram bot token (PID XXXXX)`
- Telegram shows as "failed to connect" in gateway startup
- Gateway was previously killed/crashed without proper cleanup

**Root Cause:**
Stale lock files in `~/.local/state/hermes/gateway-locks/` from a dead process that didn't clean up.

**Solution:**

1. Stop the gateway:
```bash
~/.hermes/node/bin/pm2 stop hermes-gateway
```

2. Remove stale lock files:
```bash
# Check what lock files exist
ls -la ~/.local/state/hermes/gateway-locks/

# Remove Telegram lock
rm -f ~/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock

# Remove all locks if needed (nuclear option)
rm -f ~/.local/state/hermes/gateway-locks/*.lock
```

3. Restart gateway:
```bash
~/.hermes/node/bin/pm2 start hermes-gateway
~/.hermes/node/bin/pm2 save
```

4. Verify:
```bash
~/.hermes/node/bin/pm2 status
sleep 3 && tail -20 /root/.pm2/logs/hermes-gateway-error-0.log
```

**Look for:** `Telegram fallback IPs active` (normal warning) without `ERROR` lines.

## Issue 2: Gateway Shows "stopped" in PM2

**Solution:**
```bash
~/.hermes/node/bin/pm2 start hermes-gateway
~/.hermes/node/bin/pm2 save
```

## Issue 3: Gateway Cycling/Repeatedly Restarting

Check for fatal errors in logs, common causes:
- Invalid bot token
- Network connectivity issues
- Lock conflicts

```bash
# Check last errors
tail -100 /root/.pm2/logs/hermes-gateway-error-0.log | grep -E "(ERROR|FATAL)"

# Full restart with cleanup
~/.hermes/node/bin/pm2 delete hermes-gateway
~/.hermes/node/bin/pm2 start ~/.hermes/hermes-agent/gateway/ecosystem.config.js
~/.hermes/node/bin/pm2 save
```

## Issue 4: Gateway Frozen (Process Running But Not Responding)

**Symptoms:**
- `pm2 status` shows "online" but Telegram/Discord not responding
- No new log entries despite hours passing
- Last log timestamp is old compared to current time

**Diagnosis:**
```bash
# Compare current time vs last log entry
date '+%H:%M'
tail -1 /root/.pm2/logs/hermes-gateway-error-0.log | grep -oE '[0-9]{2}:[0-9]{2}'

# Check for stale lock files even if process seems running
cat ~/.local/state/hermes/gateway-locks/*.lock | grep pid

# Count actual gateway processes (should be 1)
ps aux | grep -E "hermes.*gateway" | grep -v grep | wc -l
```

**Solution:**
```bash
# Stop PM2-managed gateway
~/.hermes/node/bin/pm2 stop hermes-gateway

# Kill ALL orphaned gateway processes by pattern
pkill -f "hermes.*gateway"

# Remove ALL lock files
rm -f ~/.local/state/hermes/gateway-locks/*.lock

# Verify no processes remain
ps aux | grep -E "hermes.*gateway" | grep -v grep

# Restart clean
~/.hermes/node/bin/pm2 start hermes-gateway
~/.hermes/node/bin/pm2 save

# Verify single process
ps aux | grep -E "hermes.*gateway" | grep -v grep | wc -l  # Should show: 1
```

## Issue 5: After Manual Process Cleanup, Multiple Processes Remain

**Symptoms:**
- Used Python/execute_code to kill specific PIDs
- Still getting "Another local Hermes gateway is already using this token" error
- Multiple gateway processes visible in `ps aux`
- After fixing, Discord shows "This token is already in use" (process 21404 scenario)

**Root Cause:**
Manually targeting specific PIDs can leave other gateway instances running. The gateway auto-restarts on failure, creating new processes. Discord token can be held by orphaned processes.

**Solution:**
```bash
# Don't target specific PIDs - kill ALL by pattern
pkill -f "hermes.*gateway"

# Or use stronger sigkill if needed
pkill -9 -f "hermes.*gateway"

# Remove locks and restart
rm -f ~/.local/state/hermes/gateway-locks/*.lock
~/.hermes/node/bin/pm2 restart hermes-gateway
```

**Key Lesson:** Always use pattern-based killing (`pkill -f`) rather than targeting specific PIDs that may have been restarted/replaced. For Discord token conflicts specifically:
1. Find orphaned Discord gateway processes with `ps aux | grep -E "hermes.*gateway.*discord"`
2. Kill via pattern or specific PID if visible
3. For multiple systemd instances, use `systemctl stop hermes-gateway` first

## Issue 6: Multiple PM2 Log Files (Confusion Over Which to Check)

**Symptoms:**
- `tail -20 /root/.pm2/logs/hermes-gateway-error-0.log` shows old logs, nothing recent
- Gateway seems to be running but no new error logs appearing
- `pm2 status` shows online but Telegram/Discord not responding

**Root Cause:**
PM2 may write to different log files:
- `hermes-gateway-error-0.log` (numbered, from older PM2 instance)  
- `hermes-gateway-error.log` (current, non-numbered)

This happens when PM2 process is deleted and recreated with same name.

**Solution:**
```bash
# List ALL log files to see which is actually being written
ls -lah ~/.pm2/logs/hermes-gateway*

# Check the most recently modified file
ls -lt ~/.pm2/logs/hermes-gateway*.log | head -5

# Or check both
for f in ~/.pm2/logs/hermes-gateway-error*.log; do
    echo "=== $f ==="
    tail -5 "$f"
done
```

**Key Lesson:** When troubleshooting, always verify you're reading the active log file by checking modification timestamps.

## Issue 7: PM2 Gateway Shows "errored" with ModuleNotFoundError

**Symptoms:**
- `pm2 status` shows status "errored" immediately after start
- No logs generated or logs show `ModuleNotFoundError: No module named 'hermes_cli'`
- Gateway exits with code 1 repeatedly

**Root Cause:**
Started PM2 with direct path to hermes binary: `pm2 start /root/.local/bin/hermes -- hermes gateway run`. This bypasses the Python virtualenv that contains hermes_cli dependencies.

**Solution:**

1. Stop the broken instance:
```bash
~/.hermes/node/bin/pm2 delete hermes-gateway
```

2. Create a wrapper script that sources the venv first (`~/.hermes/gateway-both.sh`):
```bash
#!/bin/bash
export HOME=/root
export HERMES_HOME="/root/.hermes"
export PATH="$HERMES_HOME/node/bin:$HOME/.local/bin:${PATH}"

# CRITICAL: Load virtualenv BEFORE calling hermes
source "$HERMES_HOME/hermes-agent/venv/bin/activate"

# Load environment
if [ -f "$HERMES_HOME/.env" ]; then
    set -a
    source "$HERMES_HOME/.env"
    set +a
fi

# Run gateway
exec "$HOME/.local/bin/hermes" gateway run
```

3. Start with wrapper script:
```bash
chmod +x ~/.hermes/gateway-both.sh
~/.hermes/node/bin/pm2 start ~/.hermes/gateway-both.sh --name hermes-gateway
~/.hermes/node/bin/pm2 save
```

**Key Lesson:** Never start hermes directly in PM2 — always use a bash wrapper that activates the virtualenv first.

## Issue 7: Verify Specific Platform Status

After restart, check if platforms connected:
```bash
# Should show "Telegram fallback IPs active" for Telegram
grep -E "(telegram|discord)" /root/.pm2/logs/hermes-gateway-error-0.log | tail -10
```

## Issue 7b: Cron Delivery to Discord Fails with "Unknown Channel" (Error 404)

**Symptoms:**
- Cron jobs execute with `last_status: ok` but user never receives messages on Discord
- `journalctl -u hermes-gateway.service` shows: `ERROR cron.scheduler: Job 'xxx': delivery error: Discord API error (404): {"message": "Unknown Channel", "code": 10003}`

**Root Cause:**
The `DISCORD_HOME_CHANNEL` ID in `~/.hermes/config.yaml` points to a channel that doesn't exist or the bot doesn't have access to. This happens when channels are deleted, IDs change, or the bot was removed from the channel.

**Solution:**

1. Get the correct channel ID:
   - In Discord, enable Developer Mode (Settings > Advanced > Developer Mode)
   - Right-click the target channel > "Copy Channel ID"
   - Or ask the user to copy it

2. Update the config:
```bash
grep DISCORD_HOME_CHANNEL ~/.hermes/config.yaml
```

3. Patch with the new ID and restart:
```bash
pkill -9 -f hermes_gateway
sleep 3
systemctl start hermes-gateway.service
```

4. Verify delivery:
```bash
journalctl -u hermes-gateway.service --since "1 minute ago" | grep -i delivery
```

**Key Lesson:** Always verify Discord channel IDs periodically. When setting up cron delivery to Discord, test immediately after creation.

## Issue 8: Systemd Gateway Fails with Status 200/CHDIR or Permission Denied

**Symptoms:**
- Gateway is managed via systemd (NOT PM2)
- `systemctl status hermes-gateway.service` shows `failed (Result: exit-code)` or `Status 200/CHDIR`
- Process exits after 1ms
- Gateway shows as offline on Discord/Telegram

**Root Cause:**
The systemd service was configured with `User=hermes` and `Group=hermes`, but the hermes-agent directory (`/root/.hermes/hermes-agent/`) and config files are owned by `root` with restrictive permissions (700/600). The `hermes` user cannot access WorkingDirectory or read the config.

**Solution:**

1. Check current service config:
```bash
cat /etc/systemd/system/hermes-gateway.service
```

2. Check directory permissions:
```bash
ls -la /root/.hermes/
ls -la /root/.hermes/config.yaml
su -c "cd /root/.hermes/hermes-agent && pwd" hermes  # Should fail with "Permission denied" if this is the issue
```

3. Fix by changing service to run as root (simplest for personal server):
```bash
# Edit the service file, change these lines:
# User=root
# Group=root
# Remove all Environment= lines that override HOME/USER/PATH

# OR (alternative) fix permissions:
chown -R hermes:hermes /root/.hermes/
chmod -R 755 /root/.hermes/hermes-agent/
```

4. Recommended minimal systemd unit for root user:
```ini
[Unit]
Description=Hermes Agent Gateway
After=network-online.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/root/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
WorkingDirectory=/root/.hermes/hermes-agent
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

5. Restart:
```bash
pkill -9 -f hermes_gateway
sleep 3
systemctl daemon-reload
systemctl start hermes-gateway.service
sleep 3
systemctl status hermes-gateway.service
ps aux | grep hermes_cli | grep -v grep
```

6. Verify gateway is alive:
```bash
# Should show "active (running)" and a running python process
journalctl -u hermes-gateway.service --since "1 minute ago" | tail -20
```

**Key Lesson:** When gateway runs via systemd (not PM2), the User/Group in the service unit MUST match file ownership. On a personal VPS, running as root avoids all permission headaches.

## Issue 9: Discord Bot Requires @Mention to Read Messages

**Symptoms:**
- Bot ignores messages in server channels unless @mentioned
- User wants bot to respond to all messages without needing to tag

**Root Cause:**
This is expected behavior — the gateway has `DISCORD_REQUIRE_MENTION=true` by default.

**Key environment variables** (all checked in `gateway/platforms/discord.py:592-603,2041-2052`):

- `DISCORD_REQUIRE_MENTION` (default: `true`) — If `true`, bot only responds to @mentions in server channels unless channel is in free-response list or session is in a bot-initiated thread.
- `DISCORD_FREE_RESPONSE_CHANNELS` — Comma-separated channel IDs where bot responds without mention.
- `DISCORD_IGNORE_NO_MENTION` (default: `true`) — If message @mentions other users but NOT the bot, stay silent. Set to `false` to ignore this check.

**Solution — Read all messages without mention:**

Set in `~/.hermes/config.yaml` (under `discord:`):
```yaml
discord:
  require_mention: false
```
Or in `.env`:
```
DISCORD_REQUIRE_MENTION=false
```

Restart gateway after change.

**⚠️ Warning:** With `require_mention: false`, the bot will attempt to process ALL your messages in ALL channels. Avoid in shared servers with multiple users.

## Lock File Details

Lock files prevent multiple gateways from polling the same Telegram bot (which would cause conflicts):
- **Location:** `~/.local/state/hermes/gateway-locks/`
- **Naming convention:** `{scope}-{hash}.lock` (e.g., `telegram-bot-token-caad7d40317c2c76.lock`)
- **Content:** JSON with PID, start_time, and metadata
- **Safe to delete** if the referenced PID is dead (`ps aux | grep {pid}` shows nothing)

## Prevention

Use `--replace` flag when manually restarting gateway to auto-clean locks:
```bash
hermes gateway run --replace
```

**Note:** PM2-managed gateway should auto-restart on crashes, but may leave stale locks if killed with SIGKILL or on system hard reboot.