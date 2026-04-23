---
name: crypto-portfolio-monitoring
description: Monitor cryptocurrency portfolio across exchanges — tracks positions, monitors prices, alerts on threshold breaches, and reports P&L.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [crypto, portfolio, monitoring, trading, defi]
    category: devops
---

# Crypto Portfolio Monitoring

Monitor cryptocurrency holdings across exchanges and DeFi positions. Tracks prices, alerts on threshold breaches, and reports P&L.

## When to Use

- "Show my crypto portfolio"
- "Alert me if SOL drops below $100"
- "What's my P&L this week?"
- "Monitor my DeFi positions overnight"

## Supported Exchanges/Wallets

- Binance (via API)
- Bybit (via API)
- Solana wallets (via RPC)
- Jupiter DCA orders
- WunderTrading positions (via MCP)

## Setup

```bash
# Store API keys securely
export BINANCE_API_KEY=xxx
export BINANCE_SECRET=xxx
export BYBIT_API_KEY=xxx
export BYBIT_SECRET=xxx

# Solana wallet (base58 encoded private key - use env var, never hardcode)
export SOLANA_WALLET_PRIVATE_KEY=xxx
```

## Usage

### Portfolio overview

```
User: "Show my crypto portfolio"
→ Query all connected exchanges/wallets
→ Display:
  EXCHANGES:
  Binance:
    SOL:     150 SOL    @ $120    = $18,000
    BTC:     0.5 BTC    @ $65k    = $32,500
    USDC:    2,000             = $2,000
    ─────────────────────────────────────
    Total:  $52,500

  Solana:
    Wallet:  12.5 SOL  @ $120    = $1,500
    Jupiter DCA: 3/30 days complete

  TOTAL PORTFOLIO: ~$54,000

  24h CHANGE: -2.3% (-$1,270)
  7d CHANGE:  +5.1% (+$2,610)
```

### Set price alert

```
User: "Alert me if SOL drops below $100"
→ Register alert in memory
→ Check price every 15 min via cron
→ When triggered, send Telegram alert
```

### P&L Report

```
User: "Give me a P&L report for April"
→ Pull historical balances
→ Calculate:
  Opening: $48,000
  Deposits: +$3,000
  Withdrawals: -$1,500
  P&L: +$4,500 (9.4%)
  Closing: $54,000
```

## Cron Integration

```bash
# Price monitoring every 15 minutes
hermes cron create \
  --name "Crypto price monitor" \
  --prompt "Check crypto prices, alert on threshold breaches" \
  --schedule "*/15 * * * *"

# Portfolio update every hour
hermes cron create \
  --name "Portfolio update" \
  --prompt "Update portfolio balances, log to Obsidian" \
  --schedule "0 * * * *"

# Daily P&L digest at 20:00
hermes cron create \
  --name "Daily crypto digest" \
  --prompt "Generate daily P&L digest and send to Telegram" \
  --schedule "0 20 * * *"
```

## Alert Thresholds

```yaml
alerts:
  price_drop:
    threshold: -10%  # Alert if drop > 10% in 24h
    coins: [SOL, BTC, ETH]
  volume_spike:
    threshold: 3x average
  whale_movement:
    enabled: true
    min_size: $100k
```
