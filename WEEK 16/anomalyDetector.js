/**
 * Evaluates biometric streams and checks against thresholds.
 * For example, detects if BPM is abnormally high or dangerously low.
 */

const THRESHOLDS = {
    BPM_HIGH: 100, // BPM greater than 100 is an anomaly (e.g., at rest)
    BPM_LOW: 40    // BPM lower than 40 is an anomaly
};

/**
 * Checks a data stream frame for anomalies.
 * @param {Object} streamData Format: { deviceId, timestamp, bpm }
 * @returns {Object|null} An anomaly notification object or null if normal.
 */
function detectAnomaly(streamData) {
    if (!streamData || typeof streamData.bpm !== 'number') {
        return null;
    }

    const { bpm, deviceId, timestamp } = streamData;
    let anomalyReason = '';

    if (bpm > THRESHOLDS.BPM_HIGH) {
        anomalyReason = `High BPM detected: ${bpm}`;
    } else if (bpm < THRESHOLDS.BPM_LOW) {
        anomalyReason = `Low BPM detected: ${bpm}`;
    }

    if (anomalyReason) {
        return {
            alertId: crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2, 9),
            deviceId,
            timestamp,
            severity: 'CRITICAL',
            reason: anomalyReason,
            raw_value: bpm
        };
    }

    return null;
}

// Since I used crypto above, require it (fallback to fallback string if needed)
const crypto = require('crypto');

module.exports = {
    detectAnomaly
};
