"""
OpenOil Real-Time Order Flow Analysis
Computes CVD, OFI, aggressor classification, and book imbalance from MCP ticks + DOM.
"""

from typing import Dict, List, Optional
from collections import deque
import time

class OrderFlowAnalyzer:
    def __init__(self, window: int = 50):
        self.window = window
        self.tick_buffer = deque(maxlen=window)
        self.cvd = 0.0
        self.last_price = None

    def process_tick(self, tick: Dict):
        """Classify aggressor and update CVD from a single tick."""
        if not tick or not tick.get("last"):
            return
        price = float(tick["last"])
        vol = float(tick.get("volume", 1))
        bid = float(tick.get("bid", price))
        ask = float(tick.get("ask", price))

        # Simple tick rule / quote classification
        if price >= ask:
            side = 1  # buy aggressor
        elif price <= bid:
            side = -1  # sell aggressor
        else:
            side = 1 if self.last_price and price > self.last_price else -1 if self.last_price and price < self.last_price else 0

        self.cvd += side * vol
        self.tick_buffer.append({
            "price": price,
            "volume": vol,
            "side": side,
            "time": tick.get("time", time.time())
        })
        self.last_price = price

    def process_dom(self, dom: Dict) -> Dict:
        """Compute book imbalance and depth metrics."""
        if not dom or not dom.get("available"):
            return {"book_imbalance": None}
        bids = dom.get("bids", [])
        asks = dom.get("asks", [])
        bid_vol = sum(float(b.get("volume", 0)) for b in bids)
        ask_vol = sum(float(a.get("volume", 0)) for a in asks)
        total = bid_vol + ask_vol
        imbalance = (bid_vol - ask_vol) / total if total > 0 else 0
        return {
            "book_imbalance": round(imbalance, 3),
            "bid_depth": round(bid_vol, 1),
            "ask_depth": round(ask_vol, 1),
            "levels": len(bids)
        }

    def snapshot(self, symbol: str = "USOIL") -> Dict:
        """Current order-flow state."""
        recent_sides = [t["side"] for t in list(self.tick_buffer)[-20:]]
        buy_ratio = sum(1 for s in recent_sides if s > 0) / max(1, len(recent_sides))
        return {
            "cvd": round(self.cvd, 1),
            "recent_buy_ratio": round(buy_ratio, 2),
            "ticks_in_window": len(self.tick_buffer),
            "last_price": self.last_price,
            "timestamp": time.time()
        }

    def reset(self):
        self.tick_buffer.clear()
        self.cvd = 0.0
        self.last_price = None
