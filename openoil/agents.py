"""
OpenOil Multi-Agent Reasoning
Specialized agents for technicals, fundamentals, geopolitics, and risk.
"""

from typing import Dict, Any, List
import json
try:
    from plugins import registry as plugin_registry
except Exception:
    plugin_registry = type('R', (), {'get_agents': lambda: {}})()

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
        overall = analysis.get("overall_bias", 0)
        return {
            "agent": self.name,
            "bias": overall,
            "confidence": min(0.9, abs(overall) * 1.2),
            "summary": f"Technical confluence is {'bullish' if overall > 0.2 else 'bearish' if overall < -0.2 else 'neutral'}."
        }

class FundamentalAgent(Agent):
    def __init__(self):
        super().__init__("Fundamental", "EIA inventories and supply/demand")

    def analyze(self, context: Dict) -> Dict:
        eia = context.get("eia", {})
        bias = eia.get("bias", 0)
        return {"agent": self.name, "bias": bias, "confidence": 0.6, "summary": "Inventory bias applied."}

class GeopoliticsAgent(Agent):
    def __init__(self):
        super().__init__("Geopolitics", "News, Trump/Iran, Hormuz")

    def analyze(self, context: Dict) -> Dict:
        news = context.get("news", {})
        sentiment = news.get("sentiment_bias", 0)
        return {"agent": self.name, "bias": sentiment, "confidence": 0.5, "summary": "Geopolitical sentiment applied."}

class RiskAgent(Agent):
    def __init__(self):
        super().__init__("Risk", "Position sizing, volatility")

    def analyze(self, context: Dict) -> Dict:
        return {"agent": self.name, "bias": 0.0, "confidence": 0.6, "summary": "Risk overlay applied."}

class Coordinator:
    def __init__(self):
        self.agents = [TechnicalAgent(), FundamentalAgent(), GeopoliticsAgent(), RiskAgent()]
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
        weighted_bias = sum(v.get("bias", 0) * weights.get(v.get("agent"), plugin_weight) for v in views)
        avg_conf = sum(v.get("confidence", 0.5) for v in views) / max(1, len(views))
        return {
            "views": views,
            "synthesized_bias": round(max(-1, min(1, weighted_bias)), 3),
            "avg_confidence": round(avg_conf, 2),
            "consensus": "strong" if abs(weighted_bias) > 0.4 else "moderate" if abs(weighted_bias) > 0.15 else "weak",
            "plugin_agents_used": list(self.plugin_agents.keys())
        }
