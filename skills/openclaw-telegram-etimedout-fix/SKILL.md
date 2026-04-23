---
name: openclaw-telegram-etimedout-fix
description: Fix OpenClaw Telegram bot where sendMessage works but long polling getUpdates fails with ETIMEDOUT — fix is network.dnsResultOrder ipv4first
category: devops
---

# OpenClaw Telegram ETIMEDOUT Fix

## Context
When OpenClaw Telegram bot's `sendMessage` works but long polling `getUpdates` fails with ETIMEDOUT or ENETUNREACH, and `curl` to api.telegram.org works fine — the issue is Node.js `fetch` API (used by grammyjs runner) DNS resolution preferring IPv6 when Telegram doesn't support it properly.

## Root Cause
Node.js 18+ `fetch` uses Happy Eyeballs (IPv6 first, fallback to IPv4). GrammyJS runner uses this fetch for long polling. Telegram's API responds poorly to IPv6, causing timeouts.

## Fix
Add to `~/.openclaw/openclaw.json` under `channels.telegram`:

```json
{
  "channels": {
    "telegram": {
      "network": {
        "dnsResultOrder": "ipv4first"
      }
    }
  }
}
```

Then hot-reload or restart the gateway.

## Supported Config Keys (under channels.telegram)
- `network.dnsResultOrder` — `"ipv4first"` | `"ipv6first"` (Node.js DNS order)
- `network.timeout` — request timeout in ms
- `network.retries` — retry count
- `network.allowedUpdates` — Telegram update types to receive

## Unsupported Keys (causes config errors)
- `polling` (not a channel-level config)
- `delivery`
- `proxy`
- `autoSelectFamily`

## Verification
After restart, log should show NO "fetch fallback to IPv4" or ETIMEDOUT errors. Bot responds to messages.

## References
- OpenClaw config schema: `dist/config-schema.js`
- GrammyJS runner: `@grammyjs/runner` uses native Node.js `fetch`
