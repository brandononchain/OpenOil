# MT5 MCP Contract

OpenOil expects the following tools to be exposed by the MetaTrader 5 MCP server.

## Required Tools

### mt5_get_ticks
```json
{
  "symbol": "USOIL",
  "count": 1
}
```
Response:
```json
{
  "ticks": [
    {
      "bid": 91.50,
      "ask": 91.52,
      "last": 91.51,
      "volume": 10,
      "time": 1728500000
    }
  ]
}
```

### mt5_get_rates
```json
{
  "symbol": "USOIL",
  "timeframe": "H1",
  "count": 100
}
```
Response: list of OHLC bars.

### mt5_get_market_depth / mt5_market_book_get
```json
{
  "symbol": "USOIL",
  "depth": 10
}
```
Response:
```json
{
  "bids": [{"price": 91.50, "volume": 50}, ...],
  "asks": [{"price": 91.52, "volume": 40}, ...]
}
```

### mt5_place_order
```json
{
  "symbol": "USOIL",
  "type": "buy",
  "lots": 0.1,
  "sl": 90.50,
  "tp": 93.00
}
```

### mt5_get_positions
Returns list of open positions with ticket, symbol, type, volume, price_open, sl, tp, profit.

## Notes
- All responses should be JSON.
- Errors should include an `"error"` key.
- The server runs on Windows where the MT5 terminal is installed.
- OpenOil connects via HTTP to the MCP endpoint set in `MT5_MCP_ENDPOINT`.
