---
name: crypto-paper-trader
description: Build a local crypto paper trader using Binance public API for live strategy validation — no exchange API keys needed. Useful when Alpaca/WunderTrading demo accounts don't support spot crypto.
---

# Crypto Paper Trader — Live Strategy Validator

## Trigger
Use when the user wants to paper trade or live-test a crypto trading strategy but doesn't have API keys for an exchange, or the available paper trading accounts (Alpaca, WunderTrading demo) don't support the desired asset or spot trading.

## Approach: Binance Public API + Local Simulation

Binance provides OHLCV data via public REST endpoint — no API key needed for reading prices. This enables a fully functional paper trader with zero credentials.

### Step 1 — Verify Binance Public Data Access
```bash
curl -s "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=4h&limit=10"
```
If this returns candlestick data, you're good to go.

### Step 2 — Build the Paper Trader
Core components:
1. **Data fetch** — `requests.get()` to `https://api.binance.com/api/v3/klines` with symbol, interval, limit
2. **Indicators** — pandas/TA library (RSI, EMA, ATR, Bollinger, etc.)
3. **Signal detection** — boolean masks for entry conditions
4. **Position simulation** — walk-forward loop through subsequent candles simulating TP/SL/trailing
5. **State persistence** — JSON file for capital, open trades, trade history
6. **Discord webhook** — notify on entry/exit (optional, via `requests.post`)

### Step 3 — Key Binance Endpoints (No Auth)
| Purpose | URL |
|---------|-----|
| Klines/candles | `https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=4h&limit=200` |
| 24hr ticker | `https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT` |
| Order book | `https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=10` |

**Timeframe mapping:** `1m, 5m, 15m, 1h, 4h, 1d, 1w`

### Step 4 — Limitations of This Approach
- **No real orders executed** — prices are real but orders are simulated
- Cannot verify fill quality or slippage reality
- Good for: strategy validation, signal timing, expectancy confirmation
- Not a substitute for real exchange paper trading when available

## Common Blockers Encountered
| Platform | Blocker |
|----------|---------|
| Alpaca | Paper trading does NOT support crypto — only US equities/ETFs |
| WunderTrading | Demo accounts are futures-only, not spot |
| Binance Testnet | Requires separate testnet API keys from testnet.binance.vision |
| TradingView | Paper trading only for stocks/forex, not crypto |

## Files Created
- `/home/Obsidian-Vault/Trading/paper_trader.py` — RSI Trend 40-60 live trader
- Strategy: BTC/USDT 4H, RSI 40-60, EMA21>EMA50, SL 3× ATR, 3-tranche TP + trailing

## Example Discord Notify Pattern
```python
def notify(msg: str, color: int = 0x00FF00):
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not url: return
    requests.post(url, json={
        "embeds": [{
            "title": "Paper Trader Alert",
            "description": msg,
            "color": color,
            "footer": {"text": f"BTC/USDT 4H | {datetime.now().strftime('%Y-%m-%d %H:%M')}"},
        }]
    }, timeout=10)
```
