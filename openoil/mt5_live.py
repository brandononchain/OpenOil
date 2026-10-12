"""Official MetaTrader 5 MCP client (streamable HTTP).

Terminal server is localhost-only (Tools -> Options -> MCP).
Marketdata server is https://www.metatrader.com/mcp and is reachable off-box.
Never log the API key.
"""

import json
import os
import time
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

    def list_tools(self) -> List[Dict]:
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
        return [tool for tool in tools if isinstance(tool, dict) and tool.get("name")]

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


def _missing_tool(raw: Any) -> bool:
    if not isinstance(raw, dict):
        return False
    blob = json.dumps(raw).lower()
    return "tool not found" in blob or "unknown tool" in blob


def _minutes(mt5, minutes: int):
    table = {
        1: mt5.TIMEFRAME_M1,
        5: mt5.TIMEFRAME_M5,
        15: mt5.TIMEFRAME_M15,
        60: mt5.TIMEFRAME_H1,
        240: mt5.TIMEFRAME_H4,
    }
    return table.get(int(minutes), mt5.TIMEFRAME_M15)


def _terminal():
    try:
        import MetaTrader5 as mt5
    except ImportError:
        return None, "Run: python -m pip install MetaTrader5"
    if not mt5.initialize():
        return None, f"MetaTrader5.initialize failed: {mt5.last_error()}"
    return mt5, None


def bars_from_terminal(symbol: str, minutes: int = 15):
    """Broker candles through the MetaTrader5 terminal API. No datetime-range guess."""
    mt5, err = _terminal()
    if err:
        return [], err
    if mt5.symbol_info(symbol) is None:
        return [], f"{symbol} is not on this terminal: {mt5.last_error()}"
    mt5.symbol_select(symbol, True)
    rates = mt5.copy_rates_from_pos(symbol, _minutes(mt5, minutes), 0, 300)
    if rates is None or len(rates) == 0:
        return [], f"No bars for {symbol} {minutes}m: {mt5.last_error()}"
    bars = []
    for row in rates:
        bars.append({
            "t": int(row["time"]),
            "o": float(row["open"]),
            "h": float(row["high"]),
            "l": float(row["low"]),
            "c": float(row["close"]),
        })
    return bars, None


def quote_from_terminal(symbol: str = ""):
    cfg_symbol = symbol or _config()["symbol"]
    mt5, err = _terminal()
    if err:
        return None
    mt5.symbol_select(cfg_symbol, True)
    info = mt5.symbol_info(cfg_symbol)
    tick = mt5.symbol_info_tick(cfg_symbol)
    if tick is None or not tick.bid or not tick.ask:
        return None
    digits = int(info.digits) if info is not None else 2
    bid = float(tick.bid)
    ask = float(tick.ask)
    hourly = mt5.copy_rates_from_pos(cfg_symbol, mt5.TIMEFRAME_H1, 0, 26)
    base = None
    if hourly is not None and len(hourly) >= 25:
        base = float(hourly[-25]["close"])
    change = (bid - base) if base else None
    change_pct = (change / base * 100) if base else None
    return {
        "symbol": cfg_symbol,
        "bid": bid,
        "ask": ask,
        "last": bid,
        "digits": digits,
        "spread": round(ask - bid, digits),
        "change": None if change is None else round(change, digits),
        "change_pct": None if change_pct is None else round(change_pct, 2),
        "time": int(tick.time),
    }


def _ladder(buckets: Dict[float, float], reverse: bool) -> List[Dict]:
    rows = [{"price": price, "size": round(size, 2)} for price, size in buckets.items() if size > 0]
    rows.sort(key=lambda item: item["price"], reverse=reverse)
    return rows[:12]


