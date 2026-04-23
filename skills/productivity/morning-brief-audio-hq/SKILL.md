---
name: morning-brief-audio-hq
description: High-quality audio morning briefing — synthesizes the daily brief into a natural-sounding voice memo using text-to-speech.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [morning, briefing, audio, voice, tts]
    category: productivity
---

# Morning Brief Audio HQ

Generates high-quality audio morning briefings using TTS. Part of the morning brief suite.

## When to Use

- User wants a "voice briefing" instead of text
- Morning commute — listen to the brief instead of reading
- Accessibility: prefers audio over text

## Prerequisites

```bash
# Text-to-speech is built-in via the text_to_speech tool
# No additional setup needed
```

## Usage

### Generate audio brief

```
User: "Give me this morning's brief as a voice message"
→ Load cos-proactive-reporting for content
→ Generate brief text
→ Send via text_to_speech
→ Deliver as voice message to Telegram
```

### Audio quality settings

Default: MiniMax TTS (high quality, 44.1kHz)

For higher quality (ElevenLabs):
```
Set ELEVENLABS_API_KEY in environment
Use --voice=professional or --voice=casual
```

## Brief Content

Same as cos-proactive-reporting but spoken naturally:

```
"Good morning, Marco. Here's your brief for [DATE].

YOUR DAY AT A GLANCE: You have 3 meetings and 2 deadlines today. The priority is the Q2 budget review, due by 10am with Sarah.

OPEN TASKS: 8 tasks waiting. 3 high priority, including the budget review and the VPS specs follow-up.

ACTION ITEMS: Reply to Sarah's email about the budget projections.

Have a productive day."
```

## Cron Integration

```bash
hermes cron create \
  --name "Morning audio brief" \
  --prompt "Run morning brief and deliver as high-quality voice message to Telegram" \
  --schedule "0 8 * * *" \
  --deliver telegram
```
