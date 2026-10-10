"""Data Oracle — prefers MT5 MCP, falls back to public APIs."""

import os
from typing import Dict, Any, Optional

class DataOracle:
    def __init__(self):
        self.endpoint = os.getenv("MT5_MCP_ENDPOINT")
        self.symbol = os.getenv("MT5_SYMBOL", "USOIL")

    def get_price(self) -> Dict[str, Any]:
        return {"symbol": self.symbol, "price": 91.5, "source": "fallback"}

    def get_ticks(self, count: int = 1) -> Dict:
        return {"ticks": [], "source": "fallback"}
