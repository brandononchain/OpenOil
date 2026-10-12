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
        """Attribute performance and suggest dynamic agent weights."""
        closed = [r for r in self.records if r.get("outcome") and r.get("agent_bias") is not None]
        if len(closed) < 8:
            return {
                "note": "Need more closed trades for reliable attribution",
                "current": {"Technical": 0.35, "Fundamental": 0.25, "Geopolitics": 0.25, "Risk": 0.15},
                "suggested": None
            }

        wins = [r for r in closed if r["outcome"] == "win"]
        if not wins:
            return {"note": "No wins yet", "suggested": None}

        avg_win_bias = sum(abs(r.get("agent_bias", 0)) for r in wins) / len(wins)
        suggested = {
            "Technical": 0.30 + (avg_win_bias * 0.1),
            "Fundamental": 0.25,
            "Geopolitics": 0.25 + (avg_win_bias * 0.05),
            "Risk": 0.15
        }
        total = sum(suggested.values())
        suggested = {k: round(v / total, 3) for k, v in suggested.items()}
        return {
            "trades_analyzed": len(closed),
            "win_rate": round(len(wins) / len(closed), 2),
            "suggested_weights": suggested,
            "note": "Weights adjusted based on bias magnitude on winning trades"
        }

    def settle(self, price: float, hold_seconds: int = 900) -> None:
        """Score a call once price hits the stop, the target, or 15 minutes pass."""
        if not price:
            return
        now = time.time()
        changed = False
        for rec in self.records:
            if rec.get("closed"):
                continue
            entry = rec.get("entry")
            side = rec.get("signal")
            if not entry or side not in ("BUY", "SELL"):
                continue
            sl = rec.get("sl")
            tp = rec.get("tp")
            pnl = None
            if side == "BUY":
                if tp and price >= tp:
                    pnl = tp - entry
                elif sl and price <= sl:
                    pnl = sl - entry
                elif now - rec["ts"] >= hold_seconds:
                    pnl = price - entry
            else:
                if tp and price <= tp:
                    pnl = entry - tp
                elif sl and price >= sl:
                    pnl = entry - sl
                elif now - rec["ts"] >= hold_seconds:
                    pnl = entry - price
            if pnl is None:
                continue
            rec["pnl"] = round(pnl, 4)
            rec["outcome"] = "win" if pnl > 0 else "loss"
            rec["closed"] = True
            changed = True
        if changed:
            self.save()

    def get_open_records(self) -> List[Dict]:
        return [r for r in self.records if not r.get("closed")]
