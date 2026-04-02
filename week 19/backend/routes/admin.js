const express = require('express');
const router = express.Router();
const { getStats, getLogs, getAnomalies, getUsers, deleteLogs, exportLogs } = require('../controllers/adminController');
const { authenticateToken, requireRole } = require('../middleware/auth');

// All admin routes require authentication + admin role
router.use(authenticateToken, requireRole('admin'));

router.get('/stats', getStats);
router.get('/logs', getLogs);
router.get('/anomalies', getAnomalies);
router.get('/users', getUsers);
router.delete('/logs', deleteLogs);
router.get('/export/logs', exportLogs);

module.exports = router;
