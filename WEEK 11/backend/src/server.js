require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { connectDB } = require('./config/db');

// Connect Database
connectDB();

const app = express();

// Middleware
app.use(cors());
app.use(express.json()); // Parse JSON bodies

// Routes
app.use('/api/auth', require('./routes/authRoutes'));
// We map /api/user routes. In authRoutes, we mapped /profile. Let's redirect /api/user to those specific routers.
app.use('/api/user', require('./routes/authRoutes')); // For /api/user/profile
app.use('/api/user', require('./routes/wearableRoutes')); // For /api/user/wearable and /wearable-history

app.get('/', (req, res) => {
    res.send('API is running...');
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
