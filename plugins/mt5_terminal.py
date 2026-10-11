"""Terminal connector.

Account and positions come from the local MCP server.
Candles come from the MetaTrader5 terminal API, because get_chart_history
rejects every datetime format we can see with 'invalid datetime range'.
"""

def pull(symbol: str = ""):
    from openoil.mt5_live import snapshot
    return snapshot(symbol)


def register_connector():
    return "mt5-terminal", pull
