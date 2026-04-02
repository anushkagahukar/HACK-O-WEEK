// websocket/wsServer.js
// WebSocket server — receives real-time wearable data from devices

const WebSocket = require('ws');
const { validateWearableData } = require('../utils/validator');
const { insertRecord } = require('../controllers/wearableController');
const { wsRateLimiter } = require('../middleware/rateLimiter');
const logger = require('../utils/logger');
const config = require('../config/config');

/**
 * Attaches the WebSocket server to an existing HTTP server (same port as Express).
 * This avoids cross-port issues in the browser.
 */
const startWebSocketServer = (httpServer) => {
  const wss = new WebSocket.Server({ server: httpServer });

  logger.info(`WebSocket server attached to HTTP server (same port as Express)`);

  // ── Connection event ──────────────────────────────────────────────────────
  wss.on('connection', (ws, req) => {
    const clientIp = req.socket.remoteAddress;
    logger.info(`New WebSocket client connected from: ${clientIp}`);

    // Send a welcome acknowledgement to the newly connected client
    ws.send(JSON.stringify({
      type: 'connected',
      message: 'Connected to Wearable Data Ingestion System',
      timestamp: new Date().toISOString(),
    }));

    // ── Message event ───────────────────────────────────────────────────────
    ws.on('message', (rawMessage) => {
      logger.info(`Message received from ${clientIp}`);

      // Rate limiting check
      if (!wsRateLimiter(clientIp)) {
        logger.warn(`WebSocket rate limit exceeded for: ${clientIp}`);
        return ws.send(JSON.stringify({
          type: 'error',
          message: 'Rate limit exceeded. Slow down your data transmission.',
        }));
      }

      // Parse JSON safely
      let data;
      try {
        data = JSON.parse(rawMessage);
      } catch (parseErr) {
        logger.warn(`Invalid JSON received from ${clientIp}`);
        return ws.send(JSON.stringify({
          type: 'error',
          message: 'Invalid JSON format. Please send valid JSON.',
        }));
      }

      // Validate the payload
      const validation = validateWearableData(data);
      if (!validation.valid) {
        logger.warn(`Validation failed for data from ${clientIp}`, validation.errors);
        return ws.send(JSON.stringify({
          type: 'validation_error',
          message: 'Data validation failed',
          errors: validation.errors,
        }));
      }

      // Encrypt and store in SQLite
      insertRecord(data, (err, insertedId) => {
        if (err) {
          logger.error(`DB insert failed for userId: ${data.userId}`, err.message);
          return ws.send(JSON.stringify({
            type: 'error',
            message: 'Failed to store data. Please try again.',
          }));
        }

        logger.info(`Data stored successfully — id: ${insertedId}, userId: ${data.userId}`);
        ws.send(JSON.stringify({
          type: 'success',
          message: 'Wearable data received and stored successfully',
          id: insertedId,
          userId: data.userId,
          timestamp: new Date().toISOString(),
        }));
      });
    });

    // ── Disconnect event ────────────────────────────────────────────────────
    ws.on('close', () => {
      logger.info(`WebSocket client disconnected: ${clientIp}`);
    });

    // ── Error event ─────────────────────────────────────────────────────────
    ws.on('error', (err) => {
      logger.error(`WebSocket error from ${clientIp}`, err.message);
    });
  });

  return wss;
};

module.exports = { startWebSocketServer };
