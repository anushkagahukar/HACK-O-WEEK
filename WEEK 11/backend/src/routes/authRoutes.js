const express = require('express');
const router = express.Router();
const { signup, login, getProfile } = require('../controllers/authController');
const { protect } = require('../middleware/authMiddleware');

router.post('/signup', signup);
router.post('/login', login);
// We map /api/user/profile to the auth router for convenience, or we could have a specific user routes file.
router.get('/profile', protect, getProfile);

module.exports = router;
