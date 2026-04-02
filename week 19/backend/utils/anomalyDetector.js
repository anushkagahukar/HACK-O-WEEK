const { run, get } = require('../database/db');

const WINDOW = "datetime('now', '-10 minutes')";
const FAILED_LOGIN_THRESHOLD = 5;
const UNAUTHORIZED_THRESHOLD = 3;
const RAPID_REQUEST_THRESHOLD = 20;

async function createAnomaly({ userId, anomalyType, description, severity }) {
  try {
    const recent = await get(
      `SELECT id FROM anomaly_reports WHERE userId=? AND anomalyType=? AND timestamp >= datetime('now','-5 minutes')`,
      [userId, anomalyType]
    );
    if (recent) return;
    await run(
      `INSERT INTO anomaly_reports (userId, anomalyType, description, severity) VALUES (?,?,?,?)`,
      [userId, anomalyType, description, severity]
    );
  } catch (err) { console.error('Anomaly error:', err.message); }
}

async function analyze({ userId, action, status, ipAddress }) {
  if (!userId) return;

  if (action === 'LOGIN' && status === 'failure') {
    const r = await get(`SELECT COUNT(*) as c FROM audit_logs WHERE userId=? AND action='LOGIN' AND status='failure' AND timestamp>=${WINDOW}`, [userId]);
    if (r.c >= FAILED_LOGIN_THRESHOLD)
      await createAnomaly({ userId, anomalyType: 'MULTIPLE_FAILED_LOGINS',
        description: `${r.c} failed logins in 10 min from IP: ${ipAddress}`,
        severity: r.c >= 10 ? 'HIGH' : 'MEDIUM' });
  }

  if (action === 'UNAUTHORIZED_ACCESS') {
    const r = await get(`SELECT COUNT(*) as c FROM audit_logs WHERE userId=? AND action='UNAUTHORIZED_ACCESS' AND timestamp>=${WINDOW}`, [userId]);
    if (r.c >= UNAUTHORIZED_THRESHOLD)
      await createAnomaly({ userId, anomalyType: 'REPEATED_UNAUTHORIZED_ACCESS',
        description: `${r.c} unauthorized access attempts in 10 min`, severity: 'HIGH' });
  }

  const total = await get(`SELECT COUNT(*) as c FROM audit_logs WHERE userId=? AND timestamp>=${WINDOW}`, [userId]);
  if (total.c >= RAPID_REQUEST_THRESHOLD)
    await createAnomaly({ userId, anomalyType: 'RAPID_REQUESTS',
      description: `${total.c} requests in 10 min — possible automation`, severity: 'MEDIUM' });
}

module.exports = { analyze, createAnomaly };
