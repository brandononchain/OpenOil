# OpenOil — Open Source ASI for Crude Oil Markets

**openoil.si** — Artificial Super Intelligence for WTI crude oil: multi-timeframe technicals, EIA inventories, geopolitics/news sentiment (including Trump/Iran), LLM reasoning, and MT5 execution via MCP.

## Vision
A production-grade, open-source system that continuously analyzes, reasons about, and can trade crude oil with human-level (and eventually superhuman) market understanding. Designed as the intelligence layer that pairs with any MT5 terminal.

## Current Capabilities
- Full multi-timeframe analysis (M1–W1) with EMA, RSI, MACD, ATR, Bollinger confluence
- Automatic EIA inventory pulls + week-over-week bias
- Multi-source news + refined geopolitics sentiment (Trump, Iran, Hormuz, hurricanes)
- LLM reasoning layer (narrative, adjusted bias, invalidation levels)
- Position monitoring + trailing stops
- Order execution via MT5 MCP
- ASCII-styled live dashboard (`/dashboard`) using ascii.rest components
- Full historical OHLC + tick + symbol info pulls when MCP is available
- Railway-ready Docker deployment

## Live API Data
- Public no-key endpoints from AmericasOilWatch:
  - `GET /api/v1/wti` — current WTI price
  - `GET /api/v1/us-stocks` — weekly petroleum stocks
- Integrated into analysis as primary live price source (yfinance fallback).
- New endpoint: `GET /live` returns current price + stocks.
- Optional: set `OILPRICEAPI_KEY` for OilPriceAPI (WTI/Brent futures, historical) if you want a commercial feed.

## Architecture
```
Railway / any Linux host          Windows VPS (or local)
┌─────────────────────────┐       ┌────────────────────┐
│ OpenOil Intelligence   │ HTTP  │ MetaTrader 5        │
│ (this repo)            │◄─────►│ + MCP Server        │
│ Analysis + Reasoning   │ MCP   │ (native or wrapper) │
│ Dashboard + API        │       │ Order execution     │
└─────────────────────────┘       └─────────────────────┘
```

## Quick Start
```bash
git clone https://github.com/brandononchain/OpenOil.git
cd OpenOil
pip install -r requirements.txt
export MT5_MCP_ENDPOINT=http://your-mt5-mcp:8000   # optional
export LLM_API_KEY=your_key                         # optional
python oil_super_intelligence.py
# Visit http://localhost:8000/dashboard
```

## Environment Variables
- `MT5_MCP_ENDPOINT` — MT5 MCP server URL
- `MT5_SYMBOL` — e.g. USOIL, CL, OIL.f
- `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`
- `EIA_API_KEY` — optional official EIA key
- `RISK_PER_TRADE`, `MAX_POSITIONS`, `ACCOUNT_BALANCE`

## Path to True ASI
To evolve OpenOil into a genuine artificial super intelligence for oil markets:

1. **Persistent Memory Graph** — Store every analysis, news event, EIA print, and trade outcome in a vector + graph DB. Retrieve relevant historical analogs before every decision.
2. **Multi-Agent Reasoning** — Separate agents for technicals, fundamentals, geopolitics, and risk. Debate and synthesize via a coordinator.
3. **Self-Improvement Loop** — Track signal accuracy, PnL attribution, and regime performance. Auto-tune weights and generate new features.
4. **Causal & Counterfactual Reasoning** — LLM + structured models that ask “what if Hormuz reopens tomorrow?” and update probabilities.
5. **Tick-Level Microstructure** — When MCP supports it, incorporate order-flow imbalance, depth, and high-frequency patterns.
6. **Ensemble Forecasting** — Combine statistical models, neural nets (trained on the memory graph), and LLM scenario analysis.
7. **Risk Engine with Regime Detection** — Dynamic position sizing, correlation filters (USD, gold, equities), and volatility targeting.
8. **Human-in-the-Loop Governance** — Approval queues for high-impact trades, audit logs, and explainability traces.
9. **Continuous Data Expansion** — Shipping AIS, refinery outages, satellite inventory estimates, CFTC positioning, options skew.
10. **Open Community** — Plugin architecture so others can contribute agents, data connectors, and execution adapters.

## License
MIT — Open source for the community.

## Disclaimer
Educational / research software. Oil markets are volatile. Always test on demo. Past performance does not guarantee future results.
