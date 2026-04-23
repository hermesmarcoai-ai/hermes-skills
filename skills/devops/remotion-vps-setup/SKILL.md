---
name: remotion-vps-installer
description: Install Remotion on a VPS for server-side video rendering — full setup guide for headless Chromium, FFmpeg, and Remotion deployment.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [remotion, video, vps, installation, chromium]
    category: devops
---

# Remotion VPS Installer

Install and configure [Remotion](https://remotion.dev) on a VPS for server-side video rendering.

## When to Use

- "Set up Remotion on my VPS"
- "I want to render videos on the server"
- "Install headless Chromium for video rendering"
- "Deploy Remotion to production"

## Prerequisites

- VPS with 2GB+ RAM
- Ubuntu 22.04+ or Debian 12+
- Root or sudo access
- 5GB+ free disk space

## Step 1: System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
  wget \
  unzip \
  gnupg \
  curl \
  git \
  build-essential \
  pkg-config \
  libglib2.0-0 \
  libnss3 \
  libnspr4 \
  libdbus-1-3 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libdrm2 \
  libxkbcommon0 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libpango-1.0-0 \
  libcairo2 \
  libasound2 \
  libatspi2.0-0
```

## Step 2: FFmpeg

```bash
sudo apt install -y ffmpeg
ffmpeg -version  # Verify
```

## Step 3: Node.js 20+

```bash
# Install Node.js 20 via nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20
node -v  # Should show v20.x.x
```

## Step 4: Chrome/Chromium

```bash
# Install Chromium
sudo apt install -y chromium-browser

# Or Chrome (more reliable for video)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install -y google-chrome-stable
```

## Step 5: Remotion Project

```bash
# Create Remotion project
npx create-video@latest my-remotion-app
cd my-remotion-app

# Install deps
npm install

# Test render
npx remotion render HelloWorld out/hello.mp4
```

## Step 6: PM2 Setup

```bash
# Install PM2
npm install -g pm2

# Start Remotion dev server with PM2
pm2 start npx --name remotion -- remotion preview --port 3000

# Save PM2 state
pm2 save
pm2 startup
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Chrome fails to launch | `sudo apt install -y chromium-browser` |
| FFmpeg not found | `sudo apt install ffmpeg` |
| Out of memory | Add swap: `sudo fallocate -l 2G /swapfile` |
| Permission denied | `sudo usermod -a -G video $USER` |

## Verify Installation

```bash
# Quick render test
npx remotion render HelloWorld out/test.mp4

# Check output
ls -lh out/test.mp4
```
