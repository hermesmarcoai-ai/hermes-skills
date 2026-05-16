---
name: alpaca-trading-agent
description: |
  Autonomous crypto/stock trading agent using Alpaca API. Monitors markets,
  executes paper trades, manages portfolio. Use with crypto-backtest-engine
  and smart-money-crypto-strategy skills.
trigger: "trading,alpaca,paper trading,crypto bot,automated trading"
---

# Alpaca Trading Agent

Autonomous trading agent that monitors markets and executes trades via Alpaca API.

## Setup

```bash
# Install Alpaca SDK
pip install alpaca-trade-api --break-system-packages

# Verify configuration
alpaca profile list
```

## Environment

```bash
# Required in .env
 ALPACA_API_KEY=your_key
 ALPACA_SECRET_KEY=your_secret
 ALPACA_PAPER=true
```

## Trading Strategy

- Monitor price movements on configured symbols
- Execute buy/sell based on technical signals
- Track performance and log all trades
- Manage risk with position sizing

## Commands

| Task | Command |
|------|---------|
| Check market status | `alpaca market status` |
| List positions | `alpaca position list` |
| Submit order | `alpaca order submit --symbol BTC --qty 0.1 --side buy` |
| View account | `alpaca account get` |

## Safety

- Always use paper trading mode first
- Set daily loss limit (max 5%)
- Log all decisions for review
- Never risk more than 10% of portfolio in single trade