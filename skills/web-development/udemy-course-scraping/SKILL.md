---
name: udemy-course-scraping
description: Scrape Udemy course content using Firefox ESR with real browser profile. Cloudflare blocks headless Playwright and curl. Best approach is CDP remote debugging or headed browser with real cookies.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [udemy, scraping, firefox, cloudflare, playwright]
    category: web-development
---

# Udemy Course Scraping

## The Problem

Udemy uses Cloudflare to block headless browsers, curl API calls, and even Playwright-launched browsers that don't use the user's real Firefox profile. The cf_clearance token and browser fingerprinting are the main obstacles.

## Key Insight

Cloudflare does not block YOUR actual Firefox browser. The solution is to either use the already-running Firefox profile via CDP remote debugging, or launch a new browser instance carrying real cookies and fingerprint.

## Method A - Running Firefox + CDP Remote Debugging (Best)

### Step 1: Enable Remote Debugging on Firefox

1. Open `about:config`
2. Set `devtools.debugger.remote-enabled` = **true**
3. Set `devtools.debugger.prompt-connection` = **false**

### Step 2: Start Firefox with Remote Debugging Port

```bash
firefox-esr --remote-debugging-port=9222
# or for Snap Firefox:
firefox --remote-debugging-port=9222
```

### Step 3: Connect via Playwright CDP

```python
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Connect to the running browser
    browser = p.firefox.connect("ws://localhost:9222")
    context = browser.contexts[0]
    page = context.pages[0]  # Use existing tab
    
    # Extract course URLs
    import re
    html = page.content()
    course_urls = re.findall(r'href="(https://www\.udemy\.com/course/[^"?#\s]+)"', html)
```

## Method B - Headed Browser with Real Profile Cookies

### Get Cookies from Firefox Snap Profile

```python
import sqlite3, shutil, json

src = '/home/marco/snap/firefox/common/.mozilla/firefox/8nt0aiea.default/cookies.sqlite'
dst = '/tmp/fx_cookies_copy.sqlite'
shutil.copy2(src, dst)

conn = sqlite3.connect(dst)
c = conn.cursor()
c.execute("SELECT host, name, value, path, isSecure, expiry FROM moz_cookies WHERE host LIKE '%udemy%'")
rows = c.fetchall()
conn.close()

cookies = [
    {
        'domain': h,
        'name': n,
        'value': v,
        'path': p if p else '/',
        'secure': bool(s),
        'expires': int(e / 1000)  # Firefox stores ms; Playwright wants seconds
    }
    for h, n, v, p, s, e in rows
]
```

### Launch Real Browser with DISPLAY

```python
import os, asyncio, json

os.environ['DISPLAY'] = ':0'  # Use the real display

with open('/tmp/udemy_cookies_playwright.json') as f:
    cookies = json.load(f)

async def scrape():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=False,
            args=['--width=1920', '--height=1080']
        )
        
        context = await browser.new_context()
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        await page.goto('https://www.udemy.com/home/my-courses/learning/',
                       wait_until='domcontentloaded')
        await asyncio.sleep(10)
        
        # Scroll to load all courses
        for i in range(30):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(0.5)
        
        html = await page.content()
```

## Method C - Cookie Export via Browser Extension (Recommended)

1. Install EditThisCookie Chrome/Firefox extension
2. Go to Udemy and export cookies as JSON
3. Save to `/tmp/udemy_cookies.json`
4. Convert to Playwright format and use Method B

## Known Limitations

- **Videos**: Cannot download - Udemy uses Widevine DRM
- **Curriculum on /learn/ pages**: Blocked by Cloudflare in headless mode
- **yt-dlp with cookies**: Fails due to Cloudflare + cookie format issues
- **Firefox Snap windows**: Cannot be captured via X11 screenshot from another process (sandbox blocks it)
- **curl/API calls**: ALL blocked by Cloudflare (403) regardless of cookie validity

## Trial and Error Findings

1. **Headless vs Headed does not bypass CF** - Playwright's headed mode still uses a clean browser profile that Cloudflare detects
2. **Firefox Snap cookies at**: `/home/marco/snap/firefox/common/.mozilla/firefox/<profile>/cookies.sqlite`
3. **DISPLAY=:0** - The Surface uses LXQt, DISPLAY=:0 is the local desktop
4. **X11 screenshot of Snap windows** - `import` fails with "Resource temporarily unavailable" because Snap Firefox runs in a sandbox that blocks X11 screen capture from other processes
5. **Bitwarden CLI** - Status shows "locked" even when logged in; unlock with master password or via `bw unlock`
6. **CDP via Playwright** - `p.firefox.connect(ws://...)` connects to an already-running browser; `p.firefox.launch()` always creates a fresh browser
7. **Running browser cookie source** - Cookies from the running browser profile at `~/.mozilla/firefox/` (ESR) or `~/snap/firefox/common/.mozilla/firefox/` (Snap)
