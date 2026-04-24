---
name: openclaw-on-surface
description: OpenClaw v2026.4.21 setup and management on Surface Pro 3 — gateway, config, channels, and known issues.
---

# OpenClaw on Surface Pro 3 — Setup & Management

## Overview
OpenClaw v2026.4.21 is installed on the Surface Pro 3 (this machine) at `/home/marco/.openclaw/`.  
It runs as a **systemd user service** (`openclaw-gateway.service`), managed via `systemctl --user`.

## Quick Commands
```bash
# Check if gateway is running
systemctl --user status openclaw-gateway

# Restart gateway
systemctl --user restart openclaw-gateway

# View recent logs
journalctl --user -u openclaw-gateway -n 20

# Check gateway health (port 18789)
curl http://localhost:18789/health

# View live logs
journalctl --user -u openclaw-gateway -f
```

## Default Model (CRITICAL — correct method)
The default model is set via `agents.defaults.model` in `~/.openclaw/openclaw.json`, NOT via settings.json.
settings.json is NOT read by the gateway for model defaults — it only works for some agent-level overrides.

Correct `~/.openclaw/openclaw.json`:
```json
{
  "channels": { ... },
  "gateway": { ... },
  "agents": {
    "defaults": {
      "model": "minimax/MiniMax-M2.7-highspeed"
    }
  }
}
```

**Format must be `provider/model` (e.g. `minimax/MiniMax-M2.7-highspeed`).** Without the provider prefix, OpenClaw falls back to `openai/<model>` and logs: `Model "X" specified without provider. Falling back to "openai/X".`

The gateway log (`journalctl --user -u openclaw-gateway`) shows `agent model: minimax/MiniMax-M2.7-highspeed` when correctly configured.

## Config Files
- Main config: `~/.openclaw/openclaw.json` ← **edit this for model/agent config**
- Auth profiles: `~/.openclaw/agents/main/agent/auth-profiles.json` (API keys for providers)
- Models config: `~/.openclaw/agents/main/agent/models.json` (available models per provider)
- Settings: `~/.openclaw/agents/main/agent/settings.json` (NOT read by gateway for defaults)
- Gateway log: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`
- Credentials: `~/.openclaw/credentials/telegram-pairing.json`, `telegram-allowFrom.json`

## MiniMax API Key
The API key `sk-cp-...Sd-Q` is stored in `~/.openclaw/agents/main/agent/auth-profiles.json` under the `minimax:global` profile.

## Telegram Configuration
Telegram bot token is set via `TELEGRAM_BOT_TOKEN` env var in the systemd service file.

### Pairing Flow
When a user first messages the bot, OpenClaw checks `~/.openclaw/credentials/telegram-allowFrom.json` and `telegram-pairing.json`.
- If the user's ID is in `allowFrom.json` → access granted
- Otherwise, a pairing code is generated and the bot replies with the code
- The code must be approved: `openclaw pairing approve telegram <CODE>` (CLI times out — edit files directly instead)

### Manual Pairing Approval
If CLI times out, edit the credentials files directly:
1. `~/.openclaw/credentials/telegram-allowFrom.json` — add user ID to entries array
2. `~/.openclaw/credentials/telegram-pairing.json` — remove the pending request entry (or leave it — allowFrom is sufficient)

User's Telegram ID: **8177017832** (Marco Olivero)

### Bot Account
- Bot: `@OpenClaw_LeonSurf_bot` (token in service file: `TELEGRAM_BOT_TOKEN=***MASKED***`)
- Allow list contains: `8177017832`

## Discord Configuration
- Bot: `@Leo` (ID 1496854698790228039)
- Token: `DISCORD_BOT_TOKEN` env var (see systemd service)
- Token set via `DISCORD_BOT_TOKEN` env var in systemd service file
- Config in openclaw.json: `dmPolicy: "open"`, `allowFrom: ["*"]`

### Message Content Intent
If the bot shows "Discord Message Content Intent is limited", enable it at:
https://discord.com/developers/applications → Bot → Privileged Intents → **Message Content Intent** ✅

## OpenClaw vs Hermes — They Are Completely Separate
OpenClaw and Hermes are **independent programs** with separate configurations, bot tokens, and data directories.

| | OpenClaw | Hermes |
|---|---|---|
| Bot | `@OpenClaw_LeonSurf_bot` | `@Hermes_surfer_bot` |
| Telegram Token | `***MASKED***` | `***MASKED***` |
| Discord Token | `***MASKED***` (in OpenClaw service) | `***MASKED***` (in Hermes config) |
| Config dir | `~/.openclaw/` | `~/.hermes/` |
| Gateway port | 18789 | separate process |

**Never confuse the tokens** — All real tokens are stored in /home/Obsidian-Vault/Secure/CREDENTIALS.md

## Known Issues
- **CLI commands hang** (`openclaw config set`, `openclaw pairing approve`, etc.) — do NOT use CLI. Edit config files directly.
- **Startup takes ~112 seconds (1.5-2 min).** The process appears stuck at the punycode deprecation warning during startup — it is NOT hung, it is initializing plugins. DO NOT kill/restart during this period thinking it is broken. Wait for the log message: `ready (N plugins: acpx, browser, ...)` — only then is the gateway fully operational.
- The health endpoint (`curl http://localhost:18789/health`) may return failure even when the process is running normally, because it doesn't respond until startup is complete. Check `journalctl --user -u openclaw-gateway -n 5` instead to see actual startup progress.
- The gateway uses 97%+ CPU during startup — this is normal, not an error.
- On reboot, the service needs ~2 min before accepting connections.
- The gateway restarts in a loop sometimes (StartLimitBurst=5) — if it won't stay up, check `journalctl --user -u openclaw-gateway` for config errors.
- **Node.js ETIMEDOUT/ENETUNREACH on Telegram polling**: If `curl` to `api.telegram.org` works but OpenClaw logs show `fetch fallback: enabling sticky IPv4-only dispatcher (codes=ETIMEDOUT,ENETUNREACH)`, the Node.js process has a network issue distinct from system curl. This is a known problem with Node's native HTTP client behind certain proxies/firewalls. The polling will retry automatically. The bot can send outgoing messages but won't receive incoming ones while in this state — a service restart may be needed to recover.

## Troubleshooting Discord "offline" / no response
When the bot appears offline on Discord despite the gateway being "ready":

1. Check if the gateway is crashing: `journalctl --user -u openclaw-gateway -n 20 | grep -E "ERROR|ready|crash"`
2. **Common crash cause**: `channels.telegram: invalid config: must NOT have additional properties` — this means the Telegram channel config in openclaw.json has keys that aren't allowed. Fix the `channels.telegram` section to only contain valid keys (`enabled`, `allowFrom`).
3. After restart, the gateway shows `ready (7 plugins: ...discord...)` which means Discord plugin is loaded. It may NOT show a new "logged in to discord" message on every restart — absence of an error is a good sign.
4. Use `journalctl --user -u openclaw-gateway | grep -i "discord\|logged"` to check Discord connection status across all processes.
5. If the bot is online but not responding: with Message Content Intent "limited" (bot under 100 servers), the bot can ONLY read:
   - **Direct Messages (DMs)** sent to the bot
   - Messages in servers that **@mention the bot** by name
   - Regular messages in servers without mention are NOT received.
6. Test: send the bot a **DM directly** — this is the most reliable test. If it still doesn't respond after confirming online, check `journalctl --user -u openclaw-gateway | grep -i "error\|fail\|api"` for API or model errors.
## Skills Path
OpenClaw skills installed: `~/.openclaw/skills/`
