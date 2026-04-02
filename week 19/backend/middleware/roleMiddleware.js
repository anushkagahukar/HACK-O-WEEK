const { logAction } = require('./logger');

function requireRole(...roles) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ success: false, message: 'Not authenticated' });
    }

    if (!roles.includes(req.user.role)) {
      logAction({
        userId: req.user.id,
        action: 'UNAUTHORIZED_ACCESS',
        resource: req.originalUrl,
        ipAddress: req.ip || req.connection.remoteAddress,
        status: 'failure',
      });
      return res.status(403).json({ success: false, message: 'Insufficient permissions' });
    }

    next();
  };
}

module.exports = { requireRole };
