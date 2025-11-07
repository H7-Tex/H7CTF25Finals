const mongoose = require('mongoose');
const User = require('./src/models/User');

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/nosql_ctf', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

async function seedDatabase() {
    try {
        // Clear existing users
        await User.deleteMany({});
        
        // Create test users with different roles and departments
        const testUsers = [
            // Regular users
            { username: 'user', password: 'MyStr0ng!P@ssw0rd#123', isAdmin: false, role: 'user', department: 'sales' },
            { username: 'alice', password: 'Al1ce$SecretKey!2024', isAdmin: false, role: 'user', department: 'marketing' },
            { username: 'bob', password: 'B0b#ComplicatedPass!456', isAdmin: false, role: 'user', department: 'hr' },
            { username: 'charlie', password: 'Ch@rlie&StrongAuth2024!', isAdmin: false, role: 'user', department: 'finance' },
            
            // Moderators
            { username: 'mod1', password: 'M0d3r@t0r!P@ss2024', isAdmin: false, role: 'moderator', department: 'support' },
            { username: 'support', password: 'Supp0rt#T34m!2024', isAdmin: false, role: 'moderator', department: 'support' },
            
            // Regular admins
            { username: 'admin', password: 'Adm1n!SecureP@ssw0rd2024', isAdmin: true, role: 'admin', department: 'it' },
            { username: 'manager', password: 'M@n@ger#P@ss2024!', isAdmin: true, role: 'admin', department: 'operations' },
            { username: 'itadmin', password: 'IT@dm1n!Str0ng#2024', isAdmin: true, role: 'admin', department: 'it' },
            
            // The target - superadmin (harder to find)
            { username: 'sysadmin', password: 'Syst3m@dm1n!Ult1m@t3#2024', isAdmin: true, role: 'superadmin', department: 'security' },
            { username: 'root', password: 'R00t!Acc3ss#M@st3r2024', isAdmin: true, role: 'superadmin', department: 'security' }
        ];
        
        await User.insertMany(testUsers);
        console.log('✅ Test users created successfully!');
        console.log('Users in database:');
        testUsers.forEach(user => {
            const roleDisplay = user.role === 'superadmin' ? '[SUPERADMIN]' : 
                               user.isAdmin ? '[ADMIN]' : 
                               user.role === 'moderator' ? '[MOD]' : '[USER]';
            console.log(`- ${user.username} : [DEPT: ${user.department}] ${roleDisplay}`);
        });
        
        mongoose.connection.close();
    } catch (error) {
        console.error('Error seeding database:', error);
        mongoose.connection.close();
    }
}

seedDatabase();