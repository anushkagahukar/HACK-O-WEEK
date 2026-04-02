const express = require('express');
const router = express.Router();
const { getProfile, getActivity } = require('../controllers/userController');
const { authenticateToken } = require('../middleware/auth');

router.get('/profile', authenticateToken, getProfile);
router.get('/activity', authenticateToken, getActivity);

module.exports = router;
