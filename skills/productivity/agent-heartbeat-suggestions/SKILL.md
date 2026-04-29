---
name: agent-heartbeat-suggestions
description: Periodic suggestions for the agent during heartbeats — checks system state and suggests relevant actions based on context.
trigger: Runs during periodic heartbeat checks
---

# Agent Heartbeat Suggestions

## Overview
During heartbeats, this skill checks system state and suggests contextually relevant actions. It helps the agent stay proactive without being annoying.

## Checks

### 1. Services Health
Check if all critical services are running:
```bash
systemctl --user is-active hermes.service hermes-gateway-discord.service hermes-interop.service openclaw-gateway.service 2>/dev/null
```

### 2. Message Queues
Check if there are pending messages in the interop bridge:
```bash
curl -s http://127.0.0.1:18900/status 2>/dev/null
```

### 3. Hermes Memory Check
Check if Hermes has accumulated significant memory that should be summarized:
- Check `~/.hermes/memory/` for recent entries
- Check `~/.hermes/checkpoints/` for context size

### 4. Skill Quarantine
Check if new skills are in quarantine pending review:
```bash
ls ~/.hermes/skills/.hub/quarantine/ 2>/dev/null
```

### 5. OpenClaw Sessions
Check for stalled or old sessions that might need attention:
```bash
openclaw status 2>/dev/null
```

## Suggestion Logic

**If services are down:**
→ "Hermes services need attention, consider restarting"

**If interop queue has >3 messages:**
→ "There are N messages queued for Hermes, consider processing them"

**If new skills in quarantine:**
→ "New skills pending review in quarantine"

**If Hermes memory is large (>100 entries today):**
→ "Hermes has accumulated significant memory today, consider a cleanup/summarization"

**If OpenClaw sessions are near token limit:**
→ "OpenClaw session nearing token limit, consider summarization"

## Output
When triggered, output a brief one-line suggestion if something needs attention, otherwise stay silent.
