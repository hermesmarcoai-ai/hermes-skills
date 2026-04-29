---
name: realistic-crypto-backtester
description: Build realistic crypto strategy backtesters — avoid 3 fatal bugs that produce fake edge (WR 80%+, Sharpe 30+, ROI 10000%+. Validated across 5 iterations.
triggers:
  - building a crypto backtester
  - backtest shows unrealistic returns
  - crypto strategy backtest
  - RSI MACD Bollinger backtest
---

# Realistic Crypto Backtester — Critical Bugs & Fixes

## Overview
When building a crypto strategy backtester, 3 bugs consistently produce fake "edge" — numbers that look amazing (WR 80%+, Sharpe 30+, ROI 1000%+) but are completely false. These bugs were discovered through 5 iterations on a real backtest engine (backtest_final.py v1-v5, Apr 2026).

## The 3 Fatal Bugs

### Bug 1: Partial TPs counted as separate trades
**Symptom:** Win Rate = 70-90%+, but Profit Factor < 1.1
**Root cause:** Every partial TP hit was appended to `trades_pnl` as a separate trade, inflating trade count and WR.

```python
# WRONG — each partial TP = new trade
for j, tp in enumerate(tps):
    if not pos['tp_done'][j]:
        frac = 0.5 if j < len(tps)-1 else 1.0
        trades_pnl.append(tp_pnl * frac)  # <- partial counted as trade!
```

**Fix:** ONE trade = ONE position exit. Partial TPs reduce position size but don't create new trade entries.

```python
# CORRECT — one entry per position
if exit_reason in ('sl', 'tp', 'trail', 'timeout'):
    trade_pct_pnls.append(pnl_pct)  # single entry
```

### Bug 2: PnL in ATR units compounded as multiplier
**Symptom:** ROI = 10,000%+, Sharpe = 30-50, but WR = 50%
**Root cause:** `trades_pnl` stored PnL in ATR units (e.g., +1.5 ATR per win). Then compounded directly as if it were a multiplier.

```python
# WRONG — ATR units × position size × 100 with SL_ATR=1, RISK_PCT=0.01
actual_pos_size = RISK_PCT / SL_ATR  # = 1.0
pnls_pct = pnls * actual_pos_size * 100  # 1 ATR win = +100%!
```

**Fix:** Express PnL in % of capital BEFORE compounding:
```python
# CORRECT — win = TP_atr × RISK_PCT (as %)
win_pct = tp_atr * RISK_PCT * 100          # e.g., 2.0 × 0.01 × 100 = +2%
loss_pct = -sl_atr * RISK_PCT * 100         # e.g., -1.5 × 0.01 × 100 = -1.5%
trade_pct_pnls.append(win_pct)              # ONE entry per position
```

### Bug 3: Sharpe from per-bar returns instead of per-trade
**Symptom:** Sharpe = 20-50+, unrealistic for crypto
**Root cause:** Calculated on bar-by-bar price changes instead of trade-level returns.

```python
# WRONG — per-bar returns inflate Sharpe
shp = rets.mean() / rets.std() * np.sqrt(252 * 24)  # 24 bars/day
```

**Fix:** Sharpe from trade returns, annualized assuming ~4 trades/day:
```python
# CORRECT — Sharpe from trade returns
rets = np.diff(cum) / cum[:-1]  # trade-level returns
ann_factor = np.sqrt(252 * 4)    # ~4 trades/day average
shp = rets.mean() / rets.std() * ann_factor if rets.std() > 0 else 0
```

## Realistic Sanity Checks
After fixing all bugs, verify results are plausible:

| Metric    | Buggy      | Realistic  |
|-----------|------------|------------|
| Win Rate  | 70-100%    | 40-65%     |
| Sharpe    | 20-50+     | 0.3-3.0    |
| ROI (2yr) | 1000-10000%| -50% to +300% |
| Max DD    | 1-5%       | 10-40%     |
| R:R Ratio | 0.8-1.2    | 0.8-2.5    |

If numbers are outside "Realistic" column → still have a bug.

## Core Formula Reference
```
Position Size = RISK_PCT / SL_ATR
Win P&L (%)  = TP_ATR × RISK_PCT × 100
Loss P&L (%) = -SL_ATR × RISK_PCT × 100
Compounding  = cumprod([1 + p/100 for p in trade_pct_pnls])
Sharpe       = (mean(trade_rets) / std(trade_rets)) × √(252 × avg_trades_per_day)
```

## Filters for Valid Strategies
- Min 30 trades (statistical significance)
- Win Rate < 99% (100% = overfitting)
- ROI < 5000% (higher = likely still buggy)
- Max Drawdown > -60% (higher = blowup risk)

## Known Good Baseline
Backtest v5 on 9 crypto assets × 6 timeframes (2024-01-01 to 2026-04-27):
- Median WR: 48.3%, Median Sharpe: 0.32, Median DD: -22.2%
- Total 25,623 configs tested, 20,555 passed filters

## File Location
`/home/Obsidian-Vault/Trading/backtest_final.py` — v5 realistic backtest engine
