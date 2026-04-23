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

## Cloudflare Bypass

For Cloudflare-protected sites, use the cloudflare plugin:

```bash
hermes plugins install raulvidis/hermes-cloudflare
```

Or use the Cloudflare Rendering API:

```python
# Using Cloudflare's infrastructure (no local browser needed)
import subprocess
result = subprocess.run([
    "curl", "-sL",
    "https://cloudflare.com/rendering-api",
    "-d", '{"url": "https://example.com"}'
], capture_output=True)
```

## Tips

- Always set a `user_agent` to avoid detection
- Use `page.wait_for_load_state("networkidle")` for SPAs
- Set `viewport` to a real resolution: `{"width": 1920, "height": 1080}`
- For screenshots: use `full_page=True` to capture scrolling pages
- Store cookies with `context.cookies()` to maintain sessions
