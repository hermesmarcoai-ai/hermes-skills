#!/usr/bin/env python3
"""
watch-video.py — YouTube video analyzer for Hermes
Takes URL, extracts frames + transcript, returns analysis-ready content.

Usage: python3 watch-video.py <youtube_url> [max_frames]
"""

import sys
import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path

FFMPEG_BIN = "/home/marco/.local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

def run(cmd, timeout=120):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", 1

def parse_duration(stderr):
    """Parse duration from ffmpeg stderr output."""
    for line in stderr.split('\n'):
        if 'Duration:' in line:
            t = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = t.split(':')
            return int(h)*3600 + int(m)*60 + float(s)
    return None

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    import re
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'watch\?v=([a-zA-Z0-9_-]{11})',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def get_captions(url, output_dir):
    """Get YouTube captions via yt-dlp."""
    captions_path = os.path.join(output_dir, "captions.txt")
    
    # Try to get YouTube captions
    cmd = f'yt-dlp --write-sub --write-auto-sub --sub-lang en,it --skip-download --output "{output_dir}/caption" "{url}" 2>&1'
    stdout, stderr, code = run(cmd, timeout=60)
    
    # Look for generated caption file
    for f in os.listdir(output_dir):
        if 'caption' in f and (f.endswith('.vtt') or f.endswith('.srt') or f.endswith('.txt')):
            src = os.path.join(output_dir, f)
            with open(src, 'r', encoding='utf-8') as f_read:
                content = f_read.read()
            with open(captions_path, 'w') as f_write:
                f_write.write(content)
            return captions_path
    
    return None

def extract_frames(video_path, output_dir, max_frames=8):
    """Extract frames from video using ffmpeg (via imageio-ffmpeg)."""
    frames_dir = os.path.join(output_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    try:
        # Get video duration using ffmpeg -i (ffprobe not included in imageio-ffmpeg)
        cmd = f'"{FFMPEG_BIN}" -i "{video_path}"'
        stdout, stderr, rc = run(cmd)
        duration = parse_duration(stderr)
        if not duration:
            return None
        
        # Extract frames at even intervals
        interval = duration / (max_frames + 1)
        for i in range(1, max_frames + 1):
            t = interval * i
            frame_path = os.path.join(frames_dir, f"frame_{i:02d}.jpg")
            cmd = f'"{FFMPEG_BIN}" -ss {t:.1f} -i "{video_path}" -vframes 1 -q:v 2 -y "{frame_path}"'
            _, _, code = run(cmd, timeout=30)
        
        frames = os.listdir(frames_dir)
        return frames_dir if frames else None
    except Exception as e:
        print(f"Frame extraction error: {e}")
        return None

def download_video(url, output_dir):
    """Download video audio for caption extraction."""
    output_path = os.path.join(output_dir, "video.mp4")
    cmd = f'yt-dlp -f "best[height<=720]" --merge-output-format mp4 -o "{output_path}" "{url}" 2>&1'
    stdout, stderr, code = run(cmd, timeout=180)
    
    if os.path.exists(output_path):
        return output_path
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: watch-video.py <youtube_url> [max_frames]")
        print("  max_frames: 1-20 (default: 8)")
        sys.exit(1)
    
    url = sys.argv[1]
    max_frames = min(int(sys.argv[2]) if len(sys.argv) > 2 else 8, 20)
    
    video_id = extract_video_id(url)
    if not video_id:
        print("❌ Invalid YouTube URL")
        sys.exit(1)
    
    print(f"🎬 Processing: {url}")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("⏳ Downloading video...")
        video_path = download_video(url, tmpdir)
        
        if video_path:
            print("📸 Extracting frames...")
            frames_dir = extract_frames(video_path, tmpdir, max_frames)
            if frames_dir:
                frames_count = len(os.listdir(frames_dir))
                print(f"✅ {frames_count} frames extracted → {frames_dir}")
            else:
                print("⚠️ Frame extraction failed")
        else:
            print("⚠️ Video download failed, trying captions only...")
            frames_dir = None
        
        print("📝 Getting captions...")
        captions_path = get_captions(url, tmpdir)
        
        if captions_path:
            print(f"✅ Captions saved → {captions_path}")
            with open(captions_path, 'r') as f:
                print(f"   Length: {len(f.read())} chars")
        else:
            print("⚠️ No captions available")
        
        # Output summary
        print("\n📋 ANALYSIS SUMMARY")
        print(f"   Video ID: {video_id}")
        print(f"   Frames: {frames_dir}")
        print(f"   Captions: {captions_path}")

if __name__ == "__main__":
    main()