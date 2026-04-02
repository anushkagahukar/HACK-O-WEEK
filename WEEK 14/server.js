const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3000;

// Enable CORS and JSON body parsing
app.use(cors());
app.use(express.json());

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Ensure 'data' directory exists for sqlite DB
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir);
}

// Initialize SQLite database
const dbPath = path.join(dataDir, 'wearable.db');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database', err.message);
  } else {
    console.log('Connected to the SQLite database.');
    
    // Create the wearables table if it doesn't exist
    db.run(`CREATE TABLE IF NOT EXISTS wearables (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ciphertext TEXT NOT NULL,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )`, (err) => {
      if (err) {
        console.error('Error creating table', err.message);
      } else {
        console.log('Table "wearables" ready.');
      }
    });
  }
});

// API endpoint to store encrypted data
app.post('/api/data', (req, res) => {
  const { ciphertext } = req.body;
  if (!ciphertext) {
    return res.status(400).json({ error: 'Ciphertext is required' });
  }

  const sql = 'INSERT INTO wearables (ciphertext) VALUES (?)';
  db.run(sql, [ciphertext], function(err) {
    if (err) {
      console.error('Error inserting data', err.message);
      return res.status(500).json({ error: 'Failed to store data' });
    }
    res.status(201).json({ id: this.lastID, message: 'Data stored securely' });
  });
});

// API endpoint to retrieve encrypted data
app.get('/api/data', (req, res) => {
  const sql = 'SELECT * FROM wearables ORDER BY timestamp DESC LIMIT 100';
  db.all(sql, [], (err, rows) => {
    if (err) {
      console.error('Error retrieving data', err.message);
      return res.status(500).json({ error: 'Failed to retrieve data' });
    }
    res.json(rows);
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
