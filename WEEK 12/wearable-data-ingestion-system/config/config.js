// config/config.js
// Central configuration loaded from environment variables via dotenv

require('dotenv').config();

const config = {
  // HTTP server port
  PORT: process.env.PORT || 3000,

  // WebSocket server port
  WS_PORT: process.env.WS_PORT || 8080,

  // AES-256 encryption key (must be exactly 32 characters)
  ENCRYPTION_KEY: process.env.ENCRYPTION_KEY || 'default_key_32_bytes_long_here!!',

  // Rate limiting settings
  RATE_LIMIT: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 60000, // 1 minute
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 30,
  },

  // SQLite database file path
  DB_PATH: './database/wearable.db',
};

module.exports = config;
