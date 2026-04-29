---
name: cloudflare-quick-tunnel
description: Expose local services to the internet via Cloudflare quick tunnel (no account needed). Use when you need temporary public URL for local web services.
version: 1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cloudflare, tunnel, networking, public-url, mobile-access]
---

# Cloudflare Quick Tunnel — No Account Required

Expose a local HTTP service to a temporary public URL using `cloudflared`.

## Prerequisites

```bash
# Install cloudflared (Linux amd64)
cd /tmp
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
```

## Correct Pattern (Critical!)

**The key lesson:** Multiple cloudflared processes writing to the same log cause silent failures. Always use a dedicated, clean log file. Also, the service must be running BEFORE cloudflared starts.

```bash
# 1. Kill any existing cloudflared processes
kill $(ps aux | grep cloudflared | grep -v grep | awk '{print $2}') 2>/dev/null
sleep 1

# 2. Verify your local service is running (e.g. port 8787)
ss -tlnp | grep 8787

# 3. Start cloudflared with OUTPUT REDIRECTED to a dedicated log file
cd /tmp
./cloudflared tunnel --url http://127.0.0.1:8787 > /tmp/cf.log 2>&1 &

# 4. Wait for the trycloudflare URL (usually ~10 seconds)
sleep 10
grep trycloudflare /tmp/cf.log
```

Expected output:
```
2026-04-28T11:58:15Z INF Requesting new quick Tunnel on trycloudflare.com...
2026-04-28T11:58:19Z INF |  https://your-unique-url.trycloudflare.com                                       |
```

## Common Failure Modes

- **"error" in output + tunnel dies immediately**: Port conflict — another process is using the same port. Check with `ss -tlnp | grep <port>`
- **URL never appears in log**: cloudflared process died — check with `ps aux | grep cloudflared`
- **Old log file reused**: Always rm /tmp/cf.log before restarting to avoid confusion
- **Server not running**: cloudflared connects to localhost:PORT — server MUST be running first

## Quick Tunnel vs Named Tunnel

- **Quick tunnel** (this guide): No account needed, URL changes every restart. URL format: `*.trycloudflare.com`
- **Named tunnel**: Requires free Cloudflare account, URL is permanent (e.g. `your-app.cloudflareaccess.com`). Set up via `cloudflared tunnel create <name>` + config.yml

## Use Case: Hermes WebUI on Mobile (5G)

```bash
# Hermes WebUI is on port 8787
# 1. Start webui (if not running)
cd ~/.hermes/hermes-webui && bash start.sh &

# 2. Kill old cloudflared
kill $(ps aux | grep cloudflared | grep -v grep | awk '{print $2}') 2>/dev/null

# 3. Start fresh tunnel
cd /tmp && ./cloudflared tunnel --url http://127.0.0.1:8787 > /tmp/cf.log 2>&1 &

# 4. Get URL
sleep 10 && grep trycloudflare /tmp/cf.log
```

## Use Case: iOS Web Clip Page

```bash
# Create a web directory
mkdir -p /tmp/webclip

# Place index.html with iOS web clip meta tags + icons
# Serve on a different port (e.g. 8788)
cd /tmp/webclip && python3 -m http.server 8788 &

# Tunnel it
cd /tmp && ./cloudflared tunnel --url http://127.0.0.1:8788 > /tmp/webclip-cf.log 2>&1 &
```

## Limitations

- Quick tunnels have **no uptime guarantee**
- URL **changes on every restart**
- Cloudflare may rate-limit rapid reconnections
- For production: use a free Cloudflare account with a named tunnel
