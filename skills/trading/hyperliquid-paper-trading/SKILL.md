---
name: hyperliquid-paper-trading
description: Hyperliquid paper trading setup — wallet auth, testnet API, ccxt workaround
---

# Hyperliquid Paper Trading Setup

## Setup

```bash
cd ~/.hermes/scripts
~/.local/bin/uv venv hlexec --python 3.11
~/.local/bin/uv pip install hyperliquid --python hlexec/bin/python
```

Helper script: `~/.hermes/scripts/hyperliquid_paper.py`

## Authentication

Hyperliquid uses **wallet-based auth**, NOT API key/secret.
- `apiKey` and `walletAddress` = wallet address (0x...)
- Private key NOT required for read operations
- Private key only needed for trade execution

```python
import hyperliquid.ccxt as hl

exchange = hl.hyperliquid()
exchange.set_sandbox_mode(True)
exchange.apiKey = '0xYOUR_WALLET_ADDRESS'
exchange.walletAddress = '0xYOUR_WALLET_ADDRESS'
```

## Critical: ccxt Bug on Testnet

`load_markets()` **crashes** on testnet — `fetch_spot_markets` fails when some tokens have `None` base names → `TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'`.

**Workaround**: Use direct REST API requests.

## Direct API (RELIABLE)

```python
import requests

WALLET = "0xYOUR_WALLET_ADDRESS"
BASE_URL = "https://api.hyperliquid-testnet.xyz"

def info(payload: dict) -> dict:
    return requests.post(f"{BASE_URL}/info", json=payload, timeout=10).json()

# Balance
info({"type": "clearinghouseState", "user": WALLET})

# Prices (all perpetuals)
data = info({"type": "metaAndAssetCtxs"})
# data[0]['universe'] = asset list, data[1] = price contexts
```

## What Works via ccxt

- `fetch_balance()` ✅
- `create_market_buy_order()` ❌ (crashes on load_markets)
- `fetch_open_orders()` ❌ (crashes on load_markets)

## Funding Testnet

Go to https://app.hyperliquid.xyz/testnet → connect wallet → faucet/transfer USDC.
