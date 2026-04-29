---
name: hyperperfect-trading-strategies
description: Top crypto trading strategies discovered via backtesting — all parameters, per-asset allocation, paper trader config, and Discord webhook setup. Load this when starting paper trading or running new backtests.
triggers: [paper trading, trading strategies, hyperperfect, crypto strategies, backtest results, best strategy]
tags: [trading, crypto, paper-trader, backtest, strategies]
created: 2026-04-28
owner: Marco
---

# HYPERPERFECT Trading Strategies — Skill

## 🎯 Risultati Backtest (v5 — 2024-01-01 to 2026-04-27)
**9 asset × 6 TF × 96 strategie = 25,623 configurazioni testate**

### Filtri applicati
- Minimo 30 trades
- Win Rate < 99% (overfitting detection)
- ROI < 1000%
- Max Drawdown > -60%

---

## 🏆 TOP STRATEGIE PER ASSET

### BTC/USDT
- **OBV_long 2h** — WR=52.2% | ROI=+76% | DD=-36% | Sharpe=2.54 | R:R=1.10

### ETH/USDT
- **MACD_div_both 1h** — WR=52.5% | ROI=+120% | DD=-44% | Sharpe=2.49 | R:R=1.08

### BNB/USDT
- **BB_rev_long 1h** — WR=55.2% | ROI=+152% | DD=-34% | Sharpe=4.10 | R:R=1.08
- **OBV_long 4h** — WR=53.6% | ROI=+66% | DD=-24% | Sharpe=4.83 | R:R=1.17

### SOL/USDT
- **OBV_both 1h** — WR=46.0% | ROI=+87% | DD=-44% | Sharpe=1.72 | R:R=1.31

### LINK/USDT
- **BB_rev_both 1h** — WR=45.3% | ROI=+80% | DD=-36% | Sharpe=2.72 | R:R=1.14

### XRP/USDT
- **Stoch_both 12h** — WR=54.8% | ROI=+30% | DD=-17% | Sharpe=6.73 | R:R=1.34

### ADA/USDT
- **Stoch_short 6h** — WR=57.1% | ROI=+45% | DD=-22% | Sharpe=5.80 | R:R=1.13

### AVAX/USDT
- **VWAP_both 1h** — WR=36.8% | ROI=+390% | DD=-35% | Sharpe=3.00 | R:R=1.14

### DOT/USDT
- **MACD_div_both 1h** — WR=53.1% | ROI=+119% | DD=-38% | Sharpe=2.64 | R:R=1.05

---

## 📊 BEST PER TIMEFRAME

| TF | Strategia | Asset | WR | Sharpe | DD | R:R |
|----|-----------|-------|-----|--------|-----|-----|
| 1h | BB_rev_long | BNB | 55% | 5.08 | -28% | 1.19 |
| 2h | OBV_long | BTC | 52% | 2.54 | -36% | 1.10 |
| 4h | OBV_long | BNB | 54% | 4.83 | -24% | 1.17 |
| 6h | Stoch_short | ADA | 57% | 5.80 | -22% | 1.13 |
| 12h | Stoch_both | XRP | 55% | 6.73 | -17% | 1.34 |
| 1d | Volspike_long | BNB | 64% | 13.49 | -6% | 1.33 |

---

## ✅ B&H Comparison (all 9 beat B&H on risk-adjusted returns)

| Asset | B&H ROI | B&H DD | Best Strategy ROI | Strategy DD | Verdict |
|-------|---------|---------|-------------------|------------|---------|
| BTC | +75% | -49% | +76% | -36% | ✅ Beats B&H |
| ETH | -2% | -64% | +120% | -44% | ✅ Beats B&H |
| BNB | +100% | -55% | +152% | -34% | ✅ Beats B&H |
| SOL | -23% | -70% | +87% | -44% | ✅ Beats B&H |
| LINK | -40% | -73% | +80% | -36% | ✅ Beats B&H |
| XRP | +122% | -66% | +99% | -52% | ✅ Less risk |
| ADA | -60% | -81% | +92% | -51% | ✅ Beats B&H |
| AVAX | -78% | -86% | +390% | -35% | ✅ Beats B&H |
| DOT | -86% | -90% | +119% | -38% | ✅ Beats B&H |

---

## 🛠 Paper Trader Config

**File:** `/home/Obsidian-Vault/Trading/paper_trader.py`
**9 strategie attive** (configurate in `STRATEGIES` list)

### Indicatori disponibili nel code
```
rsi, rsivol, rsipure, macd_cross, macd_div,
bb_sqz, bb_rev, engulf, obv, vwap, stoch
```

### Parametri standard per tutte le strategie
- SL: 2× ATR
- TP: 2× ATR  
- Partial TP: 50% at 0.5× TP, 50% at full TP
- Trailing: activa dopo partial TP (break-even)
- Max hold: 50 candele
- Fee: 0.1% per lato
- Slippage: 0.03%

### Run commands
```bash
# Check if running
ps aux | grep paper_trader | grep -v grep

# View live log
tail -20 /home/Obsidian-Vault/Trading/paper_trader_live.log

# Run one tick only
cd /home/Obsidian-Vault/Trading && /tmp/trading_env/bin/python paper_trader.py --once

# Run status
cd /home/Obsidian-Vault/Trading && /tmp/trading_env/bin/python paper_trader.py --status

# Restart (kill + start)
pkill -f paper_trader; cd /home/Obsidian-Vault/Trading && /tmp/trading_env/bin/python paper_trader.py >> paper_trader_live.log 2>&1 &
```

### Discord notifications
Edit `DISCORD_WEBHOOK_URL` in paper_trader.py, oppure:
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/XXXX/YYYY"
```

---

## 📁 Backtest Files

| File | Description |
|------|-------------|
| `/home/Obsidian-Vault/Trading/backtest_final.py` | v5 backtest engine (ultimo, realistico) |
| `/home/Obsidian-Vault/Trading/ultimate_v5_results_20260428_173440.json` | Full results (25,623 configs) |
| `/home/Obsidian-Vault/Trading/bh_compare.py` | Script confronto B&H |
| `/home/Obsidian-Vault/Trading/paper_trader.py` | Paper trader multi-strategia |

### Run backtest (if needed again)
```bash
cd /home/Obsidian-Vault/Trading && /tmp/trading_env/bin/python backtest_final.py >> backtest_v5.log 2>&1 &
```

---

## ⚠️ Critical Notes

1. **TP capped at 3× SL** — previene phantom edges da spikes che revertano subito
2. **Position sizing: 1% risk per trade** — non usa leverage
3. **Sharpe calculated from trade returns** (not per-bar) — annualizzato con sqrt(252×4)
4. **One trade per position exit** — partial TPs non contano come trades separati
5. **Backtest period**: 2024-01-01 → 2026-04-27 (in-sample per ora)

---

## 🔄 Todo / Next Steps

- [ ] Implementare real-time Discord notifications (webhook)
- [ ] Aggiungere più timeframe/parametri al grid
- [ ] Out-of-sample validation (dati 2023)
- [ ] Considerare transaction costs reali su exchange
- [ ] Best strategy per combinare più asset contemporaneamente
- [ ] Creare documento HYPERPERFECT finale con tutte le strategie