def depth_from_terminal(symbol: str):
    """Broker depth when it exists. Otherwise the prices the terminal actually printed."""
    mt5, err = _terminal()
    if err:
        return None
    mt5.symbol_select(symbol, True)
    info = mt5.symbol_info(symbol)
    digits = int(info.digits) if info is not None else 2
    added = mt5.market_book_add(symbol)
    book = mt5.market_book_get(symbol) if added else None
    if added and not book:
        time.sleep(0.4)
        book = mt5.market_book_get(symbol)
    tick = mt5.symbol_info_tick(symbol)
    mid = float(tick.bid) if tick else 0.0
    if book:
        bids, asks = {}, {}
        for row in book:
            price = round(float(row.price), digits)
            size = float(row.volume) or 1.0
            sell = row.type in (mt5.BOOK_TYPE_SELL, mt5.BOOK_TYPE_SELL_MARKET) or (mid and price >= mid)
            target = asks if sell else bids
            target[price] = target.get(price, 0) + size
        if bids or asks:
            return {
                "source": "mt5",
                "label": "ORDER BOOK",
                "note": "Depth from the terminal.",
                "bids": _ladder(bids, True),
                "asks": _ladder(asks, False),
            }
    start = datetime.utcnow() - timedelta(minutes=30)
    ticks = mt5.copy_ticks_from(symbol, start, 3000, mt5.COPY_TICKS_ALL)
    bids, asks = {}, {}
    if ticks is not None and len(ticks) > 0:
        names = set(getattr(ticks.dtype, "names", None) or [])
        for row in ticks:
            bid = round(float(row["bid"]), digits)
            ask = round(float(row["ask"]), digits)
            size = float(row["volume"] or 0) if "volume" in names else 1.0
            size = size or 1.0
            bids[bid] = bids.get(bid, 0) + size
            asks[ask] = asks.get(ask, 0) + size
    if len(bids) + len(asks) < 4:
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 90)
        bids, asks = {}, {}
        if rates is not None:
            for row in rates:
                price = round(float(row["close"]), digits)
                size = float(row["tick_volume"] or 1)
                if mid and price >= mid:
                    asks[price] = asks.get(price, 0) + size
                else:
                    bids[price] = bids.get(price, 0) + size
        note = "This broker sends no depth of market. Ladder is the last 90 minutes of real trades."
        label = "VOLUME"
    else:
        note = "This broker sends no depth of market. Ladder is the last 30 minutes of real quotes."
        label = "TICKS"
    if not bids and not asks:
        return {"source": "none", "label": "NO DEPTH", "note": "Terminal returned no book and no ticks.", "bids": [], "asks": []}
    return {
        "source": "ticks",
        "label": label,
        "note": note,
        "bids": _ladder(bids, True),
        "asks": _ladder(asks, False),
    }


def _tool_names(tools: List[Dict]) -> List[str]:
    return [tool.get("name", "") for tool in tools]


def _schema_for(tools: List[Dict], name: str) -> Dict:
    for tool in tools:
        if tool.get("name") == name:
            return tool.get("inputSchema") or tool.get("input_schema") or {}
    return {}


def _history_attempts(schema: Dict, symbol: str, start: datetime, end: datetime) -> List[Dict]:
    """Prefer the tool's own argument names. MetaTrader datetimes are unix seconds or YYYY.MM.DD HH:MM:SS."""
    props = (schema or {}).get("properties") or {}
    start_unix = int(start.timestamp())
    end_unix = int(end.timestamp())
    start_mt = start.strftime("%Y.%m.%d %H:%M:%S")
    end_mt = end.strftime("%Y.%m.%d %H:%M:%S")
    if props:
        built = []
        for numeric in (True, False):
            args: Dict[str, Any] = {}
            for key, spec in props.items():
                low = key.lower()
                typ = (spec or {}).get("type")
                if "symbol" in low:
                    args[key] = symbol
                elif low in ("period", "timeframe", "tf", "chart_period"):
                    args[key] = 15 if typ == "integer" else "M15"
                elif any(part in low for part in ("from", "start", "begin", "since")):
                    args[key] = start_unix if typ in ("integer", "number") or numeric else start_mt
                elif any(part in low for part in ("to", "end", "until")) and "timeframe" not in low:
                    args[key] = end_unix if typ in ("integer", "number") or numeric else end_mt
                elif any(part in low for part in ("count", "limit", "bars")):
                    args[key] = 300
            if args and args not in built:
                built.append(args)
        if built:
            return built
    return [
        {"symbol": symbol, "period": "M15", "from": start_unix, "to": end_unix},
        {"symbol": symbol, "period": "PERIOD_M15", "from": start_unix, "to": end_unix},
        {"symbol": symbol, "period": "M15", "from": start_mt, "to": end_mt},
        {"symbol": symbol, "timeframe": "M15", "from": start_unix, "to": end_unix},
        {"symbol": symbol, "period": "H1", "from": start_unix, "to": end_unix},
    ]


