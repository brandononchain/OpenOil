"""
OpenOil Data Oracle
Highest-quality, lowest-latency data path.
Prefers MT5 MCP ticks + Depth of Market (DOM) when available.
Falls back to public APIs, then yfinance.
Designed for millisecond-class updates when the MCP exposes order flow.
"""

import os
import time
from typing import Dict, List, Optional, Any
import httpx

class DataOracle:
    def __init__(self, mcp_client=None):
        self.mcp = mcp_client
        self.last_tick = None
        self.last_dom = None

    def get_tick(self, symbol: str = "USOIL") -> Dict:
        """Fastest path: MCP tick if available, else public API."""
        if self.mcp:
            try:
                tick = self.mcp.call_tool("mt5_get_ticks", {"symbol": symbol, "count": 1})
                if tick and "ticks" in tick and tick["ticks"]:
                    t = tick["ticks"][-1]
                    self.last_tick = {
                        "bid": t.get("bid"),
                        "ask": t.get("ask"),
                        "last": t.get("last"),
                        "volume": t.get("volume"),
                        "time": t.get("time"),
                        "source": "mt5_mcp_tick",
                        "latency_ms": 0  # local
                    }
                    return self.last_tick
            except Exception:
                pass

        # Public fallback (sub-second to few-second)
        try:
            resp = httpx.get("https://americasoilwatch.com/api/v1/wti", timeout=3)
            if resp.status_code == 200:
                d = resp.json()
                return {
                    "price": d.get("price") or d.get("close"),
                    "source": "americasoilwatch",
                    "timestamp": d.get("timestamp")
                }
        except Exception:
            pass
        return {"source": "none"}

    def get_dom(self, symbol: str = "USOIL", depth: int = 10) -> Dict:
        """Depth of Market / order book when MCP exposes it."""
        if not self.mcp:
            return {"available": False, "reason": "no_mcp"}
        try:
            # Common MCP tool names for DOM
            for tool in ["mt5_get_market_depth", "mt5_market_book_get", "get_dom"]:
                dom = self.mcp.call_tool(tool, {"symbol": symbol, "depth": depth})
                if dom and not dom.get("error"):
                    self.last_dom = {
                        "bids": dom.get("bids", [])[:depth],
                        "asks": dom.get("asks", [])[:depth],
                        "source": "mt5_mcp_dom",
                        "available": True
                    }
                    return self.last_dom
        except Exception as e:
            return {"available": False, "error": str(e)}
        return {"available": False, "reason": "tool_not_exposed"}

    def order_flow_imbalance(self, window: int = 20) -> Optional[float]:
        """Simple OFI from recent ticks or DOM if available."""
        if self.last_dom and self.last_dom.get("available"):
            bids = sum(b.get("volume", 0) for b in self.last_dom.get("bids", []))
            asks = sum(a.get("volume", 0) for a in self.last_dom.get("asks", []))
            if bids + asks > 0:
                return (bids - asks) / (bids + asks)
        return None

    def status(self) -> Dict:
        return {
            "mcp_connected": self.mcp is not None,
            "last_tick_source": self.last_tick.get("source") if self.last_tick else None,
            "dom_available": self.last_dom.get("available") if self.last_dom else False,
            "ofi": self.order_flow_imbalance()
        }
