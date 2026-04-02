// utils/encryption.js
// AES-256-CBC encryption/decryption utility using Node.js built-in crypto module

const crypto = require('crypto');
const config = require('../config/config');

const ALGORITHM = 'aes-256-cbc';

// Derive a 32-byte key from the config value (pad/truncate to exactly 32 bytes)
const KEY = Buffer.from(config.ENCRYPTION_KEY.padEnd(32, '0').slice(0, 32));

/**
 * Encrypts a plain-text value.
 * Returns a string in the format: iv:encryptedData (both hex-encoded)
 */
const encrypt = (value) => {
  // Generate a random 16-byte IV for each encryption (makes it non-deterministic)
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(ALGORITHM, KEY, iv);

  // Convert value to string before encrypting
  let encrypted = cipher.update(String(value), 'utf8', 'hex');
  encrypted += cipher.final('hex');

  // Return iv + encrypted data together so we can decrypt later
  return `${iv.toString('hex')}:${encrypted}`;
};

/**
 * Decrypts a value previously encrypted with encrypt().
 * Expects the format: iv:encryptedData
 */
const decrypt = (encryptedValue) => {
  const [ivHex, encrypted] = encryptedValue.split(':');
  const iv = Buffer.from(ivHex, 'hex');
  const decipher = crypto.createDecipheriv(ALGORITHM, KEY, iv);

  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return decrypted;
};

module.exports = { encrypt, decrypt };
