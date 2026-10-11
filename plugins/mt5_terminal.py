"""Terminal connector. Candles come from get_chart_history on the local MCP server."""

def pull(symbol: str = ""):
    from openoil.mt5_live import snapshot
    return snapshot(symbol)


def register_connector():
    return "mt5-terminal", pull
