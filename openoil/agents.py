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
        short = analysis.get("short_bias", 0) or 0
        swing = analysis.get("swing_bias", analysis.get("overall_bias", 0)) or 0
        day = context.get("change_pct")
        bias = max(-1.0, min(1.0, short * 0.65 + swing * 0.35))
        day_txt = "no 24h read" if day is None else f"24h {day:+.2f}%"
        side = "up" if bias > 0.12 else "down" if bias < -0.12 else "flat"
        return {
            "agent": self.name,
            "bias": round(bias, 3),
            "confidence": min(0.9, 0.35 + abs(bias)),
            "key_points": [day_txt, f"short {short:+.2f}", f"swing {swing:+.2f}"],
            "summary": f"Price is {side}. {day_txt}. Short-term {short:+.2f}, swing {swing:+.2f}.",
        }

class FundamentalAgent(Agent):
    def __init__(self):
        super().__init__("Fundamental", "EIA inventories and supply/demand")

    def analyze(self, context: Dict) -> Dict:
        eia = context.get("eia", {})
        bias = eia.get("bias", 0) or 0
        event = eia.get("event") or {}
        title = event.get("title")
        summary = f"Next {title}: forecast {event.get('forecast') or 'n/a'} vs previous {event.get('previous') or 'n/a'}." if title else "No crude inventory release on this week's Forex Factory calendar."
        return {
            "agent": self.name,
            "bias": bias,
            "confidence": 0.65 if title else 0.3,
            "key_points": [summary],
            "summary": summary,
        }

class GeopoliticsAgent(Agent):
    def __init__(self):
        super().__init__("Geopolitics", "News, Trump/Iran, Hormuz, hurricanes")

    def analyze(self, context: Dict) -> Dict:
        news = context.get("news", {})
        sentiment = news.get("sentiment_bias", 0) or 0
        mentions = news.get("trump_mentions", [])[:2]
        if mentions:
            summary = "Headline risk: " + mentions[0][:110]
        elif abs(sentiment) < 0.05:
            summary = "No oil headline is pushing price right now."
        else:
            summary = f"Oil headlines lean {'higher' if sentiment > 0 else 'lower'} ({sentiment:+.2f})."
        return {
            "agent": self.name,
            "bias": round(sentiment, 3),
            "confidence": min(0.8, 0.3 + abs(sentiment)),
            "key_points": mentions,
            "summary": summary,
        }

class RiskAgent(Agent):
    def __init__(self):
        super().__init__("Risk", "Position sizing, correlation, volatility")

    def analyze(self, context: Dict) -> Dict:
        analysis = context.get("analysis", {})
        atr = analysis.get("atr") or 0
        spread = context.get("spread") or 0
        wide = spread > max((atr or 0) * 0.2, 0.08)
        bias = -0.25 if wide else 0.0
        stop = round((atr or 0.3) * 1.5, 3)
        summary = (
            f"Spread {spread} is wide against ATR {atr}. Stand aside."
            if wide else
            f"Spread {spread} is tradable. Stop about {stop} away."
        )
        return {
            "agent": self.name,
            "bias": bias,
            "confidence": 0.7,
            "key_points": [summary],
            "summary": summary,
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
        reasons = [v.get("summary") for v in views if v.get("summary")]
        direction = "buy" if weighted_bias > 0.15 else "sell" if weighted_bias < -0.15 else "wait"
        return {
            "views": views,
            "synthesized_bias": round(max(-1, min(1, weighted_bias)), 3),
            "avg_confidence": round(avg_conf, 2),
            "consensus": "strong" if abs(weighted_bias) > 0.4 else "moderate" if abs(weighted_bias) > 0.15 else "weak",
            "decision": direction,
            "reason": " ".join(reasons[:3]),
            "plugin_agents_used": list(self.plugin_agents.keys())
        }
