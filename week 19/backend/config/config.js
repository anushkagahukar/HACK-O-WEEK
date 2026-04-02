require('dotenv').config();

module.exports = {
  JWT_SECRET: process.env.JWT_SECRET || 'super_secret_jwt_key_change_in_prod',
  JWT_EXPIRES_IN: process.env.JWT_EXPIRES_IN || '24h',
  ENCRYPTION_KEY: process.env.ENCRYPTION_KEY || '12345678901234567890123456789012', // 32 bytes
  ENCRYPTION_IV: process.env.ENCRYPTION_IV || '1234567890123456', // 16 bytes
  PORT: process.env.PORT || 3000,
  DB_PATH: process.env.DB_PATH || './database/compliance.db',
};
