const express = require('express');
const router = express.Router();
const authRoutes = require('./auth');

// Main application routes
router.use('/auth', authRoutes);

// Add other routes here as needed

module.exports = router;