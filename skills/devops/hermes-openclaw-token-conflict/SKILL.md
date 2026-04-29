---
name: hermes-openclaw-token-conflict
description: Fix token conflicts when Hermes and OpenClaw both try to use the same Discord/Telegram bot tokens
triggers:
  - openclaw gateway telegram conflict
  - openclaw gateway discord conflict
  - telegram polling conflict hermes openclaw
---

# Hermes + OpenClaw Bot Token Conflict Resolution

When both Hermes gateway and OpenClaw gateway run on the same machine with the same bot tokens, they fight over the connections.

## Symptoms

- Hermes log shows: `Telegram polling conflict (1/3), will retry in 10s. Error: Conflict: terminated by other getUpdates request`
- Discord may connect but silently fail
- `openclaw-gateway` and `hermes gateway run` processes both visible in `ps aux`

## Root Cause

OpenClaw gateway (Node.js app at `~/.openclaw/`) and Hermes gateway (Python) both poll the same Telegram bot and connect to the same Discord bot. Only ONE can hold the connection.

## Diagnosis

```bash
# Check for both processes
ps aux | grep -E "openclaw-gateway|hermes.*gateway" | grep -v grep

# Check OpenClaw channel config
cat ~/.openclaw/openclaw.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('Telegram:', d.get('channels',{}).get('telegram',{}).get('enabled')); print('Discord:', d.get('channels',{}).get('discord',{}).get('enabled'))"
```

## Solution

### Step 1: Disable channels in OpenClaw config

Edit `~/.openclaw/openclaw.json`:
```json
"channels": {
  "telegram": { "enabled": false },
  "discord": { "enabled": false }
}
```

### Step 2: Stop OpenClaw gateway service

OpenClaw runs via systemd user service — killing the process won't stop it from auto-restarting:
```bash
systemctl --user stop openclaw-gateway.service
```

Verify it's stopped:
```bash
ps aux | grep openclaw-gateway | grep -v grep  # Should be empty
```

### Step 3: Clean Hermes locks

```bash
rm -f ~/.hermes/gateway.pid
rm -f ~/.local/state/hermes/gateway-locks/*.lock
```

### Step 4: Restart Hermes gateway

```bash
hermes gateway run --replace
```

## Why not just kill the process?

The OpenClaw systemd service (`openclaw-gateway.service`) auto-restarts the process if killed manually. You must either:
1. Disable the channels in openclaw.json AND stop the service, OR
2. Uninstall/remove the openclaw-gateway service entirely

## Verification

After restart, check connections are established:
```bash
ss -tnp | grep <hermes_pid>
# Should show ESTAB connections to:
#   Discord: 162.159.x.x:443
#   Telegram: 149.154.x.x:443
```
