const { get, all } = require('../database/db');
const { logAction } = require('../middleware/logger');

async function getProfile(req, res) {
  const ip = req.ip || req.connection.remoteAddress;
  try {
    const user = await get('SELECT id,name,email,role,createdAt FROM users WHERE id=?', [req.user.id]);
    if (!user) return res.status(404).json({ success: false, message: 'User not found' });
    await logAction({ userId: req.user.id, action: 'DATA_ACCESS', resource: '/api/user/profile', ipAddress: ip });
    res.json({ success: true, user });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Server error' });
  }
}

async function getActivity(req, res) {
  const ip = req.ip || req.connection.remoteAddress;
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const offset = (page - 1) * limit;
  try {
    const logs = await all('SELECT * FROM audit_logs WHERE userId=? ORDER BY timestamp DESC LIMIT ? OFFSET ?', [req.user.id, limit, offset]);
    const total = await get('SELECT COUNT(*) as count FROM audit_logs WHERE userId=?', [req.user.id]);
    await logAction({ userId: req.user.id, action: 'DATA_ACCESS', resource: '/api/user/activity', ipAddress: ip });
    res.json({ success: true, logs, pagination: { page, limit, total: total.count, pages: Math.ceil(total.count / limit) } });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Server error' });
  }
}

module.exports = { getProfile, getActivity };
