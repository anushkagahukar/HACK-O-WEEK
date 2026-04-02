const bcrypt = require('bcrypt');
const { run, get } = require('./db');

async function seed() {
  const existing = await get('SELECT COUNT(*) as c FROM users');
  if (existing.c > 0) { console.log('Already seeded, skipping.'); return; }

  console.log('Seeding database...');
  const [ap, up, jp] = await Promise.all([bcrypt.hash('admin123',10), bcrypt.hash('user123',10), bcrypt.hash('jane123',10)]);

  const admin = await run('INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)', ['Admin User','admin@compliance.com',ap,'admin']);
  const user1 = await run('INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)', ['John Doe','john@example.com',up,'user']);
  const user2 = await run('INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)', ['Jane Smith','jane@example.com',jp,'user']);

  const aId = admin.lastID, uId = user1.lastID, jId = user2.lastID;

  const logs = [
    [aId,'LOGIN','/api/auth/login','127.0.0.1','success'],
    [aId,'ADMIN_ACCESS','/api/admin/stats','127.0.0.1','success'],
    [uId,'LOGIN','/api/auth/login','192.168.1.10','success'],
    [uId,'DATA_ACCESS','/api/user/profile','192.168.1.10','success'],
    [uId,'LOGIN','/api/auth/login','192.168.1.10','failure'],
    [uId,'LOGIN','/api/auth/login','192.168.1.10','failure'],
    [uId,'LOGIN','/api/auth/login','192.168.1.10','failure'],
    [uId,'UNAUTHORIZED_ACCESS','/api/admin/stats','192.168.1.10','failure'],
    [uId,'UNAUTHORIZED_ACCESS','/api/admin/logs','192.168.1.10','failure'],
    [uId,'UNAUTHORIZED_ACCESS','/api/admin/users','192.168.1.10','failure'],
    [jId,'LOGIN','/api/auth/login','10.0.0.5','success'],
    [jId,'DATA_ACCESS','/api/user/profile','10.0.0.5','success'],
    [aId,'EXPORT_LOGS','/api/admin/export/logs','127.0.0.1','success'],
    [aId,'LOGOUT','/api/auth/logout','127.0.0.1','success'],
  ];
  for (const l of logs) await run('INSERT INTO audit_logs (userId,action,resource,ipAddress,status) VALUES (?,?,?,?,?)', l);

  await run('INSERT INTO anomaly_reports (userId,anomalyType,description,severity) VALUES (?,?,?,?)', [uId,'MULTIPLE_FAILED_LOGINS','3 failed logins in 10 min from IP: 192.168.1.10','MEDIUM']);
  await run('INSERT INTO anomaly_reports (userId,anomalyType,description,severity) VALUES (?,?,?,?)', [uId,'REPEATED_UNAUTHORIZED_ACCESS','3 unauthorized access attempts in 10 min','HIGH']);
  await run('INSERT INTO anomaly_reports (userId,anomalyType,description,severity) VALUES (?,?,?,?)', [jId,'RAPID_REQUESTS','22 requests in 10 min — possible automation','MEDIUM']);

  console.log('Seed complete!');
  console.log('  Admin: admin@compliance.com / admin123');
  console.log('  User:  john@example.com / user123');
}

module.exports = { seed };
