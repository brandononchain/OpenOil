"""Official MetaTrader 5 MCP client (streamable HTTP).

Terminal server is localhost-only (Tools -> Options -> MCP).
Marketdata server is https://www.metatrader.com/mcp and is reachable off-box.
Never log the API key.
"""

import json
import os
from datetime import datetime, timedelta, timezone
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

    def list_tools(self) -> List[str]:
        if not self.session_id:
            init = self.initialize()
            if isinstance(init, dict) and str(init.get("error", "")).startswith("HTTP"):
                return []
        payload = self.request("tools/list", {})
        data = _unwrap(payload)
        tools = []
        if isinstance(data, dict):
            tools = data.get("tools") or []
        if not tools and isinstance(payload, dict):
            result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
            tools = result.get("tools") or []
        return [tool["name"] for tool in tools if isinstance(tool, dict) and tool.get("name")]

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
        lower = {str(k).lower(): v for k, v in row.items()}
        o = lower.get("open", lower.get("o"))
        h = lower.get("high", lower.get("h"))
        l = lower.get("low", lower.get("l"))
        c = lower.get("close", lower.get("c"))
        t = lower.get("time", lower.get("t", lower.get("datetime")))
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



def _config():
    return {
        "terminal_url": os.getenv("MT5_MCP_ENDPOINT", "http://127.0.0.1:22346/mcp"),
        "terminal_key": os.getenv("MT5_MCP_API_KEY", ""),
        "market_url": os.getenv("MT5_MARKETDATA_ENDPOINT", "https://www.metatrader.com/mcp"),
        "market_key": os.getenv("MT5_MARKETDATA_API_KEY", ""),
        "symbol": os.getenv("MT5_SYMBOL", "USOIL"),
    }


def _history(client: McpHttp, symbol: str):
    names = client.list_tools()
    known = {name.lower(): name for name in names}
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=20)).strftime("%Y-%m-%dT00:00:00Z")
    end = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    preferred = [
        "get_chart_history",
        "marketdata_symbol_history",
        "get_rates",
        "copy_rates_from_pos",
        "get_ohlc_bars",
        "get_candles_latest",
    ]
    chosen = []
    for name in preferred:
        if not names or name.lower() in known:
            chosen.append(known.get(name.lower(), name))
    for name in names:
        low = name.lower()
        if any(part in low for part in ("history", "candle", "rate", "ohlc", "bar")) and name not in chosen:
            chosen.append(name)
    arg_sets = [
        {"symbol": symbol, "timeframe": "1h", "from": start, "to": end},
        {"symbol": symbol, "period": "H1", "date_from": start, "date_to": end},
        {"symbol": symbol, "timeframe": "H1", "count": 180},
        {"symbol": symbol, "timeframe": "1h"},
        {"symbol": symbol, "timeframe": "M15", "count": 180},
    ]
    last = None
    for name in chosen:
        for args in arg_sets:
            last = client.call_tool(name, args)
            if isinstance(last, dict) and "tool not found" in json.dumps(last).lower():
                break
            bars = _bars_from(last)
            if bars:
                return bars, None, names
    return [], last, names


def snapshot(symbol: str = "") -> Dict:
    """Account and candles from the terminal. No invented prices."""
    cfg = _config()
    symbol = symbol or cfg["symbol"]
    out: Dict[str, Any] = {
        "connected": False,
        "symbol": symbol,
        "terminal": cfg["terminal_url"],
        "account": None,
        "positions": None,
        "bars": [],
        "depth": None,
        "quote": None,
        "price_source": None,
        "error": None,
        "note": "A closed market still returns the last candles and the account. Prices are never simulated.",
    }
    if not cfg["terminal_key"] and not cfg["market_key"]:
        out["error"] = "MT5_MCP_API_KEY is empty. Put it in the .env next to requirements.txt and restart."
        return out

    if cfg["terminal_key"]:
        term = McpHttp(cfg["terminal_url"], cfg["terminal_key"])
        try:
            acct = term.call_tool("get_trading_account_info", {})
            if isinstance(acct, dict) and str(acct.get("error", "")).startswith("HTTP"):
                out["error"] = f"Terminal MCP refused the key ({acct.get('error')}). Use the key next to 127.0.0.1, not the mq- key."
            else:
                parsed = _account_from(acct)
                out["account"] = parsed
                out["positions"] = term.call_tool("get_trading_open_positions", {})
                bars, raw, tools = _history(term, symbol)
                out["bars"] = bars
                out["tools"] = tools
                if bars:
                    out["price_source"] = "terminal"
                    out["connected"] = True
                else:
                    out["error"] = (
                        f"{symbol} matches Market Watch. This terminal build did not return candles. "
                        f"Tools it exposes: {', '.join(tools) or 'none'}. "
                        f"Last reply: {str(raw)[:180]}"
                    )
        except Exception as exc:
            out["error"] = str(exc)

    if not out["bars"] and cfg["market_key"]:
        market = McpHttp(cfg["market_url"], cfg["market_key"])
        try:
            bars, raw, tools = _history(market, symbol)
            out["tools"] = tools or out.get("tools")
            if bars:
                out["bars"] = bars
                out["price_source"] = "marketdata"
                out["connected"] = True
                out["error"] = None if out["account"] else "Using metatrader.com history. Account data still requires the local terminal."
            elif not out["error"]:
                out["error"] = f"Market data returned no candles for {symbol}: {str(raw)[:240]}"
        except Exception as exc:
            out["error"] = out["error"] or str(exc)
    return out
