const { get, all, run } = require('../database/db');
const { logAction } = require('../middleware/logger');

async function getStats(req, res) {
  try {
    const [users, logs, anomalies, high] = await Promise.all([
      get('SELECT COUNT(*) as c FROM users'),
      get('SELECT COUNT(*) as c FROM audit_logs'),
      get('SELECT COUNT(*) as c FROM anomaly_reports'),
      get("SELECT COUNT(*) as c FROM anomaly_reports WHERE severity='HIGH'"),
    ]);
    await logAction({ userId: req.user.id, action: 'ADMIN_ACCESS', resource: '/api/admin/stats', ipAddress: req.ip });
    res.json({ success: true, stats: { totalUsers: users.c, totalLogs: logs.c, totalAnomalies: anomalies.c, highSeverityAlerts: high.c } });
  } catch (err) { res.status(500).json({ success: false, message: 'Server error' }); }
}

async function getLogs(req, res) {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 15;
  const offset = (page - 1) * limit;
  const { action, status, date, search } = req.query;
  let where = 'WHERE 1=1'; const params = [];
  if (action) { where += ' AND al.action=?'; params.push(action); }
  if (status) { where += ' AND al.status=?'; params.push(status); }
  if (date)   { where += ' AND DATE(al.timestamp)=?'; params.push(date); }
  if (search) { where += ' AND (u.name LIKE ? OR al.action LIKE ? OR al.resource LIKE ?)'; const s=`%${search}%`; params.push(s,s,s); }
  try {
    const total = await get(`SELECT COUNT(*) as c FROM audit_logs al LEFT JOIN users u ON al.userId=u.id ${where}`, params);
    const logs = await all(`SELECT al.*,u.name as userName,u.email as userEmail FROM audit_logs al LEFT JOIN users u ON al.userId=u.id ${where} ORDER BY al.timestamp DESC LIMIT ? OFFSET ?`, [...params, limit, offset]);
    await logAction({ userId: req.user.id, action: 'ADMIN_ACCESS', resource: '/api/admin/logs', ipAddress: req.ip });
    res.json({ success: true, logs, pagination: { page, limit, total: total.c, pages: Math.ceil(total.c / limit) } });
  } catch (err) { console.error(err); res.status(500).json({ success: false, message: 'Server error' }); }
}

async function getAnomalies(req, res) {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 15;
  const offset = (page - 1) * limit;
  try {
    const total = await get('SELECT COUNT(*) as c FROM anomaly_reports');
    const anomalies = await all(`SELECT ar.*,u.name as userName,u.email as userEmail FROM anomaly_reports ar LEFT JOIN users u ON ar.userId=u.id ORDER BY ar.timestamp DESC LIMIT ? OFFSET ?`, [limit, offset]);
    res.json({ success: true, anomalies, pagination: { page, limit, total: total.c, pages: Math.ceil(total.c / limit) } });
  } catch (err) { res.status(500).json({ success: false, message: 'Server error' }); }
}

async function getUsers(req, res) {
  try {
    const users = await all('SELECT id,name,email,role,createdAt FROM users ORDER BY createdAt DESC');
    res.json({ success: true, users });
  } catch (err) { res.status(500).json({ success: false, message: 'Server error' }); }
}

async function deleteLogs(req, res) {
  try {
    await run('DELETE FROM audit_logs');
    await logAction({ userId: req.user.id, action: 'ADMIN_DELETE_LOGS', resource: '/api/admin/logs', ipAddress: req.ip });
    res.json({ success: true, message: 'All audit logs cleared' });
  } catch (err) { res.status(500).json({ success: false, message: 'Server error' }); }
}

async function exportLogs(req, res) {
  const fmt = req.query.format || 'json';
  try {
    const logs = await all(`SELECT al.*,u.name as userName,u.email as userEmail FROM audit_logs al LEFT JOIN users u ON al.userId=u.id ORDER BY al.timestamp DESC`);
    await logAction({ userId: req.user.id, action: 'EXPORT_LOGS', resource: '/api/admin/export/logs', ipAddress: req.ip });
    if (fmt === 'csv') {
      const headers = ['id','userId','userName','userEmail','action','resource','timestamp','ipAddress','status'];
      const csv = [headers.join(','), ...logs.map(l => headers.map(h => `"${l[h]||''}"`).join(','))].join('\n');
      res.setHeader('Content-Type','text/csv');
      res.setHeader('Content-Disposition','attachment; filename="audit_logs.csv"');
      return res.send(csv);
    }
    res.setHeader('Content-Type','application/json');
    res.setHeader('Content-Disposition','attachment; filename="audit_logs.json"');
    res.json(logs);
  } catch (err) { res.status(500).json({ success: false, message: 'Server error' }); }
}

module.exports = { getStats, getLogs, getAnomalies, getUsers, deleteLogs, exportLogs };
