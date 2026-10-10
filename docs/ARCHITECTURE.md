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

- Root stays clean (README, requirements, Docker, railway).
- All runtime code lives under `openoil/`.
- Plugins stay outside the package.
- Docs and tests are top-level.
- Single entry point.
