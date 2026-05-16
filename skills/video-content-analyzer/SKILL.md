---
name: video-content-analyzer
description: |
  Advanced video analyzer. Extracts transcripts, key frames, summaries.
  Works with YouTube, local videos.
trigger: "video,analyze,transcript,YouTube,course"
---

# Video Content Analyzer

## Usage
```bash
python3 ~/.hermes/scripts/watch-video.py <video_id>
yt-dlp --write-auto-sub --skip-download "URL"
```

## Output
```
# [Title] | Duration: X:XX

## Summary
## Key Sections
## Action Items
```