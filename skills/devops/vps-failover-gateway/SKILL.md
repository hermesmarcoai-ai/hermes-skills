---
name: vps-failover-gateway
description: Hermes Discord/Telegram gateway failover from VPS to Surface
---

# VPS Failover Gateway Setup

## Overview
Discord/Telegram gateway runs on VPS. Surface acts as hot standby with auto-failover.

## Scripts on Surface
- `~/.hermes/gateway-discord-standby.sh` — Discord-only standby gateway
  - `start` — manually activate standby
  - `stop` — stop standby
  - `status` — check if running
  - `auto` — auto-failover: watches VPS, activates if VPS goes down

## Activation
When VPS fails:
```bash
~/.hermes/gateway-discord-standby.sh start
# or for auto-failover:
~/.hermes/gateway-discord-standby.sh auto
```

## VPS Hermes Directory Layout
- Root install: `/root/.hermes` (runs gateway, mostly root-owned)
- User install: `/home/hermes/.hermes/hermes-agent/` (writable by hermes user)
- **Skill sync method**: clone to `~/hermes-skills`, then `cp -r ~/hermes-skills/skills/* ~/.hermes/hermes-agent/skills/`

## Key Notes
- Discord only allows ONE active gateway per bot token — never run both simultaneously
- Telegram also polls on VPS — Surface gateway uses HERMES_GATEWAY_PLATFORMS=discord only
- Auto-failover checks VPS:8080/health every 30s via curl
- Logs: `~/.hermes/logs/gateway-discord-standby.log`
- Discord bot token location in config.yaml: `discord.bot_token` and `platforms.discord.token`

## To recover when VPS comes back
```bash
# Stop Surface gateway
~/.hermes/gateway-discord-standby.sh stop
# Restart VPS gateway (via SSH)
ssh vps 'cd /root/.hermes && ./gateway-both.sh &'
```
