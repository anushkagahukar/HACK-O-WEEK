require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const config = require('./config/config');
const { initializeDatabase } = require('./database/db');
const { seed } = require('./database/seed');
const rateLimiter = require('./middleware/rateLimiter');
const errorHandler = require('./middleware/errorHandler');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(rateLimiter);

// Serve frontend
app.use(express.static(path.join(__dirname, '../frontend')));

// API Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/user', require('./routes/user'));
app.use('/api/admin', require('./routes/admin'));

app.get('/api/health', (req, res) => res.json({ success: true, message: 'Server running', timestamp: new Date() }));

// SPA fallback for frontend pages
app.get('/admin.html', (req, res) => res.sendFile(path.join(__dirname, '../frontend/admin.html')));
app.get('/user.html',  (req, res) => res.sendFile(path.join(__dirname, '../frontend/user.html')));
app.get('/signup.html',(req, res) => res.sendFile(path.join(__dirname, '../frontend/signup.html')));

app.use(errorHandler);

async function start() {
  await initializeDatabase(); // tables first
  await seed();               // then seed
  app.listen(config.PORT, () => {
    console.log(`\n🚀 Server running at http://localhost:${config.PORT}`);
    console.log(`   Login:  http://localhost:${config.PORT}/index.html`);
    console.log(`   Admin:  http://localhost:${config.PORT}/admin.html\n`);
  });
}

start().catch(err => { console.error('Startup failed:', err); process.exit(1); });
