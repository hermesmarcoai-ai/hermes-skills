---
name: alpaca-trading-agent
description: |
  Autonomous crypto/stock trading agent using Alpaca API. Monitors markets,
  executes paper trades, manages portfolio.
trigger: "trading,alpaca,paper trading,crypto bot,automated trading"
---

# Alpaca Trading Agent

## Setup
```bash
pip install alpaca-trade-api --break-system-packages
```

## Environment
```
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
ALPACA_PAPER=true
```

## Commands
| Task | Command |
|------|---------|
| Market status | `alpaca market status` |
| Positions | `alpaca position list` |
| Submit order | `alpaca order submit --symbol BTC --qty 0.1 --side buy` |

## Safety
- Always paper trade first
- Max 5% daily loss
- Never >10% portfolio single trade