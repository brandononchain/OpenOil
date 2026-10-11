# OpenOil Project Layout

```
OpenOil/
├── README.md
├── requirements.txt
├── Dockerfile
├── railway.toml
│
├── openoil/                # main package
│   ├── __init__.py
│   ├── main.py             # FastAPI app + entry
│   ├── agents.py
│   ├── memory_graph.py
│   ├── data_oracle.py
│   ├── ensemble.py
│   ├── risk_engine.py
│   ├── governance.py
│   ├── order_flow.py
│   ├── sentiment.py
│   ├── alt_data.py
│   ├── charts.py
│   ├── prediction_risk.py
│   └── mt5_mcp_client.py
│
├── plugins/                # community agents & connectors
│
├── docs/
│   ├── MT5_MCP_CONTRACT.md
│   └── ARCHITECTURE.md
│
├── tests/
│
└── .github/
```

## Entry Point

```bash
python -m openoil.main
# or
uvicorn openoil.main:app --host 0.0.0.0 --port 8000
```

## Design Principles

- Root stays clean (README, requirements, Docker, railway, scripts).
- All runtime code lives under `openoil/`. There is one copy of each module.
- The desk refuses to draw a price unless MT5 (or the MetaTrader market-data server) returned candles.
- `OPENOIL_LIVE` defaults off. The poll loop never sends an order.
