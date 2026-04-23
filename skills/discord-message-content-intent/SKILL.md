---
name: discord-message-content-intent
description: Understand Discord Message Content Intent levels and what they enable/block for bots
triggers:
  - discord bot not reading messages
  - discord bot only responds to mentions
  - message content intent limited vs none
  - openclaw discord setup
category: messaging
---

# Discord Message Content Intent

## The Critical Distinction

When a Discord bot is **under 100 servers**, the Message Content Intent is set to **"limited"** (not "none"). This has a significant effect:

| Intent Level | Reads @mentions in channels | Reads all channel messages | Receives DMs |
|---|---|---|---|
| **limited** (bot <100 servers) | ✅ Yes | ❌ No | ✅ Always |
| **none** (no intent enabled) | ❌ No | ❌ No | ✅ Always |
| **privileged** (bot >100 servers) | ✅ Yes | ✅ Yes | ✅ Always |

## Key Takeaway

A bot with **"limited"** Message Content Intent:
- ✅ **Will always receive DMs** — no special setup needed
- ✅ **Only reads messages that @mention it** in server channels
- ❌ **Cannot read regular channel messages** — even if the bot is online

## Symptoms When Misconfigured

- Bot appears online/connected in Discord developer portal
- Bot does NOT respond to messages in server channels
- Bot ONLY works when sent a DM directly
- Bot ONLY works when explicitly @mentioned in a channel

## How to Test

1. Send a **DM** to the bot — if it works, the bot is connected fine
2. In a server channel, **@mention the bot** — if it responds, intent is working
3. In a server channel, send a **regular message without @mention** — bot should NOT respond (by design)

## If You Need Full Channel Reading

To read all messages in channels (not just @mentions), the bot must:
1. Be on **100+ servers**
2. Have Message Content Intent set to **"privileged"**
3. Re-verify the bot token after changing intent
4. Restart the gateway

## Gateway (OpenClaw) Note

The gateway can be online and connected even with "limited" intent — the connection status is separate from message reading capability. An online bot doesn't mean it can read all your messages.
