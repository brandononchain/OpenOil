"""
Simple helper to call MT5 MCP tools.
Adapt the endpoint and payload format to your specific MCP server
(HTTP, SSE, or JSON-RPC style).
"""

import os
import httpx
from typing import Any, Dict

MCP_ENDPOINT = os.getenv("MT5_MCP_ENDPOINT", "http://localhost:8000")

class MT5MCPClient:
    def __init__(self, endpoint: str = MCP_ENDPOINT):
        self.endpoint = endpoint.rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict:
        """Generic tool call. Adjust path/payload to match your MCP server."""
        # Example for servers that expose /tools/call or similar
        payload = {"name": tool_name, "arguments": arguments}
        try:
            resp = self.client.post(f"{self.endpoint}/tools/call", json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e), "tool": tool_name}

    def get_rates(self, symbol: str, timeframe: str, count: int = 500):
        return self.call_tool("mt5_get_rates_from_pos", {
            "symbol": symbol,
            "timeframe": timeframe,
            "count": count
        })

    def get_account_info(self):
        return self.call_tool("mt5_get_account_info", {})

    def place_order(self, symbol: str, action: str, volume: float, sl: float = None, tp: float = None):
        """action: 'buy' or 'sell'"""
        return self.call_tool("mt5_place_order", {
            "symbol": symbol,
            "action": action,
            "volume": volume,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000
        })

    def get_positions(self, symbol: str = None):
        args = {"symbol": symbol} if symbol else {}
        return self.call_tool("mt5_get_positions", args)

# Usage example:
# client = MT5MCPClient()
# rates = client.get_rates("USOIL", "H1", 200)
# order = client.place_order("USOIL", "buy", 0.1, sl=88.5, tp=95.0)
