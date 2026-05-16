---
name: video-content-analyzer
description: |
  Advanced video content analyzer. Extracts transcripts, key frames, generates
  summaries, identifies action items. Works with YouTube, local videos, courses.
trigger: "video,analyze video,extract transcript,video summary,YouTube analysis, course"
---

# Video Content Analyzer

Advanced video analysis with transcript extraction and intelligent summarization.

## Usage

```bash
# Extract from YouTube
python3 ~/.hermes/scripts/watch-video.py <video_url_or_id>

# Get transcript only
yt-dlp --write-auto-sub --skip-download "VIDEO_URL"

# Get video info
yt-dlp --get-title --get-duration --list-subs "VIDEO_URL"
```

## Output Format

```
# [Video Title]
Duration: X:XX | Source: [URL]

## Summary
[2-3 paragraph overview]

## Key Sections
| Timestamp | Topic |
|-----------|-------|
| 0:00 | Introduction |
...

## Action Items
- [ ] Task 1
- [ ] Task 2
```