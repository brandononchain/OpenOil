# OpenOil 🛢️

**The open-source Artificial Super Intelligence for crude oil markets.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/brandononchain/OpenOil?style=social)](https://github.com/brandononchain/OpenOil)

> Analyze, predict, and optionally trade WTI crude oil with multi-agent reasoning, live data, risk governance, and full auditability. Runs on Railway or any Linux host. Connects to MetaTrader 5 via MCP.

**Website:** openoil.si · **Repo:** https://github.com/brandononchain/OpenOil

---

## Screenshots

### Live Dashboard
![OpenOil Dashboard](dashboard_preview.jpg)

### Regime View
![OpenOil Regime](regime_preview.jpg)

---

## Why OpenOil?

Most oil trading tools are either black-box signals or simple technical scripts. OpenOil is different:

- **Transparent multi-agent reasoning** — Technical, Fundamental, Geopolitics, Risk, and community plugins debate before a signal is issued.
- **Memory that improves** — Persistent graph + embeddings so the system recalls historical analogs.
- **Governed execution** — Human-in-the-loop approval queues and immutable audit logs for material trades.
- **Millisecond-preferring data** — Oracle prefers MT5 MCP ticks/DOM when available; falls back to public APIs.
- **Open and extensible** — Plugin architecture for agents and connectors. MIT licensed.

---

## Features

| Capability | Status |
|------------|--------|
| Multi-timeframe technical confluence | ✅ |
| EIA inventory pulls + bias | ✅ |
| Multi-source news + geopolitics sentiment | ✅ |
| LLM causal / counterfactual reasoning | ✅ |
| Memory graph + embeddings | ✅ |
| Multi-agent debate (with plugins) | ✅ |
| Self-improvement from closed trades | ✅ |
| Data Oracle (MT5 MCP preferred) | ✅ |
| Ensemble forecasting + regime detection | ✅ |
| Dynamic risk engine | ✅ |
| Human governance + audit traces | ✅ |
| Order flow (CVD) | ✅ |
| Alternative data (AIS, COT, refinery) | ✅ |
| Sentiment trends + alerts | ✅ |
| Multi-horizon prediction + VaR/ES | ✅ |
| Live WTI/Brent/spread | ✅ |
| ASCII charts & dashboards | ✅ |
| Plugin architecture | ✅ |
| Railway-ready Docker | ✅ |

---

## Quick Start

```bash
git clone https://github.com/brandononchain/OpenOil.git
cd OpenOil
pip install -r requirements.txt
python oil_super_intelligence.py
```

Open:
- http://localhost:8000/dashboard — main ASCII dashboard
- http://localhost:8000/charts — live charts + news
- http://localhost:8000/regime — regime view
- http://localhost:8000/market — WTI/Brent/spread snapshot

---

## Architecture

```
Linux host (Railway / VPS)          Windows VPS (MT5)
┌──────────────────────────┐ HTTP   ┌───────────────────┐
│ OpenOil Intelligence     │◄──────►│ MetaTrader 5     │
│ Analysis + Agents        │  MCP   │ + MCP Server     │
│ Dashboard + API          │        │ Execution        │
│ Memory + Governance      │        │                  │
└──────────────────────────┘        └───────────────────┘
```

See [docs/MT5_MCP_CONTRACT.md](docs/MT5_MCP_CONTRACT.md) for the exact tool contract.

---

## Plugin Architecture

Drop a `.py` file into `plugins/` that exposes `register_agent()` or `register_connector()`. It is auto-discovered and participates in the debate.

```python
def my_agent(context: dict) -> dict:
    return {"bias": 0.2, "view": "Custom view", "confidence": 0.6}

def register_agent():
    return "my_agent", my_agent
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MT5_MCP_ENDPOINT` | MT5 MCP server URL | — |
| `MT5_SYMBOL` | Trading symbol | `USOIL` |
| `LLM_API_KEY` | Optional LLM key | — |
| `EIA_API_KEY` | Optional EIA key | — |
| `RISK_PER_TRADE` | Risk fraction per trade | `0.01` |
| `ACCOUNT_BALANCE` | Account size for sizing | `10000` |
| `MEMORY_FILE` | Path to memory graph | `openoil_memory.json` |

---

## Roadmap

1. Persistent memory with richer embeddings and retrieval
2. Community plugin marketplace
3. Full tick-level microstructure when MCP exposes DOM
4. Paper-trading leaderboard
5. Web dashboard (beyond ASCII)
6. Additional alternative data sources

---

## Contributing

1. Fork the repo
2. Add an agent or connector in `plugins/`
3. Add tests
4. Open a PR

See the CI workflow in `.github/workflows/ci.yml`.

---

## License

MIT — see [LICENSE](LICENSE) if present, or the standard MIT terms.

## Disclaimer

Educational and research software only. Oil markets are volatile. Always test on demo accounts. Past performance does not guarantee future results. Not financial advice.
