"""
OpenOil — main entry point.
Run: python -m openoil.main
"""

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

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
from openoil.desk import build as build_desk

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
  .term { height: 100vh; display: grid; grid-template-rows: 48px 28px minmax(0, 1fr) 176px; }
  .top { display: flex; align-items: center; gap: 22px; padding: 0 14px; border-bottom: 1px solid #1c3a28; background: #0b100d; }
  .brand { color: #fff; letter-spacing: 2px; font-weight: 700; font-size: 16px; }
  .sym { color: #9cffc4; font-size: 13px; }
  .px { font-size: 20px; color: #3dff9a; }
  .up { color: #3dff9a; } .dn { color: #ff6b6b; }
  .muted { color: #6d8274; font-size: 12px; }
  .spacer { flex: 1; }
  .mid { display: grid; grid-template-columns: 270px minmax(0, 1fr) 300px; min-height: 0; }
  .rail { min-height: 0; overflow: auto; background: #090d0b; border-right: 1px solid #1c3a28; scrollbar-width: thin; scrollbar-color: #244832 transparent; }
  .rail::-webkit-scrollbar, .tbl::-webkit-scrollbar { width: 8px; height: 8px; }
  .rail::-webkit-scrollbar-track, .tbl::-webkit-scrollbar-track { background: #090d0b; }
  .rail::-webkit-scrollbar-thumb, .tbl::-webkit-scrollbar-thumb { background: #1c3a28; border: 2px solid #090d0b; border-radius: 8px; }
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
  .ob-row { display: grid; grid-template-columns: 1fr 64px; padding: 1px 10px; position: relative; height: 20px; align-items: center; }
  .ob-row span:last-child { text-align: right; }
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
  .tape { display: flex; align-items: center; gap: 14px; padding: 0 12px; border-bottom: 1px solid #1c3a28; background: #0b100d; overflow: hidden; white-space: nowrap; font-size: 12px; }
  .tape a { color: #3dff9a; text-decoration: none; letter-spacing: 1px; }
  .alert { color: #ffb4b4; }
  .wire { color: #9cffc4; }
  .news-item { padding: 8px 0; border-bottom: 1px solid #12261c; font-size: 12px; line-height: 1.4; }
  a.nav { color: #9cffc4; text-decoration: none; }
</style>
</head>
<body>
<div class="term">
  <header class="top">
    <div class="brand">OPENOIL</div>
    <a class="nav" href="/">DESK</a>
    <a class="nav" href="/news">NEWS</a>
    <div class="sym">USOIL · WTI</div>
    <div class="px" id="px">91.52</div>
    <div id="chg" class="up">+0.34 · +0.37%</div>
    <div class="muted">BRENT <span id="brent">95.10</span></div>
    <div class="muted">SPREAD <span id="spr">3.58</span></div>
    <div class="spacer"></div>
    <div class="muted"><span id="modeLabel">OFFLINE · waiting for MT5</span></div>
    <div class="muted" id="clock"></div>
    <div class="up">SIM</div>
  </header>
  <div class="tape"><a href="/news">ALERTS</a><span id="tape">waiting for headlines</span></div>

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
        <div class="row"><span class="k">CVD</span><span id="cvd">—</span></div>
      </div>
      <div class="sec">
        <div class="hd">ANALYSIS</div>
        <div class="row"><span class="k">ENSEMBLE</span><span id="ens">—</span></div>
        <div class="row"><span class="k">REGIME</span><span id="regime">—</span></div>
        <div class="row"><span class="k">SENTIMENT</span><span id="sent">—</span></div>
        <div class="row"><span class="k">4H</span><span id="t4">—</span></div>
        <div class="row"><span class="k">24H</span><span id="t24">—</span></div>
        <div class="row"><span class="k">VAR 95</span><span>$150</span></div>
      </div>
      <div class="sec">
        <div class="hd">SIGNALS</div>
<div id="signals"></div>
      </div>
      <div class="sec">
        <div class="hd">NEWS <a class="nav" href="/news">ALL</a></div>
        <div id="newsrail"></div>
      </div>
    </aside>

    <section class="chart-wrap">
      <div class="chart-head">
        <span id="chartTitle">USOUSD · 15m</span>
        <span class="tf" id="tfs">
          <button data-tf="1">1m</button><button data-tf="5">5m</button><button data-tf="15" class="on">15m</button><button data-tf="60">1h</button><button data-tf="240">4h</button>
        </span>
        <span class="muted" id="ohlc">o — h — l — c —</span>
      </div>
      <canvas id="chart"></canvas>
    </section>

    <aside class="rail right">
      <div class="sec" style="padding-bottom:4px">
        <div class="hd"><span id="bookTitle">ORDER BOOK</span></div>
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
let bars = [];
let state = null;

function money(n) {
  const v = Number(n);
  if (!Number.isFinite(v)) return '—';
  return v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function fmt(n) {
  const v = Number(n);
  const digits = (state && state.quote && state.quote.digits) || 2;
  return Number.isFinite(v) ? v.toFixed(digits) : '—';
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
  if (!bars.length) {
    ctx.fillStyle = '#6d8274';
    ctx.font = '14px ui-monospace, monospace';
    const msg = (state && state.error) ? state.error : 'No MT5 candles yet.';
    wrap(msg, 16, 28, w - 24);
    return;
  }
  const padL = 8, padR = 62, padT = 12, padB = 22;
  const plotW = w - padL - padR, plotH = h - padT - padB;
  if (plotW < 20 || plotH < 20) return;
  const view = bars.slice(-80);
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
    ctx.fillRect(x - bw / 2, top, bw, Math.max(1, bot - top));
  });
  const last = view[view.length - 1];
  document.getElementById('ohlc').textContent =
    'o ' + fmt(last.o) + '  h ' + fmt(last.h) + '  l ' + fmt(last.l) + '  c ' + fmt(last.c);
}

function wrap(msg, x, y, maxW) {
  const words = String(msg).split(' ');
  let line = '';
  words.forEach(word => {
    const test = line + word + ' ';
    if (ctx.measureText(test).width > maxW) {
      ctx.fillText(line, x, y);
      line = word + ' ';
      y += 18;
    } else line = test;
  });
  ctx.fillText(line, x, y);
}

function renderBook(book) {
  const title = document.getElementById('bookTitle');
  if (!book) {
    if (title) title.textContent = 'ORDER BOOK';
    document.getElementById('asks').innerHTML = '';
    document.getElementById('bids').innerHTML = '';
    document.getElementById('midline').textContent = 'no book';
    return;
  }
  if (title) title.textContent = book.label || 'ORDER BOOK';
  const rows = (side, levels) => {
    const max = Math.max(1, ...levels.map(lv => Number(lv.size || lv.volume || 0)));
    return levels.map(lv => {
      const px = Number(lv.price || lv.p);
      const sz = Number(lv.size || lv.volume || 0);
      const w = sz ? Math.round((sz / max) * 100) : 0;
      return '<div class="ob-row ' + side + '"><span>' + fmt(px) + '</span><span>' + (sz ? sz : '') + '</span><div class="ob-bar" style="width:' + w + '%"></div></div>';
    }).join('');
  };
  const asks = (book.asks || []).slice().reverse();
  document.getElementById('asks').innerHTML = rows('ask', asks);
  document.getElementById('bids').innerHTML = rows('bid', book.bids || []);
  const bestBid = (book.bids && book.bids[0] && (book.bids[0].price || book.bids[0].p)) || null;
  const bestAsk = asks.length ? (asks[asks.length - 1].price || asks[asks.length - 1].p) : null;
  document.getElementById('midline').textContent = bestBid && bestAsk
    ? (fmt(bestBid) + '  /  ' + fmt(bestAsk) + '   ·   ' + (book.source === 'mt5' ? 'depth' : 'market watch'))
    : 'no depth from terminal';
}

function renderAccount(account) {
  if (!account || account.balance == null) {
    ['bal','eq','mu','fm','ml'].forEach(id => { const el = document.getElementById(id); if (el) el.textContent = '—'; });
    return;
  }
  document.getElementById('bal').textContent = money(account.balance);
  document.getElementById('eq').textContent = money(account.equity ?? account.balance);
  document.getElementById('mu').textContent = money(account.margin || 0);
  document.getElementById('fm').textContent = money(account.margin_free ?? (Number(account.equity || account.balance) - Number(account.margin || 0)));
  document.getElementById('ml').textContent = account.margin_level != null ? Number(account.margin_level).toFixed(0) + '%' : '—';
}

function renderPositions(rows) {
  const body = document.getElementById('blotter');
  if (!rows || !rows.length) {
    body.innerHTML = '<tr><td colspan="8">No open terminal positions. Paper fills are off.</td></tr>';
    return;
  }
  body.innerHTML = rows.map(pos => {
    const pnl = Number(pos.pnl);
    const cls = pnl >= 0 ? 'up' : 'dn';
    const side = String(pos.side).toUpperCase() === 'SELL' ? 'sell' : 'buy';
    return '<tr><td>#' + (pos.id || '') + '</td><td class="' + side + '">' + (pos.side || '') + '</td><td>' + (pos.qty ?? '') +
      '</td><td>' + fmt(pos.entry) + '</td><td>' + fmt(pos.sl) + '</td><td>' + fmt(pos.tp) +
      '</td><td class="' + cls + '">' + (Number.isFinite(pnl) ? ((pnl >= 0 ? '+' : '') + pnl.toFixed(2)) : '—') +
      '</td><td>' + (pos.status || 'OPEN') + '</td></tr>';
  }).join('');
}

function apply(data) {
  state = data;
  bars = data.bars || [];
  const q = data.quote;
  const badge = document.querySelector('header .up');
  const mode = document.getElementById('modeLabel');
  if (data.mode === 'mt5' && q) {
    if (badge) badge.textContent = data.price_source === 'terminal' ? 'MT5' : 'MDATA';
    if (mode) mode.textContent = (data.live_orders ? 'LIVE ARMED' : 'READ ONLY') + ' · ' + (data.price_source || 'mt5');
    document.getElementById('px').textContent = fmt(q.last);
    const chg = document.getElementById('chg');
    chg.textContent = q.change == null
      ? '24h —'
      : ('24h  ' + (q.change >= 0 ? '+' : '') + fmt(q.change) + '  ·  ' + (Number(q.change_pct) >= 0 ? '+' : '') + Number(q.change_pct).toFixed(2) + '%');
    chg.className = q.change >= 0 ? 'up' : 'dn';
    document.getElementById('qbid').textContent = fmt(q.bid);
    document.getElementById('qask').textContent = fmt(q.ask);
    if (q.spread != null) document.getElementById('spr').textContent = Number(q.spread).toFixed(2);
    const title = document.getElementById('chartTitle');
    if (title) {
      const minutes = Number(data.timeframe || 15);
      title.textContent = (data.symbol || 'USOUSD') + ' · ' + (minutes >= 60 ? (minutes / 60) + 'h' : minutes + 'm');
    }
    const hi = Math.max(...bars.map(b => b.h));
    const lo = Math.min(...bars.map(b => b.l));
    document.getElementById('hi').textContent = fmt(hi);
    document.getElementById('lo').textContent = fmt(lo);
  } else {
    if (badge) badge.textContent = 'OFF';
    if (mode) mode.textContent = 'OFFLINE · ' + (data.error || 'no MT5 data');
    document.getElementById('px').textContent = '—';
    document.getElementById('chg').textContent = 'no simulated price';
  }
  if (data.symbol) {
    const sym = document.querySelector('.sym');
    if (sym) sym.textContent = data.symbol;
  }
  const a = data.analysis || {};
  document.getElementById('ens').textContent = a.ensemble == null ? '—' : (a.ensemble >= 0 ? '+' : '') + Number(a.ensemble).toFixed(2);
  document.getElementById('regime').textContent = a.regime || '—';
  document.getElementById('sent').textContent = a.sentiment == null ? '—' : (a.sentiment >= 0 ? '+' : '') + Number(a.sentiment).toFixed(2);
  document.getElementById('t4').textContent = a.target_4h == null ? '—' : fmt(a.target_4h);
  document.getElementById('t24').textContent = a.target_24h == null ? '—' : fmt(a.target_24h);
  document.getElementById('signals').innerHTML = (data.signals || []).map(s =>
    '<div class="sig"><span>' + s.agent + '</span><span>' + (Number(s.bias) >= 0 ? '+' : '') + Number(s.bias || 0).toFixed(2) + '</span></div>'
  ).join('') || '<div class="sig"><span>NO SIGNAL</span><span>—</span></div>';
  const news = data.news || {};
  const rows = news.alerts && news.alerts.length ? news.alerts : (news.headlines || []).map(title => ({ title: title, tag: 'WIRE' }));
  const tape = document.getElementById('tape');
  if (tape) tape.innerHTML = rows.slice(0, 6).map(row => '<span class="' + (row.tag === 'ALERT' ? 'alert' : 'wire') + '">' + row.tag + '</span> ' + row.title).join(' &nbsp;·&nbsp; ') || 'no headlines';
  const rail = document.getElementById('newsrail');
  if (rail) {
    const upcoming = (news.calendar || []).filter(item => item.oil).slice(0, 2).map(item =>
      '<div class="news-item"><span class="wire">FF</span> ' + item.title + ' · ' + (item.impact || '') + ' · ' + (item.forecast || 'n/a') + '</div>'
    ).join('');
    rail.innerHTML = (rows.slice(0, 4).map(row => '<div class="news-item"><span class="' + (row.tag === 'ALERT' ? 'alert' : 'wire') + '">' + row.tag + '</span> ' + row.title + '</div>').join('') || '') + upcoming || '<div class="news-item">no oil headlines</div>';
  }
  renderAccount(data.account);
  renderBook(data.book);
  renderPositions(data.positions);
  draw();
}

let tf = 15;
async function pull() {
  try {
    const res = await fetch('/api/state?tf=' + tf);
    apply(await res.json());
  } catch (err) {
    apply({ mode: 'offline', error: 'Desk request failed', bars: [], positions: [] });
  }
}
async function pullQuote() {
  try {
    const q = await (await fetch('/api/quote')).json();
    if (!q || q.bid == null) return;
    document.getElementById('qbid').textContent = fmt(q.bid);
    document.getElementById('qask').textContent = fmt(q.ask);
    document.getElementById('px').textContent = fmt(q.last || q.bid);
    if (q.spread != null) document.getElementById('spr').textContent = Number(q.spread).toFixed((state && state.quote && state.quote.digits) || 2);
    if (bars.length && q.bid != null) {
      const last = bars[bars.length - 1];
      const px = Number(q.bid);
      last.c = px;
      last.h = Math.max(Number(last.h), px);
      last.l = Math.min(Number(last.l), px);
      draw();
    }
  } catch (err) {}
}
document.getElementById('tfs').addEventListener('click', (event) => {
  const button = event.target.closest('button');
  if (!button) return;
  tf = button.dataset.tf;
  document.querySelectorAll('#tfs button').forEach((item) => item.classList.toggle('on', item === button));
  pull();
});

function clock() {
  document.getElementById('clock').textContent = new Date().toISOString().slice(0, 19).replace('T', ' ');
}
window.addEventListener('resize', resize);
clock(); setInterval(clock, 1000);
pull(); setInterval(pull, 4000); setInterval(pullQuote, 1000);
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

NEWS_HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>OpenOil News</title>
<style>
  body { margin: 0; background: #070907; color: #d7ffe4; font-family: ui-monospace, "Cascadia Mono", "Courier New", monospace; }
  header { display: flex; gap: 18px; align-items: center; padding: 14px 18px; border-bottom: 1px solid #1c3a28; }
  a { color: #3dff9a; text-decoration: none; }
  main { max-width: 860px; padding: 18px; }
  .meta { color: #6d8274; font-size: 12px; margin-bottom: 14px; }
  .item { padding: 12px 0; border-bottom: 1px solid #163024; }
  .alert { color: #ffb4b4; } .wire { color: #9cffc4; }
  h1 { font-size: 16px; letter-spacing: 2px; margin: 0; }
</style>
</head>
<body>
<header>
  <h1>OPENOIL</h1>
  <a href="/">DESK</a>
  <a href="/news">NEWS</a>
</header>
<main>
  <div class="meta" id="meta">loading</div>
  <div id="list"></div>
</main>
<script>
async function load() {
  const data = await (await fetch('/api/news')).json();
  document.getElementById('meta').textContent =
    'bias ' + Number(data.bias || 0).toFixed(2) + '  ·  ' + ((data.sources || []).join(', ') || 'no source yet');
  const rows = data.headlines || [];
  const hot = new Set((data.alerts || []).filter(a => a.tag === 'ALERT').map(a => a.title));
  document.getElementById('list').innerHTML = rows.map(title => {
    const tag = hot.has(title) ? 'ALERT' : 'WIRE';
    return '<div class="item"><div class="' + (tag === 'ALERT' ? 'alert' : 'wire') + '">' + tag + '</div>' + title + '</div>';
  }).join('') || '<div class="item">No oil headlines yet.</div>';
  const cal = data.calendar || [];
  if (cal.length) {
    document.getElementById('list').innerHTML += '<div class="item"><div class="wire">FOREX FACTORY</div></div>' + cal.map(item =>
      '<div class="item"><div class="wire">' + (item.country || '') + ' · ' + (item.impact || '') + '</div>' +
      item.title + ' · forecast ' + (item.forecast || 'n/a') + ' · previous ' + (item.previous || 'n/a') + '</div>'
    ).join('');
  }
}
load();
setInterval(load, 20000);
</script>
</body>
</html>
"""

@app.get("/news", response_class=HTMLResponse)
def news_page():
    return NEWS_HTML

@app.get("/api/news")
def api_news():
    from openoil.desk import news_public
    return news_public()

@app.get("/api/state")
def api_state(tf: int = 15):
    return build_desk(tf)

@app.get("/api/quote")
def api_quote():
    from openoil.mt5_live import quote_from_terminal
    return quote_from_terminal() or {}

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
