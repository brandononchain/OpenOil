"""
OpenOil Real-Time Sentiment Analysis
Multi-source news aggregation with weighted geopolitics, supply, and demand scoring.
"""

import re
import time
from typing import Dict, List
import httpx

POSITIVE = {
    "draw", "shortage", "outage", "attack", "strike", "escalation", "sanction",
    "disruption", "hurricane", "storm", "conflict", "war", "blockade", "cut",
    "reduction", "tighter", "bullish", "surge", "spike", "inventory drop"
}
NEGATIVE = {
    "build", "surplus", "increase", "easing", "talks", "ceasefire", "deal",
    "reopen", "production rise", "export", "bearish", "glut", "oversupply",
    "inventory rise", "peace", "agreement"
}
TRUMP_IRAN = {"trump", "iran", "hormuz", "strait", "nuclear", "sanction"}

class SentimentAnalyzer:
    def __init__(self):
        self.last_score = 0.0
        self.last_update = 0

    def score_headlines(self, headlines: List[str]) -> Dict:
        if not headlines:
            return {"sentiment_bias": 0.0, "details": {}}
        score = 0.0
        trump_hits = []
        for h in headlines:
            hl = h.lower()
            pos = sum(1 for w in POSITIVE if w in hl)
            neg = sum(1 for w in NEGATIVE if w in hl)
            weight = 1.5 if any(w in hl for w in TRUMP_IRAN) else 1.0
            delta = (pos - neg) * weight
            score += delta
            if any(w in hl for w in TRUMP_IRAN):
                trump_hits.append(h[:120])
        # Normalize to [-1, 1]
        bias = max(-1.0, min(1.0, score / max(1, len(headlines) * 2)))
        self.last_score = bias
        self.last_update = time.time()
        return {
            "sentiment_bias": round(bias, 3),
            "raw_score": round(score, 2),
            "headlines_scored": len(headlines),
            "trump_iran_mentions": trump_hits[:5],
            "details": {"positive_signals": pos, "negative_signals": neg}
        }

    def fetch_realtime(self) -> Dict:
        """Pull from multiple live sources and score."""
        headlines = []
        sources = []
        # AmericasOilWatch
        try:
            r = httpx.get("https://americasoilwatch.com/api/v1/news-feed", timeout=8)
            if r.status_code == 200:
                items = r.json().get("headlines") or r.json().get("items") or []
                headlines.extend([str(i) for i in items[:8]])
                sources.append("americasoilwatch")
        except Exception:
            pass
        # OilPrice RSS
        try:
            r = httpx.get("https://oilprice.com/rss/main", timeout=8)
            if r.status_code == 200:
                titles = re.findall(r"<title>(.*?)</title>", r.text, re.I)[1:8]
                headlines.extend([t.strip() for t in titles if t.strip()])
                sources.append("oilprice")
        except Exception:
            pass
        # Rigzone
        try:
            r = httpx.get("https://www.rigzone.com/news/rss/rigzone_latest.aspx", timeout=8)
            if r.status_code == 200:
                titles = re.findall(r"<title>(.*?)</title>", r.text, re.I)[1:6]
                headlines.extend([t.strip() for t in titles if t.strip()])
                sources.append("rigzone")
        except Exception:
            pass

        scored = self.score_headlines(headlines)
        scored["sources"] = sources
        scored["headlines"] = headlines[:12]
        scored["updated"] = time.time()
        return scored
