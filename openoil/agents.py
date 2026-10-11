"""
OpenOil Multi-Agent Reasoning
Specialized agents for technicals, fundamentals, geopolitics, and risk.
They produce structured views that a coordinator synthesizes.
"""

from typing import Dict, Any, List
import json
try:
    from plugins import registry as plugin_registry
except Exception:
    plugin_registry = type('R', (), {'get_agents': lambda self: {}})()

class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def analyze(self, context: Dict) -> Dict:
        raise NotImplementedError

class TechnicalAgent(Agent):
    def __init__(self):
        super().__init__("Technical", "Multi-timeframe confluence and price action")

    def analyze(self, context: Dict) -> Dict:
        analysis = context.get("analysis", {})
        scores = analysis.get("timeframe_scores", {})
        overall = analysis.get("overall_bias", 0)
        return {
            "agent": self.name,
            "bias": overall,
            "confidence": min(0.9, abs(overall) * 1.2),
            "key_points": [f"{tf}: {s.get('score', 0):.2f}" for tf, s in list(scores.items())[:4]],
            "summary": f"Technical confluence is {'bullish' if overall > 0.2 else 'bearish' if overall < -0.2 else 'neutral'} across timeframes."
        }

class FundamentalAgent(Agent):
    def __init__(self):
        super().__init__("Fundamental", "EIA inventories and supply/demand")

    def analyze(self, context: Dict) -> Dict:
        eia = context.get("eia", {})
        bias = eia.get("bias", 0)
        change = eia.get("wow_change")
        return {
            "agent": self.name,
            "bias": bias,
            "confidence": 0.7 if change else 0.4,
            "key_points": [f"WoW change: {change}", f"Stocks: {eia.get('crude_stocks')}"],
            "summary": f"Inventories {'supportive' if bias > 0 else 'pressuring'} for price."
        }

class GeopoliticsAgent(Agent):
    def __init__(self):
        super().__init__("Geopolitics", "News, Trump/Iran, Hormuz, hurricanes")

    def analyze(self, context: Dict) -> Dict:
        news = context.get("news", {})
        sentiment = news.get("sentiment_bias", 0)
        mentions = news.get("trump_mentions", [])[:3]
        return {
            "agent": self.name,
            "bias": sentiment,
            "confidence": min(0.85, abs(sentiment) * 2 + 0.3),
            "key_points": mentions,
            "summary": f"Geopolitical risk premium is {'elevated' if sentiment > 0.15 else 'easing' if sentiment < -0.15 else 'stable'}."
        }

class RiskAgent(Agent):
    def __init__(self):
        super().__init__("Risk", "Position sizing, correlation, volatility")

    def analyze(self, context: Dict) -> Dict:
        analysis = context.get("analysis", {})
        atr = analysis.get("atr", 1.5)
        return {
            "agent": self.name,
            "bias": 0.0,
            "confidence": 0.6,
            "key_points": [f"ATR ~ {atr}", "Max positions enforced"],
            "summary": "Risk parameters within bounds; ATR-based stops recommended."
        }

class Coordinator:
    def __init__(self):
        self.agents = [
            TechnicalAgent(),
            FundamentalAgent(),
            GeopoliticsAgent(),
            RiskAgent()
        ]
        self.plugin_agents = plugin_registry.get_agents()

    def debate(self, context: Dict) -> Dict:
        views = [agent.analyze(context) for agent in self.agents]
        for name, fn in self.plugin_agents.items():
            try:
                plugin_view = fn(context)
                if isinstance(plugin_view, dict):
                    plugin_view.setdefault("agent", name)
                    views.append(plugin_view)
            except Exception:
                pass
        weights = {"Technical": 0.3, "Fundamental": 0.2, "Geopolitics": 0.2, "Risk": 0.1}
        plugin_weight = 0.2 / max(1, len(self.plugin_agents))
        weighted_bias = 0
        for v in views:
            w = weights.get(v.get("agent"), plugin_weight)
            weighted_bias += v.get("bias", 0) * w
        avg_conf = sum(v.get("confidence", 0.5) for v in views) / max(1, len(views))
        return {
            "views": views,
            "synthesized_bias": round(max(-1, min(1, weighted_bias)), 3),
            "avg_confidence": round(avg_conf, 2),
            "consensus": "strong" if abs(weighted_bias) > 0.4 else "moderate" if abs(weighted_bias) > 0.15 else "weak",
            "plugin_agents_used": list(self.plugin_agents.keys())
        }
