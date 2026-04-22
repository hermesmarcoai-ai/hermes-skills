---
name: hermes-multi-gateway-pm2
description: Run multiple Hermes messaging gateways (Discord, Telegram, etc.) simultaneously via PM2 with proper isolation
---

# Hermes Multi-Gateway Setup with PM2

Run multiple Hermes messaging gateways (Discord, Telegram, WhatsApp, etc.) simultaneously on the same machine using PM2 with proper lock isolation.

## The Problem

Hermes gateway uses PID file locking to prevent duplicate instances. By default, all gateways share the same lock file at `~/.hermes/gateway.pid`, which means:
- You cannot run Discord and Telegram gateways at the same time
- Starting a second gateway kills the first one with "Gateway already running" error
- PM2 restart loops occur when multiple platforms are configured

## The Solution: HERMES_GATEWAY_LOCK_DIR

Hermes supports the `HERMES_GATEWAY_LOCK_DIR` environment variable to isolate gateway locks by platform. Each platform gets its own lock directory, allowing concurrent operation.

## Setup Steps

### 1. Create Platform-Specific Lock Directories

```bash
mkdir -p ~/.hermes/locks/discord
mkdir -p ~/.hermes/locks/telegram
mkdir -p ~/.hermes/locks/whatsapp  # If needed
```

### 2. Create Wrapper Scripts

**~/.hermes/discord-gateway.sh:**
```bash
#!/bin/bash
export PATH="/root/.hermes/node/bin:/root/.local/bin:${PATH}"
export HERMES_HOME="/root/.hermes"

# Load environment variables
if [ -f "$HERMES_HOME/.env" ]; then
    set -a
    source "$HERMES_HOME/.env"
    set +a
fi

# Platform-specific lock directory (CRITICAL for multi-gateway)
export HERMES_GATEWAY_LOCK_DIR="$HERMES_HOME/locks/discord"
mkdir -p "$HERMES_GATEWAY_LOCK_DIR"

# Force Discord platform only
export HERMES_GATEWAY_PLATFORMS=discord

# Run gateway in foreground for PM2
exec /root/.local/bin/hermes gateway run
```

**~/.hermes/telegram-gateway.sh:**
```bash
#!/bin/bash
export PATH="/root/.hermes/node/bin:/root/.local/bin:${PATH}"
export HERMES_HOME="/root/.hermes"

# Load environment variables
if [ -f "$HERMES_HOME/.env" ]; then
    set -a
    source "$HERMES_HOME/.env"
    set +a
fi

# Platform-specific lock directory (CRITICAL for multi-gateway)
export HERMES_GATEWAY_LOCK_DIR="$HERMES_HOME/locks/telegram"
mkdir -p "$HERMES_GATEWAY_LOCK_DIR"

# Force Telegram platform only
export HERMES_GATEWAY_PLATFORMS=telegram

# Run gateway in foreground for PM2
exec /root/.local/bin/hermes gateway run
```

Make scripts executable:
```bash
chmod +x ~/.hermes/discord-gateway.sh ~/.hermes/telegram-gateway.sh
```

### 3. Create PM2 Ecosystem Config

**~/.hermes/pm2-ecosystem.config.js:**
```javascript
module.exports = {
  apps: [
    {
      name: 'hermes-discord',
      script: '/root/.hermes/discord-gateway.sh',
      exec_interpreter: 'bash',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      kill_timeout: 5000,
      env: {
        PATH: '/root/.hermes/node/bin:/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
        HERMES_HOME: '/root/.hermes',
        HERMES_GATEWAY_PLATFORMS: 'discord'
      },
      log_file: '/root/.hermes/logs/discord-combined.log',
      time: true
    },
    {
      name: 'hermes-telegram',
      script: '/root/.hermes/telegram-gateway.sh',
      exec_interpreter: 'bash',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      kill_timeout: 5000,
      env: {
        PATH: '/root/.hermes/node/bin:/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
        HERMES_HOME: '/root/.hermes',
        HERMES_GATEWAY_PLATFORMS: 'telegram'
      },
      log_file: '/root/.hermes/logs/telegram-combined.log',
      time: true
    }
  ]
};
```

