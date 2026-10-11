# OpenOil

**Open-source intelligence layer for WTI crude oil markets.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/brandononchain/OpenOil)](https://github.com/brandononchain/OpenOil)

OpenOil reads MetaTrader 5 through its local MCP server, scores the real candles with a technical, fundamental, geopolitics, and risk panel, and writes every decision to an audit log. It does not invent prices. Live orders stay off unless `OPENOIL_LIVE=1`, and even then a human approval is queued before anything can be sent.

**Site:** [openoil.si](https://openoil.si) · **Source:** [github.com/brandononchain/OpenOil](https://github.com/brandononchain/OpenOil)

## Quick Start

```bash
git clone https://github.com/brandononchain/OpenOil.git
cd OpenOil
pip install -r requirements.txt
python -m openoil.main
```

On Windows without Git, download the zip of `main` and run it from the extracted folder.

## Configuration

Create a `.env` file in this folder, next to `requirements.txt`. It is gitignored.

```text
MT5_MCP_ENDPOINT=http://127.0.0.1:22346/mcp
MT5_MCP_API_KEY=terminal-key-from-the-top-box
MT5_MARKETDATA_API_KEY=mq-key-from-metatrader.com
MT5_SYMBOL=USOIL
OPENOIL_LIVE=0
```

`MT5_SYMBOL` must match the name in Market Watch. Leave `OPENOIL_LIVE` at `0`. Setting it to `1` only queues an approval. OpenOil does not send an order on its own.

The chart, account, and blotter come from the terminal. If MetaTrader is down or the symbol is wrong, the desk shows **OFFLINE** instead of a fake price. A closed market still shows the last candles. The order book is labeled **SIM BOOK** until the terminal returns real depth.

## Run on the MT5 machine

The terminal MCP server listens on `127.0.0.1` only, so OpenOil has to run on that same Windows VPS. Railway cannot see it.

```powershell
cd C:\Users\Administrator\OpenOil-main
python -m pip install -r requirements.txt
python -m openoil.main
```

Start it at boot, 90 seconds after Windows, so MetaTrader can open first:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-openoil-task.ps1 -WorkDir C:\Users\Administrator\OpenOil-main
```

## Project Layout

```
OpenOil/
├── openoil/          # the only runtime package
├── plugins/          # community agents and connectors
├── scripts/          # Windows startup task
├── docs/
├── requirements.txt
├── Dockerfile
└── railway.toml
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Endpoints

- `/` dashboard
- `/api/state` desk payload (bars, account, signals, book)
- `/mt5/snapshot` raw terminal response
- `/health`

## Plugin System

Drop a module in `plugins/` that implements `register_agent()` or `register_connector()`. It is auto-discovered.

## License

MIT

## Disclaimer

Research and educational use only. Not financial advice.
