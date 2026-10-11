"""
OpenOil Alternative Data Expansion
AIS (Hormuz tanker crossings), CFTC COT positioning, refinery/outage signals from news,
options skew proxy, and satellite/inventory proxies.
"""

from typing import Dict, List, Optional
import httpx
import re
import time

class AlternativeData:
    def __init__(self):
        self.last_ais = {}
        self.last_cot = {}

    def fetch_hormuz_ais(self) -> Dict:
        """Live Strait of Hormuz tanker crossings and oil export proxy."""
        result = {"available": False, "source": "none"}
        try:
            r = httpx.get("https://hormuz.data-tracking.net/api/summary?hours=24", timeout=10)
            if r.status_code == 200:
                data = r.json()
                result = {
                    "available": True,
                    "source": "hormuz_ais",
                    "crossings_24h": data.get("crossings") or data.get("total_crossings"),
                    "tankers": data.get("tankers") or data.get("tanker_count"),
                    "oil_export_proxy": data.get("oil_export") or data.get("outbound_tankers"),
                    "timestamp": time.time()
                }
                self.last_ais = result
                return result
        except Exception:
            pass
        # Fallback
        try:
            r = httpx.get("https://hormuz.now/api/daily.json", timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and data:
                    latest = data[-1]
                    result = {
                        "available": True,
                        "source": "hormuz_now",
                        "crossings_24h": latest.get("total") or latest.get("crossings"),
                        "tankers": latest.get("tankers"),
                        "timestamp": time.time()
                    }
                    self.last_ais = result
        except Exception:
            pass
        return result

    def fetch_cot(self) -> Dict:
        """CFTC COT managed money net for WTI (proxy via public pages or note)."""
        result = {"available": False, "managed_money_net": None, "bias": 0.0}
        try:
            r = httpx.get("https://futuresbench.com/cot/crude-oil/", timeout=10)
            if r.status_code == 200:
                text = r.text.lower()
                m = re.search(r"managed money.*?([+-]?\d[\d,]*)", text)
                if m:
                    net = int(m.group(1).replace(",", ""))
                    result = {
                        "available": True,
                        "source": "futuresbench_proxy",
                        "managed_money_net": net,
                        "bias": 0.2 if net > 50000 else -0.2 if net < 0 else 0.0,
                        "note": "Proxy extraction — prefer official CFTC or paid COT API"
                    }
                    self.last_cot = result
                    return result
        except Exception:
            pass
        result["note"] = "COT data requires periodic official pull or API key for full history"
        return result

    def fetch_refinery_signals(self) -> Dict:
        """Scan recent news for refinery outages / disruptions."""
        signals = []
        try:
            r = httpx.get("https://oilprice.com/rss/main", timeout=8)
            if r.status_code == 200:
                titles = re.findall(r"<title>(.*?)</title>", r.text, re.I)[1:15]
                for t in titles:
                    tl = t.lower()
                    if any(w in tl for w in ["refinery", "outage", "shutdown", "hurricane", "fire", "disruption"]):
                        signals.append(t.strip()[:140])
        except Exception:
            pass
        bias = 0.15 if len(signals) > 1 else 0.05 if signals else 0.0
        return {
            "outage_signals": signals[:5],
            "count": len(signals),
            "bias_adjust": round(bias, 2),
            "source": "news_scan"
        }

    def options_skew_proxy(self) -> Dict:
        """Placeholder for options skew (requires paid options data)."""
        return {
            "available": False,
            "note": "True options skew requires CME/ICE options chain or paid feed (e.g. Databento, OilPriceAPI futures+options). Using news/COT as proxy.",
            "proxy_bias": 0.0
        }

    def full_snapshot(self) -> Dict:
        return {
            "ais_hormuz": self.fetch_hormuz_ais(),
            "cot": self.fetch_cot(),
            "refinery": self.fetch_refinery_signals(),
            "options_skew": self.options_skew_proxy(),
            "timestamp": time.time()
        }
