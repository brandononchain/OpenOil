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

HIST_PRICES = [88.2, 88.9, 89.4, 90.1, 89.7, 90.5, 91.2, 90.8, 91.6, 91.1, 91.8, 91.5, 92.0, 91.7, 91.52]

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>OpenOil</title>
<style>
  html, body { height: 100%; margin: 0; background: #070907; color: #d7ffe4; font-family: ui-monospace, "Cascadia Mono", "Courier New", monospace; }
  * { box-sizing: border-box; }
  .term { height: 100vh; display: grid; grid-template-rows: 48px minmax(0, 1fr) 176px; }
  .top { display: flex; align-items: center; gap: 22px; padding: 0 14px; border-bottom: 1px solid #1c3a28; background: #0b100d; }
  .brand { color: #fff; letter-spacing: 2px; font-weight: 700; font-size: 16px; }
  .sym { color: #9cffc4; font-size: 13px; }
  .px { font-size: 20px; color: #3dff9a; }
  .up { color: #3dff9a; } .dn { color: #ff6b6b; }
  .muted { color: #6d8274; font-size: 12px; }
  .spacer { flex: 1; }
  .mid { display: grid; grid-template-columns: 270px minmax(0, 1fr) 300px; min-height: 0; }
  .rail { min-height: 0; overflow: auto; background: #090d0b; border-right: 1px solid #1c3a28; }
  .rail.right { border-right: none; border-left: 1px solid #1c3a28; }
  .sec { padding: 10px 12px 12px; border-bottom: 1px solid #163024; }
  .hd { color: #7d9; font-size: 11px; letter-spacing: 1px; margin-bottom: 6px; }
  .row { display: flex; justify-content: space-between; gap: 8px; margin: 3px 0; font-size: 12px; }
  .k { color: #6d8274; }
  .sig { font-size: 12px; padding: 4px 0; border-bottom: 1px solid #12261c; display: flex; justify-content: space-between; }
  .chart-wrap { min-width: 0; min-height: 0; display: flex; flex-direction: column; background: #070907; }
  .chart-head { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; font-size: 12px; border-bottom: 1px solid #163024; }
  .tf button { background: transparent; color: #6d8274; border: 1px solid #1c3a28; padding: 2px 8px; font-family: inherit; cursor: pointer; }
  .tf button.on { color: #3dff9a; border-color: #3dff9a; }
  #chart { flex: 1; width: 100%; min-height: 0; display: block; }
  .ob { font-size: 12px; }
  .ob-row { display: grid; grid-template-columns: 1fr 72px 72px; padding: 1px 10px; position: relative; height: 18px; align-items: center; }
  .ob-bar { position: absolute; top: 1px; bottom: 1px; right: 0; opacity: .22; }
  .ask { color: #ff8a8a; } .ask .ob-bar { background: #ff5d5d; }
  .bid { color: #3dff9a; } .bid .ob-bar { background: #3dff9a; }
  .spread { text-align: center; padding: 6px 8px; border-top: 1px solid #163024; border-bottom: 1px solid #163024; color: #cfe; font-size: 12px; }
  .bottom { border-top: 1px solid #1c3a28; background: #090d0b; display: flex; flex-direction: column; min-height: 0; }
  .tabs { display: flex; gap: 14px; padding: 6px 12px; border-bottom: 1px solid #163024; font-size: 12px; color: #6d8274; }
  .tabs .on { color: #3dff9a; }
  .tbl { overflow: auto; flex: 1; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th { text-align: left; color: #6d8274; font-weight: 500; padding: 4px 10px; position: sticky; top: 0; background: #090d0b; }
  td { padding: 5px 10px; border-top: 1px solid #12261c; }
  .buy { color: #3dff9a; } .sell { color: #ff8a8a; }
</style>
</head>
<body>
<div class="term">
  <header class="top">
    <div class="brand">OPENOIL</div>
    <div class="sym">USOIL · WTI</div>
    <div class="px" id="px">91.52</div>
    <div id="chg" class="up">+0.34 · +0.37%</div>
    <div class="muted">BRENT <span id="brent">95.10</span></div>
    <div class="muted">SPREAD <span id="spr">3.58</span></div>
    <div class="spacer"></div>
    <div class="muted" id="clock"></div>
    <div class="up">LIVE</div>
  </header>

  <div class="mid">
    <aside class="rail">
      <div class="sec">
        <div class="hd">QUOTE</div>
        <div class="row"><span class="k">BID</span><span class="bid" id="qbid">91.50</span></div>
        <div class="row"><span class="k">ASK</span><span class="ask" id="qask">91.54</span></div>
        <div class="row"><span class="k">HIGH</span><span id="hi">92.40</span></div>
        <div class="row"><span class="k">LOW</span><span id="lo">89.43</span></div>
        <div class="row"><span class="k">CVD</span><span class="up" id="cvd">+1,240</span></div>
      </div>
      <div class="sec">
        <div class="hd">ANALYSIS</div>
        <div class="row"><span class="k">ENSEMBLE</span><span class="up">+0.34</span></div>
        <div class="row"><span class="k">REGIME</span><span>TRENDING</span></div>
        <div class="row"><span class="k">SENTIMENT</span><span class="up">+0.18</span></div>
        <div class="row"><span class="k">4H</span><span>92.40</span></div>
        <div class="row"><span class="k">24H</span><span>93.10</span></div>
        <div class="row"><span class="k">VAR 95</span><span>$150</span></div>
      </div>
      <div class="sec">
        <div class="hd">SIGNALS</div>
        <div class="sig"><span>TECHNICAL</span><span class="up">+0.42</span></div>
        <div class="sig"><span>FUNDAMENTAL</span><span class="up">+0.28</span></div>
        <div class="sig"><span>GEOPOLITICS</span><span class="up">+0.31</span></div>
        <div class="sig"><span>RISK</span><span>0.80x</span></div>
      </div>
    </aside>

    <section class="chart-wrap">
      <div class="chart-head">
        <span>USOIL · CANDLES</span>
        <span class="tf">
          <button>1m</button><button>5m</button><button class="on">15m</button><button>1h</button><button>4h</button>
        </span>
        <span class="muted" id="ohlc">o — h — l — c —</span>
      </div>
      <canvas id="chart"></canvas>
    </section>

    <aside class="rail right">
      <div class="sec" style="padding-bottom:4px">
        <div class="hd">ORDER BOOK</div>
      </div>
      <div class="ob" id="asks"></div>
      <div class="spread" id="midline">91.52 · spread 0.04</div>
      <div class="ob" id="bids"></div>
    </aside>
  </div>

  <footer class="bottom">
    <div class="tabs"><span class="on">TRADES / POSITIONS</span><span>FILLS</span><span>AUDIT</span></div>
    <div class="tbl">
      <table>
        <thead><tr><th>ID</th><th>SIDE</th><th>QTY</th><th>ENTRY</th><th>SL</th><th>TP</th><th>PNL</th><th>STATUS</th></tr></thead>
        <tbody>
          <tr><td>#1024</td><td class="buy">BUY</td><td>0.10</td><td>91.20</td><td>90.40</td><td>92.80</td><td class="up" id="openpnl">+$32</td><td class="up">OPEN</td></tr>
          <tr><td>#1021</td><td class="sell">SELL</td><td>0.05</td><td>92.10</td><td>92.80</td><td>91.20</td><td class="up">+$84</td><td>WIN</td></tr>
          <tr><td>#1018</td><td class="buy">BUY</td><td>0.10</td><td>90.55</td><td>89.90</td><td>91.40</td><td class="dn">-$42</td><td>LOSS</td></tr>
          <tr><td>#1012</td><td class="buy">BUY</td><td>0.20</td><td>89.10</td><td>88.20</td><td>91.00</td><td class="up">+$210</td><td>WIN</td></tr>
        </tbody>
      </table>
    </div>
  </footer>
</div>
<script>
const canvas = document.getElementById('chart');
const ctx = canvas.getContext('2d');
let mid = 91.52;
const candles = [];

function seed() {
  let p = 88.4;
  const now = Date.now();
  for (let i = 60; i >= 0; i--) {
    const o = p;
    const drift = (Math.random() - 0.46) * 0.55;
    const h = o + Math.abs(drift) + Math.random() * 0.35;
    const l = o - Math.abs(drift) * 0.6 - Math.random() * 0.28;
    const c = Math.max(l, Math.min(h, o + drift));
    p = c;
    candles.push({ t: now - i * 15 * 60000, o, h, l, c });
  }
  mid = candles[candles.length - 1].c;
}
seed();

function resize() {
  const r = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.floor(r.width * dpr));
  canvas.height = Math.max(1, Math.floor(r.height * dpr));
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  draw();
}

function draw() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  ctx.clearRect(0, 0, w, h);
  const padL = 8, padR = 62, padT = 12, padB = 22;
  const plotW = w - padL - padR, plotH = h - padT - padB;
  if (plotW < 20 || plotH < 20) return;
  const view = candles.slice(-48);
  let lo = Math.min(...view.map(c => c.l));
  let hi = Math.max(...view.map(c => c.h));
  const pad = (hi - lo) * 0.08 || 0.2;
  lo -= pad; hi += pad;
  const y = v => padT + (hi - v) / (hi - lo) * plotH;
  const slot = plotW / view.length;

  ctx.strokeStyle = '#163024';
  ctx.lineWidth = 1;
  for (let i = 0; i < 5; i++) {
    const gy = padT + (plotH / 4) * i;
    ctx.beginPath(); ctx.moveTo(padL, gy); ctx.lineTo(w - padR, gy); ctx.stroke();
    const price = hi - (hi - lo) * (i / 4);
    ctx.fillStyle = '#6d8274';
    ctx.font = '11px ui-monospace, monospace';
    ctx.textAlign = 'left';
    ctx.fillText(price.toFixed(2), w - padR + 6, gy + 4);
  }

  view.forEach((c, i) => {
    const x = padL + i * slot + slot / 2;
    const up = c.c >= c.o;
    ctx.strokeStyle = up ? '#3dff9a' : '#ff6b6b';
    ctx.fillStyle = up ? '#3dff9a' : '#ff6b6b';
    ctx.beginPath();
    ctx.moveTo(x, y(c.h)); ctx.lineTo(x, y(c.l)); ctx.stroke();
    const top = y(Math.max(c.o, c.c));
    const bot = y(Math.min(c.o, c.c));
    const bh = Math.max(1, bot - top);
    const bw = Math.max(3, slot * 0.62);
    ctx.globalAlpha = up ? 0.9 : 0.85;
    ctx.fillRect(x - bw / 2, top, bw, bh);
    ctx.globalAlpha = 1;
  });

  const last = view[view.length - 1];
  ctx.setLineDash([3, 3]);
  ctx.strokeStyle = '#3dff9a';
  ctx.beginPath(); ctx.moveTo(padL, y(last.c)); ctx.lineTo(w - padR, y(last.c)); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = '#0b100d';
  ctx.fillRect(w - padR + 4, y(last.c) - 8, 54, 16);
  ctx.fillStyle = '#3dff9a';
  ctx.fillText(last.c.toFixed(2), w - padR + 8, y(last.c) + 4);

  document.getElementById('ohlc').textContent =
    'o ' + last.o.toFixed(2) + '  h ' + last.h.toFixed(2) + '  l ' + last.l.toFixed(2) + '  c ' + last.c.toFixed(2);
}

function fmt(n) { return n.toFixed(2); }

function renderBook() {
  const levels = 14;
  let asks = [], bids = [];
  for (let i = levels; i >= 1; i--) {
    const ap = mid + 0.02 * i + (Math.random() - 0.5) * 0.01;
    const bp = mid - 0.02 * i + (Math.random() - 0.5) * 0.01;
    asks.push({ p: ap, s: Math.round(8 + Math.random() * 220) });
    bids.push({ p: bp, s: Math.round(8 + Math.random() * 220) });
  }
  asks.sort((a, b) => b.p - a.p);
  bids.sort((a, b) => b.p - a.p);
  const maxA = Math.max(...asks.map(x => x.s));
  const maxB = Math.max(...bids.map(x => x.s));
  const row = (side, lv, max) => {
    const w = Math.round((lv.s / max) * 100);
    return '<div class="ob-row ' + side + '"><span>' + fmt(lv.p) + '</span><span>' + lv.s + '</span><span></span><div class="ob-bar" style="width:' + w + '%"></div></div>';
  };
  document.getElementById('asks').innerHTML = asks.map(lv => row('ask', lv, maxA)).join('');
  document.getElementById('bids').innerHTML = bids.map(lv => row('bid', lv, maxB)).join('');
  const spread = (asks[asks.length - 1].p - bids[0].p);
  document.getElementById('midline').textContent = fmt(mid) + '  ·  spread ' + Math.abs(spread).toFixed(2);
  document.getElementById('qbid').textContent = fmt(bids[0].p);
  document.getElementById('qask').textContent = fmt(asks[asks.length - 1].p);
}

function tickPrice() {
  const last = candles[candles.length - 1];
  const nxt = last.c + (Math.random() - 0.47) * 0.08;
  last.c = nxt;
  last.h = Math.max(last.h, nxt);
  last.l = Math.min(last.l, nxt);
  if (Math.random() < 0.18) {
    candles.push({ t: Date.now(), o: nxt, h: nxt, l: nxt, c: nxt });
    if (candles.length > 120) candles.shift();
  }
  mid = nxt;
  const chg = mid - 91.18;
  const el = document.getElementById('chg');
  el.textContent = (chg >= 0 ? '+' : '') + chg.toFixed(2) + '  ·  ' + (chg >= 0 ? '+' : '') + ((chg / 91.18) * 100).toFixed(2) + '%';
  el.className = chg >= 0 ? 'up' : 'dn';
  document.getElementById('px').textContent = fmt(mid);
  document.getElementById('brent').textContent = (mid + 3.58).toFixed(2);
  const pnl = (mid - 91.20) * 10;
  const pe = document.getElementById('openpnl');
  pe.textContent = (pnl >= 0 ? '+' : '-') + '$' + Math.abs(pnl).toFixed(0);
  pe.className = pnl >= 0 ? 'up' : 'dn';
  draw();
}

function clock() {
  document.getElementById('clock').textContent = new Date().toISOString().slice(0, 19).replace('T', ' ');
}

window.addEventListener('resize', resize);
clock(); setInterval(clock, 1000);
renderBook(); setInterval(renderBook, 450);
setInterval(tickPrice, 700);
resize();
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
