// app.js — Frontend logic for Wearable Data Dashboard

// Use explicit localhost so there's no ambiguity
const API    = 'http://localhost:3000/api';
const WS_URL = 'ws://localhost:3000';

let ws        = null;
let feedCount = 0;
let hrChart   = null;
let stepsChart = null;

// ── Toast ─────────────────────────────────────────────────────────────────────
function showToast(msg, isError = false) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'show' + (isError ? ' err' : '');
  setTimeout(() => { t.className = ''; }, 3000);
}

// ── Load dashboard ────────────────────────────────────────────────────────────
async function loadDashboard() {
  const userId = document.getElementById('user-input').value.trim();
  if (!userId) return showToast('Enter a User ID', true);

  try {
    const [statsRes, historyRes] = await Promise.all([
      fetch(`${API}/wearable/stats/${userId}`),
      fetch(`${API}/wearable/history/${userId}`)
    ]);

    const statsJson   = await statsRes.json();
    const historyJson = await historyRes.json();

    if (!statsJson.success) {
      // Clear cards if no data
      ['stat-hr','stat-steps','stat-cal','stat-sleep','stat-total'].forEach(id => {
        document.getElementById(id).textContent = '--';
      });
      document.getElementById('history-count').textContent = '';
      document.getElementById('history-body').innerHTML =
        `<tr><td colspan="6" style="color:#8b949e;padding:12px">No data found for ${userId}</td></tr>`;
      return showToast(`No data found for ${userId}`, true);
    }

    const s = statsJson.stats;
    document.getElementById('stat-hr').textContent    = s.avgHeartRate;
    document.getElementById('stat-steps').textContent = s.totalSteps.toLocaleString();
    document.getElementById('stat-sleep').textContent = s.avgSleepHours;
    document.getElementById('stat-total').textContent = s.totalRecords;

    if (historyJson.success && historyJson.data.length > 0) {
      document.getElementById('stat-cal').textContent = historyJson.data[0].calories;
      renderCharts(historyJson.data);
      renderTable(historyJson.data);
      document.getElementById('history-count').textContent = `${historyJson.count} records`;
    }

    showToast(`Loaded data for ${userId}`);
  } catch (err) {
    console.error('loadDashboard error:', err);
    showToast('Failed to fetch — is the server running?', true);
  }
}

// ── Charts ────────────────────────────────────────────────────────────────────
function renderCharts(data) {
  const sorted    = [...data].reverse();
  const labels    = sorted.map(d => new Date(d.timestamp).toLocaleTimeString());
  const hrData    = sorted.map(d => d.heartRate);
  const stepsData = sorted.map(d => d.steps);
  const calData   = sorted.map(d => d.calories);

  if (hrChart)    hrChart.destroy();
  if (stepsChart) stepsChart.destroy();

  hrChart = new window.Chart(document.getElementById('hrChart'), {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Heart Rate (bpm)',
        data: hrData,
        borderColor: '#f85149',
        backgroundColor: 'rgba(248,81,73,0.1)',
        tension: 0.4, fill: true,
        pointBackgroundColor: '#f85149', pointRadius: 4,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: '#8b949e', font: { size: 11 } } } },
      scales: {
        x: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: '#21262d' } },
        y: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: '#21262d' } }
      }
    }
  });

  stepsChart = new window.Chart(document.getElementById('stepsChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Steps',    data: stepsData, backgroundColor: 'rgba(88,166,255,0.7)',  borderRadius: 4, yAxisID: 'y'  },
        { label: 'Calories', data: calData,   backgroundColor: 'rgba(227,179,65,0.7)', borderRadius: 4, yAxisID: 'y1' }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: '#8b949e', font: { size: 11 } } } },
      scales: {
        x:  { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: '#21262d' } },
        y:  { ticks: { color: '#58a6ff', font: { size: 10 } }, grid: { color: '#21262d' }, position: 'left'  },
        y1: { ticks: { color: '#e3b341', font: { size: 10 } }, grid: { drawOnChartArea: false }, position: 'right' }
      }
    }
  });
}

// ── History table ─────────────────────────────────────────────────────────────
function renderTable(data) {
  const tbody = document.getElementById('history-body');
  tbody.innerHTML = '';
  data.forEach((row, i) => {
    const hrClass = row.heartRate > 120 ? 'hr-high' : row.heartRate < 60 ? 'hr-low' : 'hr-ok';
    tbody.innerHTML += `
      <tr>
        <td style="color:#8b949e">${i + 1}</td>
        <td><span class="badge ${hrClass}">${row.heartRate}</span></td>
        <td>${row.steps.toLocaleString()}</td>
        <td>${row.calories}</td>
        <td>${row.sleepHours}h</td>
        <td style="color:#8b949e;font-size:0.72rem">${new Date(row.timestamp).toLocaleString()}</td>
      </tr>`;
  });
}

