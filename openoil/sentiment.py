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

OIL_WORDS = ("oil", "crude", "wti", "brent", "opec", "petroleum", "refiner", "hormuz", "barrel", "inventor")
UA = {"User-Agent": "OpenOil/1.0 (research; oil desk)"}


def _clean(title: str) -> str:
    text = re.sub(r"<[^>]+>", "", title or "")
    amp = "&" + "amp;"
    quot = "&" + "quot;"
    text = text.replace(amp, "&").replace("&#39;", "'").replace(quot, '"')
    return text.strip()


def _oilish(title: str) -> bool:
    low = title.lower()
    return any(word in low for word in OIL_WORDS)


def _ff_number(value) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "").replace("%", "")
    if text.endswith(("M", "m", "K", "k")):
        text = text[:-1]
    try:
        return float(text)
    except ValueError:
        return None


def _calendar() -> List[Dict]:
    try:
        response = httpx.get("https://nfs.faireconomy.media/ff_calendar_thisweek.json", headers=UA, timeout=8)
        if response.status_code != 200:
            return []
        rows = response.json()
    except Exception:
        return []
    kept = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "")
        country = str(row.get("country") or "")
        impact = str(row.get("impact") or "")
        oil = _oilish(title)
        macro = country == "USD" and impact == "High"
        if not oil and not macro:
            continue
        kept.append({
            "title": title,
            "country": country,
            "impact": impact,
            "date": row.get("date"),
            "forecast": row.get("forecast") or "",
            "previous": row.get("previous") or "",
            "oil": oil,
        })
    return kept[:12]


def _inventory_bias(events: List[Dict]) -> Dict:
    for event in events:
        if "crude" not in event["title"].lower() and "inventor" not in event["title"].lower():
            continue
        forecast = _ff_number(event.get("forecast"))
        previous = _ff_number(event.get("previous"))
        bias = 0.0
        if forecast is not None and previous is not None:
            bias = max(-1.0, min(1.0, (previous - forecast) / 5))
        return {"bias": round(bias, 3), "event": event, "forecast": event.get("forecast"), "previous": event.get("previous")}
    return {"bias": 0.0}


class SentimentAnalyzer:
    def __init__(self):
        self.last_score = 0.0
        self.last_update = 0

    def score_headlines(self, headlines: List[str]) -> Dict:
        if not headlines:
            return {"sentiment_bias": 0.0, "details": {}}
        score = 0.0
        trump_hits = []
        pos = 0
        neg = 0
        for h in headlines:
            hl = h.lower()
            p = sum(1 for w in POSITIVE if w in hl)
            n = sum(1 for w in NEGATIVE if w in hl)
            pos += p
            neg += n
            weight = 1.5 if any(w in hl for w in TRUMP_IRAN) else 1.0
            score += (p - n) * weight
            if any(w in hl for w in TRUMP_IRAN):
                trump_hits.append(h[:140])
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
        headlines = []
        sources = []
        feeds = [
            ("oilprice", "https://oilprice.com/rss/main"),
            ("google-news", "https://news.google.com/rss/search?q=crude+oil+OR+WTI+OR+OPEC+OR+EIA+inventories&hl=en-US&gl=US&ceid=US:en"),
            ("rigzone", "https://www.rigzone.com/news/rss/rigzone_latest.aspx"),
        ]
        for name, url in feeds:
            try:
                response = httpx.get(url, headers=UA, timeout=8, follow_redirects=True)
                if response.status_code != 200:
                    continue
                titles = [_clean(item) for item in re.findall(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", response.text, re.I | re.S)]
                oil = [title for title in titles if _oilish(title) and "rss" not in title.lower()]
                if oil:
                    headlines.extend(oil[:6])
                    sources.append(name)
            except Exception:
                continue
        seen = []
        for title in headlines:
            if title not in seen:
                seen.append(title)
        calendar = _calendar()
        if calendar:
            sources.append("forexfactory")
        scored = self.score_headlines(seen)
        scored["sources"] = sources
        scored["headlines"] = seen[:16]
        scored["calendar"] = calendar
        scored["eia"] = _inventory_bias(calendar)
        scored["updated"] = time.time()
        return scored
