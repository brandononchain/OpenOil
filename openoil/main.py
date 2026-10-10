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
    <div class="row"><span class="label">LIVE CHART</span><span class="value">WTI CANDLESTICKS</span></div>
    <ascii-art piece="candlesticks" options='{"start":91.5,"seed":42}'></ascii-art>
    <div class="row" style="margin-top:8px"><span class="label">WTI</span><span class="value">$91.52</span></div>
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
