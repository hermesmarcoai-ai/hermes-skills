---
name: wealthyeducation-scraper
description: Scrape WealthyEducation.com course content — public pages and member area. WE lessons redirect to Udemy.
version: 2.0
author: Marco
metadata:
  hermes:
    tags: [wealthyeducation, trading, scraping, membership]
    category: web-development
---

# WealthyEducation Scraper (v2 — Updated 2026-04-27)

## Architecture Discovery

**CRITICAL:** WealthyEducation (`member.wealthyeducation.com`) is a **course aggregator/membership site** on WordPress + Thrive Theme. Individual lesson pages **redirect to Udemy course URLs**. This means:
- Scraping WE alone gives curriculum outlines, NOT video content
- Actual course videos are on Udemy
- Full content extraction requires Udemy access (same credentials work)

### URL Differences
| Resource | URL Pattern |
|----------|-------------|
| WE Login | `https://member.wealthyeducation.com/login/` (NOT `/wp-login.php`) |
| WE Courses | `https://member.wealthyeducation.com/courses/` |
| WE Course | `https://member.wealthyeducation.com/learn/{slug}/` |
| WE Lesson | `https://member.wealthyeducation.com/course/{slug}-module-{N}-lesson-{N}/` |

Note: Lesson URLs use `/course/` NOT `/lesson/`

## Credentials

From Bitwarden (`wealthyeducation` item):
- Username: `marco.info@zohomail.com.au`
- Password: `xudtin-5fyZje-kypkaw`
- Same credentials work on Udemy

## Bitwarden Unlock

```bash
# Master password: Coccobil-$0165361501

# Interactive:
bw unlock
# (paste password when prompted)

# Non-interactive via Python:
python3 -c "
import subprocess
proc = subprocess.Popen(['bw', 'unlock', '--raw'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
output = proc.communicate(input='Coccobil-\$0165361501\n')[0]
print(output)
"
# Extract BW_SESSION from output (base64 key printed after "Your vault is now unlocked!")

# Search credentials:
export BW_SESSION="<session_key>"
bw list items --search wealthyeducation --session "$BW_SESSION"
```

Session token in `~/.bashrc` (may be expired): `grep BW_SESSION ~/.bashrc`

## Playwright Scraping (Recommended)

Use Playwright with Chromium (NOT Firefox ESR — Firefox has issues on this system).

```python
from playwright.sync_api import sync_playwright
import time

EMAIL = "marco.info@zohomail.com.au"
PASSWORD = "xudtin-5fyZje-kypkaw"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    # Login to WE — use /login/ URL, fill by name attribute
    page.goto("https://member.wealthyeducation.com/login/", timeout=30000)
    time.sleep(2)
    page.fill("input[name='log']", EMAIL)
    page.fill("input[name='pwd']", PASSWORD)
    page.click("input[name='wp-submit']")
    time.sleep(4)
    
    # Scrape course list
    page.goto("https://member.wealthyeducation.com/courses/", timeout=30000)
    time.sleep(3)
    
    # Get course URLs
    links = page.query_selector_all("a[href*='/learn/']")
    
    # For each course, get lesson URLs
    for link in links:
        href = link.get_attribute('href')
        page.goto(href, timeout=30000)
        time.sleep(3)
        # Lesson URLs: a[href*='/course/'][href*='module']
        # IMPORTANT: /course/ NOT /lesson/
```

### Why Not Firefox ESR
Firefox ESR remote debugging doesn't work reliably on this system (Surface Pro 3, Ubuntu). Chromium via Playwright works consistently.

## Known WE Courses (2026-04-27)
1. the-complete-short-selling-course
2. the-complete-day-trading-course
3. the-complete-swing-trading-course
4. the-complete-fibonacci-trading-course
5. the-complete-technical-analysis-course
6. the-complete-candlestick-trading-course
7. the-advanced-technical-analysis-course
8. the-complete-cryptocurrency-trading-course
9. the-advanced-cryptocurrency-trading-course
10. the-complete-forex-trading-course
11. the-complete-stock-trading-course
12. the-complete-options-trading-course
13. the-advanced-options-trading-course

## Output
- Course metadata + curriculum → `/tmp/we_courses.json`
- Full lesson content → `/tmp/we_full_content.json`
- Analysis → Obsidian Vault: `/home/Obsidian-Vault/Trading/`

## Existing Knowledge Base
**Master Trading Strategy** already exists:
`/home/Obsidian-Vault/Trading/Master-Trading-Strategy.md` (generated 2026-04-26 from 13 Udemy courses + The Smarter Trader)

## Pitfalls
- Login form uses `name=` attributes, not `id=` (different from standard WordPress)
- Lesson URLs use `/course/` not `/lesson/` — easy to miss
- WE pages redirect to Udemy for actual lesson content — scraping WE alone is insufficient
- Bitwarden session expires — master password `Coccobil-$0165361501` needed each session