def _terminal_history(client: McpHttp, symbol: str):
    """get_chart_history is a terminal tool. Open the chart, then request a closed unix range."""
    tools = client.list_tools()
    names = _tool_names(tools)
    schema = _schema_for(tools, "get_chart_history")
    end = datetime.now(timezone.utc) - timedelta(minutes=2)
    clock = client.call_tool("get_time_information", {})
    if isinstance(clock, dict):
        for key in ("server_time", "time", "datetime", "now"):
            if clock.get(key):
                break
    start = end - timedelta(days=5)
    client.call_tool("chart_open", {"symbol": symbol, "period": "M15"})
    time.sleep(1.5)
    if names and "get_chart_history" not in names:
        return [], {"error": "get_chart_history is not in tools/list", "schema": schema}, names, schema
    last = None
    for args in _history_attempts(schema, symbol, start, end):
        last = client.call_tool("get_chart_history", args)
        if _missing_tool(last):
            return [], last, names, schema
        bars = _bars_from(last)
        if bars:
            return bars, None, names, schema
        if isinstance(last, dict) and "invalid datetime" not in json.dumps(last).lower():
            break
    return [], {"reply": last, "schema": list((schema.get("properties") or {}).keys())}, names, schema


def _market_history(client: McpHttp, symbol: str):
    """marketdata_symbol_history lives only on https://www.metatrader.com/mcp."""
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    queries = [symbol, "WTI", "CL", "USOIL", "Crude Oil"]
    symbols = []
    for query in queries:
        found = client.call_tool("marketdata_symbol_search", {"query": query})
        if _missing_tool(found):
            return [], found
        symbols.extend(_symbol_names(found))
    symbols = list(dict.fromkeys(symbols + queries))
    last = None
    for name in symbols[:8]:
        for timeframe in ("1h", "4h", "1d"):
            last = client.call_tool("marketdata_symbol_history", {
                "symbol": name,
                "timeframe": timeframe,
                "from": start,
                "to": end,
            })
            if _missing_tool(last):
                return [], last
            bars = _bars_from(last)
            if bars:
                return bars, None
    return [], last


def _symbol_names(raw: Any) -> List[str]:
    rows = raw if isinstance(raw, list) else []
    if isinstance(raw, dict):
        for key in ("symbols", "results", "items", "data"):
            if isinstance(raw.get(key), list):
                rows = raw[key]
                break
    names = []
    for row in rows:
        if isinstance(row, str):
            names.append(row)
        elif isinstance(row, dict):
            for key in ("symbol", "ticker", "name"):
                if row.get(key):
                    names.append(str(row[key]))
                    break
    return names


def snapshot(symbol: str = "", minutes: int = 15) -> Dict:
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
                bars, rate_error = bars_from_terminal(symbol, minutes)
                out["timeframe"] = int(minutes)
                out["quote"] = quote_from_terminal(symbol)
                out["depth"] = depth_from_terminal(symbol)
                if bars:
                    out["bars"] = bars
                    out["price_source"] = "terminal"
                    out["connected"] = True
                    out["error"] = None
                else:
                    mcp_bars, raw, tools, schema = _terminal_history(term, symbol)
                    out["bars"] = mcp_bars
                    out["tools"] = tools
                    out["history_schema"] = list((schema.get("properties") or {}).keys())
                    if mcp_bars:
                        out["price_source"] = "terminal"
                        out["connected"] = True
                        out["error"] = None
                    else:
                        out["error"] = rate_error or (
                            f"{symbol} is the broker symbol. get_chart_history did not return candles. "
                            f"Reply: {str(raw)[:220]}"
                        )
        except Exception as exc:
            out["error"] = str(exc)

    if not out["bars"] and cfg["market_key"]:
        market = McpHttp(cfg["market_url"], cfg["market_key"])
        try:
            bars, raw = _market_history(market, symbol)
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
