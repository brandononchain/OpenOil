"""Regime detection and dynamic risk sizing."""

from typing import Dict

class RiskEngine:
    def detect_regime(self, analysis: Dict) -> Dict:
        atr = analysis.get("atr", 1.5)
        regime = "high_vol" if atr > 2.0 else "trending" if abs(analysis.get("overall_bias", 0)) > 0.3 else "ranging"
        return {"regime": regime, "size_multiplier": 0.5 if regime == "high_vol" else 1.0}

    def apply_regime(self, signal: Dict) -> Dict:
        return signal
