---
name: hermes-openai-whisper-stt
description: Configure OpenAI Whisper for voice message transcription in Hermes Telegram gateway
category: devops
---

# Hermes OpenAI Whisper STT Configuration

Configure Hermes messaging gateway to transcribe voice messages using OpenAI Whisper API instead of local models.

## Prerequisites
- Hermes gateway running (via PM2 recommended)
- OpenAI API key
- Telegram bot configured

## The Problem

Local STT (`provider: local`) uses `model: base` which may fail with:
```
Invalid model size 'whisper-1', expected one of: tiny.en, tiny, base...
```

OpenAI Whisper provides better quality but requires proper configuration.

## Critical Finding

**Hermes uses `VOICE_TOOLS_OPENAI_KEY`** (not `OPENAI_API_KEY`) for the STT provider.

## Setup Steps

### 1. Add API Key to .env

Edit `~/.hermes/.env`:
```bash
VOICE_TOOLS_OPENAI_KEY=sk-your-key-here
```

Do NOT use `OPENAI_API_KEY` — Hermes specifically looks for `VOICE_TOOLS_OPENAI_KEY` for voice transcription.

### 2. Update config.yaml

Edit `~/.hermes/config.yaml`:

```yaml
stt:
  enabled: true
  provider: openai          # ← change from 'local'
  local:
    model: base
  openai:
    model: whisper-1        # ← OpenAI model name
  model: whisper-1          # ← must match
```

### 3. Restart Gateway with Environment Reload

If using PM2:
```bash
pm2 restart hermes-telegram --update-env
```

Without `--update-env`, the new API key won't be loaded from `.env`.

### 4. Test Voice Message

Send a voice message via Telegram. Should receive transcription response.

## Troubleshooting

**"no STT provider is configured" error:**
- Check `provider: openai` is set in config.yaml
- Verify `VOICE_TOOLS_OPENAI_KEY` in .env (not `OPENAI_API_KEY`)
- Ensure `--update-env` was used during restart

**Config not taking effect:**
- PM2 caches environment — must use `--update-env` flag
- Check with: `pm2 env hermes-telegram | grep VOICE`

**Key exposure concerns:**
- Store key in `.env` (not config.yaml)
- Hermes reads it from environment securely
- Delete Telegram message containing key after setup