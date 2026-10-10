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
from openoil.mt5_live import snapshot as mt5_snapshot

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
    <div class="muted">PAPER · not a live perpetual</div>
    <div class="muted" id="clock"></div>
    <div class="up">SIM</div>
  </header>

  <div class="mid">
    <aside class="rail">
      <div class="sec">
        <div class="hd">ACCOUNT</div>
        <div class="row"><span class="k">BALANCE</span><span id="bal">10,000.00</span></div>
        <div class="row"><span class="k">EQUITY</span><span id="eq">10,000.00</span></div>
        <div class="row"><span class="k">MARGIN USED</span><span id="mu">0.00</span></div>
        <div class="row"><span class="k">FREE MARGIN</span><span id="fm">10,000.00</span></div>
        <div class="row"><span class="k">MARGIN LEVEL</span><span id="ml">—</span></div>
        <div class="row"><span class="k">LEVERAGE</span><span>1:100</span></div>
      </div>
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
        <span class="tf" id="tfs">
          <button data-tf="1">1m</button><button data-tf="5">5m</button><button data-tf="15" class="on">15m</button><button data-tf="60">1h</button><button data-tf="240">4h</button>
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
        <tbody id="blotter"></tbody>
      </table>
    </div>
  </footer>
</div>
<script>
const canvas = document.getElementById('chart');
const ctx = canvas.getContext('2d');
const CONTRACT = 1000;
const LEVERAGE = 100;
let mid = 91.52;
let tf = 15;
let balance = 10000;
let nextId = 1025;
const ticks = [];
const closed = [
  {id:1021, side:'SELL', qty:0.05, entry:92.10, sl:92.80, tp:91.20, pnl:84, status:'WIN'},
  {id:1018, side:'BUY', qty:0.10, entry:90.55, sl:89.90, tp:91.40, pnl:-42, status:'LOSS'},
  {id:1012, side:'BUY', qty:0.20, entry:89.10, sl:88.20, tp:91.00, pnl:210, status:'WIN'}
];
const openPos = [
  {id:1024, side:'BUY', qty:0.10, entry:91.20, sl:90.40, tp:92.80}
];

function seedTicks() {
  let p = 88.4;
  const startT = Date.now() - 90 * 240 * 60000;
  const n = 90 * 240;
  for (let i = 0; i < n; i += 2) {
    p += (Math.random() - 0.482) * 0.16;
    ticks.push({ t: startT + i * 60000, p });
  }
  mid = ticks[ticks.length - 1].p;
}
seedTicks();

function bars(minutes) {
  const ms = minutes * 60000;
  const buckets = new Map();
  for (const tk of ticks) {
    const b = Math.floor(tk.t / ms) * ms;
    let c = buckets.get(b);
    if (!c) buckets.set(b, { t: b, o: tk.p, h: tk.p, l: tk.p, c: tk.p });
    else {
      c.h = Math.max(c.h, tk.p);
      c.l = Math.min(c.l, tk.p);
      c.c = tk.p;
    }
  }
  return [...buckets.values()].sort((a, b) => a.t - b.t);
}

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
  const view = (liveMode && window.__mt5Bars && window.__mt5Bars.length)
    ? window.__mt5Bars.slice(-60)
    : bars(tf).slice(-60);
  if (!view.length) return;
  let lo = Math.min(...view.map(c => c.l));
  let hi = Math.max(...view.map(c => c.h));
  const pad = (hi - lo) * 0.08 || 0.2;
  lo -= pad; hi += pad;
  const y = v => padT + (hi - v) / (hi - lo) * plotH;
  const slot = plotW / view.length;
  ctx.strokeStyle = '#163024';
  ctx.lineWidth = 1;
  ctx.font = '11px ui-monospace, monospace';
  ctx.textAlign = 'left';
  for (let i = 0; i < 5; i++) {
    const gy = padT + (plotH / 4) * i;
    ctx.beginPath(); ctx.moveTo(padL, gy); ctx.lineTo(w - padR, gy); ctx.stroke();
    ctx.fillStyle = '#6d8274';
    ctx.fillText((hi - (hi - lo) * (i / 4)).toFixed(2), w - padR + 6, gy + 4);
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
    const bw = Math.max(2, slot * 0.62);
    ctx.globalAlpha = 0.9;
    ctx.fillRect(x - bw / 2, top, bw, Math.max(1, bot - top));
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
    tfLabel() + '  o ' + last.o.toFixed(2) + '  h ' + last.h.toFixed(2) + '  l ' + last.l.toFixed(2) + '  c ' + last.c.toFixed(2);
  const hiEl = document.getElementById('hi');
  const loEl = document.getElementById('lo');
  hiEl.textContent = Math.max(...view.map(c => c.h)).toFixed(2);
  loEl.textContent = Math.min(...view.map(c => c.l)).toFixed(2);
}

