---
name: hermes-webui-ops
description: Operate and troubleshoot Hermes WebUI on Surface Pro 3 — start, restart, LAN access, and common issues.
version: 1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes-webui, webui, surface, ops]
    related_skills: [sudo-password-delivery]
---

# Hermes WebUI Operations

Location: `~/.hermes/hermes-webui/`

## Start / Restart

**Always use `start.sh`** — it sources `.env` before launching the server.

```bash
cd ~/.hermes/hermes-webui && bash start.sh
```

**Restart** (after editing `.env`):
```bash
kill $(ps aux | grep 'server.py' | grep -v grep | awk '{print $2}')
sleep 1
cd ~/.hermes/hermes-webui && bash start.sh
```

## Check Status

```bash
ss -tlnp | grep 8787
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8787
```

## Configure LAN Access (phone on same WiFi)

Edit `~/.hermes/hermes-webui/.env`:
```bash
HERMES_WEBUI_HOST=0.0.0.0
```

Then restart. Access from phone: `http://<surface-lan-ip>:8787`

Find Surface LAN IP: `ip -4 addr show | grep inet | grep -v 127.0.0.1`

## Cloudflare Tunnel (remote access from anywhere)

Download binary (not in apt):
```bash
cd /tmp && curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared && chmod +x cloudflared
```

Quick tunnel (no account, URL changes on restart):
```bash
# CRITICAL: kill any existing cloudflared first to avoid port conflicts
kill $(ps aux | grep cloudflared | grep -v grep | awk '{print $2}') 2>/dev/null

# Ensure webui is running on 127.0.0.1:8787 first
ss -tlnp | grep 8787

# Start cloudflared with output redirected to own log
cd /tmp && exec ./cloudflared tunnel --url http://127.0.0.1:8787 > /tmp/cf.log 2>&1

# Wait for URL (10-15s), then check log
sleep 12 && cat /tmp/cf.log | grep trycloudflare
```

For permanent URL: create free Cloudflare account, create named tunnel, write config to `~/.cloudflared/config.yml`.

**Tunnel goes down frequently** — if URL stops responding, kill cloudflared processes, wait 1s, restart. Quick tunnels without a Cloudflare account have no uptime guarantee. Consider a named tunnel for reliability.

## Key Gotcha

`server.py` does NOT read `.env` directly. `start.sh` sources `.env` before calling the Python server. Always restart via `start.sh` after config changes.

**Also**: `bootstrap.py` is the onboarding entry point, `start.sh` calls `bootstrap.py --no-browser`. `server.py` is the raw server (used by `bootstrap.py`). Always use `start.sh` to start.
