// testClient.js
// Simulates a wearable device — sends random data to the WebSocket server
// Run with: node testClient.js

const WebSocket = require('ws');

const WS_URL = 'ws://localhost:8081';
const SEND_INTERVAL_MS = 3000; // Send data every 3 seconds

let ws;
let reconnectTimer = null;

// ── Random data generators ───────────────────────────────────────────────────
const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const randomFloat = (min, max) => parseFloat((Math.random() * (max - min) + min).toFixed(1));

const generatePayload = () => ({
  userId:     'U' + randomInt(100, 105),          // Simulates 6 different users
  deviceId:   'D' + randomInt(400, 405),
  heartRate:  randomInt(55, 160),
  steps:      randomInt(0, 15000),
  calories:   randomInt(50, 800),
  sleepHours: randomFloat(3, 10),
  timestamp:  new Date().toISOString(),
});

// ── Connect to WebSocket server ──────────────────────────────────────────────
const connect = () => {
  console.log(`[CLIENT] Connecting to ${WS_URL}...`);
  ws = new WebSocket(WS_URL);

  ws.on('open', () => {
    console.log('[CLIENT] Connected to WebSocket server');

    // Start sending data at regular intervals
    const interval = setInterval(() => {
      if (ws.readyState !== WebSocket.OPEN) {
        clearInterval(interval);
        return;
      }

      const payload = generatePayload();
      console.log('[CLIENT] Sending data:', payload);
      ws.send(JSON.stringify(payload));
    }, SEND_INTERVAL_MS);
  });

  ws.on('message', (raw) => {
    try {
      const response = JSON.parse(raw);
      console.log(`[CLIENT] Server response [${response.type}]:`, response.message);
      if (response.id) console.log(`[CLIENT] Stored with ID: ${response.id}`);
    } catch {
      console.log('[CLIENT] Raw message:', raw.toString());
    }
  });

  ws.on('close', () => {
    console.log('[CLIENT] Disconnected. Reconnecting in 5 seconds...');
    // Auto-reconnect after 5 seconds
    reconnectTimer = setTimeout(connect, 5000);
  });

  ws.on('error', (err) => {
    console.error('[CLIENT] WebSocket error:', err.message);
  });
};

// ── Start the client ─────────────────────────────────────────────────────────
connect();

// Graceful shutdown on Ctrl+C
process.on('SIGINT', () => {
  console.log('\n[CLIENT] Shutting down...');
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (ws) ws.close();
  process.exit(0);
});
