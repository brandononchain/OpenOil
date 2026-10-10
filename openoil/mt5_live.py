"""Official MetaTrader 5 MCP client (streamable HTTP).

Terminal server is localhost-only (Tools -> Options -> MCP).
Marketdata server is https://www.metatrader.com/mcp and is reachable off-box.
Never log the API key.
"""

import json
import os
from typing import Any, Dict, List, Optional

import httpx

TERMINAL_URL = os.getenv("MT5_MCP_ENDPOINT", "http://127.0.0.1:22346/mcp")
TERMINAL_KEY = os.getenv("MT5_MCP_API_KEY", "")
MARKET_URL = os.getenv("MT5_MARKETDATA_ENDPOINT", "https://www.metatrader.com/mcp")
MARKET_KEY = os.getenv("MT5_MARKETDATA_API_KEY", "")
SYMBOL = os.getenv("MT5_SYMBOL", "USOIL")


class McpHttp:
    def __init__(self, url: str, api_key: str):
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.session_id: Optional[str] = None
        self.http = httpx.Client(timeout=20.0)
        self._id = 1

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        return headers

    def _next_id(self) -> int:
        self._id += 1
        return self._id

    @staticmethod
    def _parse(resp: httpx.Response) -> Any:
        sid = resp.headers.get("mcp-session-id") or resp.headers.get("Mcp-Session-Id")
        text = resp.text or ""
        if "text/event-stream" in resp.headers.get("content-type", "") or text.startswith("event:") or text.startswith("data:"):
            last = None
            for line in text.splitlines():
                if line.startswith("data:"):
                    raw = line[5:].strip()
                    if raw:
                        last = json.loads(raw)
            return sid, last
        if not text:
            return sid, None
        return sid, resp.json()

    def request(self, method: str, params: Optional[Dict] = None, notify: bool = False) -> Any:
        body: Dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if not notify:
            body["id"] = self._next_id()
        if params is not None:
            body["params"] = params
        resp = self.http.post(self.url, headers=self._headers(), json=body)
        if resp.status_code >= 400:
            return {"error": f"HTTP {resp.status_code}", "body": resp.text[:400]}
        sid, payload = self._parse(resp)
        if sid:
            self.session_id = sid
        return payload

    def initialize(self) -> Any:
        result = self.request("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "openoil", "version": "0.1.0"},
        })
        self.request("notifications/initialized", notify=True)
        return result

    def call_tool(self, name: str, arguments: Dict) -> Any:
        if not self.session_id:
            init = self.initialize()
            if isinstance(init, dict) and init.get("error") and "HTTP" in str(init.get("error")):
                return init
        payload = self.request("tools/call", {"name": name, "arguments": arguments})
        return _unwrap(payload)


def _unwrap(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    if "error" in payload and "result" not in payload:
        return payload
    result = payload.get("result", payload)
    content = result.get("content") if isinstance(result, dict) else None
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(block.get("text", ""))
        joined = "\n".join(texts).strip()
        if joined:
            try:
                return json.loads(joined)
            except json.JSONDecodeError:
                return {"text": joined}
    return result


def _bars_from(raw: Any) -> List[Dict]:
    rows = raw
    if isinstance(raw, dict):
        for key in ("bars", "rates", "history", "candles", "data"):
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
        o = row.get("open", row.get("o"))
        h = row.get("high", row.get("h"))
        l = row.get("low", row.get("l"))
        c = row.get("close", row.get("c"))
        t = row.get("time", row.get("t", row.get("datetime")))
        if None in (o, h, l, c):
            continue
        out.append({"t": t, "o": float(o), "h": float(h), "l": float(l), "c": float(c)})
    return out


def _account_from(raw: Any) -> Optional[Dict]:
    if not isinstance(raw, dict):
        return None
    src = raw.get("account", raw)
    if not isinstance(src, dict):
        return None
    keys = ("balance", "equity", "margin", "margin_free", "margin_level", "leverage")
    if not any(k in src for k in keys):
        # nested text dumps sometimes use Pascal case
        lower = {str(k).lower(): v for k, v in src.items()}
        src = {
            "balance": lower.get("balance"),
            "equity": lower.get("equity"),
            "margin": lower.get("margin"),
            "margin_free": lower.get("margin_free") or lower.get("freemargin"),
            "margin_level": lower.get("margin_level") or lower.get("marginlevel"),
            "leverage": lower.get("leverage"),
        }
    if src.get("balance") is None and src.get("equity") is None:
        return None
    return src


def snapshot(symbol: str = SYMBOL) -> Dict:
    """Account and history from the local terminal. History falls back to metatrader.com."""
    out: Dict[str, Any] = {
        "connected": False,
        "symbol": symbol,
        "terminal": TERMINAL_URL,
        "account": None,
        "positions": None,
        "bars": [],
        "quote": None,
        "error": None,
        "note": "Closed markets still return the last quote, history, and account.",
    }
    if not TERMINAL_KEY and not MARKET_KEY:
        out["error"] = "Set MT5_MCP_API_KEY (local terminal) and restart. Do not commit the key."
        return out

    if TERMINAL_KEY:
        term = McpHttp(TERMINAL_URL, TERMINAL_KEY)
        try:
            acct = term.call_tool("get_trading_account_info", {})
            out["account"] = _account_from(acct) or acct
            out["positions"] = term.call_tool("get_trading_open_positions", {})
            bars = term.call_tool("get_chart_history", {"symbol": symbol, "timeframe": "M15", "count": 120})
            if not _bars_from(bars):
                bars = term.call_tool("get_chart_history", {"symbol": symbol, "period": "PERIOD_M15", "count": 120})
            out["bars"] = _bars_from(bars)
            out["connected"] = not (isinstance(acct, dict) and str(acct.get("error", "")).startswith("HTTP"))
            if isinstance(acct, dict) and acct.get("error"):
                out["error"] = acct.get("error")
        except Exception as exc:
            out["error"] = str(exc)

    if not out["bars"] and MARKET_KEY:
        market = McpHttp(MARKET_URL, MARKET_KEY)
        try:
            hist = market.call_tool("marketdata_symbol_history", {"symbol": symbol, "timeframe": "1h"})
            out["bars"] = _bars_from(hist)
            quote = market.call_tool("marketdata_symbol_get", {"symbol": symbol})
            out["quote"] = quote
            out["connected"] = out["connected"] or bool(out["bars"] or quote)
        except Exception as exc:
            out["error"] = out["error"] or str(exc)
    return out
