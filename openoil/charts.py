"""ASCII charts."""

from typing import List, Dict

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

class ChartGenerator:
    def multi_chart(self, wti: List[float], brent: List[float] = None) -> Dict:
        return {"wti": {"sparkline": sparkline(wti), "last": wti[-1] if wti else None}}
