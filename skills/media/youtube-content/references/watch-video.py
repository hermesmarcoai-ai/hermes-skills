#!/usr/bin/env python3
"""Extract frames and captions from YouTube videos for visual analysis.

Usage:
    python3 watch-video.py <video_id_or_url> [max_frames]

Output:
    - /tmp/video_analysis/{id}_frame_NN.jpg  (extracted frames)
    - /tmp/video_analysis/{id}_video.mp4      (downloaded video, cleaned up)
    - /tmp/video_analysis/{id}_captions.txt   (subtitle text if available)
"""

import sys
import re
import subprocess
from pathlib import Path

FFMPEG_PATH = "/home/marco/.local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

def parse_duration(stderr):
    """Extract duration from ffmpeg stderr output.

    ffmpeg writes Duration: HH:MM:SS.mm to stderr, not stdout.
    subprocess.run returns bytes — must decode before regex.
    """
    if isinstance(stderr, bytes):
        stderr = stderr.decode('utf-8', errors='ignore')
    match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 0

def get_video_id(url):
    """Extract 11-char video ID from any YouTube URL format."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url.strip()

def extract_captions(video_id, output_dir):
    """Try to extract subtitles/captions from video."""
    captions_file = output_dir / f"{video_id}_captions.txt"

    cmd = [
        "yt-dlp", "--write-auto-sub", "--write-sub", "--sub-lang", "en,it",
        "--skip-download", "--output", str(output_dir / "temp_%(id)s"),
        f"https://www.youtube.com/watch?v={video_id}"
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        for ext in ['.vtt', '.srt', '.ass']:
            temp_file = output_dir / f"temp_{video_id}{ext}"
            if temp_file.exists():
                with open(temp_file) as f:
                    content = f.read()
                text = re.sub(r'<[^>]+>', '', content)
                text = re.sub(r'\n+', '\n', text).strip()
                with open(captions_file, 'w') as f:
                    f.write(text)
                temp_file.unlink()
                break
    except Exception:
        pass

    return captions_file

def extract_frames(video_id, output_dir, max_frames=4):
    """Download video and extract frames at regular intervals."""
    cmd = [
        "yt-dlp", "-f", "best[height<=480]", "--no-playlist",
        "-o", str(output_dir / f"{video_id}_video.mp4"),
        f"https://www.youtube.com/watch?v={video_id}"
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    video_path = output_dir / f"{video_id}_video.mp4"

    if not video_path.exists():
        return []

    duration = parse_duration(result.stderr)
    if duration == 0:
        probe = subprocess.run(
            [FFMPEG_PATH, "-i", str(video_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        duration = parse_duration(probe.stderr)

    frames = []
    interval = max(duration / (max_frames + 1), 1)

    for i in range(1, max_frames + 1):
        timestamp = int(interval * i)
        frame_path = output_dir / f"{video_id}_frame_{i:02d}.jpg"

        subprocess.run(
            [FFMPEG_PATH, "-ss", str(timestamp), "-i", str(video_path),
             "-vframes", "1", "-q:v", "2", str(frame_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if frame_path.exists() and frame_path.stat().st_size > 0:
            frames.append(str(frame_path))

    return frames

def main():
    if len(sys.argv) < 2:
        print("Usage: watch-video.py <video_id_or_url> [max_frames]")
        sys.exit(1)

    video_id = get_video_id(sys.argv[1])
    max_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    output_dir = Path("/tmp/video_analysis")
    output_dir.mkdir(exist_ok=True)

    print(f"Video ID: {video_id}")

    captions_file = extract_captions(video_id, output_dir)
    if captions_file.exists():
        with open(captions_file) as f:
            text = f.read()
        print(f"\n=== CAPTIONS ({len(text)} chars) ===")
        print(text[:500] if len(text) > 500 else text)
    else:
        print("\n=== CAPTIONS: not available ===")

    frames = extract_frames(video_id, output_dir, max_frames)
    print(f"\n=== FRAMES: {len(frames)} extracted ===")
    for frame in frames:
        print(f"  {frame}")

    return video_id

if __name__ == "__main__":
    main()