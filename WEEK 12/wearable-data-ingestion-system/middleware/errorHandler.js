// middleware/errorHandler.js
// Global Express error handling middleware

const logger = require('../utils/logger');

/**
 * Catches any errors passed via next(err) in route handlers.
 * Must be registered LAST in Express middleware chain.
 */
const errorHandler = (err, req, res, next) => {
  logger.error(`Unhandled error on ${req.method} ${req.path}`, err.message);

  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    success: false,
    message: err.message || 'Internal server error',
  });
};

module.exports = errorHandler;
