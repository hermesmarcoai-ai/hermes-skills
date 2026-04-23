---
name: openclaw-telegram-etimedout
description: Fix OpenClaw Telegram bot where sendMessage works but getUpdates (long polling) fails with ETIMEDOUT/ENETUNREACH from Node.js fetch, while curl to api.telegram.org works fine
triggers:
  - openclaw telegram ETIMEDOUT
  - openclaw telegram ENETUNREACH
  - openclaw fetch fallback sticky IPv4
  - telegram bot not receiving messages
---

## Problem

OpenClaw Telegram bot:
- ✅ **sendMessage works** (curl to api.telegram.org succeeds)
- ❌ **getUpdates fails** — Node.js `fetch` to api.telegram.org gets ETIMEDOUT/ENETUNREACH
- ❌ Bot receives no messages (long polling is broken)

The log shows repeatedly:
```
[telegram] fetch fallback: enabling sticky IPv4-only dispatcher (codes=ETIMEDOUT,ENETUNREACH)
```

## Root Cause

Node.js `fetch` (undici-based) fails to connect to api.telegram.org even though:
- `curl` works fine
- `node https.get` works fine
- DNS resolution works (149.154.166.110)

This suggests a network-level difference between curl's HTTP client and Node.js's fetch implementation — possibly related to IPv6 vs IPv4, MTU, or connection tracking.

## Symptoms

1. Gateway starts successfully (ready in ~112 seconds)
2. Telegram provider starts: `[default] starting provider (@OpenClaw_LeonSurf_bot)`
3. Immediately: `fetch fallback: enabling sticky IPv4-only dispatcher`
4. No incoming messages ever received
5. `curl https://api.telegram.org/bot<TOKEN>/getMe` → 200 OK
6. `curl https://api.telegram.org/bot<TOKEN>/sendMessage` → works (bot can send)

## Verification Commands

```bash
# Test from curl (works)
curl -s "https://api.telegram.org/bot<TOKEN>/getMe"

# Test from Node.js (also works - surprising)
node -e "const https = require('https'); https.get('https://api.telegram.org/bot<TOKEN>/getMe', r => { let d=''; r.on('data', c => d+=c); r.on('end', () => console.log(d.substring(0,100))); }).on('error', e => console.log(e.message));"

# But OpenClaw's fetch-based getUpdates fails
```

## Mitigation: Use Hermes VPS Instead

The Hermes VPS (46.224.196.229) successfully runs the same Telegram bot token. Consider running OpenClaw Telegram on VPS instead of Surface if this persists.

## Workarounds Tried (Did Not Fix)

1. **deleteWebhook + reset updates** — didn't help
2. **IPv4 dispatcher** — already auto-enabled as fallback, still fails
3. **network.dnsResultOrder** config key — rejected as invalid by OpenClaw
4. **Adding Telegram to no_proxy** — not applicable (no proxy in use)
5. **Restart gateway** — same ETIMEDOUT pattern every time

## Key Findings

- The issue is **consistent and reproducible** on Surface Pro 3 (Ubuntu)
- `https.get` from Node works but `fetch` fails — suggests the undici fetch implementation has different network requirements
- OpenClaw automatically retries with IPv4-only dispatcher after first failure, but still fails
- The bot CAN send messages, just can't receive via long polling

## Gateway Startup Time

OpenClaw takes ~112 seconds to fully start. Don't assume it's crashed during this time — check journalctl for actual status.
