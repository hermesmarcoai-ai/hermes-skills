---
name: hermes-persistent-gateway-pm2
description: Setup Hermes messaging gateway to run 24/7 via PM2 with auto-restart
---

# Hermes Persistent Gateway via PM2

Setup Hermes messaging gateway to run 24/7 in background with auto-restart, independent of terminal sessions.

## Prerequisites
- Hermes CLI installed (`pip install hermes-agent` or similar)
- PM2 installed (`npm install -g pm2`)
- Messaging platform configured (Telegram, Discord, etc.) in `~/.hermes/config.yaml`

## The Problem
Running `hermes gateway` directly attaches to terminal. Closing terminal kills gateway.
PM2 alone fails because:
1. Missing PATH/hermes binary (exit code 127)
2. Gateway lock files prevent multiple instances from same session
3. **CRITICAL:** Multiple platform instances (Discord + Telegram) share token-based locks — **MUST use ONE gateway for all platforms**

## CRITICAL: Single Gateway for All Platforms

**DO NOT** attempt to run separate PM2 processes for Discord and Telegram. They share token-based gateway locks that cause fatal conflicts:
- Discord lock: `discord-bot-token-<hash>.lock`
- Telegram lock: `telegram-bot-token-<hash>.lock`

Both get written to `~/.local/state/hermes/gateway-locks/` and if separate processes try to hold them, one will fail with "token already in use".

**SOLUTION:** Use ONE gateway process that handles ALL configured platforms.

## Solution: Wrapper Script with `gateway run`

**IMPORTANT:** Hermes uses token-based locking that prevents running separate Discord and Telegram instances. Use ONE gateway process for ALL platforms.

Create unified wrapper script at `~/.hermes/gateway-both.sh`:

```bash
#!/bin/bash
# CRITICAL: Source the virtualenv first, otherwise hermes fails with:
# "ModuleNotFoundError: No module named 'hermes_cli'"
export HOME=/root
export HERMES_HOME="/root/.hermes"
export PATH="$HERMES_HOME/node/bin:$HOME/.local/bin:${PATH}"

# Load virtualenv BEFORE calling hermes
source "$HERMES_HOME/hermes-agent/venv/bin/activate"

# Load environment variables
if [ -f "$HERMES_HOME/.env" ]; then
    set -a
    source "$HERMES_HOME/.env"
    set +a
fi

# Load platform-specific tokens (e.g., Discord token)
if [ -f "$HERMES_HOME/discord-env" ]; then
    set -a
    source "$HERMES_HOME/discord-env"
    set +a
fi

# DO NOT set HERMES_GATEWAY_PLATFORMS — let gateway handle all configured platforms

# Use FULL PATH to hermes binary (after activating venv)
exec "$HOME/.local/bin/hermes" gateway run
```

Save and make executable:
```bash
chmod +x ~/.hermes/gateway-both.sh
```

## PM2 Setup

### Single Gateway (All Platforms)
```bash
# Must use wrapper script, NOT direct path to hermes binary
pm2 start ~/.hermes/gateway-both.sh --name hermes-gateway
pm2 save
```

**CRITICAL:** Do NOT use `pm2 start /root/.local/bin/hermes` directly — it will fail with ModuleNotFoundError because the virtualenv isn't loaded.

### Or use ecosystem config:

Create `~/.hermes/pm2-gateway.config.js`:
```javascript
module.exports = {
  apps: [
    {
      name: 'hermes-gateway',
      script: '/home/USER/.hermes/gateway-both.sh',
      exec_interpreter: 'bash',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      env: {
        PATH: '/home/USER/.hermes/node/bin:/home/USER/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin',
        HERMES_HOME: '/home/USER/.hermes'
      },
      log_file: '/home/USER/.hermes/logs/gateway-combined.log',
      time: true
    }
  ]
};
```

Start:
```bash
pm2 start ~/.hermes/pm2-gateway.config.js
```

## Commands

```bash
pm2 status                    # Check all gateway statuses
pm2 logs hermes-discord --lines 50   # View Discord logs
pm2 logs hermes-telegram    # View Telegram logs
pm2 restart hermes-discord  # Restart Discord gateway
pm2 restart hermes-telegram # Restart Telegram gateway
pm2 stop all                # Stop all gateways
pm2 delete all              # Remove all from PM2
```

## Auto-Start on Boot

```bash
pm2 save        # Save current process list
pm2 startup     # Generate systemd service
# Then run the command PM2 outputs (usually: systemctl enable pm2-USER)
```

## Key Insights

1. **Use `gateway run` (foreground)** — NOT `gateway --replace` (flag doesn't exist in v0.6.0+)
2. **Use FULL path to hermes** — `/home/USER/.local/bin/hermes` not just `hermes`
3. **Include `.local/bin` in PATH** — PM2 doesn't inherit full shell env
4. **DO NOT set `HERMES_GATEWAY_PLATFORMS`** — This forces single platform but token locks still conflict. Let gateway handle ALL platforms.
5. **Clean lock files when switching configs** — Remove `~/.hermes/sessions/gateway*.json` and `~/.local/state/hermes/gateway-locks/*.lock`
6. **Use ecosystem config** — Cleaner than separate `pm2 start` commands
7. **Verify with `gateway_state.json`** — Check platform connection status after start

## Troubleshooting

**Exit code 127 (command not found):**
- Check `which hermes` and use full path in script
- Ensure PATH includes `.local/bin` and `hermes/node/bin`

**"Gateway already running" errors:**
- Delete lock files in `~/.hermes/sessions/` and `~/.local/state/hermes/gateway-locks/`
- **CRITICAL:** Do NOT use `HERMES_GATEWAY_PLATFORMS` to run separate Discord/Telegram instances — they share token locks. Use ONE gateway for all platforms.

**Gateway stops immediately:**
- Check logs: `pm2 logs hermes-discord`
- Verify `.env` has correct tokens/credentials
- Ensure `config.yaml` has platform enabled

**Config changes not applied:**
```bash
pm2 restart hermes-discord --update-env
```

## Discord Token Troubleshooting

If Discord token appears truncated/masked in `.env` (e.g., `MTQ4OT...lSnk`):

1. Create separate env file: `~/.hermes/discord-env`
2. Source it AFTER `.env` in wrapper script (to override)
3. Or directly edit `.env` with full token

## Test Persistence

1. Start gateway with PM2
2. Close terminal / disconnect SSH
3. Wait 10 seconds
4. Send message on platform — should respond
5. Check: `pm2 status` should show "online"