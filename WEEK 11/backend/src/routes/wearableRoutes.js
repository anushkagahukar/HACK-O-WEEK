const express = require('express');
const router = express.Router();
const { syncWearableData, getWearableHistory } = require('../controllers/wearableController');
const { protect } = require('../middleware/authMiddleware');

router.post('/wearable', protect, syncWearableData);
router.get('/wearable-history', protect, getWearableHistory);

module.exports = router;
