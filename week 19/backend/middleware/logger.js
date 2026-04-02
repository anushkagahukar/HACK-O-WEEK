const { run } = require('../database/db');

async function logAction({ userId = null, action, resource, ipAddress = 'unknown', status = 'success' }) {
  try {
    await run(
      `INSERT INTO audit_logs (userId, action, resource, ipAddress, status) VALUES (?, ?, ?, ?, ?)`,
      [userId, action, resource, ipAddress, status]
    );
  } catch (err) {
    console.error('Audit log error:', err.message);
  }
}

// Express middleware — auto-logs every API request
function requestLogger(req, res, next) {
  res.on('finish', () => {
    const userId = req.user ? req.user.id : null;
    const status = res.statusCode < 400 ? 'success' : 'failure';
    const ip = req.ip || req.connection.remoteAddress;
    if (req.originalUrl.startsWith('/api/')) {
      logAction({ userId, action: `${req.method} ${req.originalUrl.split('?')[0]}`,
        resource: req.originalUrl, ipAddress: ip, status });
    }
  });
  next();
}

module.exports = { logAction, requestLogger };
