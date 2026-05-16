# watch-video.py — Implementation Notes

## Location
`~/.hermes/scripts/watch-video.py` — installed locally, NOT part of any skill directory.

## Key Technical Fixes (bugs found and fixed)

### 1. subprocess.run — capture_output vs stderr
**Error:** `ValueError: stdout and stderr arguments may not be used with capture_output`

```python
# WRONG — can't mix capture_output with stdout/stderr pipes
subprocess.run(cmd, capture_output=True, stderr=subprocess.PIPE)

# CORRECT — use explicit pipes
subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
```

### 2. text=True keyword repeated
**Error:** `SyntaxError: keyword argument repeated: text`

```python
# WRONG — 'text' appears twice
subprocess.run(cmd, capture_output=True, text=True, stderr=subprocess.PIPE, text=True)

# CORRECT
subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
```

### 3. bytes vs string in parse_duration
**Error:** `TypeError: cannot use a string pattern on a bytes-like object`

```python
def parse_duration(stderr):
    if isinstance(stderr, bytes):
        stderr = stderr.decode('utf-8', errors='ignore')
    match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', stderr)
    ...
```

### 4. Duration in stderr, not stdout
ffmpeg writes duration info to **stderr**, not stdout. This is counter-intuitive but true.

### 5. Hardcoded ffmpeg path
The script uses a specific imageio-ffmpeg binary path for Python 3.12 compatibility:
```python
FFMPEG_PATH = "/home/marco/.local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
```

## Workflow

1. `python3 watch-video.py <video_id>` — extracts 4 frames at evenly-spaced intervals
2. Frames saved to `/tmp/video_analysis/<video_id>_frame_XX.jpg`
3. Video downloaded to `/tmp/video_analysis/<video_id>_video.mp4` (480p max for speed)
4. Captions attempted via `yt-dlp --write-auto-sub` but often fail (HTTP 429)

## Known Limitations

- Captions often unavailable → check transcripts manually
- Frame extraction requires download → takes time for long videos
- Telegram media sending can timeout if sending too many frames at once
- ffmpeg path is hardcoded — will break if imageio-ffmpeg is updated or Python version changes