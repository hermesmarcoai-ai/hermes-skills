---
name: jupiter-trading-setup
description: Jupiter trading infrastructure setup — configure Jupiter swap aggregator, DCA bots, and trading strategies for Solana DeFi.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [trading, jupiter, solana, defi, swap, dca]
    category: devops
---

# Jupiter Trading Setup

Configure and manage Jupiter swap aggregator, DCA bots, and trading strategies for Solana DeFi.

## When to Use

- Setting up automated DCA (dollar-cost averaging) on Solana
- Configuring Jupiter swap strategies
- Portfolio rebalancing across Solana tokens
- Monitoring Jupiter liquidity and prices

## Prerequisites

```bash
# Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
solana-keygen new
solana airdrop 2  # Test SOL for gas

# Jupiter aggregator API
# No API key needed for basic usage
```

## Setup DCA Bot

```bash
# Create a DCA order on Jupiter
# Assumes WunderTrading MCP is configured

python3 << 'EOF'
import requests

# Jupiter DCA API
JUPITER_DCA_API = "https://quote-api.jup.ag/v6/dca"

# Example: DCA $10/day into SOL
dca_order = {
    "owner": "<your_wallet>",
    "inputMint": "So11111111111111111111111111111111111111112",  # SOL
    "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "bidAmount": 10_000_000,  # 10 USDC (in microlamports)
    "bidFrequency": 86400,  # daily
}
EOF
```

## Usage Patterns

### Swap SOL for USDC

```
User: "Swap 0.5 SOL to USDC at market price"
→ Use Jupiter aggregator API
→ Find best route
→ Execute swap transaction
```

### Set up recurring DCA

```
User: "DCA $5/day into SOL"
→ Calculate DCA schedule
→ Create Jupiter DCA order
→ Monitor execution via cron
```

### Portfolio rebalance

```
User: "Rebalance to 60% SOL, 40% USDC"
→ Check current holdings
→ Calculate gap
→ Execute series of swaps via Jupiter
```

## Jupiter API Endpoints

| Endpoint | Use |
|----------|-----|
| `/v6/quote` | Get swap quote |
| `/v6/swap` | Execute swap |
| `/v6/dca` | DCA orders |
| `/v6/price` | Token price |

## Monitoring

```bash
# Check DCA status
curl "https://quote-api.jup.ag/v6/dca?owner=<wallet>"

# Cron: monitor every hour
hermes cron create \
  --name "Jupiter DCA monitor" \
  --prompt "Check Jupiter DCA orders, report any failures" \
  --schedule "0 * * * *"
```

## Tips

- Always check `slippage` setting (default 0.5%)
- Use `/v6/quote` before executing to verify price
- DCA frequency: minimum 1 hour
- Check network congestion before large swaps
