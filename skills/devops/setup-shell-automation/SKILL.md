---
name: remotion-vps-setup
description: Configure and deploy Remotion projects on VPS — project structure, deployment scripts, and production optimization.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [remotion, video, deployment, vps, production]
    category: devops
---

# Remotion VPS Setup

Configure, optimize, and deploy Remotion projects on VPS. See also `remotion-vps-installer` for initial setup.

## When to Use

- "Deploy my Remotion project to production"
- "Configure Remotion for server-side rendering"
- "Optimize video rendering performance"
- "Set up a Remotion rendering pipeline"

## Project Structure

```
my-remotion-project/
├── src/
│   ├── Root.tsx          # Entry point
│   ├── HelloWorld/        # Composition
│   │   ├── index.tsx
│   │   └── Title.tsx
│   └── MyComposition/
│       └── index.tsx
├── out/                   # Rendered videos
├── package.json
└── remotion.config.ts
```

## Configuration

```typescript
// remotion.config.ts
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// Memory settings
Config.setXvfbSettings(["-ac", "-n", "+extension", "GLX"]);

// Timeout (10 minutes per frame for complex videos)
Config.setFrameRange(0, 300);
```

## Production Deployment

### Option 1: Direct render

```bash
# Render on VPS (slow, uses local resources)
npx remotion render MyComposition out/video.mp4
```

### Option 2: Lambda (AWS)

```bash
# Deploy to AWS Lambda (fast, scalable)
npx remotion lambda deploy

# Render on Lambda
npx remotion lambda render MyComposition out/video.mp4
```

### Option 3: Render farm

```bash
# Set up render queue with concurrency control
pm2 start --name render-queue "node scripts/render-queue.js"

# Submit render jobs
curl -X POST http://localhost:3001/render \
  -d '{"composition": "MyComposition", "duration": 60}'
```

## Cron: Automated Rendering

```bash
# Daily render pipeline
hermes cron create \
  --name "Remotion render daily brief" \
  --prompt "Run: cd ~/my-remotion-project && npx remotion render DailyBrief out/brief.mp4 && mv out/brief.mp4 /var/www/html/brief.mp4" \
  --schedule "0 8 * * *"
```

## Performance Tips

- Pre-compose complex compositions in After Effects
- Use `preload` for fonts/assets
- Set `max_concurrent_renders = 1` on VPS (memory limited)
- Use JPEG instead of PNG for frames (5x smaller)
- Render to tempfs (RAM disk) for speed:

```bash
# Create 2GB RAM disk
sudo mkdir -p /mnt/ramdisk
sudo mount -t tmpfs -o size=2G tmpfs /mnt/ramdisk

# Render to RAM disk
npx remotion render MyComposition /mnt/ramdisk/video.mp4
```

## Integration with Skills Pipeline

```
manim-video → Render animation → Remotion → Add audio → Final video
ascii-video  → Convert frames  → Remotion → Add audio → Final video
```

## Monitoring

```bash
# Watch render progress
pm2 logs remotion --lines 20 --nostream

# Resource usage
htop
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Render stuck at frame 0 | Check Chromium: `chromium --version` |
| Out of memory | Reduce concurrent renders, add swap |
| Font missing | Preload fonts in config |
| Slow render | Use Lambda or reduce composition complexity |
