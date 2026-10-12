"""Desk state. Prices come from MT5 only. No random walk."""

import os
import time
from typing import Dict, List

from openoil.agents import Coordinator
from openoil.ensemble import EnsembleForecaster
from openoil.governance import Governance
from openoil.mt5_live import snapshot
from openoil.prediction_risk import PricePredictor
from openoil.risk_engine import RiskEngine
from openoil.sentiment import SentimentAnalyzer

coordinator = Coordinator()
ensemble = EnsembleForecaster()
governance = Governance()
risk = RiskEngine()
sentiment = SentimentAnalyzer()
predictor = PricePredictor()

_cache = {"news": None, "news_at": 0.0, "last_dir": None}


def _num(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _positions(raw) -> List[Dict]:
    rows = raw
    if isinstance(raw, dict):
        for key in ("positions", "items", "data", "open_positions"):
            if isinstance(raw.get(key), list):
                rows = raw[key]
                break
        else:
            return []
    if not isinstance(rows, list):
        return []
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        side = str(row.get("type") or row.get("side") or "")
        if side in ("0", "buy", "BUY", "POSITION_TYPE_BUY"):
            side = "BUY"
        elif side in ("1", "sell", "SELL", "POSITION_TYPE_SELL"):
            side = "SELL"
        out.append({
            "id": row.get("ticket") or row.get("id") or row.get("position") or "",
            "symbol": row.get("symbol") or "",
            "side": side,
            "qty": row.get("volume") or row.get("lots") or row.get("qty"),
            "entry": row.get("price_open") or row.get("price") or row.get("entry"),
            "sl": row.get("sl") or row.get("price_sl"),
            "tp": row.get("tp") or row.get("price_tp"),
            "pnl": row.get("profit") or row.get("pnl"),
            "status": "OPEN",
        })
    return out


def _technical(bars: List[Dict]) -> Dict:
    closes = [_num(bar["c"]) for bar in bars]
    ranges = [abs(_num(bar["h"]) - _num(bar["l"])) for bar in bars]
    atr = sum(ranges[-14:]) / max(1, min(14, len(ranges)))
    look = closes[-20:] if len(closes) >= 20 else closes
    base = look[0] or closes[-1]
    move = (closes[-1] - base) / base if base else 0.0
    short_base = closes[-8] if len(closes) >= 8 else closes[0]
    swing_base = closes[-40] if len(closes) >= 40 else closes[0]
    short = (closes[-1] - short_base) / short_base if short_base else 0.0
    swing = (closes[-1] - swing_base) / swing_base if swing_base else 0.0
    bias = max(-1.0, min(1.0, (short * 18) + (swing * 8)))
    return {
        "overall_bias": round(bias, 3),
        "short_bias": round(max(-1.0, min(1.0, short * 40)), 3),
        "swing_bias": round(max(-1.0, min(1.0, swing * 12)), 3),
        "strength": round(min(1.0, abs(move) * 30), 3),
        "atr": round(atr, 4),
        "last": closes[-1],
        "change": round(closes[-1] - base, 4),
        "change_pct": round(move * 100, 3),
    }


def _book(mid: float, depth) -> Dict:
    if isinstance(depth, dict) and (depth.get("bids") or depth.get("asks")):
        return {"source": "mt5", "label": "ORDER BOOK", "bids": depth.get("bids") or [], "asks": depth.get("asks") or []}
    asks, bids = [], []
    for i in range(1, 13):
        asks.append({"price": round(mid + 0.02 * i, 2), "size": 20 + ((i * 37) % 180)})
        bids.append({"price": round(mid - 0.02 * i, 2), "size": 20 + ((i * 53) % 180)})
    return {"source": "sim", "label": "SIM BOOK", "asks": list(reversed(asks)), "bids": bids}


def _pack_news(news: Dict) -> Dict:
    headlines = [str(item) for item in (news.get("headlines") or []) if item]
    hot_words = ("attack", "outage", "hormuz", "sanction", "war", "hurricane", "trump", "iran", "opec", "strike", "shortage", "blockade")
    alerts = []
    for title in headlines:
        hot = any(word in title.lower() for word in hot_words)
        alerts.append({"title": title, "tag": "ALERT" if hot else "WIRE"})
    return {
        "bias": news.get("sentiment_bias", 0),
        "sources": news.get("sources") or [],
        "headlines": headlines[:24],
        "alerts": [row for row in alerts if row["tag"] == "ALERT"][:8] or alerts[:6],
        "calendar": news.get("calendar") or [],
        "trump_iran_mentions": news.get("trump_iran_mentions") or [],
        "eia": news.get("eia") or {"bias": 0.0},
        "updated": news.get("updated"),
    }


def news_public() -> Dict:
    return _pack_news(_news())


def _news() -> Dict:
    now = time.time()
    if _cache["news"] is None or now - _cache["news_at"] > 60:
        try:
            _cache["news"] = sentiment.fetch_realtime()
        except Exception as exc:
            _cache["news"] = {"sentiment_bias": 0.0, "headlines": [], "error": str(exc)}
        _cache["news_at"] = now
    return _cache["news"] or {"sentiment_bias": 0.0}


def build(minutes: int = 15) -> Dict:
    live = os.getenv("OPENOIL_LIVE", "0") == "1"
    snap = None
    try:
        from plugins import registry as plugin_registry
        pull = plugin_registry.get_connectors().get("mt5-terminal")
        if pull:
            snap = pull(minutes=minutes)
    except Exception:
        snap = None
    if not isinstance(snap, dict):
        snap = snapshot("", minutes)
    bars = snap.get("bars") or []
    account = snap.get("account") if isinstance(snap.get("account"), dict) else None
    positions = _positions(snap.get("positions"))
    news = _pack_news(_news())
    base = {
        "live_orders": live,
        "symbol": snap.get("symbol"),
        "error": snap.get("error"),
        "price_source": snap.get("price_source"),
        "account": account,
        "positions": positions,
        "bars": bars[-120:],
        "news": news,
        "headlines": news["headlines"][:6],
        "note": "Orders stay off unless OPENOIL_LIVE=1. Nothing is sent automatically.",
    }
    if not bars:
        base.update({
            "mode": "offline",
            "book": None,
            "analysis": None,
            "signals": [],
            "quote": None,
        })
        return base

    tech = _technical(bars)
    live_quote = snap.get("quote") if isinstance(snap.get("quote"), dict) else {}
    context = {
        "analysis": tech,
        "eia": news.get("eia") or {"bias": 0.0},
        "calendar": news.get("calendar") or [],
        "news": {
            "sentiment_bias": news.get("bias", 0),
            "trump_mentions": news.get("trump_iran_mentions") or [],
        },
        "change_pct": live_quote.get("change_pct"),
        "spread": live_quote.get("spread") or 0,
        "ofi": None,
    }
    debate = coordinator.debate(context)
    forecast = ensemble.forecast({**context, "analysis": {**tech, "overall_bias": debate["synthesized_bias"]}})
    regime = risk.detect_regime({"strength": tech["strength"], "total_score": tech["overall_bias"] * 10}, {"ofi": 0})
    prediction = predictor.predict(
        {"ensemble": forecast, "overall_bias": debate["synthesized_bias"], "strength": tech["strength"], "regime": regime},
        tech["last"],
        tech["atr"] or 0.5,
    )
    direction = forecast["direction"]
    if direction != _cache["last_dir"]:
        governance.audit("signal", {
            "symbol": snap.get("symbol"),
            "direction": direction,
            "bias": forecast["ensemble_bias"],
            "regime": regime["regime"],
            "live_orders": live,
            "sent": False,
        })
        if live and direction in ("BUY", "SELL"):
            governance.request_approval(
                {"action": direction, "symbol": snap.get("symbol"), "lots": 0.01},
                {"overall_bias": debate["synthesized_bias"], "ensemble": forecast, "regime": regime},
                reason="OPENOIL_LIVE is on. Queued. Not sent.",
            )
        _cache["last_dir"] = direction

    last = tech["last"]
    bid = live_quote.get("bid")
    ask = live_quote.get("ask")
    last_px = live_quote.get("last") or last
    depth = snap.get("depth")
    if isinstance(depth, dict) and (depth.get("bids") or depth.get("asks")):
        book = depth
    elif bid and ask:
        book = {
            "source": "quote",
            "label": "BID / ASK",
            "asks": [{"price": ask, "size": ""}],
            "bids": [{"price": bid, "size": ""}],
        }
    else:
        book = None
    base.update({
        "mode": "mt5",
        "timeframe": int(minutes),
        "quote": {
            "last": last_px,
            "bid": bid if bid is not None else last_px,
            "ask": ask if ask is not None else last_px,
            "digits": live_quote.get("digits") or 2,
            "spread": live_quote.get("spread"),
            "change": live_quote.get("change"),
            "change_pct": live_quote.get("change_pct"),
        },
        "analysis": {
            "ensemble": forecast["ensemble_bias"],
            "decision": debate.get("decision"),
            "reason": debate.get("reason"),
            "regime": regime["regime"],
            "sentiment": news.get("bias", 0),
            "atr": tech["atr"],
            "target_4h": prediction["forecasts"]["4h"]["target"],
            "target_24h": prediction["forecasts"]["24h"]["target"],
        },
        "signals": [
            {"agent": view.get("agent"), "bias": view.get("bias"), "summary": view.get("summary")}
            for view in debate["views"]
        ],
        "book": book,
    })
    return base
