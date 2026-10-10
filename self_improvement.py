"""
OpenOil Self-Improvement Loop
Tracks signal outcomes, attributes performance, and suggests weight adjustments.
"""

import json
import time
from typing import Dict, List
import os

PERF_FILE = os.getenv("PERF_FILE", "openoil_performance.json")

class SelfImprovement:
    def __init__(self):
        self.records: List[Dict] = []
        self.load()

    def load(self):
        if os.path.exists(PERF_FILE):
            try:
                with open(PERF_FILE) as f:
                    self.records = json.load(f)
            except Exception:
                self.records = []

    def save(self):
        try:
            with open(PERF_FILE, "w") as f:
                json.dump(self.records[-500:], f, default=str)  # keep last 500
        except Exception:
            pass

    def record_signal(self, signal: Dict, analysis: Dict, multi_agent: Dict):
        rec = {
            "ts": time.time(),
            "signal": signal.get("action"),
            "entry": signal.get("entry"),
            "sl": signal.get("sl"),
            "tp": signal.get("tp"),
            "bias": analysis.get("overall_bias"),
            "agent_bias": multi_agent.get("synthesized_bias"),
            "outcome": None,  # filled later
            "pnl": None
        }
        self.records.append(rec)
        self.save()
        return len(self.records) - 1  # id

    def update_outcome(self, record_id: int, pnl: float, closed: bool = True):
        if 0 <= record_id < len(self.records):
            self.records[record_id]["pnl"] = pnl
            self.records[record_id]["outcome"] = "win" if pnl > 0 else "loss"
            self.records[record_id]["closed"] = closed
            self.save()

    def performance_summary(self) -> Dict:
        closed = [r for r in self.records if r.get("outcome")]
        if not closed:
            return {"trades": 0, "win_rate": 0, "avg_pnl": 0}
        wins = sum(1 for r in closed if r["outcome"] == "win")
        avg_pnl = sum(r.get("pnl", 0) for r in closed) / len(closed)
        return {
            "trades": len(closed),
            "win_rate": round(wins / len(closed), 2),
            "avg_pnl": round(avg_pnl, 2),
            "total_pnl": round(sum(r.get("pnl", 0) for r in closed), 2)
        }

    def suggest_weights(self) -> Dict:
        """Simple attribution: which agent bias correlated with wins."""
        closed = [r for r in self.records if r.get("outcome")]
        if len(closed) < 5:
            return {"note": "Need more trades for attribution", "weights": None}
        # Placeholder: return current defaults with a note
        return {
            "note": "Attribution available after more closed trades",
            "suggested": {"Technical": 0.35, "Fundamental": 0.25, "Geopolitics": 0.25, "Risk": 0.15}
        }
