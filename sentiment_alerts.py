"""
OpenOil Historical Sentiment Trends + Real-Time Alerts + Whale Liquidity
Tracks sentiment history, raises alerts on extremes, and monitors large liquidity moves.
"""

import time
import json
import os
from typing import Dict, List
from collections import deque

ALERT_FILE = os.getenv("ALERT_FILE", "openoil_alerts.jsonl")

class SentimentTrend:
    def __init__(self, max_history: int = 200):
        self.history = deque(maxlen=max_history)
        self.load()

    def load(self):
        path = "openoil_sentiment_history.json"
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                    self.history = deque(data[-self.history.maxlen:], maxlen=self.history.maxlen)
            except Exception:
                pass

    def save(self):
        try:
            with open("openoil_sentiment_history.json", "w") as f:
                json.dump(list(self.history), f)
        except Exception:
            pass

    def add(self, bias: float, source: str = "realtime"):
        entry = {"ts": time.time(), "bias": bias, "source": source}
        self.history.append(entry)
        self.save()

    def trend(self, window: int = 20) -> Dict:
        if len(self.history) < 3:
            return {"slope": 0, "avg": 0, "direction": "insufficient_data"}
        recent = list(self.history)[-window:]
        biases = [e["bias"] for e in recent]
        avg = sum(biases) / len(biases)
        if len(biases) > 1:
            slope = (biases[-1] - biases[0]) / len(biases)
        else:
            slope = 0
        direction = "rising" if slope > 0.02 else "falling" if slope < -0.02 else "stable"
        return {
            "avg": round(avg, 3),
            "slope": round(slope, 4),
            "direction": direction,
            "samples": len(recent),
            "latest": biases[-1] if biases else 0
        }

class AlertEngine:
    def __init__(self):
        self.last_alert = 0

    def check_and_alert(self, sentiment: Dict, alt: Dict, order_flow: Dict) -> List[Dict]:
        alerts = []
        bias = sentiment.get("sentiment_bias", 0)
        if abs(bias) > 0.5:
            alerts.append({
                "type": "sentiment_extreme",
                "level": "high" if abs(bias) > 0.7 else "medium",
                "message": f"Sentiment bias extreme: {bias}",
                "ts": time.time()
            })
        ais = alt.get("ais_hormuz", {})
        if ais.get("available") and ais.get("crossings_24h", 0) < 5:
            alerts.append({
                "type": "ais_disruption",
                "level": "high",
                "message": "Very low Hormuz crossings — potential supply disruption",
                "ts": time.time()
            })
        cvd = order_flow.get("cvd", 0)
        if abs(cvd) > 500:
            alerts.append({
                "type": "whale_liquidity",
                "level": "medium",
                "message": f"Large CVD move: {cvd} — potential whale flow",
                "ts": time.time()
            })
        if alerts:
            try:
                with open(ALERT_FILE, "a") as f:
                    for a in alerts:
                        f.write(json.dumps(a) + "\n")
            except Exception:
                pass
        return alerts

    def recent_alerts(self, limit: int = 20) -> List[Dict]:
        if not os.path.exists(ALERT_FILE):
            return []
        try:
            with open(ALERT_FILE) as f:
                lines = f.readlines()[-limit:]
            return [json.loads(l) for l in lines if l.strip()]
        except Exception:
            return []
