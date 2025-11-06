const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const Database = require('./database');
const path = require('path');

const app = express();
const db = new Database();
const PORT = process.env.PORT || 3000;

// Middleware setup
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// Session tracking (basic)
const sessions = new Map();

// Utility function to generate session ID
function generateSessionId() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

// Routes

// Home page
app.get('/', (req, res) => {
    res.render('index', { 
        title: 'SecureHR - Employee Management System',
        company: 'SecureHR Solutions'
    });
});

// About page
app.get('/about', (req, res) => {
    res.redirect('/');
});

// Contact page  
app.get('/contact', (req, res) => {
    res.redirect('/');
});

// Search page (requires authentication)
app.get('/search', (req, res) => {
    const sessionId = req.cookies?.session;
    const session = sessions.get(sessionId);
    
    if (!session) {
        return res.redirect('/login?error=Please login to access employee search');
    }
    
    res.render('search', { 
        results: [], 
        query: '', 
        error: null,
        user: session.user
    });
});

// VULNERABLE: User search endpoint - main attack vector (requires authentication)
app.post('/search', (req, res) => {
    const { query } = req.body;
    
    // Check authentication
    const sessionId = req.cookies?.session;
    const session = sessions.get(sessionId);
    
    if (!session) {
        return res.redirect('/login?error=Session expired. Please login again.');
    }
    
    if (!query) {
        return res.render('search', { 
            error: 'Please provide a search query', 
            results: [], 
            query: '',
            user: session.user
        });
    }

    // Basic security measures (bypassable)
    const blockedKeywords = ['union select', 'or 1=1', 'drop table', 'delete from',"1==1",];
    const lowercaseQuery = query.toLowerCase().replace(/\s+/g, ' ');
    
    // Check for blocked keywords (simple pattern matching)
    for (const keyword of blockedKeywords) {
        if (lowercaseQuery.includes(keyword)) {
            return res.render('search', { 
                error: `Invalid search query. Please use appropriate search terms.`, 
                results: [], 
                query: query,
                user: session.user
            });
        }
    }

    // Execute search
    db.searchUsers(query, (err, results) => {
        if (err) {
            console.error('❌ Search error:', err.message);
            return res.render('search', { 
                error: 'An error occurred while searching. Please try again.', 
                results: [], 
                query: query,
                user: session.user
            });
        }
        
        res.render('search', { 
            results: results || [], 
            query: query, 
            error: null,
            user: session.user
        });
    });
});

// Exposed endpoint that leaks user data (including password hashes)
app.get('/getusers', (req, res) => {
    db.getAllUsers((err, users) => {
        if (err) {
            return res.status(500).json({ 
                error: 'Database error occurred' 
            });
        }
        
        res.json({
            message: 'Employee database export',
            total_users: users.length,
            users: users.map(user => ({
                id: user.id,
                username: user.username,
                password_hash: user.password_hash,
                role: user.role,
                email: user.email,
                created_at: user.created_at
            }))
        });
    });
});

// VULNERABLE: User details endpoint
app.get('/user/:username', (req, res) => {
    const { username } = req.params;
    
    db.getUserDetails(username, (err, user) => {
        if (err) {
            return res.json({ 
                error: 'Database error occurred'
            });
        }
        
        if (!user) {
            return res.json({ 
                error: 'User not found',
                username: username
            });
        }
        
        res.json({ 
            user: user,
            message: 'User found successfully!'
        });
    });
});

// Login endpoint
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    
    if (!username || !password) {
        return res.render('login', { 
            error: 'Please provide both username and password',
            hint: null
        });
    }
    
    db.authenticateUser(username, password, (err, user) => {
        if (err) {
            return res.render('login', { 
                error: 'Authentication error occurred. Please try again.',
                hint: null
            });
        }
        
        if (user) {
            const sessionId = generateSessionId();
            sessions.set(sessionId, { user: user, timestamp: new Date() });
            
            res.cookie('session', sessionId);
            res.render('dashboard', { 
                user: user,
                message: 'Welcome! You are now logged in.',
                hint: null
            });
        } else {
            res.render('login', { 
                error: 'Invalid username or password',
                hint: null
            });
        }
    });
});

// Login page
app.get('/login', (req, res) => {
    const error = req.query.error || null;
    res.render('login', { 
        error: error,
        hint: null
    });
});

// Dashboard page (requires authentication)
app.get('/dashboard', (req, res) => {
    const sessionId = req.cookies?.session;
    const session = sessions.get(sessionId);
    
    if (!session) {
        return res.redirect('/login?error=Please login to access dashboard');
    }
    
    res.render('dashboard', { 
        user: session.user,
        message: null,
        hint: null
    });
});

// Admin endpoint (requires authentication)
app.post('/admin/reports', (req, res) => {
    const { report_type } = req.body;
    
    if (!report_type) {
        return res.json({ error: 'Report type required' });
    }
    
    // Simulate admin check
    const sessionId = req.cookies?.session;
    const session = sessions.get(sessionId);
    
    if (!session || session.user?.role !== 'admin') {
        return res.json({ 
            error: 'Access denied. Administrator privileges required.'
        });
    }
    
    // Simple report generation (placeholder)
    res.json({ 
        message: 'Report generated successfully',
        report_type: report_type,
        timestamp: new Date().toISOString()
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).render('404', { 
        path: req.path,
        hint: null
    });
});

// Error handler
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({ 
        error: 'Internal server error'
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`SecureHR Employee Management System`);
    console.log(`Server running at: http://localhost:${PORT}`);
    console.log(`Status: Online\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down server...');
    db.close();
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down server...');
    db.close();
    process.exit(0);
});