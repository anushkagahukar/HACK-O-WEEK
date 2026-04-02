// database/db.js
// SQLite database setup and connection using sqlite3

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const config = require('../config/config');
const logger = require('../utils/logger');

// Resolve absolute path to the .db file
const DB_PATH = path.resolve(__dirname, '../database/wearable.db');

// Open (or create) the SQLite database file
const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    logger.error('Failed to connect to SQLite database', err.message);
    process.exit(1);
  }
  logger.info(`SQLite database connected at: ${DB_PATH}`);
});

/**
 * Creates the wearable_data table if it doesn't already exist.
 * Called once at server startup.
 */
const initializeDatabase = () => {
  const createTableSQL = `
    CREATE TABLE IF NOT EXISTS wearable_data (
      id                  INTEGER PRIMARY KEY AUTOINCREMENT,
      userId              TEXT NOT NULL,
      deviceId            TEXT NOT NULL,
      encryptedHeartRate  TEXT NOT NULL,
      encryptedSteps      TEXT NOT NULL,
      encryptedCalories   TEXT NOT NULL,
      encryptedSleepHours TEXT NOT NULL,
      timestamp           TEXT NOT NULL,
      createdAt           TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `;

  db.run(createTableSQL, (err) => {
    if (err) {
      logger.error('Failed to create wearable_data table', err.message);
    } else {
      logger.info('wearable_data table is ready');
    }
  });
};

module.exports = { db, initializeDatabase };
