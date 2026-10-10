"""Sentiment analysis from news sources."""

from typing import Dict

class SentimentAnalyzer:
    def score(self, headlines: List[str] = None) -> Dict:
        return {"sentiment_bias": 0.0, "headlines": headlines or []}
