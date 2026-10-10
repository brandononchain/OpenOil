# OpenOil Project Layout

```
OpenOil/
├── README.md
├── requirements.txt
├── Dockerfile
├── railway.toml
├── pyproject.toml          # optional, for packaging
│
├── openoil/                # main package
│   ├── __init__.py
│   ├── main.py             # FastAPI app + trading loop entry
│   ├── analyzer.py         # OilAnalyzer core
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
│   ├── __init__.py
│   └── example_agent.py
│
├── docs/
│   ├── MT5_MCP_CONTRACT.md
│   └── ARCHITECTURE.md
│
├── tests/
│   └── test_basic.py
│
└── .github/
    └── workflows/
        └── ci.yml
```

## Entry Point

```bash
python -m openoil.main
# or
uvicorn openoil.main:app --host 0.0.0.0 --port 8000
```

## Design Principles

- Keep the root clean.
- All runtime code lives under `openoil/`.
- Plugins stay outside the package so they can be added without touching core.
- Docs and tests are top-level.
- The FastAPI app and trading loop are started from a single module.