function tfLabel() {
  return ({1:'1m', 5:'5m', 15:'15m', 60:'1h', 240:'4h'})[tf];
}

function money(n) {
  return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function pnlOf(pos, px) {
  const dir = pos.side === 'BUY' ? 1 : -1;
  return dir * (px - pos.entry) * pos.qty * CONTRACT;
}
function marginOf(pos, px) {
  return pos.qty * CONTRACT * px / LEVERAGE;
}

function renderBlotter() {
  const rows = [];
  for (const pos of openPos) {
    const u = pnlOf(pos, mid);
    const cls = u >= 0 ? 'up' : 'dn';
    const side = pos.side === 'BUY' ? 'buy' : 'sell';
    rows.push('<tr><td>#' + pos.id + '</td><td class="' + side + '">' + pos.side + '</td><td>' + pos.qty.toFixed(2) +
      '</td><td>' + pos.entry.toFixed(2) + '</td><td>' + pos.sl.toFixed(2) + '</td><td>' + pos.tp.toFixed(2) +
      '</td><td class="' + cls + '">' + (u >= 0 ? '+' : '-') + '$' + Math.abs(u).toFixed(0) +
      '</td><td class="up">OPEN</td></tr>');
  }
  for (const pos of closed.slice(0, 6)) {
    const side = pos.side === 'BUY' ? 'buy' : 'sell';
    const cls = pos.pnl >= 0 ? 'up' : 'dn';
    rows.push('<tr><td>#' + pos.id + '</td><td class="' + side + '">' + pos.side + '</td><td>' + pos.qty.toFixed(2) +
      '</td><td>' + pos.entry.toFixed(2) + '</td><td>' + pos.sl.toFixed(2) + '</td><td>' + pos.tp.toFixed(2) +
      '</td><td class="' + cls + '">' + (pos.pnl >= 0 ? '+' : '-') + '$' + Math.abs(pos.pnl).toFixed(0) +
      '</td><td>' + pos.status + '</td></tr>');
  }
  document.getElementById('blotter').innerHTML = rows.join('');
}

function renderAccount() {
  let upnl = 0, used = 0;
  for (const pos of openPos) {
    upnl += pnlOf(pos, mid);
    used += marginOf(pos, mid);
  }
  const equity = balance + upnl;
  const free = equity - used;
  const level = used > 0 ? (equity / used) * 100 : 0;
  document.getElementById('bal').textContent = money(balance);
  document.getElementById('eq').textContent = money(equity);
  document.getElementById('mu').textContent = money(used);
  document.getElementById('fm').textContent = money(free);
  document.getElementById('ml').textContent = used > 0 ? level.toFixed(0) + '%' : '—';
}

function managePositions() {
  for (let i = openPos.length - 1; i >= 0; i--) {
    const pos = openPos[i];
    const hitTp = pos.side === 'BUY' ? mid >= pos.tp : mid <= pos.tp;
    const hitSl = pos.side === 'BUY' ? mid <= pos.sl : mid >= pos.sl;
    if (hitTp || hitSl) {
      const realized = pnlOf(pos, hitTp ? pos.tp : pos.sl);
      balance += realized;
      closed.unshift({ ...pos, pnl: realized, status: realized >= 0 ? 'WIN' : 'LOSS' });
      openPos.splice(i, 1);
    }
  }
  if (openPos.length < 2 && Math.random() < 0.04) {
    const side = Math.random() > 0.45 ? 'BUY' : 'SELL';
    const qty = Math.random() > 0.5 ? 0.10 : 0.05;
    const sl = side === 'BUY' ? mid - 0.80 : mid + 0.80;
    const tp = side === 'BUY' ? mid + 1.40 : mid - 1.40;
    openPos.push({ id: nextId++, side, qty, entry: mid, sl, tp });
  }
}

function fmt(n) { return n.toFixed(2); }

function renderBook() {
  const levels = 14;
  const asks = [], bids = [];
  for (let i = 1; i <= levels; i++) {
    asks.push({ p: mid + 0.02 * i, s: Math.round(12 + Math.random() * 240) });
    bids.push({ p: mid - 0.02 * i, s: Math.round(12 + Math.random() * 240) });
  }
  asks.sort((a, b) => b.p - a.p);
  const maxA = Math.max(...asks.map(x => x.s));
  const maxB = Math.max(...bids.map(x => x.s));
  const row = (side, lv, max) => {
    const w = Math.round((lv.s / max) * 100);
    return '<div class="ob-row ' + side + '"><span>' + fmt(lv.p) + '</span><span>' + lv.s + '</span><span></span><div class="ob-bar" style="width:' + w + '%"></div></div>';
  };
  document.getElementById('asks').innerHTML = asks.map(lv => row('ask', lv, maxA)).join('');
  document.getElementById('bids').innerHTML = bids.map(lv => row('bid', lv, maxB)).join('');
  const bestAsk = asks[asks.length - 1].p;
  const bestBid = bids[0].p;
  document.getElementById('midline').textContent = fmt(mid) + '  ·  spread ' + (bestAsk - bestBid).toFixed(2);
  document.getElementById('qbid').textContent = fmt(bestBid);
  document.getElementById('qask').textContent = fmt(bestAsk);
  document.getElementById('spr').textContent = (3.58 + (Math.random() - 0.5) * 0.04).toFixed(2);
}

function tickPrice() {
  if (liveMode) return;
  const prev = ticks[ticks.length - 1].p;
  const nxt = prev + (Math.random() - 0.47) * 0.07;
  ticks.push({ t: Date.now(), p: nxt });
  if (ticks.length > 30000) ticks.splice(0, ticks.length - 20000);
  mid = nxt;
  const base = ticks[Math.max(0, ticks.length - 240)].p;
  const chg = mid - base;
  const el = document.getElementById('chg');
  el.textContent = (chg >= 0 ? '+' : '') + chg.toFixed(2) + '  ·  ' + (chg >= 0 ? '+' : '') + ((chg / base) * 100).toFixed(2) + '%';
  el.className = chg >= 0 ? 'up' : 'dn';
  document.getElementById('px').textContent = fmt(mid);
  document.getElementById('brent').textContent = (mid + 3.58).toFixed(2);
  managePositions();
  renderAccount();
  renderBlotter();
  draw();
}

document.getElementById('tfs').addEventListener('click', (ev) => {
  const btn = ev.target.closest('button');
  if (!btn) return;
  tf = +btn.dataset.tf;
  document.querySelectorAll('#tfs button').forEach(b => b.classList.toggle('on', b === btn));
  draw();
});

function clock() {
  document.getElementById('clock').textContent = new Date().toISOString().slice(0, 19).replace('T', ' ');
}
let liveMode = false;

async function pullMt5() {
  try {
    const res = await fetch('/mt5/snapshot');
    const data = await res.json();
    if (!data || !data.connected) return;
    liveMode = true;
    const badge = document.querySelector('header .up');
    if (badge) badge.textContent = 'MT5';
    const note = document.querySelector('header .muted');
    if (data.account && typeof data.account === 'object' && data.account.balance != null) {
      const a = data.account;
      document.getElementById('bal').textContent = money(Number(a.balance));
      document.getElementById('eq').textContent = money(Number(a.equity ?? a.balance));
      document.getElementById('mu').textContent = money(Number(a.margin || 0));
      document.getElementById('fm').textContent = money(Number(a.margin_free ?? (Number(a.equity || a.balance) - Number(a.margin || 0))));
      document.getElementById('ml').textContent = a.margin_level != null ? Number(a.margin_level).toFixed(0) + '%' : '—';
    }
    if (Array.isArray(data.bars) && data.bars.length) {
      window.__mt5Bars = data.bars;
      const last = data.bars[data.bars.length - 1];
      mid = last.c;
      document.getElementById('px').textContent = fmt(mid);
      draw();
    }
  } catch (err) {}
}

window.addEventListener('resize', resize);
clock(); setInterval(clock, 1000);
renderBook(); setInterval(renderBook, 450);
renderAccount(); renderBlotter();
pullMt5(); setInterval(pullMt5, 5000);
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

@app.get("/mt5/snapshot")
def mt5_state():
    return mt5_snapshot()

@app.get("/health")
def health():
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}

@app.get("/price")
def price():
    return {"symbol": "USOIL", "last": HIST_PRICES[-1], "history": HIST_PRICES[-20:]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
