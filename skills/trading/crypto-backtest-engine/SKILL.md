---
name: crypto-backtest-engine
description: Realistic vectorized crypto backtest framework — avoids the critical PnL-in-ATR bug that inflates WR/ROI to impossible values
triggers:
  - run crypto backtest
  - backtest trading strategies
  - crypto strategy validation
  - backtest WR=100% ROI=infinite bug
---

# Crypto Backtest Engine — Realistic Framework

## Context
Backtesting crypto strategies requires careful handling of:
1. Position sizing relative to stop loss (not TP)
2. PnL expressed as % of capital, not ATR units
3. One trade = one position exit (not per partial TP)
4. Realistic benchmarks (WR < 70%, Sharpe < 10, ROI < 500%)

## The Critical Bug: P&L in ATR Units → Compounded as %

**WRONG (causes WR=100%, ROI=10^58):**
```python
# Every ATR unit treated as 100% of capital
pnls_pct = pnls_atr * actual_pos_size * 100
# With sl_atr=1.0, RISK_PCT=1%: actual_pos_size=1.0
# → 1 ATR win = 100% per trade → explodes with compounding
```

**CORRECT:**
```python
# PnL = ATR distance × risk_pct (as % of capital)
RISK_PCT = 0.01  # 1% per trade
# Win:  TP_atr × RISK_PCT = 2.0 × 0.01 = +2% of capital
# Loss: -SL_atr × RISK_PCT = -1.5 × 0.01 = -1.5% of capital
win_pct  =  tp_atr * RISK_PCT * 100   # e.g. +2%
loss_pct = -sl_atr * RISK_PCT * 100   # e.g. -1.5%
```

## Position Sizing Formula
```python
# Position size = risk_amount / stop_distance (NOT TP distance)
# This prevents overestimating risk when TP >> SL
pos_size = RISK_PCT / sl_atr  # gives units of capital per ATR
```

## One Trade = One Position Exit (not per partial TP)
- Partial TPs reduce position size, they do NOT create new trades
- Count ONE trade when position is fully closed (by SL, TP full, or timeout)
- This prevents WR inflation from partial exits

## Partial TP Implementation
```python
# When TP1 hits: close 50% of position, stay in trade
# When TP2 hits: close remaining 50%, exit trade
# PnL = avg TP level × RISK_PCT × 100
# Count as ONE trade at final exit
```

## TP Cap
- Max TP = 3× stop ATR (prevents phantom edges from distant TPs catching noise)
- TP beyond 3:1 reward:risk is unrealistic in live trading

## Expected Realistic Ranges (crypto, 2024-2026)
| Metric | Realistic | Suspicious | Overfitting |
|---------|-----------|------------|-------------|
| Win Rate | 45-65% | 70-85% | 85-100% |
| Sharpe | 0.3-3.0 | 5-15 | 15+ |
| ROI (2yr) | -30% to +200% | 300-1000% | 1000%+ |
| Max Drawdown | 10-40% | 5-10% | 1-3% |
| R:R | 0.8-2.0 | 2.0-3.0 | 3.0+ |

## Run the Backtest
```bash
cd /home/Obsidian-Vault/Trading
# Rebuild venv if needed
python3 -m venv /tmp/trading_env
/tmp/trading_env/bin/pip install ccxt pandas numpy scipy -q
# Launch
/tmp/trading_env/bin/python backtest_final.py >> backtest_v5.log 2>&1 &
# Monitor
tail -f backtest_v5.log
```

## Files
- `/home/Obsidian-Vault/Trading/backtest_final.py` — v5 realistic backtest (9 assets × 6 TFs × 48 strategies)
- `/home/Obsidian-Vault/Trading/ultimate_v5_results_*.json` — results
- `/home/Obsidian-Vault/Trading/paper_trader.py` — live multi-strategy paper trader
- `/home/Obsidian-Vault/Trading/bh_compare.py` — buy & hold comparison script
