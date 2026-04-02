const crypto = require('crypto');
const config = require('../config/config');

const ALGORITHM = 'aes-256-cbc';
const KEY = Buffer.from(config.ENCRYPTION_KEY, 'utf8').slice(0, 32);
const IV = Buffer.from(config.ENCRYPTION_IV, 'utf8').slice(0, 16);

function encrypt(text) {
  if (!text) return text;
  const cipher = crypto.createCipheriv(ALGORITHM, KEY, IV);
  let encrypted = cipher.update(String(text), 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return encrypted;
}

function decrypt(encryptedText) {
  if (!encryptedText) return encryptedText;
  try {
    const decipher = crypto.createDecipheriv(ALGORITHM, KEY, IV);
    let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  } catch (e) {
    return encryptedText; // return as-is if not encrypted
  }
}

module.exports = { encrypt, decrypt };
