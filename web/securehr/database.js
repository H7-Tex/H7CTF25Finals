const sqlite3 = require('sqlite3').verbose();
const crypto = require('crypto');

class Database {
    constructor() {
        // Using in-memory database for CTF challenge
        this.db = new sqlite3.Database(':memory:');
        this.init();
    }

    init() {
        this.db.serialize(() => {
            // Create users table with decoy data
            this.db.run(`CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                password_hash TEXT,
                role TEXT DEFAULT 'user',
                email TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )`);

            // Create the hidden admin secrets table (main target)
            this.db.run(`CREATE TABLE admin_secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                secret_key TEXT,
                flag TEXT,
                access_level INTEGER,
                description TEXT
            )`);

            // Create system logs table for additional complexity
            this.db.run(`CREATE TABLE system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                status TEXT
            )`);

            // Create products table as a red herring
            this.db.run(`CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price DECIMAL(10,2),
                category TEXT,
                description TEXT
            )`);

            // Insert decoy users with both plain and hashed passwords
            const users = [
                ['nishanth', 'N1sh@nTh#2024$Secure!K3y', 'user', 'nishanth@company.com'],
                ['abu', 'Ab@u$tr0ng#P@ssw0rd2024!', 'user', 'abu@company.com'],
                ['rohith', 'password123', 'user', 'rohith@company.com'],        // EASY TO CRACK
                ['mative', 'admin123', 'moderator', 'mative@company.com'],      // EASY TO CRACK  
                ['admin_user', 'Adm1n#Sup3r$3cur3!P@ss2024', 'admin', 'admin@company.com'],
                ['divesh', 'D1v3sh#C0mplex$P@ssw0rd!2024', 'user', 'divesh@company.com'],
                ['saiteja', 'S@iT3j@#Str0ng$K3y!2024', 'user', 'saiteja@company.com']
            ];

            const userStmt = this.db.prepare("INSERT INTO users (username, password, password_hash, role, email) VALUES (?, ?, ?, ?, ?)");
            users.forEach(user => {
                const [username, password, role, email] = user;
                const passwordHash = crypto.createHash('sha256').update(password).digest('hex');
                userStmt.run(username, password, passwordHash, role, email);
            });
            userStmt.finalize();

            // Insert the REAL FLAG and decoy secrets
            const dynamicFlag = process.env.DYNAMIC_FLAG || 'H7CTF{W1LD_C4RD5_4R3_D4NG3R0U5_1N_5QL_1NJ3CT10N}';
            const secrets = [
                ['FAKE_KEY_001', 'H7CTF{this_is_not_the_real_flag}', 1, 'Decoy flag to confuse attackers'],
                ['SUPER_SECRET_ADMIN_KEY_2024', dynamicFlag, 9, 'The real flag - highly classified'],
                ['BACKUP_KEY_999', 'H7CTF{backup_systems_are_important}', 5, 'Backup system access key']
            ];

            const secretStmt = this.db.prepare("INSERT INTO admin_secrets (secret_key, flag, access_level, description) VALUES (?, ?, ?, ?)");
            secrets.forEach(secret => secretStmt.run(secret));
            secretStmt.finalize();

            // Insert system logs
            const logs = [
                ['admin', 'failed_login', '192.168.1.100', 'FAILED'],
                ['alice_wonder', 'successful_login', '10.0.0.15', 'SUCCESS'],
                ['unknown_user', 'sql_injection_attempt', '192.168.1.200', 'BLOCKED'],
                ['bob_builder', 'password_change', '10.0.0.25', 'SUCCESS'],
                ['eve_hacker', 'multiple_failed_attempts', '192.168.1.150', 'SUSPICIOUS']
            ];

            const logStmt = this.db.prepare("INSERT INTO system_logs (username, action, ip_address, status) VALUES (?, ?, ?, ?)");
            logs.forEach(log => logStmt.run(log));
            logStmt.finalize();

            // Insert products (red herring data)
            const products = [
                ['Secure Password Manager', 29.99, 'Software', 'Keep your passwords safe'],
                ['Encryption Tool Pro', 49.99, 'Software', 'Military-grade encryption'],
                ['Firewall Guardian', 99.99, 'Security', 'Advanced network protection'],
                ['Vulnerability Scanner', 149.99, 'Security', 'Find security holes before hackers do']
            ];

            const productStmt = this.db.prepare("INSERT INTO products (name, price, category, description) VALUES (?, ?, ?, ?)");
            products.forEach(product => productStmt.run(product));
            productStmt.finalize();
        });
    }

    // Search function using wildcards
    searchUsers(query, callback) {
        // Direct string concatenation (vulnerable)
        const sql = `SELECT username, email, role, created_at FROM users WHERE username LIKE '%${query}%' OR email LIKE '%${query}%'`;
        
        this.db.all(sql, [], (err, rows) => {
            if (err) {
                return callback(err, null);
            }
            callback(null, rows);
        });
    }

    // User details endpoint
    getUserDetails(username, callback) {
        const sql = `SELECT id, username, email, role, created_at, last_login FROM users WHERE username = '${username}'`;
        
        this.db.get(sql, [], (err, row) => {
            if (err) {
                return callback(err, null);
            }
            callback(null, row);
        });
    }

    // Login function (now secure - no wildcards)
    authenticateUser(username, password, callback) {
        const sql = `SELECT * FROM users WHERE username = ? AND password = ?`;
        
        this.db.get(sql, [username, password], (err, row) => {
            if (err) {
                return callback(err, null);
            }
            callback(null, row);
        });
    }

    // Get all users for the getusers endpoint
    getAllUsers(callback) {
        const sql = `SELECT id, username, password_hash, role, email, created_at FROM users`;
        this.db.all(sql, [], callback);
    }

    // Method to get all table names (for advanced exploitation)
    getTables(callback) {
        const sql = "SELECT name FROM sqlite_master WHERE type='table'";
        this.db.all(sql, [], callback);
    }

    // Method to get table schema (for advanced exploitation)
    getTableSchema(tableName, callback) {
        const sql = `PRAGMA table_info(${tableName})`;
        this.db.all(sql, [], callback);
    }

    close() {
        this.db.close((err) => {
            if (err) {
                console.error('Error closing database:', err.message);
            }
        });
    }
}

module.exports = Database;