"""
OpenOil Real-Time Oil Price Charts
ASCII sparklines and simple line charts for live WTI/Brent prices.
"""

from typing import List, Dict
import math

def sparkline(values: List[float], width: int = 40) -> str:
    if not values or len(values) < 2:
        return "▁" * width
    mn, mx = min(values), max(values)
    rng = mx - mn if mx != mn else 1
    blocks = "▁▂▃▄▅▆▇█"
    out = ""
    step = max(1, len(values) // width)
    for i in range(0, len(values), step):
        v = values[i]
        idx = int((v - mn) / rng * (len(blocks) - 1))
        out += blocks[min(idx, len(blocks) - 1)]
    return out[:width]

def ascii_line_chart(values: List[float], height: int = 8, width: int = 50) -> str:
    if not values:
        return "No data"
    mn, mx = min(values), max(values)
    rng = mx - mn if mx != mn else 1
    lines = []
    for row in range(height, 0, -1):
        threshold = mn + (rng * row / height)
        line = ""
        for v in values[-width:]:
            line += "█" if v >= threshold else " "
        lines.append(line)
    return "\n".join(lines)

class ChartGenerator:
    def generate_price_chart(self, prices: List[float], label: str = "WTI") -> Dict:
        return {
            "label": label,
            "sparkline": sparkline(prices),
            "line_chart": ascii_line_chart(prices),
            "min": round(min(prices), 2) if prices else None,
            "max": round(max(prices), 2) if prices else None,
            "last": round(prices[-1], 2) if prices else None,
            "points": len(prices)
        }

    def multi_chart(self, wti: List[float], brent: List[float] = None) -> Dict:
        charts = {"wti": self.generate_price_chart(wti, "WTI")}
        if brent:
            charts["brent"] = self.generate_price_chart(brent, "Brent")
            if wti and brent and len(wti) == len(brent):
                spread = [b - w for b, w in zip(brent, wti)]
                charts["spread"] = self.generate_price_chart(spread, "Brent-WTI Spread")
        return charts
