---
name: video-watcher
description: 'Analyze YouTube videos by extracting frames + captions for visual understanding. Use when Marco sends a YouTube URL and wants a real "watch" analysis (not just transcript read). Triggers: "guarda questo video", "analizza video", "watch this video", video URL + "riassunto/analizza".'
category: productivity
---

# Video Watcher

Analyze YouTube videos by extracting visual frames + captions so Claude/Hermes can truly "watch" instead of just read.

## How It Works

1. Takes YouTube URL → downloads video + gets captions
2. Extracts N representative frames (default: 8)
3. Captions provide transcript context
4. Frames are analyzed with vision tool for visual content

## Usage

```bash
python3 ~/.hermes/scripts/watch-video.py <youtube_url> [max_frames]
```

Or use directly in Hermes conversation — just send a YouTube link with "guarda e analizza".

## Skill Behavior

When user sends YouTube URL + "analizza/riassunto/guarda":
1. Run `watch-video.py` to extract frames to temp dir
2. Send each frame to vision analysis with caption context
3. Synthesize findings into summary

## Output Format

```
📺 [Video Title]
**Duration:** X min | **Frames analyzed:** N
**Visual content:** (what was seen in frames)
**Transcript summary:** (from captions)
**Key moments:** (timestamps with notable content)
**Actionable insights:** (implementation recommendations)
```

## Frame Extraction Config

- max_frames: 8 (cap at 20)
- resolution: 720p height (balance quality/size)
- spacing: even intervals across video duration

## Requirements

- `yt-dlp` — video download
- `moviepy` — frame extraction (via imageio-ffmpeg)
- Hermes vision capability — analyze frames

## Notes

- Video download takes 1-3 min depending on length
- Caption availability varies (YouTube auto-captions sometimes missing)
- Alternative: use Groq Whisper for audio transcription if captions unavailable