// Re-exports logAction from middleware/logger for backward compatibility
const { logAction } = require('../middleware/logger');
module.exports = { logAction };
