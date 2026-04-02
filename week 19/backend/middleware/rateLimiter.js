// Simple in-memory rate limiter
const requestCounts = new Map();

const WINDOW_MS = 60 * 1000; // 1 minute
const MAX_REQUESTS = 100;

function rateLimiter(req, res, next) {
  const ip = req.ip || req.connection.remoteAddress;
  const now = Date.now();

  if (!requestCounts.has(ip)) {
    requestCounts.set(ip, { count: 1, startTime: now });
    return next();
  }

  const record = requestCounts.get(ip);

  if (now - record.startTime > WINDOW_MS) {
    // Reset window
    requestCounts.set(ip, { count: 1, startTime: now });
    return next();
  }

  record.count++;

  if (record.count > MAX_REQUESTS) {
    return res.status(429).json({
      success: false,
      message: 'Too many requests. Please slow down.',
    });
  }

  next();
}

// Clean up old entries every 5 minutes
setInterval(() => {
  const now = Date.now();
  for (const [ip, record] of requestCounts.entries()) {
    if (now - record.startTime > WINDOW_MS * 2) {
      requestCounts.delete(ip);
    }
  }
}, 5 * 60 * 1000);

module.exports = rateLimiter;
