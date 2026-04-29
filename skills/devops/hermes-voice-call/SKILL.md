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

**Latenza stimata**: 3-5 secondi end-to-end. Non è conversazione simultanea reale — è voice-in, voice-out in sequenza.

## Current Status (2026-04-29)

- Pipecat 1.1.0 ✅ installed on VPS
- DailyTransport ✅ working
- MiniMaxHttpTTSService ✅ available
- OpenRouterLLMService ✅ available  
- WhisperSTTService ✅ available
- SileroVADAnalyzer ✅ installed
- Bot code: `/home/hermes/voice-bot/bot.py` ✅ written
- **BLOCKED**: Missing `OPENAI_API_KEY` for Whisper STT (key not found anywhere)
- **BLOCKED**: `MINIMAX_API_KEY` not on VPS (only `OPENROUTER_API_KEY` present)

## VPS Setup — Full Steps

### 1. Install Dependencies
```bash
ssh vps
pip3 install --break-system-packages \
  pipecat-ai \
  pipecat-ai[daily] \
  aiohttp fastapi uvicorn pydantic-settings python-dotenv silero-vad
```
Note: Use `--break-system-packages` on Ubuntu 24.04 Python 3.12 (no root apt).

### 2. Create Bot Directory
```bash
ssh vps "mkdir -p /home/hermes/voice-bot"
```

### 3. Bot Code (Pipecat v1.1.0 — CORRECTED API)

The Pipecat v1.1.0 API differs significantly from older versions. Correct class names and imports:

```python
#!/usr/bin/env python3
import asyncio, os, sys, aiohttp
from loguru import logger

from pipecat.transports.daily.transport import DailyTransport, DailyParams
from pipecat.services.openrouter.llm import OpenRouterLLMService
from pipecat.services.whisper.stt import WhisperSTTService
from pipecat.services.minimax.tts import MiniMaxHttpTTSService
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair, LLMUserAggregatorParams,
)
from pipecat.runner.daily import configure
from pipecat.frames.frames import LLMRunFrame

DAILY_API_KEY = os.environ["DAILY_API_KEY"]

async def main():
    async with aiohttp.ClientSession() as session:
        (room_url, token) = await configure(session, api_key=DAILY_API_KEY, room_exp_duration=24.0)

        transport = DailyTransport(
            room_url, token, "Hermes",
            DailyParams(audio_in_enabled=True, audio_out_enabled=True, transcription_enabled=True),
        )

        # Pipeline: user audio → STT → LLM → TTS → bot audio
        # Correct v1.1.0 pipeline order:
        pipeline = Pipeline([
            transport.input(),          # Raw user audio
            WhisperSTTService(api_key=os.environ["OPENAI_API_KEY"]),
            LLMContextAggregatorPair(context=LLMContext(), user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()))[0],  # user agg
            OpenRouterLLMService(api_key=os.environ["OPENROUTER_API_KEY"], settings=OpenRouterLLMService.Settings(model="minimax/minimax-2026-04-15")),
            MiniMaxHttpTTSService(api_key=os.environ["MINIMAX_API_KEY"], settings=MiniMaxHttpTTSService.Settings(model="speech-02-turbo", voice="male-qn-qingse")),
            transport.output(),         # Bot audio out
            LLMContextAggregatorPair(context=LLMContext(), user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()))[1],  # assistant agg
        ])

        # ... rest of bot setup
```

### 4. VPS Environment Variables

VPS needs 3 keys. Check what's available:
```bash
# On VPS (hermes user):
python3 -c "import json; d=json.load(open('/home/hermes/.hermes/auth.json')); pool=d.get('credential_pool',{}); [(print(p, c['label'], len(c.get('access_token','')))) for p,v in pool.items() for c in v if isinstance(v,list)]"
```

Currently: `OPENROUTER_API_KEY` ✅ on VPS. `MINIMAX_API_KEY` and `OPENAI_API_KEY` ❌ missing.

To add missing keys, either:
- Copy from Surface `~/.hermes/auth.json` (credential_pool structure)
- Or set as env vars before running bot

### 5. Run the Bot
```bash
ssh vps
cd /home/hermes/voice-bot
OPENAI_API_KEY=sk-pro... MINIMAX_API_KEY=sk-cp-aOTN... OPENROUTER_API_KEY=sk-or-v1-... DAILY_API_KEY=pk_... \
  PATH=$HOME/.local/bin:$PATH PYTHONPATH=$HOME/.local/lib/python3.12/site-packages:$PYTHONPATH \
  python3 bot.py
```

### 6. Access from iPhone
- Open Safari on iPhone
- Navigate to the room URL (printed on bot start)
- Allow microphone access
- Speak — Hermes responds with voice

## Key Pipecat v1.1.0 Discoveries

| Item | Old/Wrong | Correct (v1.1.0) |
|------|-----------|-------------------|
| Daily transport class | `DailyTransportClient` | `DailyTransport` |
| Daily init signature | `(room_url, api_key, ...)` | `(room_url, token, bot_name, params)` |
| Room URL + token | Manual API call | `configure()` from `pipecat.runner.daily` |
| MiniMax TTS class | `MiniMaxTTSService` | `MiniMaxHttpTTSService` |
| MiniMax default model | `speech-02-hd` | `speech-02-turbo` |
| Pipeline user agg | `user_aggregator` separate | `LLMContextAggregatorPair(...)[0]` |
| Pipeline bot agg | `assistant_aggregator` separate | `LLMContextAggregatorPair(...)[1]` |
| Transport input | `transport` directly | `transport.input()` |
| Transport output | `transport` directly | `transport.output()` |

## Critical Constraints

- **MiniMax speech-02-hd NOT in $40 plan** — use `speech-02-turbo` or `speech-02-hd` requires upgrade
- **VPS Python 3.12** — requires `--break-system-packages` for pip
- **VPS sudo unavailable** — can't apt-get install, use pip with --break-system-packages
- **Missing OPENAI_API_KEY** — Marco must provide to enable Whisper STT
- **~3-5s latency** — not simultaneous conversation, sequential voice interaction
- **Must run on VPS** — Surface behind NAT, not reachable from iPhone

## Daily.co API Key

Saved in Bitwarden as "Daily.co API Key" (token: `pk_f96bf006-fde6-48c9-b7ff-f69cd7f1991f`)
