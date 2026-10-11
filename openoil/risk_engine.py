"""
OpenOil Dynamic Risk Engine with Regime Detection
Adjusts position size, stops, and exposure based on detected market regime.
"""

from typing import Dict, Any
import numpy as np

class RiskEngine:
    def __init__(self):
        self.current_regime = "unknown"
        self.vol_lookback = 20

    def detect_regime(self, analysis: Dict, oracle_status: Dict) -> Dict:
        """Simple regime detection: trend efficiency + volatility + OFI."""
        strength = analysis.get("strength", 0)
        ofi = oracle_status.get("ofi") or 0
        # Proxy volatility from strength and recent moves
        vol_proxy = min(1.0, abs(analysis.get("total_score", 0)) / 15)

        if vol_proxy > 0.6:
            regime = "high_volatility"
            size_mult = 0.4
            stop_mult = 1.8
        elif abs(strength) > 0.5 and abs(ofi) < 0.3:
            regime = "trending"
            size_mult = 1.0
            stop_mult = 1.2
        else:
            regime = "ranging"
            size_mult = 0.6
            stop_mult = 1.0

        self.current_regime = regime
        return {
            "regime": regime,
            "size_multiplier": round(size_mult, 2),
            "stop_multiplier": round(stop_mult, 2),
            "volatility_proxy": round(vol_proxy, 2),
            "notes": f"Regime {regime}: size x{size_mult}, stops x{stop_mult}"
        }

    def adjust_signal(self, signal: Dict, regime: Dict) -> Dict:
        """Apply regime-based adjustments to a signal."""
        if signal.get("action") == "HOLD":
            return signal
        mult = regime.get("size_multiplier", 1.0)
        signal["lots"] = round(signal.get("lots", 0.01) * mult, 2)
        signal["regime"] = regime["regime"]
        signal["risk_note"] = regime["notes"]
        return signal
