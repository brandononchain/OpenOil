"""
OpenOil Ensemble Forecasting
Combines statistical, technical, multi-agent, and LLM scenario forecasts.
Weights are dynamically adjusted by the self-improvement loop.
"""

from typing import Dict, List, Any
import numpy as np

class EnsembleForecaster:
    def __init__(self):
        self.models = ["technical", "fundamental", "geopolitics", "llm_scenario", "microstructure"]
        self.default_weights = {
            "technical": 0.30,
            "fundamental": 0.20,
            "geopolitics": 0.20,
            "llm_scenario": 0.15,
            "microstructure": 0.15
        }

    def forecast(self, context: Dict, weights: Dict = None) -> Dict:
        w = weights or self.default_weights
        components = {}

        # Technical (from multi-TF)
        tech = context.get("analysis", {}).get("overall_bias", 0)
        components["technical"] = tech

        # Fundamental (EIA)
        components["fundamental"] = context.get("eia", {}).get("bias", 0)

        # Geopolitics
        components["geopolitics"] = context.get("news", {}).get("sentiment_bias", 0)

        # LLM scenario / counterfactual
        cf = context.get("counterfactual", {})
        components["llm_scenario"] = cf.get("magnitude", 0)

        # Microstructure (OFI)
        ofi = context.get("ofi")
        components["microstructure"] = ofi if ofi is not None else 0

        used = ["technical", "fundamental", "geopolitics"]
        if abs(components["microstructure"]) > 0.001:
            used.append("microstructure")
        if abs(components["llm_scenario"]) > 0.001:
            used.append("llm_scenario")
        total = sum(w.get(name, 0) for name in used) or 1
        ensemble_bias = sum(components.get(name, 0) * w.get(name, 0) for name in used) / total
        ensemble_bias = max(-1.0, min(1.0, ensemble_bias))

        return {
            "ensemble_bias": round(ensemble_bias, 3),
            "components": {k: round(v, 3) for k, v in components.items()},
            "weights": w,
            "direction": "BUY" if ensemble_bias > 0.08 else "SELL" if ensemble_bias < -0.08 else "HOLD",
            "confidence": round(min(0.95, abs(ensemble_bias) + 0.25), 2)
        }

    def update_weights(self, performance: Dict) -> Dict:
        """Adjust weights from self-improvement suggestions."""
        suggested = performance.get("suggested_weights")
        if suggested:
            # Map agent names to model names where possible
            self.default_weights["technical"] = suggested.get("Technical", 0.30)
            self.default_weights["fundamental"] = suggested.get("Fundamental", 0.20)
            self.default_weights["geopolitics"] = suggested.get("Geopolitics", 0.20)
        return self.default_weights
