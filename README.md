# OpenOil

**Open-source intelligence layer for WTI crude oil markets.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/brandononchain/OpenOil)](https://github.com/brandononchain/OpenOil)

OpenOil continuously analyzes multi-timeframe technicals, EIA inventories, news sentiment, order flow, and alternative data. It synthesizes signals through multi-agent debate, applies regime-aware risk controls, and optionally routes execution to MetaTrader 5 via MCP. All material decisions can be gated by human approval and are written to an immutable audit log.

**Site:** [openoil.si](https://openoil.si) · **Source:** [github.com/brandononchain/OpenOil](https://github.com/brandononchain/OpenOil)

## Quick Start

```bash
git clone https://github.com/brandononchain/OpenOil.git
cd OpenOil
pip install -r requirements.txt
python -m openoil.main
```

Or:

```bash
uvicorn openoil.main:app --host 0.0.0.0 --port 8000
```

## Project Layout

```
OpenOil/
├── openoil/          # main package (entry: openoil.main)
├── plugins/          # community agents & connectors
├── docs/
├── tests/
├── requirements.txt
├── Dockerfile
└── railway.toml
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full layout.

## Endpoints

- `/` and `/health`
- `/dashboard`
- `/charts`
- `/regime`
- `/market`
- `/predict`
- `/risk`

## Plugin System

Drop a module in `plugins/` that implements `register_agent()` or `register_connector()`. It is auto-discovered.

## License

MIT

## Disclaimer

Research and educational use only. Not financial advice.
