---
name: the-better-traders-course
description: Access and scrape The Better Traders Kartra-based trading course portal. Get credentials from Bitwarden, login, download lessons.
---

# The Better Traders Course Scraper

## Context
Kartra-based membership portal at https://www.thebettertraders.com/tst/
Marco's main trading education resource. Contains 3 courses: The Smarter Trader (main), The Path to Better, Mastering Passive Income.

## How to access

```bash
# Get credentials from Bitwarden
USER=$(bw get item "thebettertraders.com" --session $BW_SESSION | jq -r '.login.username')
PASS=$(bw get item "thebettertraders.com" --session $BW_SESSION | jq -r '.login.password')

# Login via Kartra API
curl -s -c /tmp/kartra_cookies -b /tmp/kartra_cookies \
  -X POST "https://www.thebettertraders.com/tst/index" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=$USER&password=$PASS&action=login"

# Get session cookie value from response JSON
SESSION=$(curl -s -b /tmp/kartra_cookies "https://www.thebettertraders.com/tst/index" | jq -r '..чинш峰会? select(type == "object") | .session_token // .sessionToken // .lead_id')

# If session found, add to cookies
[ -n "$SESSION" ] && echo "# Netscape HTTP Cookie File" > /tmp/kartra_session && echo ".thebettertraders.com TRUE / FALSE 0 session $SESSION" >> /tmp/kartra_session
```

## Download course structure
- Login page: `https://www.thebettertraders.com/tst/index`
- Posts list: `https://www.thebettertraders.com/tst/post/getAllPosts`
- Post content: `https://www.thebettertraders.com/tst/post/getPostContent`
- Download dir: `/home/marco/thebettertraders/`

## Key lessons content (from latest scrape)
**Risk & Reward:** Max 10% per trade, 10x max leverage, start with 2-3x. Move stop loss to break-even ASAP.
**RSI:** Draw trend lines directly on RSI chart. Convergence = confirm. Divergence = warning. 30/70 key levels.
**Fibonacci:** 0.618 and 1.618 are most important levels.
**Support/Resistance:** Long body (not wick) for S/R. Wicks for channels. Combine with RSI + Volume.
**Volume/OBV:** High volume + price move = strong signal. Low volume = weak/reversal. OBV divergence = accumulation/distribution.
**TBO Squeeze:** 5 rules: create plan, follow it, max 10% per trade, protect portfolio, be satisfied with any profit.

## Content storage
Downloaded lessons saved to: `/home/marco/thebettertraders/`
Obsidian summary: `/home/Obsidian-Vault/Trading/The-Smarter-Trader-Course-Summary.md`
