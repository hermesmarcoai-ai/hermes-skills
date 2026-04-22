---
name: hermes-discord-bot-orchestration
description: Orchestrate multi-bot conversations on Discord via human-in-the-loop pattern
trigger: When coordinating multiple AI bots on Discord that cannot directly communicate
---

# Multi-Bot Orchestration on Discord

## Overview
Discord gateway receives ONLY messages with direct mentions (tags, DMs, thread replies). Bots cannot see each other's messages directly.

## Pattern: Human as Orchestrator
1. User tags both bots in same message/thread with a question
2. Bot A responds with its analysis
3. User forwards Bot A's response to Bot B: "@BotB, cosa pensi di quello che ha detto @BotA? [quote]"
4. Bot B responds, user can relay back to Bot A

## Limitations and Configuration
- **By default**, bots CANNOT see channel messages without @mentions (controlled by `DISCORD_REQUIRE_MENTION=true`)
- **To disable the mention requirement**: set `DISCORD_REQUIRE_MENTION=false` in config or `.env`. The bot will then read ALL messages in all channels from allowed users.
- **For specific channels only**: use `DISCORD_FREE_RESPONSE_CHANNELS` with comma-separated channel IDs. Bot responds without mention only in those channels.
- Bots CANNOT message each other directly
- User MUST act as the relay/context provider (for multi-bot conversations)
- Works best in threads (keeps conversation organized)

## Setup Requirements
- Each bot on Discord responds to mentions
- Same server, same channel/thread
- Bots can have different capabilities (e.g., one for code, one for research)

## Pitfalls
- Context gets lost if relay is incomplete — always quote the full previous bot response
- Token limits: long back-and-forth conversations may exhaust context windows
- Each bot only knows what it's been told in the current conversation
