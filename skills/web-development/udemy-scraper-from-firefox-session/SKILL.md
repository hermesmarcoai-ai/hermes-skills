---
name: udemy-scraper-from-firefox-session
description: Scrape Udemy course content using an active Firefox browser session. Bypasses Cloudflare using the browser's cookies including cf_clearance token. For text/content only — video download requires separate DRM bypass.
version: 1.0
trigger: udemy, scrape udemy, download udemy course
---

# Udemy Scraper from Firefox Session

Scrape Udemy course pages using your active Firefox session cookies, bypassing Cloudflare protection.

## When to Use

- User is logged into Udemy in Firefox and wants to scrape course content
- yt-dlp / curl / headless Playwright blocked by Cloudflare 403
- Need course descriptions, curriculum structure, objectives (NOT video download)

## Prerequisites

1. Firefox must be running with an active Udemy session
2. Firefox profile path: `/home/marco/snap/firefox/common/.mozilla/firefox/8nt0aiea.default/cookies.sqlite`
3. Playwright with Chromium installed

## Cookie Extraction

```python
import sqlite3, shutil
from playwright.sync_api import sync_playwright

src = '/home/marco/snap/firefox/common/.mozilla/firefox/8nt0aiea.default/cookies.sqlite'
dst = '/tmp/fx_cookies_copy.sqlite'
shutil.copy2(src, dst)

conn = sqlite3.connect(dst)
c = conn.cursor()
c.execute("SELECT host, name, value, path, isSecure, expiry FROM moz_cookies WHERE host LIKE '%udemy%'")
rows = c.fetchall()
conn.close()

cookies = [
    {'domain': h, 'name': n, 'value': v, 'path': p if p else '/',
     'secure': bool(s), 'expires': int(e/1000)}
    for h, n, v, p, s, e in rows
]
```

## Scraping a Course Page

```python
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled',
              '--disable-dev-shm-usage', '--no-sandbox']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    )
    context.add_cookies(cookies)
    page = context.new_page()
    page.set_default_timeout(20000)

    page.goto('https://www.udemy.com/course/<SLUG>/',
              wait_until='domcontentloaded', timeout=15000)
    time.sleep(8)  # CRITICAL: wait for JS to render

    text = page.inner_text('body')
```

## Key Tricks

1. **`wait_until='domcontentloaded'` NOT `networkidle`** — Udemy keeps persistent connections (analytics). `networkidle` always times out.

2. **DO NOT use `wait_for_selector`** — it resolves before Cloudflare challenge clears, producing ~261 char placeholder pages.

3. **8-second sleep after domcontentloaded** — minimum needed for Udemy's JS to fully render.

4. **Fresh browser context per course** — prevents Cloudflare clearance conflicts.

5. **yt-dlp with Firefox cookies DOES NOT WORK** — `http.cookiejar` crashes on URL-encoded colons in `access_token` (which contains a JWT with `:` characters).

6. **Only `/users/me/subscribed-courses/` API works for course list** — other endpoints return 403 Cloudflare.

7. **Video download not possible** — Udemy uses Widevine DRM.

## Getting the Course List

```python
page.goto('https://www.udemy.com/api-2.0/users/me/subscribed-courses/?fields[course]=title,id,url,num_lectures&page_size=50',
          wait_until='domcontentloaded', timeout=15000)
time.sleep(2)
data = json.loads(page.inner_text('body'))
```

## Marco's Course IDs (April 2026)

| ID | Title | Lectures |
|----|-------|----------|
| 1349152 | Cryptocurrency: Complete Bitcoin, Ethereum, Altcoins! | 74 |
| 1368274 | ICOs/IEOs: Investing in Initial Coin/Exchange Offerings 2021 | 58 |
| 1400386 | Cryptocurrency Trading/TA Course: Achieve Wins Daily! | 54 |
| 1422012 | Bitcoin Trading Robot - Cryptocurrency Never Losing Formula | 34 |
| 1623098 | The Complete Cryptocurrency Course | 226 |
| 1753904 | The Complete Cryptocurrency & Bitcoin Trading Course (2026) | 97 |
| 1493516 | Crypto Trading & Investing: Technical Analysis for Bitcoin | 103 |
| 1405126 | Blockchain cryptocurrency course 101 | 11 |
| 2106840 | Crypto Trading Strategy For Winning Trades | 19 |
| 1366438 | Day Trading: Breakouts, Chart Analysis & Risk Management | 88 |
| 6862379 | Bitcoin Blueprint: Learn, Invest & Build Long-Term Wealth | 10 |

Note: IDs 1247394 and 2561954 returned "page not found" — those courses were removed from Udemy.
