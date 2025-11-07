const express = require('express');
const router = express.Router();
const User = require('../models/User');

// Debug endpoint (commonly left in production by mistake)
router.get('/debug', async (req, res) => {
    try {
        const userCount = await User.countDocuments();
        const adminCount = await User.countDocuments({ isAdmin: true });
        
        res.json({
            status: "Authentication service online",
            database: "Connected",
            version: "SecureAuth v2.1.3",
            stats: {
                total_users: userCount,
                admin_users: adminCount,
                departments: ["it", "hr", "finance", "security", "operations", "sales", "marketing"],
                roles: ["user", "admin", "moderator", "superadmin"]
            },
            endpoints: {
                login: "/api/auth/login",
                register: "/api/auth/register", 
                users: "/api/auth/users",
                debug: "/api/auth/debug"
            },
            note: "Debug mode - Remove before production deployment"
        });
    } catch (error) {
        res.status(500).json({ error: 'Debug service unavailable' });
    }
});

// User enumeration endpoint (more realistic discovery)
router.get('/users', async (req, res) => {
    try {
        const { department, role, limit } = req.query;
        
        // If no parameters, show basic usage info (common mistake)
        if (!department && !role) {
            return res.json({
                message: "SecureAuth User Directory Service",
                usage: "Specify department or role parameters for user lookup",
                examples: {
                    departments: ["it", "hr", "finance", "security", "operations", "sales", "marketing"],
                    roles: ["user", "admin", "moderator", "superadmin"]
                },
                sample_queries: [
                   
                    "/api/auth/users?department=security&role=superadmin"
                ],
                note: "Limited to 10 results per query for performance"
            });
        }
        
        let query = {};
        if (department) query.department = department;
        if (role) query.role = role;
        
        const users = await User.find(query, 'username department role -_id');
        res.json({ 
            total: users.length,
            query: query,
            users: users.slice(0, parseInt(limit) || 10)
        });
    } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

// User registration route
router.post('/register', async (req, res) => {
    const { username, password } = req.body;
    try {
        const newUser = new User({ username, password });
        await newUser.save();
        res.status(201).json({ message: 'User registered successfully' });
    } catch (error) {
        res.status(500).json({ message: 'Error registering user', error });
    }
});

// User login route (VULNERABLE to NoSQL injection)
router.post('/login', async (req, res) => {
    try {
        let { username, password } = req.body;
        
        // Basic input validation (but still vulnerable)
        if (!username || !password) {
            return res.status(400).json({ 
                success: false, 
                message: 'Username and password are required' 
            });
        }

        // Simulate some "security" measures that don't actually help
        if (typeof username === 'object' || typeof password === 'object') {
            console.log('⚠️  Potential injection attempt detected from IP:', req.ip);
            // But we still process it anyway (bad security)
        }

        console.log('Login attempt:', { username: typeof username === 'object' ? '[OBJECT]' : username, password: '[HIDDEN]' });
        
        // Rate limiting simulation (doesn't actually prevent injection)
        const loginAttempts = req.session?.loginAttempts || 0;
        if (loginAttempts > 3) {
            return res.status(429).json({ 
                success: false, 
                message: 'Too many login attempts. Please try again later.' 
            });
        }

        // VULNERABLE: Still directly passing user input to MongoDB query
        // Even with the "security" checks above, the core vulnerability remains
        // Using native collection to bypass Mongoose sanitization
        console.log('Query object:', { username: username, password: password });
        
        const db = require('mongoose').connection.db;
        const collection = db.collection('users');
        
        // Debug: Check what collections exist
        const collections = await db.listCollections().toArray();
        console.log('Available collections:', collections.map(c => c.name));
        
        // Debug: Check what's in the users collection
        const allUsers = await collection.find({}).toArray();
        console.log('All users in collection:', allUsers.map(u => ({ username: u.username, hasPassword: !!u.password })));
        
        const user = await collection.findOne({ 
            username: username,
            password: password 
        });
        
        console.log('User found:', user ? user.username : null);        if (user) {
            // Only superadmins get the real flag - make it more challenging
            if (user.isAdmin && user.role === 'superadmin') {
                const dynamicFlag = process.env.DYNAMIC_FLAG || 'H7CTF{adv4nc3d_n0sql_1nj3ct10n_m4st3r_2024}';
                res.status(200).json({ 
                    success: true,
                    message: 'Superadmin access granted!',
                    redirect: '/dashboard.html',
                    user: user.username,
                    isAdmin: true,
                    role: user.role,
                    flag: dynamicFlag
                });
            } else if (user.isAdmin) {
                // Regular admins get access but no flag
                res.status(200).json({ 
                    success: true,
                    message: 'Admin access granted, but insufficient privileges for system tokens.',
                    redirect: '/dashboard.html',
                    user: user.username,
                    isAdmin: true,
                    role: user.role || 'admin',
                    flag: 'Access granted, but you need SUPERADMIN privileges for the flag. Try targeting: sysadmin, root'
                });
            } else {
                res.status(200).json({ 
                    success: true,
                    message: 'Login successful!',
                    redirect: '/dashboard.html',
                    user: user.username,
                    isAdmin: false,
                    role: user.role || 'user',
                    flag: 'Nice try! Admin privileges required for system access token.'
                });
            }
        } else {
            res.status(401).json({ 
                success: false,
                message: 'Invalid credentials' 
            });
        }
    } catch (error) {
        // Don't reveal too much information in errors
        console.error('Login error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Authentication service temporarily unavailable' 
        });
    }
});

module.exports = router;