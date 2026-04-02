// routes/wearableRoutes.js
// Defines all REST API routes for the wearable data system

const express = require('express');
const router = express.Router();
const { rateLimiter } = require('../middleware/rateLimiter');
const {
  healthCheck,
  getHistory,
  getLatest,
  getStats,
  insertTestData,
} = require('../controllers/wearableController');

// Apply rate limiting to all routes in this router
router.use(rateLimiter);

// GET /api/health — server health check
router.get('/health', healthCheck);

// GET /api/wearable/history/:userId — all records for a user
router.get('/wearable/history/:userId', getHistory);

// GET /api/wearable/latest/:userId — most recent record for a user
router.get('/wearable/latest/:userId', getLatest);

// GET /api/wearable/stats/:userId — aggregated stats for a user
router.get('/wearable/stats/:userId', getStats);

// POST /api/wearable/test — insert mock data manually
router.post('/wearable/test', insertTestData);

module.exports = router;
