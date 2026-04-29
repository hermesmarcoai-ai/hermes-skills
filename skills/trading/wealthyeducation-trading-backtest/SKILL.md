---
name: wealthyeducation-trading-backtest
description: Massive crypto trading backtest framework — scrape WealthyEducation course content, build knowledge base, then run 6,144+ strategy/coin/timeframe/leva combinations to find the most profitable setup. Applied to Udemy, The Better Trader, and WealthyEducation.
category: trading
---

# WealthyEducation Trading Backtest Framework

## Workflow
1. **Scrape course content** → BeautifulSoup + Firefox session → all lectures/text
2. **Build knowledge base** → save to `~/.hermes/wealthyeducation/knowledge/`
3. **Run massive backtest** → vectorized numpy/pandas, 6,144+ combinations
4. **Output winner** → best strategy/coin/timeframe/leva combination

## Best Result Found (April 2026)
- **Strategy**: S6_Stoch_Reversal (Stochastic Reversal)
- **Timeframe**: 4H
- **Leva**: 10x
- **TP**: TP3:5 (3x and 5x risk)
- **Best Coin**: ADA (+2.842% avg return, 80% WR)
- **2nd**: SOL (+2.504%, 56% WR)
- **3rd**: ETH (+1.669%, 67% WR)

## Key Metrics
| Metric | Value |
|---|---|
| Total combinations tested | 6,144 |
| Best avg return | +1.081% (Stoch_Reversal, 4H) |
| Best win rate | 88.1% conditions profitable |
| Drawdown (best) | 1.5% |
| Worst performer | BTC (strategy doesn't work well on BTC) |

## Insights
- **4H timeframe wins** over 15m, 1h, 1D
- **ADA and SOL** are best coins for this strategy
- **10x leverage** = +165% avg vs 2x = +12%
- **Altcoins > BTC** for this strategy type
- **Stoch_Reversal** = 88% success rate across 512 tests

## Backtest Parameters
```python
COINS = ['ADA', 'SOL', 'ETH', 'AVAX', 'DOGE', 'XRP', 'BNB', 'BTC']
TIMEFRAMES = ['15m', '1h', '4h', '1D']
LEVERAGE = [2, 3, 5, 10]
STRATEGIES = [
    'EMA_Cross', 'RSI_Reversal', 'BB_Squeeze', 'MACD_Cross',
    'Stoch_Reversal', 'Volume_Spike', 'SwingLow', 'EMA_Pullback'
]
TP_COMBOS = [
    ('TP1:2', 1, 2), ('TP1:3', 1, 3), ('TP2:3', 2, 3),
    ('TP2:5', 2, 5), ('TP3:5', 3, 5), ('TP3:10', 3, 10)
]
```

## Commands
```bash
# Run the full backtest
cd ~/.hermes/wealthyeducation && python3 backtest_runner.py

# Output JSON for analysis
python3 backtest_runner.py --json | jq '.results | sort_by(.avg_return) | reverse'
```
