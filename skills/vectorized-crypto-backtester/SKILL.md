---
name: vectorized-crypto-backtester
description: Build fast crypto backtesters using vectorized numpy + pandas. Solves slow Python loops over OHLCV candles.
tags: [trading, python, backtesting, pandas, numpy, ccxt, crypto]
category: trading
created: 2026-04-27
---

# Vectorized Crypto Backtester

## Problem
Backtesting OHLCV data with pure Python loops is ~1000x too slow. A single strategy over 4000 candles can take 10+ minutes.

## Solution: Pre-compute + Numpy + Boolean Masks

### Architecture

```python
# 1. PRE-COMPUTE all indicators once per dataset
def prep(df):
    df = df.copy()
    df['rsi'] = rsi(df.close, 14)
    df['atr'] = atr(df.high, df.low, df.close, 14)
    df['vol_ma'] = df.vol.rolling(20).mean()
    df['vol_ratio'] = df.vol / df.vol_ma
    df['ema9'] = ema(df.close, 9)
    df['ema21'] = ema(df.close, 21)
    df['ema50'] = ema(df.close, 50)
    df['trend_up'] = (df.close > df.ema21) & (df.ema21 > df.ema50)
    return df

# 2. VECTORIZED signal generation — creates boolean mask columns
def sig_rsi_bounce_40_60(df):
    df = df.copy()
    df['long'] = (df.rsi_shift < 40) & (df.rsi >= 40) & (df.rsi < 55) & df.trend_up & (df.vol_ratio > 0.9)
    df['short'] = (df.rsi_shift > 60) & (df.rsi <= 60) & (df.rsi > 45) & df.trend_dn & (df.vol_ratio > 0.9)
    return df

# 3. NUMPY arrays for fast backtest inner loop
open_arr = df.open.values    # numpy array
high_arr = df.high.values
low_arr = df.low.values
close_arr = df.close.values
atr_arr = df.atr.values
long_mask = df['long'].values   # boolean mask
short_mask = df['short'].values
```

### Pandas API Warning

**Newer pandas (>=2.0?) requires keyword for `concat`:**
```python
# WRONG (deprecated):
pd.concat([a, b, c], 1).max(1)

# CORRECT:
pd.concat([a, b, c], axis=1).max(axis=1)
```

This caused silent errors in backtester v3 — always test with `pd.concat(..., axis=1)`.

### Inner Loop Pattern (still per-trade but minimal Python overhead)

```python
entry_idx = np.where(entries)[0]  # all entry signal indices at once
for idx in entry_idx:
    if idx < 25 or idx >= n-2: continue
    atr_val = atr_vals[idx]
    if np.isnan(atr_val) or atr_val == 0: continue
    
    pos = 'long' if long_mask[idx] else 'short'
    entry_p = open_arr[idx+1] * (1+slip) if pos=='long' else open_arr[idx+1] * (1-slip)
    sl_dist = atr_val * sl_atr
    
    for j in range(idx+1, min(idx+61, n)):
        # check SL/TP against numpy arrays (fast)
        ...
```

### Key Rules for Speed

1. **Never loop over all candles** for signal generation — use vectorized pandas boolean ops
2. **Only loop over entry signals** — `np.where(signal_mask)[0]` gives indices
3. **Use numpy arrays** not pandas Series inside the inner loop
4. **Limit max hold** to 60 candles to avoid unlimited loops
5. **Start with a tiny grid** (2 syms × 2 TFs × 8 sigs × 8 exits = 224 configs) and expand only after verifying it runs in <5 min

## Common Bugs & Pitfalls (v1→v4 lessons)

### Bug 1: Partial TPs counted as separate trades → WR inflated to 100%
**Symptom:** Win rate shows 100% across thousands of configs. `avg_loss = 0`.
**Cause:** Each partial TP exit was appended to `trades_pnl` as a separate trade, so a single position hitting 3 partial TPs counted as 3 wins with 0 losses.
**Fix:** Track ONE trade per position entry. Record full PnL only at position close (SL hit, all TP hit, or max bars expired).

