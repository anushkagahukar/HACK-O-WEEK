// middleware/rateLimiter.js
// Simple in-memory rate limiter to prevent spam requests

const config = require('../config/config');
const logger = require('../utils/logger');

// Map to track request counts per IP: { ip -> { count, resetTime } }
const requestCounts = new Map();

/**
 * Rate limiting middleware for Express routes.
 * Limits each IP to maxRequests per windowMs.
 */
const rateLimiter = (req, res, next) => {
  const ip = req.ip || req.connection.remoteAddress;
  const now = Date.now();
  const { windowMs, maxRequests } = config.RATE_LIMIT;

  const record = requestCounts.get(ip);

  if (!record || now > record.resetTime) {
    // First request or window expired — reset counter
    requestCounts.set(ip, { count: 1, resetTime: now + windowMs });
    return next();
  }

  if (record.count >= maxRequests) {
    logger.warn(`Rate limit exceeded for IP: ${ip}`);
    return res.status(429).json({
      success: false,
      message: 'Too many requests. Please slow down.',
    });
  }

  record.count += 1;
  next();
};

/**
 * WebSocket rate limiter — returns true if the client is allowed, false if blocked.
 * Uses the same in-memory map.
 */
const wsRateLimiter = (ip) => {
  const now = Date.now();
  const { windowMs, maxRequests } = config.RATE_LIMIT;
  const record = requestCounts.get(ip);

  if (!record || now > record.resetTime) {
    requestCounts.set(ip, { count: 1, resetTime: now + windowMs });
    return true;
  }

  if (record.count >= maxRequests) {
    return false;
  }

  record.count += 1;
  return true;
};

module.exports = { rateLimiter, wsRateLimiter };
