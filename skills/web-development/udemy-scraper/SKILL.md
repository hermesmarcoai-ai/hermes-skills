---
name: udemy-scraper
description: Scrape Udemy course content (text/descriptions/curriculum) using Playwright + Firefox cookies from the local browser profile. Landing pages and course lists work; /learn/ player pages and API endpoints are blocked by Cloudflare in headless mode without a real browser fingerprint.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [udemy, scraping, playwright, cloudflare]
    category: web-development
---

# Udemy Scraper (Playwright + Firefox Cookies)

## When to Use

- User wants to extract course content, descriptions, curriculum structure, or other text from Udemy
- Course landing pages: fully accessible
- `/learn/` player pages: **BLOCKED** by Cloudflare in headless Playwright (returns ~261 chars of CF challenge)
- API endpoints (`/api-2.0/...`): **BLOCKED** (403) in headless Playwright
- Subscribed courses list via API: **BLOCKED** (403) — use the `/users/me/subscribed-courses/` page instead

## Prerequisites

Firefox must be **running and logged in** to Udemy. Cookies are read directly from the live Firefox profile.

## Step 1 — Get Cookies from Running Firefox

Firefox Snap stores cookies at:
## When to Use

- User wants to extract course content, descriptions, curriculum structure, or other text from Udemy
- Course landing pages: fully accessible
- `/learn/` player pages: **BLOCKED** by Cloudflare in headless Playwright (returns ~261 chars of CF challenge)
- API endpoints (`/api-2.0/...`): **BLOCKED** (403) in headless Playwright
- Subscribed courses list via API: **BLOCKED** (403) — use the `/users/me/subscribed-courses/` page instead

## Prerequisites

### Firefox ESR (NOT Snap) — Critical for CDP

Firefox Snap blocks CDP remote debugging. Install Firefox ESR:
```bash
sudo apt-add-repository -y ppa:mozillateam/ppa && sudo apt update && sudo apt install -y firefox-esr
```

Enable remote debugging on Firefox ESR:
1. Open `about:config`
2. Set `devtools.debugger.remote-enabled` → `true`
3. Set `devtools.debugger.prompt-connection` → `false`
4. Launch: `firefox-esr --remote-debugging-port=9222`

### Cookie Source Options

**Option A — From Firefox Snap cookies.sqlite (already logged in):**
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
        'expires': int(e / 1000)  # Firefox stores expiry in MILLISECONDS; divide by 1000 for Playwright
    }
    for h, n, v, p, s, e in rows
]
```

**Option B — From browser cookie export (Netscape format):**
```python
import json

# Marco exports via browser extension → doc_*.txt
with open('/path/to/doc_*.txt') as f:
    cookies_json = json.load(f)

playwright_cookies = [{
    'domain': c['domain'],
    'name': c['name'],
    'value': c['value'],
    'path': c.get('path', '/'),
    'secure': c.get('secure', False),
    'expires': c.get('expirationDate', 0)
} for c in cookies_json]
```

## Step 2 — Scrape via CDP (Real Firefox ESR Browser)

**CRITICAL**: Cloudflare blocks ALL headless browsers — Chromium and Firefox headless both return CF challenges. You MUST connect to a real Firefox ESR with a visible/remote debugging session.

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Connect to running Firefox ESR via CDP
    browser = p.firefox.connect('http://localhost:9222')
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    # Navigate to learning page
    page.goto('https://www.udemy.com/home/my-courses/learning/',
              wait_until='domcontentloaded', timeout=30000)
    time.sleep(10)
    
    # Scroll to load all courses
    for i in range(30):
        page.mouse.wheel(0, 1000)
        time.sleep(0.5)
    time.sleep(5)
    
    html = page.content()
    # ... extract course URLs from HTML
```

## Step 3 — Scrape Course Landing Pages (Headless OK for Landing Pages Only)

After getting course URLs, landing pages CAN be scraped with headless Chromium — but use a **fresh context per request** to avoid Cloudflare gates:

```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled',
              '--disable-dev-shm-usage', '--no-sandbox']
    )
    
    for course in courses:
        slug = course['url'].replace('/course/', '').replace('/learn/', '').replace('/', '')
        
        # Fresh context each time — prevents Cloudflare gate
        context = browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        context.add_cookies(cookies)
        page = context.new_page()
        page.set_default_timeout(20000)
        
        page.goto(f'https://www.udemy.com/course/{slug}/',
                  wait_until='domcontentloaded', timeout=15000)
        time.sleep(6)  # Wait for JS to render
        
        text = page.inner_text('body')
        if len(text) < 1000:
            print(f'⚠ Cloudflare blocked: {slug}')
        else:
            print(f'✓ Got {len(text)} chars for {slug}')
        
        page.close()
        context.close()
        time.sleep(1)
    
    browser.close()
```

## Known Limitations

- **Videos**: Cannot download — Udemy uses Widevine DRM requiring HDCP keys; no browser-less solution works
- **Curriculum on /learn/ pages**: Blocked by Cloudflare in headless mode; only course landing page text is accessible
- **API endpoints**: All return 403 via curl/headless — Cloudflare blocks without a real browser fingerprint
- **yt-dlp**: Fails due to Cloudflare + cookie format issues with colons in cookie values

## Extracting Course Data from Landing Page

```python
data = page.evaluate('''() => {
    let getText = sel => {
        let el = document.querySelector(sel);
        return el ? el.innerText.trim() : '';
    };
    return {
        title: getText('[data-testid="main-title"] h1, h1'),
        headline: getText('[data-purpose="course-headline"]'),
        description: getText('[data-purpose="course-description"]'),
        objectives: Array.from(
            document.querySelectorAll('[data-purpose="learning objectives"] li')
        ).map(li => li.innerText),
        instructor: getText('[data-purpose="instructor-name"]'),
        rating: getText('[data-testid="rating-number"]'),
        students: getText('[data-purpose="enrollment"]'),
        num_lectures: getText('[data-purpose="num-lectures"]'),
        duration: getText('[data-purpose="content-length"]'),
    };
}''')
```

## Key Lessons Learned

1. **Firefox Snap + CDP = blocked** — Snap sandboxing blocks `/walkie-talkie/` pipe needed for CDP. Use Firefox ESR from Mozilla PPA.
2. **Cloudflare blocks ALL headless browsers** — Even with valid `cf_clearance` cookie, headless Chromium/Firefox get CF challenges. CDP to a real Firefox ESR is the only working approach for scraping learning pages.
3. **curl/API always blocked** — No amount of valid cookies bypasses Cloudflare on direct HTTP. Needs a real browser.
4. **Fresh context per request** — Cloudflare gates after ~5 requests in same context (for landing page scraping with headless Chromium).
5. **Expiry in milliseconds** — Firefox SQLite stores expiry as ms; divide by 1000 for Playwright.
6. **wait_for_selector is dangerous** — Cloudflare elements satisfy selectors before real content loads; use fixed `time.sleep(6)` instead.
7. **yt-dlp cookie format** — URL-encoding cookie values (especially colons in `access_token`) breaks Netscape format.