### 4. Start with PM2

```bash
export PATH="/root/.hermes/node/bin:$PATH"
pm2 start ~/.hermes/pm2-ecosystem.config.js

# Save for auto-restart on boot
pm2 save
pm2 startup
```

## Configuration Requirements

### Environment Variables (in ~/.hermes/.env)

```bash
# Discord
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_APPLICATION_ID=your_app_id
DISCORD_ALLOWED_USERS=your_user_id

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_ALLOWED_USERS=your_user_id
TELEGRAM_HOME_CHANNEL=your_chat_id
```

### config.yaml Settings

```yaml
discord:
  enabled: true
  bot_token: ${DISCORD_BOT_TOKEN}
  application_id: ${DISCORD_APPLICATION_ID}
  allowed_users: ${DISCORD_ALLOWED_USERS}
  require_mention: true
  auto_thread: true
  reactions: true

telegram:
  enabled: true
  bot_token: ${TELEGRAM_BOT_TOKEN}
  allowed_users: ${TELEGRAM_ALLOWED_USERS}
  home_channel: ${TELEGRAM_HOME_CHANNEL}
```

## Management Commands

```bash
# View status
pm2 status

# View logs
pm2 logs hermes-discord
pm2 logs hermes-telegram

# Restart specific gateway
pm2 restart hermes-discord
pm2 restart hermes-telegram

# Restart all
pm2 restart all

# Stop specific gateway
pm2 stop hermes-discord

# Stop all
pm2 stop all

# Reload after config changes
pm2 restart all --update-env
```

## Troubleshooting

### "Gateway already running" error in logs

**Cause:** Two gateways sharing the same lock directory.

**Fix:** Ensure each wrapper script sets a unique `HERMES_GATEWAY_LOCK_DIR`.

### Gateway exits with code 127

**Cause:** `hermes` command not found in PATH.

**Fix:** Use full path `/root/.local/bin/hermes` in wrapper scripts and include `/root/.local/bin` in PATH.

### Changes not taking effect after restart

**Fix:** Use `--update-env` flag:
```bash
pm2 restart hermes-discord --update-env
```

### Gateway process won't stop

**Force kill:**
```bash
pm2 stop hermes-discord
pm2 delete hermes-discord
pkill -9 -f "hermes gateway"
rm -rf ~/.hermes/locks/discord/*
pm2 start ~/.hermes/pm2-ecosystem.config.js --only hermes-discord
```

## Key Technical Details

### Why HERMES_GATEWAY_LOCK_DIR works

Hermes creates a lock file based on a hash of the bot token identity. By using separate directories:
- Discord lock: `~/.hermes/locks/discord/telegram-<hash>.lock` or `discord-<hash>.lock`
- Telegram lock: `~/.hermes/locks/telegram/telegram-<hash>.lock`
- Each gateway only checks its own lock directory
- No collision between platforms

### HERMES_GATEWAY_PLATFORMS variable

This variable restricts which platforms the gateway initializes. If not set, the gateway tries to start ALL configured platforms (Discord + Telegram + WhatsApp), causing conflicts even with separate lock dirs.

Valid values:
- `discord` - Discord only
- `telegram` - Telegram only
- `whatsapp` - WhatsApp only
- `discord,telegram` - Both (not recommended without lock isolation)

## Verification

Check both gateways are running independently:

```bash
# Should show both processes
pm2 status

# Should show separate lock files
ls -la ~/.hermes/locks/discord/
ls -la ~/.hermes/locks/telegram/

# Test both platforms
# Send message on Discord - should respond
# Send message on Telegram - should respond
```

## References

- Source: `/root/.hermes/hermes-agent/gateway/status.py` (lock logic)
- Source: `/root/.hermes/hermes-agent/gateway/run.py` (platform initialization)
- PM2 docs: https://pm2.keymetrics.io/
