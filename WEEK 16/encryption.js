const crypto = require('crypto');

// Normally, you would load these securely from environment variables.
// Generating random ones here for demonstration purposes.
const algorithm = 'aes-256-cbc';
const key = crypto.randomBytes(32);
const iv = crypto.randomBytes(16);

/**
 * Encrypts a payload object using AES-256-CBC.
 * @param {Object} payload 
 * @returns {String} Encrypted JSON string in format: iv:encryptedData
 */
function encryptPayload(payload) {
    const text = JSON.stringify(payload);
    const cipher = crypto.createCipheriv(algorithm, Buffer.from(key), iv);
    
    let encrypted = cipher.update(text);
    encrypted = Buffer.concat([encrypted, cipher.final()]);
    
    return iv.toString('hex') + ':' + encrypted.toString('hex');
}

/**
 * Decrypts a payload string encrypted by encryptPayload.
 * @param {String} text Encrypted JSON string
 * @returns {Object} Decrypted payload object
 */
function decryptPayload(text) {
    const textParts = text.split(':');
    const extractIv = Buffer.from(textParts.shift(), 'hex');
    const encryptedText = Buffer.from(textParts.join(':'), 'hex');
    
    const decipher = crypto.createDecipheriv(algorithm, Buffer.from(key), extractIv);
    
    let decrypted = decipher.update(encryptedText);
    decrypted = Buffer.concat([decrypted, decipher.final()]);
    
    return JSON.parse(decrypted.toString());
}

module.exports = {
    encryptPayload,
    decryptPayload
};
