"""Order flow analysis — CVD, aggressor classification."""

from typing import Dict, List

class OrderFlowAnalyzer:
    def __init__(self):
        self.cvd = 0.0

    def update(self, ticks: List[Dict]) -> Dict:
        return {"cvd": self.cvd, "buy_ratio": 0.5, "imbalance": 0.0}
