---
name: browser-harness
description: Browser automation harness for Hermes Agent — headless Chrome via Playwright, CDP control, multi-profile management, and Cloudflare bypass.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [browser, automation, headless, cdp, chrome, scraping]
    category: web-development
---

# Browser Harness

Headless browser automation for Hermes Agent using Playwright, CDP (Chrome DevTools Protocol), and Cloudflare-rendering plugins.

## When to Use

- User asks to "browse", "scrape", "take screenshot of", or "extract content from" a website
- Website blocks simple curl/fetch (Cloudflare, JavaScript-rendered)
- Need to interact with a page (click, fill forms, scroll)
- Multi-account testing with different Chrome profiles

## Prerequisites

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Optional: Chrome profiles plugin
# hermes plugins install anpicasso/hermes-plugin-chrome-profiles

# Optional: Cloudflare bypass
# hermes plugins install raulvidis/hermes-cloudflare
```

## Usage Patterns

### Basic browsing

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")
    content = page.content()
    screenshot = page.screenshot()
    browser.close()
```

### Withstealth mode (avoid bot detection)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
    )
    page = browser.new_page()
    # ... use normally
```

### CDP (Chrome DevTools Protocol)

```python
# Access raw CDP for advanced control
browser = p.chromium.launch(headless=True)
client = page.context.new_cdp_session(page)
client.send("Network.enable")
client.send("Page.navigate", {"url": "https://example.com"})
```

### Multi-profile browsing

```bash
# Using hermes-plugin-chrome-profiles
hermes plugins install anpicasso/hermes-plugin-chrome-profiles
hermes chrome-profiles --list
hermes chrome-profiles --switch work
```

## Common Tasks

| Task | Command |
|------|---------|
| Screenshot | `page.screenshot()` |
| Full page PDF | `page.pdf()` |
| Extract text | `page.inner_text("body")` |
| Click element | `page.click("#button-id")` |
| Fill form | `page.fill("input[name=email]", "test@example.com")` |
| Wait for element | `page.wait_for_selector("#result", timeout=5000)` |
| Handle alert | `page.on("dialog", lambda d: d.accept())` |
| Block requests | `page.route("**/*.{png,jpg,gif}", lambda r: r.abort())` |

## Opening Firefox GUI on Surface Desktop

On Surface Pro 3 (Ubuntu/LXQt), `/usr/bin/firefox` is a **snap wrapper** that fails with:
```
error: cannot communicate with server: Post "http://localhost/v2/snapctl": connection refused
ERROR: not connected to the gnome-42-2204 content interface.
```
The real Firefox binary is `firefox-esr` (Mozilla Firefox ESR package).

**To open a visible Firefox window as the `marco` user:**
```bash
sudo -u marco env DISPLAY=:0 HOME=/home/marco DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus firefox-esr --new-window [URL]
```

Key env vars required: `DISPLAY=:0`, `HOME=/home/marco`, `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus`

**Firefox Snap Cookies — Critical Gotcha**

Firefox Snap stores cookies in SQLite but with **expiry in milliseconds** (Unix epoch in ms), NOT seconds. When converting for Playwright, divide by 1000:

```python
# Firefox Snap: expiry stored as milliseconds
expiry_ms = row[5]  # e.g. 1811773890000
exp_sec = int(expiry_ms / 1000)  # → 1811773890
```

Also: Firefox Snap cookie files are **locked while the browser runs**. Copy with retry logic:
```python
for attempt in range(3):
    try:
        shutil.copy2(src, dst)
        break
    except sqlite3.OperationalError:
        time.sleep(1)
```

## Cloudflare Bypass — Browser Cookie Extraction

Cloudflare Clearance tokens (`cf_clearance`) are browser-fingerprint-specific and **do not work server-side**. Headless Playwright/Selenium are blocked by Cloudflare's bot detection. The working pattern:

### Step 1: Export cookies from user's browser

**Firefox (Snap) — copy cookies while browser is running:**
```python
import sqlite3, shutil

src = "/home/marco/snap/firefox/common/.mozilla/firefox/<profile>/cookies.sqlite"
dst = "/tmp/exported_cookies.sqlite"

# Copy file (may need retry if DB is locked)
try:
    shutil.copy2(src, dst)
except sqlite3.OperationalError:
    import time; time.sleep(1)
    shutil.copy2(src, dst)

conn = sqlite3.connect(dst)
# Filter relevant cookies
c.execute("SELECT host, name, value, path, expiry FROM moz_cookies WHERE host LIKE '%targetsite%'")
```

**Chrome — use --user-data-dir to copy profile or export via cookie file.**

### Step 2: Write Netscape-format cookie file

```python
with open('/tmp/cookies.txt', 'w') as f:
    f.write("# Netscape HTTP Cookie File\n\n")
    for host, name, value, path, expiry in rows:
        secure = 1 if 'targetsite.com' in host else 0
        domain = host if host.startswith('.') else host
        f.write(f"{domain}\tTRUE\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
```

### Step 3: Use with curl + Bearer token

```bash
curl -s -b /tmp/cookies.txt \
  -H "Authorization: Bearer <access_token>" \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0" \
  "https://api.targetsite.com/endpoint"
```

## Udemy — Logged-in Session with Playwright + Firefox Cookies

Once cookies are extracted from Firefox, use Playwright Chromium with `wait_until='domcontentloaded'` (NOT `networkidle`) since Udemy is SPA-heavy:

```python
# Convert Firefox ms timestamps to seconds
cookies = [{'domain': h, 'name': n, 'value': v, 'path': p or '/', 
            'secure': bool(s), 'expires': int(e/1000) if e else -1} 
           for h,n,v,p,s,e in rows]

# Udemy API (works with session cookies)
page.goto('https://www.udemy.com/api-2.0/users/me/subscribed-courses/?'
          'fields[course]=title,headline,thumbnail,url&page_size=20',
          wait_until='networkidle', timeout=20000)
```

### Critical lessons learned

- **Bearer token + cookie combination** authenticates where curl alone fails (Cloudflare blocks)
- **Cloudflare clearance tokens** (`cf_clearance`, `__cf_bm`) are tied to browser fingerprint — copy from running browser's cookie store
- **Database locking**: Firefox SQLite cookies can be copied even while browser runs (try/copy/retry)
- **REST API limits**: Some sites (e.g. Udemy) don't expose lesson content via API — only metadata
- **Headless browsers bypass**: Cloudflare blocks headless Chrome/Firefox even with stealth args; real browser profile + cookie export works
- **Firefox Snap expiry**: cookies stored as ms, Playwright needs seconds — divide by 1000
- **SPA routing**: Udemy uses `domcontentloaded` not `networkidle` for navigation

## Cloudflare Plugin (fallback)

```bash
hermes plugins install raulvidis/hermes-cloudflare
```

## Tips

- Always set a `user_agent` to avoid detection
- Use `page.wait_for_load_state("networkidle")` for SPAs
- Set `viewport` to a real resolution: `{"width": 1920, "height": 1080}`
- For screenshots: use `full_page=True` to capture scrolling pages
- Store cookies with `context.cookies()` to maintain sessions
