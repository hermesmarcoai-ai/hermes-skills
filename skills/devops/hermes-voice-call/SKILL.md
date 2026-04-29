---
name: hermes-voice-call
description: Real-time voice calling with Hermes Agent via Pipecat + Daily.co WebRTC on VPS
---

# Hermes Voice Call Setup

Enable real-time voice conversation (phone-call style) with Hermes from iPhone/Android/browser.

## Architecture

```
iPhone → Daily.co (WebRTC) → Pipecat (VPS) → Whisper STT → MiniMax M2.7 (OpenRouter) → MiniMax TTS → Daily.co → iPhone
```

## Prerequisites

| Component | Provider | Status |
|-----------|----------|--------|
| STT (speech→text) | OpenAI Whisper (`sk-pro...`) | Already configured in `config.yaml` |
| LLM (reasoning) | OpenRouter / MiniMax M2.7 | Already configured |
| TTS (voice output) | MiniMax | Already configured |
| WebRTC transport | **Daily.co** | Needs account |
| Server | VPS (port 443 open) | Available |

## Setup Steps

### 1. Create Daily.co account
- Go to daily.co → sign up (free tier)
- Get API key from dashboard

### 2. Install Pipecat on VPS
```bash
ssh vps
pip3 install pipecat-ai[openai,minimax,daily] --break-system-packages
```

### 3. Configure Pipecat
Create `~/.hermes/voice-bot.py` with Daily.co room, Whisper STT, MiniMax LLM via OpenRouter, MiniMax TTS.

### 4. Start bot + access from iPhone Safari

## Key Discovery

Pipecat supports MiniMax TTS + OpenRouter LLM + OpenAI Whisper natively. No new API costs.

## Constraints

- Must run on VPS (Surface NAT blocked from iPhone)
- ~3-5s latency (not true simultaneous conversation)
- MiniMax speech-02-hd NOT in $40 plan (only base TTS)
- MiniMax plan: request-based limits, not token-based