### Bug 2: ATR PnL compounded as direct % of capital → ROI = 10^58
**Symptom:** ROI values like `+661215189807537...%` with Sharpe in the millions.
**Cause:** `avg_win=400` means "400 ATR units of profit". Code did `roi *= (1 + 400 * 0.01)` = 5× per trade. With 4000 trades: (5)^4000 = astronomical. The PnL was in ATR units, not % of capital.
**THE CORRECT FORMULA:**

The key insight: if you risk exactly `RISK_PCT` (e.g., 1%) of capital per trade, then:
```
position_size_units = RISK_PCT / SL_ATR   (in ATR terms)

Win%  = TP_atr × RISK_PCT  (e.g., TP=2, RISK=1% → 2% per win)
Loss% = -SL_atr × RISK_PCT (e.g., SL=2, RISK=1% → -2% per loss)
```
A position sizing of 1% risk / 2 ATR stop = 0.5 units. A 2 ATR win on 0.5 units = 1 ATR total = 1% of capital. NOT 100%.

**Example:** RISK_PCT=0.01, SL_ATR=2.0, TP_ATR=2.0:
- `actual_pos_size = 0.01 / 2.0 = 0.005` (position units)
- Win: `pnl_pct = 2.0 × 0.01 × 100 = 2.0%` ✅ CORRECT
- Loss: `pnl_pct = -2.0 × 0.01 × 100 = -2.0%` ✅ CORRECT

NOT `pnl_atr × pos_size × 100` where `pos_size = RISK_PCT / SL_ATR` → with sl_atr=1.0 gives `pos_size = 0.01/1 = 0.01`, so `1 ATR win × 0.01 × 100 = 100%` per trade ❌

### Bug 5: Sharpe ratio calculated per-bar instead of per-trade
**Symptom:** Sharpe = 30-50 (impossible for trading strategies).
**Cause:** Per-bar returns (24 bars/day for 1h) are tiny and compounding them gives absurd Sharpe values.
**Fix:** Calculate returns only at trade close (not per bar). Annualize with `sqrt(252 * avg_trades_per_day)`. For 1-2 trades per day on 4H: `sqrt(252 * 1.5) ≈ 19.4` — still high, but the real issue was per-bar computation.

### Bug 3: Distant TPs create phantom edges → 100% WR
**Symptom:** Wide TP (e.g., 400 ATR) + tight signal = almost every signal catches a spike and exits via TP.
**Cause:** A TP at 400× stop distance will almost always be hit eventually because the signal catches micro-movements that don't correspond to real edge.
**Fix:** Cap TP at realistic multiples of stop: `TP_max = 3.0 * SL_ATR`. In crypto, no legitimate strategy has a 100:1 reward-risk ratio.

### Bug 4: Only 1000 candles downloaded (default Binance limit)
**Symptom:** Backtest only covers ~40 days instead of 2 years.
**Fix:** Use `fetch_data()` with pagination loop, fetching 2000 candles per request until `since` reaches END date.

## Realistic ROI Expectations
- Genuinely good strategy: 50-200% annualized, Sharpe 1.5-3.0
- Legendary strategy (e.g., RSI divergence on BTC 2017-2021): 300-500% annualized, Sharpe 2-4
- Anything with Sharpe > 10 or ROI > 1000% in 2 years is almost certainly a backtest bug
- If max drawdown is always exactly -3%, the DD calculation is broken
- If all configs show >95% WR, the signal or exit logic is wrong

### Example: Full Pipeline