// ── WebSocket ─────────────────────────────────────────────────────────────────
function connectWS() {
  if (ws && ws.readyState === WebSocket.OPEN) return showToast('Already connected');

  try {
    ws = new WebSocket(WS_URL);
  } catch (e) {
    return showToast('Could not create WebSocket', true);
  }

  ws.onopen = () => {
    setWsStatus(true);
    showToast('WebSocket connected');
    document.getElementById('btn-connect').style.display    = 'none';
    document.getElementById('btn-disconnect').style.display = 'inline-block';
    addFeedItem({ type: 'connected', message: 'Connected to WebSocket server' });
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      addFeedItem(msg);
      if (msg.type === 'success' && msg.userId === document.getElementById('user-input').value.trim()) {
        loadDashboard();
      }
    } catch {
      addFeedItem({ type: 'error', message: String(event.data) });
    }
  };

  ws.onclose = () => {
    setWsStatus(false);
    document.getElementById('btn-connect').style.display    = 'inline-block';
    document.getElementById('btn-disconnect').style.display = 'none';
    addFeedItem({ type: 'error', message: 'Disconnected from server' });
  };

  ws.onerror = (e) => {
    console.error('WS error', e);
    showToast('WebSocket error — check server is running', true);
    setWsStatus(false);
  };
}

function disconnectWS() {
  if (ws) ws.close();
}

function setWsStatus(connected) {
  document.getElementById('ws-dot').className       = connected ? 'connected' : '';
  document.getElementById('ws-label').textContent   = connected ? 'WebSocket: Connected' : 'WebSocket: Disconnected';
}

// ── Live feed ─────────────────────────────────────────────────────────────────
function addFeedItem(msg) {
  feedCount++;
  document.getElementById('feed-count').textContent = `${feedCount} messages`;
  const feed = document.getElementById('live-feed');
  if (feedCount === 1) feed.innerHTML = '';

  const div = document.createElement('div');
  const ts  = new Date().toLocaleTimeString();

  if (msg.type === 'success') {
    div.className = 'feed-item success';
    div.innerHTML = `<div class="ts">${ts}</div><div>✅ <span class="uid">${msg.userId}</span> — stored (ID: ${msg.id})</div>`;
  } else if (msg.type === 'validation_error') {
    div.className = 'feed-item error';
    div.innerHTML = `<div class="ts">${ts}</div><div>⚠️ Validation: ${(msg.errors || [msg.message]).join(', ')}</div>`;
  } else if (msg.type === 'connected') {
    div.className = 'feed-item';
    div.innerHTML = `<div class="ts">${ts}</div><div>🔌 ${msg.message}</div>`;
  } else {
    div.className = 'feed-item error';
    div.innerHTML = `<div class="ts">${ts}</div><div>❌ ${msg.message}</div>`;
  }

  feed.insertBefore(div, feed.firstChild);
}

// ── Send mock data ────────────────────────────────────────────────────────────
function sendMockData() {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    return showToast('Connect WebSocket first', true);
  }
  const userId = document.getElementById('user-input').value.trim() || 'U123';
  ws.send(JSON.stringify({
    userId,
    deviceId:   'D' + Math.floor(Math.random() * 900 + 100),
    heartRate:  Math.floor(Math.random() * 120 + 55),
    steps:      Math.floor(Math.random() * 12000),
    calories:   Math.floor(Math.random() * 600 + 50),
    sleepHours: parseFloat((Math.random() * 8 + 2).toFixed(1)),
    timestamp:  new Date().toISOString(),
  }));
  showToast(`Sent mock data for ${userId}`);
}

// ── Seed data if DB is empty, then load ───────────────────────────────────────
async function seedAndLoad() {
  try {
    // Check if U123 already has data
    const check = await fetch(`${API}/wearable/stats/U123`);
    const json  = await check.json();

    if (!json.success) {
      // Insert a few seed records so the dashboard has something to show
      const seeds = [
        { userId:'U123', deviceId:'D456', heartRate:82,  steps:5400,  calories:230, sleepHours:6.5, timestamp:'2026-04-02T08:00:00Z' },
        { userId:'U123', deviceId:'D456', heartRate:95,  steps:8200,  calories:410, sleepHours:7.0, timestamp:'2026-04-02T09:00:00Z' },
        { userId:'U123', deviceId:'D456', heartRate:110, steps:12000, calories:600, sleepHours:5.5, timestamp:'2026-04-02T10:00:00Z' },
      ];
      for (const s of seeds) {
        await fetch(`${API}/wearable/test`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(s)
        });
      }
    }
  } catch (e) {
    console.warn('Seed check failed:', e.message);
  }
  loadDashboard();
}

window.addEventListener('load', seedAndLoad);
