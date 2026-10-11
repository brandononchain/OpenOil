"""
OpenOil Real-Time Oil Price Prediction & Risk Analysis
Produces short-term price forecasts with confidence intervals and quantitative risk metrics.
"""

from typing import Dict, Any
import math

class PricePredictor:
    def __init__(self):
        self.horizon_hours = [1, 4, 24]

    def predict(self, analysis: Dict, current_price: float, atr: float = 1.5) -> Dict:
        """Multi-horizon directional forecast with expected move."""
        bias = analysis.get("ensemble", {}).get("ensemble_bias", 0) or analysis.get("overall_bias", 0)
        strength = abs(analysis.get("strength", 0))
        regime = analysis.get("regime", {}).get("regime", "ranging")
        vol_mult = 1.8 if regime == "high_volatility" else 1.0 if regime == "trending" else 0.7

        forecasts = {}
        for h in self.horizon_hours:
            expected_move = atr * math.sqrt(h / 24) * vol_mult * (0.5 + strength)
            direction = 1 if bias > 0.1 else -1 if bias < -0.1 else 0
            target = current_price + direction * expected_move
            conf = min(0.85, 0.4 + abs(bias) * 0.4 + strength * 0.2)
            forecasts[f"{h}h"] = {
                "target": round(target, 2),
                "expected_move": round(expected_move, 2),
                "direction": "up" if direction > 0 else "down" if direction < 0 else "neutral",
                "confidence": round(conf, 2),
                "upper": round(current_price + expected_move * 1.5, 2),
                "lower": round(current_price - expected_move * 1.5, 2)
            }

        return {
            "current_price": current_price,
            "forecasts": forecasts,
            "primary_horizon": "4h",
            "method": "ensemble_bias_atr_regime"
        }

class RiskAnalyzer:
    def __init__(self):
        pass

    def analyze(self, analysis: Dict, signal: Dict, current_price: float, atr: float = 1.5) -> Dict:
        """Quantitative risk: position risk, VaR-style, expected shortfall proxy."""
        lots = signal.get("lots", 0.01)
        sl = signal.get("sl")
        if not sl or not current_price:
            return {"status": "insufficient_data"}

        risk_per_lot = abs(current_price - sl) * 10  # rough $ per lot for oil
        position_risk = risk_per_lot * lots
        account = 10000  # configurable
        risk_pct = (position_risk / account) * 100

        # Simple parametric VaR (1-day, 95%)
        daily_vol = atr / current_price
        var_95 = current_price * daily_vol * 1.65 * lots * 10
        es_95 = var_95 * 1.25  # rough expected shortfall

        regime = analysis.get("regime", {}).get("regime", "ranging")
        risk_adjustment = 1.5 if regime == "high_volatility" else 1.0

        return {
            "position_risk_usd": round(position_risk * risk_adjustment, 2),
            "risk_pct_account": round(risk_pct * risk_adjustment, 2),
            "var_95_1d": round(var_95 * risk_adjustment, 2),
            "expected_shortfall_95": round(es_95 * risk_adjustment, 2),
            "atr_used": atr,
            "regime_multiplier": risk_adjustment,
            "recommendation": "reduce_size" if risk_pct > 2 else "acceptable"
        }
