// utils/logger.js
// Simple logging utility that prefixes every message with a timestamp

const log = (level, message, data = null) => {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [${level.toUpperCase()}]`;

  if (data) {
    console.log(`${prefix} ${message}`, data);
  } else {
    console.log(`${prefix} ${message}`);
  }
};

module.exports = {
  info:  (msg, data) => log('INFO',  msg, data),
  warn:  (msg, data) => log('WARN',  msg, data),
  error: (msg, data) => log('ERROR', msg, data),
  debug: (msg, data) => log('DEBUG', msg, data),
};
