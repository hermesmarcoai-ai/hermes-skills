---
name: backtest-vectorized-crypto
description: Framework per backtest vettorizzato di strategie crypto su Binance. Include fix per bug critici (PnL in ATR, signal generation, bytecode caching) e criteri realistici di valutazione.
trigger: "backtest crypto | trading strategy | backtest v4 | RSI grid"
---

# Crypto Backtest Vectorizzato — Framework v4

## Quando Usare
Backtest di strategie crypto su Binance con molteplici asset, timeframe e configurazioni di parametri. Usa per trovare edge reali nel trading.

## Stack
- Python 3 venv: `/tmp/trading_env/` (ccxt, pandas, numpy, scipy)
- Directory di lavoro: `/home/Obsidian-Vault/Trading/`
- File: `backtest_final.py` (v4 realistic)

## Configurazione Asset e Timeframe
```python
ASSETS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 
          'LINK/USDT', 'XRP/USDT', 'ADA/USDT', 'AVAX/USDT', 'DOT/USDT']
TIMEFRAMES = ['1h', '2h', '4h', '6h', '12h', '1d']
DATE_START = '2024-01-01'
DATE_END   = '2026-04-27'
FETCH_LIMIT = 2000  # Binance max per chiamata — per 20K candele chiama 10x
```

## ⚠️ BUG CRITICI DA EVITARE

### Bug 1: PnL in unità ATR → numeri falsissimi
**Sintomo**: WR=100%, ROI=10^58, avg_win=400 ATR
**Causa root**: avg_win in ATR units viene usato come moltiplicatore diretto nel compounding.
TP/Stop era espresso in ATR (es. tp=400, sl=2 → ratio=200:1) → risultati impossibili.
**Fix**: 
- Cap TP max = 3× distanza stop ATR
- Position sizing da SL ONLY: `position_size = risk_amount / SL_distance`
- PnL in % capitale: win = `sl_mult * risk_pct`, loss = `-sl_mult * risk_pct`

### Bug 2: Signal generation — int(s[:2]) su strategie non-RSI
**Sintomo**: `ValueError: invalid literal for int() with base 10: ''`
**Causa root**: `strat.split('_')` su `'eng_long'` → `['eng','long']` → `int('lo')` fail
**Fix**:
```python
def generate_signals(d, strat):
    s = strat.split('_')
    is_rsi_strategy = (len(s) >= 2 and len(s[1]) >= 2 and s[1][:2].isdigit())
    if is_rsi_strategy:
        lo, hi = int(s[1][:2]), int(s[1][2:])
        sig = ((d['rsi'] < lo).astype(int) * 1 + (d['rsi'] > hi).astype(int) * -1)
    else:
        sig = compute_signal(d, strat)
    return sig
```

### Bug 3: Bytecode caching
**Sintomo**: fix applicato ma errore persiste
**Fix**: `rm -rf __pycache__ *.pyc` PRIMA di ogni rilancio

### Bug 4: venv cancellato
**Sintomo**: `/tmp/trading_env/bin/python: No such file`
**Fix**: `python3 -m venv /tmp/trading_env && pip install ccxt pandas numpy scipy`

## Criteri di Valutazione REALISTICI

| Metrica | Minimo | ✅ Buono | 🌟 Eccellente |
|---------|--------|---------|--------------|
| Trades | ≥ 30 | ≥ 50 | ≥ 100 |
| Win Rate | ≥ 48% | ≥ 54% | ≥ 60% |
| Profit Factor | ≥ 1.2 | ≥ 1.5 | ≥ 2.0 |
| Avg Win/Loss | ≥ 1.0 | ≥ 1.5 | ≥ 2.0 |
| Max DD | ≤ 35% | ≤ 20% | ≤ 12% |
| Sharpe | ≥ 0.5 | ≥ 1.0 | ≥ 1.5 |

**Eliminatori**: WR=100% (overfitting), ROI>50x annuo (data snooping), <30 trades (non significativo), DD>50% (blow-up risk)

## Strategie Testate
```
RSI-based:  rsi_{lo}_{hi}  (20/80, 25/75, 30/70, 35/65, 40/60)
            rsivol_{lo}_{hi}, rsipure_{lo}_{hi}, comb_{lo}_{hi}
Momentum:   macd_long, macd_short, macd_long_short
Mean Rev:   bb_long, bb_short, bb_long_short
Pattern:    eng_long, eng_short, eng_long_short
Volume:     volspike_long, volspike_short
VWAP:       vwap_long, vwap_short
OBV:        obv_long, obv_short
Stoch:      stoch_long, stoch_short
```

## Position Sizing Corretta
```python
risk_pct = 0.01  # 1% per trade
sl_mult = abs(entry_price - stop_loss) / atr
win_pct = sl_mult * risk_pct
loss_pct = -sl_mult * risk_pct
compounding: equity *= (1 + win_pct) if win else (1 + loss_pct)
```

## Avvio e Monitoraggio
```bash
cd /home/Obsidian-Vault/Trading
rm -rf __pycache__
/tmp/trading_env/bin/python backtest_final.py >> backtest_final5.log 2>&1 &

# Monitoraggio
tail -5 backtest_final5.log
ps aux | grep backtest_final | grep -v grep
```

## Tempo Stimato
9 asset × 6 TF × ~288 cfg = ~15,552 configurazioni → ~15-20 min
