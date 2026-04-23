---
name: portfolio-brief-with-x-sentiment
description: Generate portfolio brief enriched with X/Twitter sentiment analysis — combine crypto positions with social media sentiment for trading context.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [portfolio, crypto, xwitter, sentiment, trading]
    category: devops
---

# Portfolio Brief with X Sentiment

Combines crypto portfolio data with X/Twitter sentiment analysis for trading context. Know what the market thinks about your positions.

## When to Use

- "Give me a portfolio update with market sentiment"
- "What are people saying about SOL right now?"
- "Should I be worried about my crypto positions?"
- "Morning brief with social sentiment"

## Setup

```bash
# X credentials (for xitter or xurl skill)
export X_API_KEY=xxx
export X_API_SECRET=xxx

# Crypto portfolio (see crypto-portfolio-monitoring skill)
```

## Usage

### Full brief with sentiment

```
User: "Portfolio brief with X sentiment"
→ Pull portfolio positions
→ Fetch recent X posts mentioning each coin
→ Run sentiment analysis
→ Generate brief:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PORTFOLIO BRIEF — Apr 23, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💼 POSITIONS
  SOL: 150 @ $122 = $18,300
  BTC: 0.5 @ $66k = $33,000
  USDC: $2,000
  Total: $53,300

📊 24H P&L: +$1,200 (+2.3%)
📈 7D P&L:   +$3,100 (+6.2%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
X SENTIMENT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 SOL — 1,247 posts in 24h
  Bullish: 62%  📈
  Bearish: 21%  📉
  Neutral: 17%
  Avg sentiment: 0.72/1.0 (POSITIVE)
  Key themes:
    • "Jupiter DCA momentum building"
    • "Solana DeFi TVL hit new ATH"
    • "Memecoin season = SOL pumps"

🔍 BTC — 3,891 posts in 24h
  Bullish: 58%
  Bearish: 28%
  Neutral: 14%
  Avg sentiment: 0.61/1.0 (POSITIVE)
  Key themes:
    • "ETF inflows continue"
    • "Fed pivot speculation"

⚠️ ALERT: BTC sentiment dropping (was 0.71 yesterday)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 RECOMMENDATION: HOLD
  • SOL momentum positive, DCA looks good
  • BTC sentiment cooling but not alarming
  • No action needed — monitor for 24h
```

## Sentiment Sources

- X/Twitter posts (via xitter or xurl)
- Keyword search per coin: `$SOL`, `#Solana`, `$BTC`, `#Bitcoin`
- Fallback: crypto news headlines if X unavailable

## Cron Integration

```bash
# Morning brief with sentiment
hermes cron create \
  --name "Portfolio + sentiment morning brief" \
  --prompt "Run portfolio-brief-with-x-sentiment, deliver to Telegram" \
  --schedule "0 8 * * 1-5" \
  --deliver telegram
```

## Alert Triggers

```
Sentiment shift > 20% in 24h → Alert
Sentiment drops below 0.4 (bearish) → Alert
Whale activity detected → Include in brief
```
