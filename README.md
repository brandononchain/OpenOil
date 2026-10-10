# OpenOil — Open Source ASI for Crude Oil Markets

**Domain:** openoil.si  
**Repo:** https://github.com/brandononchain/OpenOil

OpenOil is a production-oriented, open-source Artificial Super Intelligence layer for WTI crude oil. It continuously analyzes multi-timeframe technicals, fundamentals (EIA), geopolitics/news sentiment, order flow, alternative data, and generates forecasts, risk metrics, and optional MT5 execution signals.

## Features

- Multi-timeframe technical confluence (EMA, RSI, MACD, ATR, Bollinger)
- Live EIA inventory pulls + bias
- Multi-source news + geopolitics sentiment (including Trump/Iran)
- LLM reasoning + causal/counterfactual analysis
- Memory graph with hybrid retrieval
- Multi-agent debate (Technical, Fundamental, Geopolitics, Risk + Coordinator)
- Self-improvement loop with closed-position feedback and dynamic weights
- Data Oracle preferring MT5 MCP ticks/DOM
- Ensemble forecasting + regime detection
- Dynamic risk engine + human-in-the-loop governance + immutable audit log
- Real-time order flow (CVD, aggressor classification)
- Alternative data (AIS Hormuz, COT proxy, refinery signals)
- Sentiment trends + real-time alerts + whale liquidity detection
- Multi-horizon price prediction + quantitative risk (VaR, ES)
- Live WTI/Brent/spread market data
- ASCII charts and dashboards
- **Plugin architecture** for community agents and connectors
- Railway-ready Docker deployment

## Quick Start

```bash
git clone https://github.com/brandononchain/OpenOil.git
cd OpenOil
pip install -r requirements.txt
python oil_super_intelligence.py
```

- Dashboard: http://localhost:8000/dashboard
- Regime: http://localhost:8000/regime
- Charts: http://localhost:8000/charts
- Market: http://localhost:8000/market

## Plugin Architecture

Drop Python files into the `plugins/` directory. Implement `register_agent()` or `register_connector()` and they are auto-discovered at startup.

Example agent plugin:

```python
def my_agent(context: dict) -> dict:
    return {"bias": 0.2, "view": "Custom view"}

def register_agent():
    return "my_agent", my_agent
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MT5_MCP_ENDPOINT` | MT5 MCP server URL |
| `MT5_SYMBOL` | Trading symbol (USOIL, CL, etc.) |
| `LLM_API_KEY` | Optional LLM key |
| `EIA_API_KEY` | Optional official EIA key |
| `RISK_PER_TRADE` | Position risk fraction |
| `ACCOUNT_BALANCE` | Account size for sizing |

## Architecture

```
Linux host (Railway / VPS)          Windows VPS (MT5)
┌──────────────────────────┐ HTTP   ┌──────────────────┐
│ OpenOil Intelligence    │◄──────►│ MetaTrader 5     │
│ Analysis + Agents       │  MCP   │ + MCP Server     │
│ Dashboard + API         │        │ Execution        │
└──────────────────────────┘        └───────────────────┘
```

## Roadmap to True ASI

1. Persistent memory graph with vector retrieval
2. Multi-agent debate and synthesis
3. Self-improvement from closed trades
4. Causal / counterfactual reasoning
5. Tick-level microstructure when MCP exposes DOM
6. Ensemble forecasting
7. Regime-aware dynamic risk
8. Human governance + full audit traces
9. Continuous alternative data expansion
10. Community plugin ecosystem

## Contributing

1. Fork the repo
2. Add agents or connectors in `plugins/`
3. Open a PR with tests and docs
4. Follow the MIT license

## License

MIT

## Disclaimer

Educational and research software only. Oil markets are volatile. Always test on demo accounts. Past performance does not guarantee future results.
