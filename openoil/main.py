"""
OpenOil — main entry point.
Run: python -m openoil.main
"""

import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openoil.memory_graph import MemoryGraph
from openoil.agents import Coordinator
from openoil.data_oracle import DataOracle
from openoil.risk_engine import RiskEngine
from openoil.governance import Governance
from openoil.order_flow import OrderFlowAnalyzer
from openoil.sentiment import SentimentAnalyzer
from openoil.alt_data import AlternativeData
from openoil.charts import ChartGenerator
from openoil.prediction_risk import PricePredictor, RiskAnalyzer

app = FastAPI(title="OpenOil", version="0.1.0")

memory = MemoryGraph()
coordinator = Coordinator()
oracle = DataOracle()
risk_engine = RiskEngine()
governance = Governance()
order_flow = OrderFlowAnalyzer()
sentiment = SentimentAnalyzer()
alt_data = AlternativeData()
charts = ChartGenerator()
predictor = PricePredictor()
risk_analyzer = RiskAnalyzer()

# Mock historical series (replace with real feed later)
HIST_PRICES = [88.2, 88.9, 89.4, 90.1, 89.7, 90.5, 91.2, 90.8, 91.6, 91.1, 91.8, 91.5, 92.0, 91.7, 91.52]

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>OpenOil</title>
<style>
  body { background:#0a0a0a; color:#00ff9f; font-family: 'Courier New', monospace; margin:0; padding:20px; }
  .wrap { max-width:960px; margin:0 auto; }
  h1 { color:#fff; letter-spacing:2px; margin-bottom:4px; }
  .sub { color:#666; margin-bottom:16px; }
  .panel { border:1px solid #00ff9f; padding:12px 16px; margin:12px 0; background:#111; }
  .row { display:flex; justify-content:space-between; margin:4px 0; }
  .label { color:#888; }
  .value { color:#00ff9f; }
  .bull { color:#00ff9f; }
  .bear { color:#ff6b6b; }
  a { color:#00ff9f; text-decoration:none; }
  a:hover { text-decoration:underline; }
  ascii-art { display:block; margin:8px 0; }
  .trade-row { font-size:13px; padding:2px 0; border-bottom:1px solid #222; }
  .spark { font-size:16px; letter-spacing:1px; color:#00ff9f; margin:6px 0; }
  .chart-meta { font-size:12px; color:#666; }
</style>
<script type="module" src="https://ascii.rest/ascii.js"></script>
</head>
<body>
<div class="wrap">
  <h1>OPENOIL</h1>
  <div class="sub">open-source intelligence for crude oil markets</div>

  <div class="panel">
    <div class="row"><span class="label">STATUS</span><span class="value">LIVE</span></div>
    <div class="row"><span class="label">TIME</span><span class="value" id="clock"></span></div>
    <div class="row"><span class="label">SYMBOL</span><span class="value">USOIL</span></div>
  </div>

  <div class="panel">
    <div class="row"><span class="label">CHART</span><span class="value">LIVE + HISTORICAL</span></div>
    <div class="chart-meta">Historical (last ~15 bars)</div>
    <div class="spark" id="spark"></div>
    <div class="chart-meta" style="margin-top:10px">Live forming candle</div>
    <ascii-art piece="candlesticks" options='{"start":91.5,"seed":42}'></ascii-art>
    <div class="row" style="margin-top:8px"><span class="label">WTI</span><span class="value" id="wti">$91.52</span></div>
    <div class="row"><span class="label">BRENT</span><span class="value">$95.10</span></div>
    <div class="row"><span class="label">SPREAD</span><span class="value">3.58</span></div>
  </div>

  <div class="panel">
    <div class="row"><span class="label">ANALYSIS</span></div>
    <div class="row"><span class="label">ENSEMBLE BIAS</span><span class="value bull">+0.34</span></div>
    <div class="row"><span class="label">REGIME</span><span class="value">TRENDING</span></div>
    <div class="row"><span class="label">CVD</span><span class="value bull">+1,240</span></div>
    <div class="row"><span class="label">SENTIMENT</span><span class="value bull">+0.18</span></div>
    <div class="row"><span class="label">4H TARGET</span><span class="value">92.40</span></div>
    <div class="row"><span class="label">24H TARGET</span><span class="value">93.10</span></div>
  </div>

  <div class="panel">
    <div class="row"><span class="label">SIGNALS</span></div>
    <div class="trade-row">TECHNICAL &nbsp;&nbsp; bullish confluence &nbsp;&nbsp; +0.42</div>
    <div class="trade-row">FUNDAMENTAL &nbsp; EIA supportive &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; +0.28</div>
    <div class="trade-row">GEOPOLITICS &nbsp; risk premium elevated +0.31</div>
    <div class="trade-row">RISK &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; size 0.8x regime &nbsp;&nbsp; 0.00</div>
  </div>

  <div class="panel">
    <div class="row"><span class="label">TRADES</span></div>
    <div class="trade-row">#1024 BUY 0.10 @ 91.20 &nbsp; SL 90.40 &nbsp; TP 92.80 &nbsp; <span class="bull">OPEN</span></div>
    <div class="trade-row">#1021 SELL 0.05 @ 92.10 &nbsp; closed +$84 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span class="bull">WIN</span></div>
    <div class="trade-row">#1018 BUY 0.10 @ 90.55 &nbsp; closed -$42 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span class="bear">LOSS</span></div>
  </div>

  <div class="panel">
    <div class="row"><span class="label">ENDPOINTS</span></div>
    <div style="margin-top:6px">
      <a href="/dashboard">/dashboard</a> &nbsp;
      <a href="/health">/health</a> &nbsp;
      <a href="/docs">/docs</a>
    </div>
  </div>
</div>
<script>
function tick(){ document.getElementById('clock').textContent = new Date().toISOString().slice(0,19).replace('T',' '); }
tick(); setInterval(tick, 1000);

function sparkline(values) {
  if (!values || values.length < 2) return '▁'.repeat(30);
  const mn = Math.min(...values), mx = Math.max(...values);
  const rng = (mx - mn) || 1;
  const blocks = '▁▂▃▄▅▆▇█';
  return values.map(v => blocks[Math.min(7, Math.floor((v - mn) / rng * 7))]).join('');
}

const hist = """ + str(HIST_PRICES) + """;
document.getElementById('spark').textContent = sparkline(hist);

// Light live tick simulation on the last price
setInterval(() => {
  const last = hist[hist.length - 1];
  const next = +(last + (Math.random() - 0.48) * 0.15).toFixed(2);
  hist.push(next);
  if (hist.length > 40) hist.shift();
  document.getElementById('spark').textContent = sparkline(hist);
  document.getElementById('wti').textContent = '$' + next.toFixed(2);
}, 3000);
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def root():
    return DASHBOARD_HTML

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_HTML

@app.get("/health")
def health():
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}

@app.get("/price")
def price():
    return {"symbol": "USOIL", "last": HIST_PRICES[-1], "history": HIST_PRICES[-20:]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
