"""MT5 MCP client stub."""

import os
from typing import Dict, Any

class MT5MCPClient:
    def __init__(self):
        self.endpoint = os.getenv("MT5_MCP_ENDPOINT")

    def get_rates(self, symbol: str, timeframe: str, count: int) -> Dict:
        return {"rates": []}
