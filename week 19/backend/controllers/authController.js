const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { run, get } = require('../database/db');
const config = require('../config/config');
const { logAction } = require('../middleware/logger');
const { analyze } = require('../utils/anomalyDetector');

async function signup(req, res) {
  const { name, email, password, role } = req.body;
  const ip = req.ip || req.connection.remoteAddress;
  if (!name || !email || !password)
    return res.status(400).json({ success: false, message: 'All fields are required' });
  if (password.length < 6)
    return res.status(400).json({ success: false, message: 'Password must be at least 6 characters' });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    return res.status(400).json({ success: false, message: 'Invalid email format' });
  try {
    const existing = await get('SELECT id FROM users WHERE email=?', [email]);
    if (existing) return res.status(409).json({ success: false, message: 'Email already registered' });
    const hashed = await bcrypt.hash(password, 10);
    const userRole = role === 'admin' ? 'admin' : 'user';
    const result = await run('INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)', [name, email, hashed, userRole]);
    await logAction({ userId: result.lastID, action: 'SIGNUP', resource: '/api/auth/signup', ipAddress: ip });
    res.status(201).json({ success: true, message: 'Account created successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: 'Server error during signup' });
  }
}

async function login(req, res) {
  const { email, password } = req.body;
  const ip = req.ip || req.connection.remoteAddress;
  if (!email || !password)
    return res.status(400).json({ success: false, message: 'Email and password are required' });
  try {
    const user = await get('SELECT * FROM users WHERE email=?', [email]);
    if (!user || !(await bcrypt.compare(password, user.password))) {
      await logAction({ userId: user?.id || null, action: 'LOGIN', resource: '/api/auth/login', ipAddress: ip, status: 'failure' });
      if (user) await analyze({ userId: user.id, action: 'LOGIN', status: 'failure', ipAddress: ip });
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
    const token = jwt.sign({ id: user.id, email: user.email, role: user.role, name: user.name }, config.JWT_SECRET, { expiresIn: config.JWT_EXPIRES_IN });
    await logAction({ userId: user.id, action: 'LOGIN', resource: '/api/auth/login', ipAddress: ip, status: 'success' });
    res.json({ success: true, message: 'Login successful', token, user: { id: user.id, name: user.name, email: user.email, role: user.role } });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: 'Server error during login' });
  }
}

async function logout(req, res) {
  const ip = req.ip || req.connection.remoteAddress;
  if (req.user) await logAction({ userId: req.user.id, action: 'LOGOUT', resource: '/api/auth/logout', ipAddress: ip });
  res.json({ success: true, message: 'Logged out successfully' });
}

module.exports = { signup, login, logout };
