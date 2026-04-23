---
name: openclaw-telegram-pairing-troubleshooting
description: Troubleshoot and fix OpenClaw Telegram "access not configured" errors and pairing issues when CLI commands hang
triggers:
  - openclaw pairing hang
  - openclaw telegram access not configured
  - openclaw approve timeout
---

## Problem

When running `openclaw pairing approve telegram <CODE>`, the command hangs indefinitely. The bot sends the pairing code to Telegram but the approval step fails, leaving users stuck with "access not configured".

## Root Cause

The OpenClaw gateway RPC interface times out when the CLI tries to communicate with it. This can happen even when the gateway process is running and the bot successfully sends messages.

## Workaround: Direct HTTP API

1. **Start the gateway** in background with a generous wait:
   ```bash
   openclaw gateway start --timeout 30 &
   sleep 20
   curl http://localhost:19001/health
   ```

2. **Find the gateway port** — check the startup output for "HTTP API listening on port N"

3. **Approve via HTTP directly**:
   ```bash
   GATEWAY_PORT=19001  # or whatever port is in use
   CODE="YOUR_CODE"
   curl -X POST "http://localhost:$GATEWAY_PORT/api/v1/pairing/approve" \
     -H "Content-Type: application/json" \
     -d "{\"platform\":\"telegram\",\"code\":\"$CODE\"}"
   ```

## Alternative: Manual JSON Edit

If the HTTP API also fails, edit the allowed_users file directly:

1. Find it:
   ```bash
   find ~/.openclaw* -name "allowed_users.json" 2>/dev/null
   find /tmp/openclaw* -name "*.json" 2>/dev/null
   ```

2. Add your Telegram user ID to the allowed list:
   ```json
   {
     "telegram": ["8177017832"]
   }
   ```

3. Restart the gateway:
   ```bash
   openclaw gateway stop; sleep 2; openclaw gateway start --timeout 30 &
   ```

## Key Insight

The **token** is set via `Environment=TELEGRAM_BOT_TOKEN=<token>` in the systemd service (see `openclaw-configure-telegram-token` skill). The **pairing/approval** is a separate step — even with a correct token, if the user isn't in `allowed_users`, they get "access not configured".

## Verification

After approval, test with:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:19001/api/v1/ping
```

Or simply send a message to the bot on Telegram and check if Hermes responds.
