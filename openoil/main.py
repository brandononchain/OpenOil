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
  .wrap { max-width:900px; margin:0 auto; }
  h1 { color:#fff; letter-spacing:2px; }
  .panel { border:1px solid #00ff9f; padding:12px 16px; margin:12px 0; background:#111; }
  .row { display:flex; justify-content:space-between; }
  .label { color:#888; }
  .value { color:#00ff9f; }
  a { color:#00ff9f; }
  .spark { font-size:14px; letter-spacing:1px; }
</style>
</head>
<body>
<div class="wrap">
  <h1>OPENOIL</h1>
  <p style="color:#666">open-source intelligence for crude oil markets</p>

  <div class="panel">
    <div class="row"><span class="label">STATUS</span><span class="value">LIVE</span></div>
    <div class="row"><span class="label">TIME</span><span class="value" id="clock"></span></div>
    <div class="row"><span class="label">SYMBOL</span><span class="value">USOIL</span></div>
  </div>

  <div class="panel">
    <div class="row"><span class="label">WTI</span><span class="value">$91.52</span></div>
    <div class="row"><span class="label">BRENT</span><span class="value">$95.10</span></div>
    <div class="row"><span class="label">SPREAD</span><span class="value">3.58</span></div>
    <div class="spark" style="margin-top:8px">▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆</div>
  </div>

  <div class="panel">
    <div class="row"><span class="label">ENSEMBLE BIAS</span><span class="value">+0.34</span></div>
    <div class="row"><span class="label">REGIME</span><span class="value">TRENDING</span></div>
    <div class="row"><span class="label">CVD</span><span class="value">+1,240</span></div>
    <div class="row"><span class="label">SENTIMENT</span><span class="value">+0.18</span></div>
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
