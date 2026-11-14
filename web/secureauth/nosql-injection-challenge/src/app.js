const express = require('express');
const mongoose = require('mongoose');
const dotenv = require('dotenv');
const path = require('path');
const session = require('express-session');
const authRoutes = require('./routes/auth');
const app = express();

// Load environment variables from .env file
dotenv.config();

// Middleware
app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false, maxAge: 24 * 60 * 60 * 1000 } // 24 hours
}));
app.use(express.json()); // Parses JSON content
app.use(express.urlencoded({ extended: true })); // Parses form data
app.use(express.static(path.join(__dirname, '../public')));

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('MongoDB connected'))
    .catch(err => console.error('MongoDB connection error:', err));

// Routes
app.use('/api/auth', authRoutes);

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════╗
║   SecureAuth Enterprise Authentication Portal        ║
║   Server running on http://localhost:${PORT}            ║
║   Access Portal: http://localhost:${PORT}/login.html   ║
╚═══════════════════════════════════════════════════════╝
    `);
});