---
name: alpaca-paper-trading-crypto-myth
description: Alpaca Paper Trading does NOT support cryptocurrency — only US equities/ETFs
---

# Alpaca Paper Trading — Crypto Myth Debunked

## Key Finding

**Alpaca Paper Trading does NOT support cryptocurrency.**

Even when `crypto_status: ACTIVE` appears in the account response, the paper trading endpoint (`https://paper-api.alpaca.markets/v2`) only supports US equities and ETFs. The `crypto_status` field means the *live account profile* is crypto-enabled for potential upgrade, not that paper trading works for crypto.

## Verified Behavior
- Account info endpoint: ✅ works
- US equities/ETFs: ✅ paper trading works
- Crypto (BTC, ETH, etc.): ❌ NOT supported
- Crypto asset listing: returns US equities only (5.6MB of stock data)

## How to Confirm
```bash
curl -s "https://paper-api.alpaca.markets/v2/assets?status=active" \
  -H "APCA-API-KEY-ID: $ALPACA_KEY_ID" \
  -H "APCA-API-SECRET-KEY: $ALPACA_SECRET" \
  | python3 -c "import json,sys; [print(a['symbol'], a['class']) for a in json.load(sys.stdin) if a.get('class')=='crypto']"
# Returns: nothing — no crypto assets available
```

## Working Crypto Paper Alternatives
| Platform | Crypto Paper | Notes |
|----------|-------------|-------|
| **Binance Testnet** | ✅ All pairs | Best for crypto |
| **ccxt dry_run** | ✅ All pairs | Used in backtester |
| **Alpaca** | ❌ Crypto | US equities only |

## Current Credentials (Surface)
- Endpoint: `https://paper-api.alpaca.markets/v2`
- Key ID: `PKJTQ4OXEGBIHHRJJ7GXHK3KRC`
- Secret: (CREDENTIALS.md — never in chat)
- Status: ✅ Active for US equities/ETFs
- Buying power: ~$200k paper
