// server.js
// Entry point — starts the Express HTTP server and WebSocket server

require('dotenv').config();

const express = require('express');
const config = require('./config/config');
const { initializeDatabase } = require('./database/db');
const { startWebSocketServer } = require('./websocket/wsServer');
const wearableRoutes = require('./routes/wearableRoutes');
const errorHandler = require('./middleware/errorHandler');
const logger = require('./utils/logger');

const app = express();

// ── Middleware ───────────────────────────────────────────────────────────────
app.use(express.json());                  // Parse incoming JSON request bodies
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));        // Serve frontend dashboard

// ── Routes ───────────────────────────────────────────────────────────────────
app.use('/api', wearableRoutes);

// 404 handler for unknown routes
app.use((req, res) => {
  res.status(404).json({ success: false, message: `Route ${req.path} not found` });
});

// Global error handler (must be last)
app.use(errorHandler);

// ── Startup ──────────────────────────────────────────────────────────────────
const startServer = () => {
  // 1. Initialize SQLite (creates table if not exists)
  initializeDatabase();

  // 2. Start HTTP server and get the server instance
  const httpServer = app.listen(config.PORT, () => {
    logger.info(`HTTP server running at http://localhost:${config.PORT}`);
    logger.info(`API endpoints available at http://localhost:${config.PORT}/api`);
    logger.info(`Dashboard available at http://localhost:${config.PORT}`);
  });

  // 3. Attach WebSocket server to the SAME HTTP server (same port)
  startWebSocketServer(httpServer);
};

startServer();
