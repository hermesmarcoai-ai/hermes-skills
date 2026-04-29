---
name: ios-web-clip
description: Create an iOS Web Clip — an HTML page that can be added to the iPhone Home Screen like an app. Used for quick access to web apps from mobile.
version: 1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ios, web-clip, mobile, home-screen, pwa]
---

# iOS Web Clip — Create a Home Screen Shortcut

An iOS Web Clip is a webpage that, when added to the iPhone Home Screen, looks and behaves like a native app (full-screen, no Safari chrome).

## The Complete Workflow

1. Create an HTML page with iOS meta tags + icons
2. Serve it publicly (via cloudflare tunnel or any web host)
3. User opens URL on iPhone → Share → Add to Home Screen

## HTML Template

Save as `index.html` in a served directory:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="App Name">
  <meta name="mobile-web-app-capable" content="yes">

  <!-- Icons (PNG, pre-generated from SVG) -->
  <link rel="apple-touch-icon" href="/icon-192.png">
  <link rel="apple-touch-icon" sizes="152x152" href="/icon-152.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/icon-180.png">

  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #0f0f23;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
    }
    .spinner { /* loading spinner */ }
    .btn {
      margin-top: 30px;
      background: #6366f1;
      color: white;
      border: none;
      padding: 14px 32px;
      border-radius: 12px;
      font-size: 16px;
      text-decoration: none;
      display: inline-block;
    }
    .note { margin-top: 20px; font-size: 11px; color: #475569; }
  </style>
</head>
<body>
  <div class="spinner"></div>
  <h1>App Name</h1>
  <p>Loading...</p>
  <a href="https://your-actual-app-url.com" class="btn">Open App</a>
  <p class="note">Tap Share → Add to Home Screen</p>

  <script>
    // Auto-redirect to the real app
    window.location.href = 'https://your-actual-app-url.com';
  </script>
</body>
</html>
```

## Generating Icons from SVG

```bash
# Using ImageMagick (available on Surface)
convert -background none -size 192x192 /path/to/icon.svg icon-192.png
convert -background none -size 152x152 /path/to/icon.svg icon-152.png
convert -background none -size 180x180 /path/to/icon.svg icon-180.png
```

## Serving the Web Clip

```bash
# Local test server
mkdir -p /tmp/webclip
# (copy index.html and icons here)
cd /tmp/webclip && python3 -m http.server 8788

# Then expose via cloudflare tunnel
cd /tmp && ./cloudflared tunnel --url http://127.0.0.1:8788 > /tmp/webclip-cf.log 2>&1 &
sleep 10 && grep trycloudflare /tmp/webclip-cf.log
```

## User Instructions (iPhone)

1. Open the URL in Safari
2. Tap the **Share** button (square with arrow up)
3. Scroll down and tap **Add to Home Screen**
4. Name it and tap **Add**
5. App appears as an icon — opens full-screen without Safari UI

## Key Meta Tags

| Meta Tag | Purpose |
|----------|---------|
| `apple-mobile-web-app-capable` | Makes it full-screen (no address bar) |
| `apple-mobile-web-app-status-bar-style` | Status bar style: `black-translucent` recommended |
| `apple-mobile-web-app-title` | Name shown under the icon |
| `apple-touch-icon` | Icon image (180x180 for best quality) |
