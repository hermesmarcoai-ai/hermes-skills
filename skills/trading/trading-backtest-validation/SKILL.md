---
name: trading-backtest-validation
description: Lezione critica sul gap tra simulazione Monte Carlo e backtest reale su dati BTC
triggers: [backtest, trading-strategy, monte-carlo]
---

# Trading Backtest Validation — Lezione Reale

## Contesto
Backtest Monte Carlo simulato (10k trade) su strategia "Smart Money Fusion":
- Win Rate: 79.7%
- Profit Factor: 9.05

Backtest REALE su dati Binance BTCUSDT H4 (Nov 2025 – Apr 2026, 14 trades):
- Win Rate: 50.0%
- Profit Factor: 1.02
- Return: +0.3%
- Max Drawdown: 5.7%

## Lezione Appresa
**Gap enorme tra simulazione Monte Carlo e backtest reale.**

I pattern documentati in letteratura (Failure Swing, OB Reclamation, Deviation & Reclaim) hanno WR elevati solo se:
1. Implementazione ESATTA dei criteri di pattern
2. Filtro di confluenza correttamente calibrato
3. Dati storici con volatility filter adeguata

## Regola di Validazione
- Monte Carlo = ipotesi plausibile, non conferma
- Backtest reale su dati storici = validazione necessaria
- < 30 trades in backtest = sample size insufficiente
- Sempre testare su almeno 2-3 anni di dati per validare edge

## Pattern di Fallimento Identificati
1. Filtro OTE + Killzone troppo restrittivo → solo 14 trades in 6 mesi
2. Logica di detection troppo semplicistica per replicare la letteratura
3. Nessun filtro volatilità per evitare ranging markets

## Actions Required Prossimo Backtest
- Allentare filtri per aumentare sample size (>100 trades/anno)
- Aggiungere filtro volatilità (ATR o ADX)
- Testare su timeframe multipli (H1 + H4)
- Implementare logiche di pattern detection più precise
