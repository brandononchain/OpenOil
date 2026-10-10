"""
OpenOil — main entry point.
Run: python -m openoil.main
"""

import os
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

@app.get("/")
def root():
    return {"status": "ok", "service": "OpenOil", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
    <html><body style="background:#0a0a0a;color:#00ff9f;font-family:monospace;padding:20px">
    <h1>OpenOil</h1>
    <p>Structured package layout is live.</p>
    <p>Endpoints: /health /dashboard /charts /regime /market /predict /risk</p>
    </body></html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
