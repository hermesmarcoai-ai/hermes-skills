---
name: smart-money-crypto-strategy
description: Marco's institutional-grade crypto trading system — Smart Money detection (Order Blocks, FVG, Breaker Blocks, Liquidity) + confluence scoring + WunderTrading auto-execution
triggers: [crypto, trading, smart-money, order-blocks, fair-value-gap, paper-trader]
---

# Smart Money Crypto Strategy — Marco's System

## Concept & Vision
Institutional-grade crypto trading system that detects and follows smart money (order blocks, fair value gaps, breaker blocks, liquidity sweeps) using confluence scoring to filter noise and size positions accordingly. Goal: maximum ROI through high-probability institutional entries. This is Marco's primary income generation system.

## Architecture

### Signal Generation Pipeline
```
Binance API (public klines)
    ↓
Indicators (RSI, MACD, Bollinger, Stochastic, VWAP, OBV)
    ↓
Smart Money Detection
  ├── Order Blocks (institutional accumulation/distribution zones)
  ├── Fair Value Gaps (aggressive price moves leaving gaps)
  ├── Breaker Blocks (flipped S/R after structure breaks)
  └── Liquidity Zones (swing HH/LL sweep detection)
    ↓
Market Structure (HH/HL/LH/LL detection)
Candlestick Patterns (engulfing, hammer, doji, stars)
Multi-timeframe Alignment (1H + 4H confirmation)
    ↓
Confluence Scoring (1-7 stars)
Position Sizing (by star count)
SL/TP placed at S/R zones
    ↓
WunderTrading Demo Execution (via MCP)
```

## Smart Money Components

### Order Blocks (OB)
**Definition:** The last candle BEFORE a strong directional move >= 2.5 ATR.
- Bullish OB: bearish candle followed by >= 2.5 ATR bullish move → accumulation zone
- Bearish OB: bullish candle followed by >= 2.5 ATR bearish move → distribution zone

**Detection:**
```python
threshold = atr * 2.5
# Look at next 3 candles after each candle
# If body < 0 and next candles push up >= 2.5 ATR → bullish OB
# If body > 0 and next candles push down >= 2.5 ATR → bearish OB
```

**Usage:** Price returning to an OB zone is a high-probability entry.

### Fair Value Gaps (FVG)
**Definition:** Gaps between candle bodies where price moved too fast.
- Bullish FVG: candle N-2 high < candle N low (gap up between N-2 and N, N-1 is middle)
- Bearish FVG: candle N-2 low > candle N high (gap down)

**Detection:**
```python
# For i >= 2:
# Bullish: df.iloc[i-2]["high"] < df.iloc[i]["low"]
# Bearish: df.iloc[i-2]["low"] > df.iloc[i]["high"]
```

**Usage:** Price returning to fill an FVG = strong entry (market reprices).

### Breaker Blocks
**Definition:** When a previous S/R zone FLIPS POLARITY after being broken.
- Old high broken → recaptured → old resistance becomes support = bullish breaker
- Old low broken → recaptured → old support becomes resistance = bearish breaker

### Liquidity Zones
**Definition:** Areas above swing highs (stops above) and below swing lows (stops below).
- Price sweeps above recent highs = potential reversal for shorts
- Price sweeps below recent lows = potential reversal for longs

## Confluence Scoring

**Scale: 1-7 stars** — minimum 2/7 required to execute.

| Star | Factor | Description |
|------|--------|-------------|
| ⭐ | base_indicator | Primary indicator signal |
| ⭐ | rsi_oversold/overbought | RSI < 40 (long) or > 60 (short) |
| ⭐ | high_volume | Volume ratio > 1.3x MA |
| ⭐ | vwap_bullish/bearish | Price above/below VWAP |
| ⭐ | near_support/resistance | Within 2% of S/R zone |
| ⭐ | structure_uptrend/downtrend | Market structure confirms direction |
| ⭐ | near_bullish/bearish_OB | Within 1.5% of order block |
| ⭐ | fvg_support/resistance_near | Within 1% of FVG zone |
| ⭐ | bullish/bearish_breaker | Near breaker block |
| ⭐ | liq_sweep_confirmed | Liquidity sweep detected |
| ⭐ | pattern_* | Candlestick pattern match |
| ⭐ | mtf_aligned | 1H and/or 4H confirm |

## Position Sizing

| Stars | Size (USDT) |
|-------|-------------|
| 5 | $100 |
| 4 | $75 |
| 3 | $50 |
| 2 | $30 |

## Current Strategies

| Name | Symbol | TF | Direction | Indicator |
|------|--------|----|-----------|-----------|
| OBV_LONG_BTC | BTC/USDT | 2h | long | OBV |
| MACD_ETH | ETH/USDT | 1h | both | MACD divergence |
| BB_REV_BNB | BNB/USDT | 1h | long | Bollinger reversal |
| OBV_SOL | SOL/USDT | 1h | both | OBV |
| BB_REV_LINK | LINK/USDT | 1h | both | Bollinger reversal |
| STOCH_XRP | XRP/USDT | 12h | both | Stochastic |
| STOCH_ADA | ADA/USDT | 6h | short | Stochastic |
| VWAP_AVAX | AVAX/USDT | 1h | both | VWAP |
| MACD_DOT | DOT/USDT | 1h | both | MACD divergence |

## SL/TP Logic

- **Base:** SL = entry ± 2× ATR, TP = entry ∓ 2× ATR
- **Long SL:** below nearest support/OB/FVG with 0.5 ATR buffer
- **Short SL:** above nearest resistance/OB/FVG with 0.5 ATR buffer
- **TP:** midpoint between entry and nearest opposing S/R zone

## Session Filter

- Blocked: weekends, hour 13-14 UTC
- Reason: reduce noise from low-liquidity periods

## Running

```bash
# Dry run (no execution)
python wunder_paper_trader_v3.py --once --dry-run

# Live execution
python wunder_paper_trader_v3.py --once --place

# Continuous loop
python wunder_paper_trader_v3.py --place

# Status check
python wunder_paper_trader_v3.py --status
```

## Files

- `wunder_paper_trader_v3.py` — Main engine
- `wun_states_v3/` — State persistence
- `wunder_paper_trader_v3.log` — Run log
- State: `{strategy_name}.json` per strategy

## Execution Platform

- WunderTrading Demo — Binance Futures
- Profile: `4eac262f7a6a7102f54f0a53`
- Exchange: `BINANCE_FUTURES`
- MCP: `mcp_wundertrading_place_strategy_trade`

## Key Lessons

1. **Confluence > single indicator** — 2+ stars required filters low-quality trades (XRP Stoch-only blocked)
2. **MTF alignment lifts low-star signals** — 1H+4H agreement compensates for lower TF confluence
3. **OB/FVG near price = strongest signals** — institutional zones within 1-2% are best entries
4. **Liquidity sweeps precede reversals** — detecting HH/HL sweeps avoids false breakouts
5. **Size by confidence** — 5-star gets 3x the size of 2-star

## Cron Automation

- Every 5 minutes via Hermes cron job
- Delivers results to Discord
- Auto-executes via `--place`
