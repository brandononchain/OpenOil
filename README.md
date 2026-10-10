# OpenOil

**Open-source intelligence layer for WTI crude oil markets.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/brandononchain/OpenOil)](https://github.com/brandononchain/OpenOil)

OpenOil continuously analyzes multi-timeframe technicals, EIA inventories, news sentiment, order flow, and alternative data. It synthesizes signals through multi-agent debate, applies regime-aware risk controls, and optionally routes execution to MetaTrader 5 via MCP. All material decisions can be gated by human approval and are written to an immutable audit log.

**Site:** [openoil.si](https://openoil.si) · **Source:** [github.com/brandononchain/OpenOil](https://github.com/brandononchain/OpenOil)

## Screenshots

| Live Dashboard | Regime View |
|----------------|-------------|
| ![Dashboard](dashboard_preview.jpg) | ![Regime](regime_preview.jpg) |

## Capabilities

- Multi-timeframe technical confluence (EMA, RSI, MACD, ATR, Bollinger)
- Live EIA inventory analysis and fundamental bias
- Multi-source news and geopolitics sentiment scoring
- LLM-based causal and counterfactual reasoning
- Persistent memory graph with optional sentence-transformer embeddings
- Multi-agent debate (Technical, Fundamental, Geopolitics, Risk + plugins)
- Self-improvement loop driven by closed-position outcomes
- Data Oracle that prefers MT5 MCP ticks and depth-of-market
- Ensemble forecasting and volatility/trend regime detection
- Dynamic position sizing and risk engine
- Human-in-the-loop governance with append-only audit traces
- Real-time order-flow metrics (CVD, aggressor classification)
- Alternative data layer (AIS, COT proxy, refinery signals)
- Multi-horizon price forecasts and quantitative risk (VaR, expected shortfall)
- Live WTI / Brent / spread market data
- ASCII terminal dashboards and charts
- Plugin architecture for community agents and connectors
- Docker deployment ready for Railway or any Linux host

## Quick Start

```bash
git clone https://github.com/brandononchain/OpenOil.git
cd OpenOil
pip install -r requirements.txt
python oil_super_intelligence.py
```

Available endpoints:

- `/dashboard` — primary status view
- `/charts` — live price charts and news feed
- `/regime` — current market regime
- `/market` — WTI, Brent, and spread snapshot
- `/predict` — multi-horizon forecasts
- `/risk` — quantitative risk metrics

## Architecture

```
┌────────────────────────────┐     HTTP/MCP     ┌────────────────────┐
│ Linux host (Railway / VPS)  │◄────────────────►│ Windows VPS         │
│                             │                  │                     │
│ • Analysis & agents         │                  │ • MetaTrader 5      │
│ • Memory graph              │                  │ • MCP server        │
│ • Governance & audit        │                  │ • Order execution   │
│ • Dashboard & API           │                  │                     │
└────────────────────────────┘                  └────────────────────┘
```

The expected MCP tool contract is documented in [docs/MT5_MCP_CONTRACT.md](docs/MT5_MCP_CONTRACT.md).

## Plugin System

Place a Python module in the `plugins/` directory. Implement either `register_agent()` or `register_connector()`. The module is loaded automatically at startup and its agent participates in the multi-agent debate.

```python
def my_agent(context: dict) -> dict:
    return {
        "bias": 0.15,
        "confidence": 0.65,
        "view": "Custom signal from external data"
    }

def register_agent():
    return "my_agent", my_agent
```

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `MT5_MCP_ENDPOINT` | URL of the MT5 MCP server | — |
| `MT5_SYMBOL` | Symbol to analyze and trade | `USOIL` |
| `LLM_API_KEY` | Key for optional LLM reasoning | — |
| `EIA_API_KEY` | Key for official EIA data | — |
| `RISK_PER_TRADE` | Fraction of account risked per trade | `0.01` |
| `ACCOUNT_BALANCE` | Account size used for position sizing | `10000` |
| `MEMORY_FILE` | Path to the persistent memory graph | `openoil_memory.json` |

## Roadmap

- Richer embedding retrieval and long-term memory
- Community plugin registry
- Tick-level microstructure when MCP exposes full order book
- Paper-trading performance leaderboard
- Optional web-based dashboard
- Expanded alternative data sources

## Contributing

1. Fork the repository.
2. Add an agent or connector under `plugins/`.
3. Include tests where practical.
4. Open a pull request.

Continuous integration runs on every push via `.github/workflows/ci.yml`.

## License

Released under the MIT License.

## Disclaimer

This software is provided for research and educational purposes only. Crude oil markets are highly volatile. Always validate behavior on a demo account before any live use. Past performance is not indicative of future results. Nothing in this repository constitutes financial advice.
