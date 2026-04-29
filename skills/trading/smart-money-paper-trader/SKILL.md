---
name: smart-money-paper-trader
description: Automated crypto paper trading with Smart Money detection on WunderTrading Demo
---

# Smart Money Paper Trader

## What it does
Automated crypto paper trading on WunderTrading Demo (BINANCE_FUTURES).
Monitors 9 strategies, detects institutional order flow, executes with high-confluence signals.

## Files
- `/home/Obsidian-Vault/Trading/wunder_paper_trader_v4.py` — Production trading engine
- `/home/Obsidian-Vault/Trading/wun_states_v4/` — Per-strategy state (JSON)
- `/home/Obsidian-Vault/Trading/wunder_paper_trader_v4.log` — Run log
- `/home/Obsidian-Vault/Trading/SMART-MONEY-TRADING.md` — Full documentation

## Running
```bash
# Dry run (no execution)
python wunder_paper_trader_v4.py --once --dry-run

# Live execution
python wunder_paper_trader_v4.py --once --place

# Status
python wunder_paper_trader_v4.py --status

# Continuous loop
python wunder_paper_trader_v4.py --place
```

## Cron Job
- Job name: "Smart Money Paper Trader v4"
- Schedule: `*/5 * * * *`
- Auto-delivers results to chat
- Cron ID: `e9172c4260c8`

## Smart Money Components
1. **Order Blocks** — last candle before >=2.5 ATR directional move
2. **Fair Value Gaps** — gaps between candle bodies (N-2 high < N low = bullish FVG)
3. **Breaker Blocks** — flipped S/D zones after structure breaks
4. **Liquidity Zones** — swing HH/LL sweeps where stops cluster

## Confluence Scoring (1-7 stars, min 2 to execute)
Each factor = 1 star:
- base_indicator, rsi_oversold/overbought, high_volume, vwap_bullish/bearish
- near_support/resistance, structure_uptrend/downtrend
- near_bullish/bearish_OB, fvg_support/resistance_near
- bullish/bearish_breaker, liq_sweep_confirmed
- pattern_*, mtf_aligned

## Position Sizing
- 5 stars: $100 | 4 stars: $75 | 3 stars: $50 | 2 stars: $30

## Risk Management
- **Max concurrent positions**: 4
- **Drawdown cap**: 5% → emergency close all
- **Daily loss cap**: 3% → stop new entries
- **Volatility filter**: ATR > ATR_SMA * 2.5 → block new entries
- **Session filter**: weekends + 13-14 UTC blocked

## Discord Webhook
Set via env var: `DISCORD_WEBHOOK=https://discord.com/api/webhooks/...`
Webhooks sent for: new trades executed, emergency closes.

## WunderTrading Config
- Profile code: `4eac262f7a6a7102f54f0a53` (DemoAccount)
- Exchange: `BINANCE_FUTURES`
- 9 strategies: BTC, ETH, BNB, SOL, LINK, XRP, ADA, AVAX, DOT
