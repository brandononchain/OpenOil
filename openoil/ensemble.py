"""Ensemble forecasting."""

from typing import Dict

class EnsembleForecaster:
    def combine(self, views: list) -> Dict:
        bias = sum(v.get("bias", 0) for v in views) / max(1, len(views))
        return {"ensemble_bias": round(bias, 3)}
