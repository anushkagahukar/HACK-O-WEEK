// utils/validator.js
// Validates incoming wearable data payloads before processing

/**
 * Validates a wearable data payload.
 * Returns { valid: true } on success, or { valid: false, errors: [...] } on failure.
 */
const validateWearableData = (data) => {
  const errors = [];

  // userId: required string
  if (!data.userId || typeof data.userId !== 'string' || data.userId.trim() === '') {
    errors.push('userId is required and must be a non-empty string');
  }

  // deviceId: required string
  if (!data.deviceId || typeof data.deviceId !== 'string' || data.deviceId.trim() === '') {
    errors.push('deviceId is required and must be a non-empty string');
  }

  // heartRate: numeric, range 40–200
  if (data.heartRate === undefined || data.heartRate === null) {
    errors.push('heartRate is required');
  } else if (typeof data.heartRate !== 'number' || data.heartRate < 40 || data.heartRate > 200) {
    errors.push('heartRate must be a number between 40 and 200');
  }

  // steps: non-negative number
  if (data.steps === undefined || data.steps === null) {
    errors.push('steps is required');
  } else if (typeof data.steps !== 'number' || data.steps < 0) {
    errors.push('steps must be a non-negative number');
  }

  // calories: non-negative number
  if (data.calories === undefined || data.calories === null) {
    errors.push('calories is required');
  } else if (typeof data.calories !== 'number' || data.calories < 0) {
    errors.push('calories must be a non-negative number');
  }

  // sleepHours: 0–24 range
  if (data.sleepHours === undefined || data.sleepHours === null) {
    errors.push('sleepHours is required');
  } else if (typeof data.sleepHours !== 'number' || data.sleepHours < 0 || data.sleepHours > 24) {
    errors.push('sleepHours must be a number between 0 and 24');
  }

  // timestamp: valid ISO 8601 date string
  if (!data.timestamp) {
    errors.push('timestamp is required');
  } else {
    const parsed = new Date(data.timestamp);
    if (isNaN(parsed.getTime())) {
      errors.push('timestamp must be a valid ISO 8601 date string');
    }
  }

  return errors.length === 0
    ? { valid: true }
    : { valid: false, errors };
};

module.exports = { validateWearableData };
