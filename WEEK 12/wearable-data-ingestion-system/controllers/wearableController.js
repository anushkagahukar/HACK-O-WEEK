// controllers/wearableController.js
// Handles all REST API logic for wearable data

const { db } = require('../database/db');
const { encrypt, decrypt } = require('../utils/encryption');
const { validateWearableData } = require('../utils/validator');
const logger = require('../utils/logger');

// In-memory cache: stores the latest record per userId
const latestCache = new Map();

/**
 * Updates the in-memory cache with the most recent record for a user.
 */
const updateCache = (userId, record) => {
  latestCache.set(userId, record);
};

/**
 * GET /api/health
 * Simple health check endpoint.
 */
const healthCheck = (req, res) => {
  res.json({
    success: true,
    message: 'Wearable Data Ingestion System is running',
    timestamp: new Date().toISOString(),
  });
};

/**
 * GET /api/wearable/history/:userId
 * Returns all records for a given user, sorted by timestamp descending.
 */
const getHistory = (req, res, next) => {
  const { userId } = req.params;

  const sql = `
    SELECT * FROM wearable_data
    WHERE userId = ?
    ORDER BY timestamp DESC
  `;

  db.all(sql, [userId], (err, rows) => {
    if (err) return next(err);

    if (rows.length === 0) {
      return res.status(404).json({ success: false, message: 'No records found for this user' });
    }

    // Decrypt sensitive fields before sending to client
    const decrypted = rows.map(decryptRow);
    logger.info(`History fetched for userId: ${userId}, records: ${rows.length}`);
    res.json({ success: true, userId, count: decrypted.length, data: decrypted });
  });
};

/**
 * GET /api/wearable/latest/:userId
 * Returns the most recent record for a user (checks cache first).
 */
const getLatest = (req, res, next) => {
  const { userId } = req.params;

  // Serve from cache if available
  if (latestCache.has(userId)) {
    logger.info(`Cache hit for latest data, userId: ${userId}`);
    return res.json({ success: true, source: 'cache', data: latestCache.get(userId) });
  }

  const sql = `
    SELECT * FROM wearable_data
    WHERE userId = ?
    ORDER BY timestamp DESC
    LIMIT 1
  `;

  db.get(sql, [userId], (err, row) => {
    if (err) return next(err);
    if (!row) return res.status(404).json({ success: false, message: 'No records found for this user' });

    const decrypted = decryptRow(row);
    updateCache(userId, decrypted);
    logger.info(`Latest data fetched from DB for userId: ${userId}`);
    res.json({ success: true, source: 'database', data: decrypted });
  });
};

/**
 * GET /api/wearable/stats/:userId
 * Returns aggregated stats: avg heart rate, total steps, avg sleep hours.
 */
const getStats = (req, res, next) => {
  const { userId } = req.params;

  const sql = `SELECT * FROM wearable_data WHERE userId = ?`;

  db.all(sql, [userId], (err, rows) => {
    if (err) return next(err);
    if (rows.length === 0) {
      return res.status(404).json({ success: false, message: 'No records found for this user' });
    }

    // Decrypt and compute stats
    let totalHeartRate = 0, totalSteps = 0, totalSleep = 0;

    rows.forEach((row) => {
      totalHeartRate += parseFloat(decrypt(row.encryptedHeartRate));
      totalSteps     += parseFloat(decrypt(row.encryptedSteps));
      totalSleep     += parseFloat(decrypt(row.encryptedSleepHours));
    });

    const count = rows.length;
    const stats = {
      userId,
      totalRecords:   count,
      avgHeartRate:   parseFloat((totalHeartRate / count).toFixed(2)),
      totalSteps:     Math.round(totalSteps),
      avgSleepHours:  parseFloat((totalSleep / count).toFixed(2)),
    };

    logger.info(`Stats calculated for userId: ${userId}`);
    res.json({ success: true, stats });
  });
};

/**
 * POST /api/wearable/test
 * Inserts a mock wearable record manually (useful for testing without WebSocket).
 */
const insertTestData = (req, res, next) => {
  const mockData = {
    userId:     req.body.userId     || 'TEST_USER',
    deviceId:   req.body.deviceId   || 'TEST_DEVICE',
    heartRate:  req.body.heartRate  || 75,
    steps:      req.body.steps      || 3000,
    calories:   req.body.calories   || 150,
    sleepHours: req.body.sleepHours || 7,
    timestamp:  req.body.timestamp  || new Date().toISOString(),
  };

  const validation = validateWearableData(mockData);
  if (!validation.valid) {
    return res.status(400).json({ success: false, errors: validation.errors });
  }

  insertRecord(mockData, (err, id) => {
    if (err) return next(err);
    logger.info(`Test data inserted with id: ${id}`);
    res.status(201).json({ success: true, message: 'Test data inserted', id });
  });
};

// ─── Helpers ────────────────────────────────────────────────────────────────

/**
 * Inserts an encrypted wearable record into SQLite.
 * Callback: (err, insertedId)
 */
const insertRecord = (data, callback) => {
  const sql = `
    INSERT INTO wearable_data
      (userId, deviceId, encryptedHeartRate, encryptedSteps, encryptedCalories, encryptedSleepHours, timestamp, createdAt)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `;

  const params = [
    data.userId,
    data.deviceId,
    encrypt(data.heartRate),
    encrypt(data.steps),
    encrypt(data.calories),
    encrypt(data.sleepHours),
    data.timestamp,
    new Date().toISOString(),
  ];

  db.run(sql, params, function (err) {
    if (err) return callback(err);
    // Update cache with decrypted version of what we just stored
    updateCache(data.userId, { ...data, id: this.lastID });
    callback(null, this.lastID);
  });
};

/**
 * Decrypts sensitive fields in a database row for API responses.
 */
const decryptRow = (row) => ({
  id:         row.id,
  userId:     row.userId,
  deviceId:   row.deviceId,
  heartRate:  parseFloat(decrypt(row.encryptedHeartRate)),
  steps:      parseFloat(decrypt(row.encryptedSteps)),
  calories:   parseFloat(decrypt(row.encryptedCalories)),
  sleepHours: parseFloat(decrypt(row.encryptedSleepHours)),
  timestamp:  row.timestamp,
  createdAt:  row.createdAt,
});

module.exports = {
  healthCheck,
  getHistory,
  getLatest,
  getStats,
  insertTestData,
  insertRecord,
  updateCache,
};
