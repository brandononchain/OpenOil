"""The trading mind. It argues, it can disagree with the score, and it stands down after losses."""

import os
from typing import Dict, List, Optional

import httpx


def _side_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    upper = text.upper()
    for side in ("FLAT", "SELL", "BUY"):
        if side in upper.split() or upper.strip().endswith(side):
            return side
    return None


def _argument(facts: Dict, rule_side: str) -> str:
    day = facts.get("change_pct") or 0
    short = facts.get("short_bias") or 0
    swing = facts.get("swing_bias") or 0
    imbalance = facts.get("imbalance") or 0
    spread = facts.get("spread") or 0
    headline = facts.get("headline") or "no oil headline"
    book = "buyers" if imbalance > 0.15 else "sellers" if imbalance < -0.15 else "balanced"
    tape = "down" if day < -0.3 or short < -0.1 else "up" if day > 0.3 or short > 0.1 else "flat"
    return (
        f"The tape is {tape} ({day:+.2f}% over 24h, short {short:+.2f}, swing {swing:+.2f}). "
        f"Printed size is with the {book} ({imbalance:+.2f}). Spread is {spread}. "
        f"Headline: {headline}. The score says {rule_side}."
    )


def ask_model(brief: str) -> Optional[str]:
    key = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY") or ""
    if not key:
        return None
    try:
        response = httpx.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": "Bearer " + key},
            json={
                "model": os.getenv("OPENOIL_MODEL", "grok-3-mini"),
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are the OpenOil mind for WTI crude. Argue in four sentences: tape, depth, news, then the call. "
                            "End with exactly one word: BUY, SELL, or FLAT. You do not send orders."
                        ),
                    },
                    {"role": "user", "content": brief},
                ],
            },
            timeout=12,
        )
        if response.status_code != 200:
            return None
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def decide(rule: Dict, facts: Dict, records: List[Dict], model_text: Optional[str]) -> Dict:
    side = rule.get("side") or "FLAT"
    thought = _argument(facts, side)
    source = "tape"
    model_side = _side_from_text(model_text or "")
    if model_text:
        source = "grok"
        thought = model_text
        if model_side in ("BUY", "SELL", "FLAT"):
            if model_side != side and side in ("BUY", "SELL") and model_side in ("BUY", "SELL"):
                side = "FLAT"
                thought = "Mind and tape disagree, so no trade. " + model_text
            else:
                side = model_side
    same_side = [row for row in records[-8:] if row.get("outcome") and row.get("signal") == side]
    losses = sum(1 for row in same_side if row["outcome"] == "loss")
    if side in ("BUY", "SELL") and losses >= 2 and abs(rule.get("score") or 0) < 0.45:
        thought += " Stood down. The last calls on this side lost."
        side = "FLAT"
        source = "memory"
    return {"side": side, "thought": thought, "source": source, "stood_down": source == "memory"}