```python
import ccxt, pandas as pd, numpy as np
from datetime import datetime, timedelta

def fetch(symbol, tf, days=730):
    ex = ccxt.binance()
    data = []
    since = ex.parse8601(f"{(datetime.now()-timedelta(days=days)):%Y-%m-%dT00:00:00Z}")
    while True:
        try:
            d = ex.fetch_ohlcv(symbol, tf, since=since, limit=1000)
            if not d: break
            data.extend(d)
            since = d[-1][0] + 1
            if len(d) < 1000: break
        except: break
    df = pd.DataFrame(data, columns='ts open high low close vol'.split())
    df['ts'] = pd.to_datetime(df['ts'], unit='ms').dt.tz_localize(None)
    df.set_index('ts', inplace=True)
    df = df[~df.index.duplicated(keep='first')].sort_index()
    return df

# Indicators
def ema(s, n): return s.ewm(span=n, adjust=False).mean()
def rsi(s, n=14):
    d = s.diff()
    g = d.where(d>0,0).rolling(n).mean()
    l = (-d.where(d<0,0)).rolling(n).mean()
    return 100-(100/(1+g/l.replace(0,np.inf)))
def atr(h,l,c,n=14):
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()
```

## Verified Signal Strategies (Top Performers)

From HyperPerfect v5 backtest (224+ configs, BTC 4H+1D) + v4 comprehensive grid (73K configs, 9 assets × 6 TFs):

### 🏆 TOP TIER — Most Consistent (lowest drawdown, most appearances in top 25)
| Strategy | Sym | TF | WR | Sharpe | ROI | DD | Trades |
|----------|-----|----|-----|--------|-----|-----|--------|
| **rsi_vol_50** LONG | BTC | 4h | 48.3% avg | varies | varies | **20.6%** | many |
| rsi_t40_60 LONG | BTC | 4h | 45.9% | — | **+320.3%** | -59.1% | — |
| rsi_t46_54 LONG | BTC | 4h | 47.7% avg | — | +59.3% avg | **-28.6%** | — |

### ✅ RECOMMENDED FOR REAL TRADING — Best Risk-Adjusted Balance
**rsi_t46_54** (RSI threshold 46-54 band, volume confirmation):
- WR: ~47.7% average | ROI: +59.3% | DD: -28.6%
- Works well on BTC 4H with SL=2×ATR, TP=(1,2,4)×SL, trail after TP2

### 📊 BEST RISK-REWARD
**obv_confirm** (OBV confirmation strategy):
- WR: 47.5% | ROI: +37.4% | DD: -50.9%

### ⚠️ HIGH ROI BUT HIGH DD
**rsi_t40_60** (wider 40-60 RSI band):
- ROI: +320.3% | WR: 45.9% | DD: -59.1%
- Only use with strict position sizing

### RSI Band Grid (from comprehensive v4 backtest)
- **30_70**: Extreme oversold/overbought — works on altcoins (ADA, DOT, LINK) with high WR but low trade count
- **35_65**: Strong mean-reversion on alts, BTC — most robust across assets
- **40_60**: Classic range-bound — highest trade count on BTC, moderate DD
- **45_55**: Tightest band — lowest trade count but best selection
- **46_54**: Balanced — best risk-adjusted on BTC
- **48_52**: Very tight — fewest trades but highest per-trade edge
- **50_60**: Trend-following bias — long works on BTC, short on alts

### Key Insight: BTC DOMINATES other assets for mean-reversion RSI strategies
All other assets (ETH, SOL, BNB, LINK) significantly underperform BTC on these strategies.

### Verified Parameters
- **RSI threshold bands**: 46-54 (tight balanced) > 40-60 (wide high-reward) > 45-55 (previous best)
- **Volume filter**: vol_ratio > 0.9 confirms entries; rsi_vol_50 with tighter vol filtering is most consistent
- **SL**: 2×ATR is standard; 1.5×ATR for tighter strategies
- **TP**: (1×SL, 2×SL, 4×SL) with tranches 50%/35%/15% — **cap TP at 3× SL maximum** to avoid phantom edges
- **Trail**: activate after TP2 hit → move SL to break-even
- **Max hold**: 60 candles

## Exit Strategy Template

```python
# TP tranches: TP1=50%, TP2=35%, TP3=15% of position
# After TP2 hit → move SL to break-even
# Max hold: 60 candles (10 days on 4H, 60 days on 1D)
```
