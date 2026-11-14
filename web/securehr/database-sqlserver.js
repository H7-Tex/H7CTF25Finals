const sql = require('mssql');

class SQLServerDatabase {
    constructor() {
        this.config = {
            user: 'sa',
            password: 'YourPassword123!',
            server: 'localhost',
            database: 'H7CTF_Challenge',
            options: {
                encrypt: false, // Use true for Azure
                trustServerCertificate: true
            }
        };
        this.pool = null;
        this.init();
    }

    async init() {
        try {
            console.log('🚀 Connecting to SQL Server...');
            this.pool = await sql.connect(this.config);
            console.log('✅ Connected to SQL Server');
            
            await this.createTables();
            await this.insertSampleData();
            
            console.log('✅ Database initialized with sample data');
            console.log('🎯 Challenge: Find the hidden flag using SQL injection with wildcards!');
        } catch (err) {
            console.error('❌ Database connection failed:', err);
        }
    }

    async createTables() {
        try {
            // Drop tables if they exist
            await this.pool.request().query(`
                IF OBJECT_ID('admin_secrets', 'U') IS NOT NULL DROP TABLE admin_secrets;
                IF OBJECT_ID('system_logs', 'U') IS NOT NULL DROP TABLE system_logs;
                IF OBJECT_ID('products', 'U') IS NOT NULL DROP TABLE products;
                IF OBJECT_ID('users', 'U') IS NOT NULL DROP TABLE users;
            `);

            // Create users table
            await this.pool.request().query(`
                CREATE TABLE users (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    username NVARCHAR(50) UNIQUE,
                    password NVARCHAR(100),
                    role NVARCHAR(20) DEFAULT 'user',
                    email NVARCHAR(100),
                    created_at DATETIME2 DEFAULT GETDATE(),
                    last_login DATETIME2
                )
            `);

            // Create admin secrets table
            await this.pool.request().query(`
                CREATE TABLE admin_secrets (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    secret_key NVARCHAR(100),
                    flag NVARCHAR(200),
                    access_level INT,
                    description NVARCHAR(500)
                )
            `);

            // Create system logs table
            await this.pool.request().query(`
                CREATE TABLE system_logs (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    username NVARCHAR(50),
                    action NVARCHAR(100),
                    timestamp DATETIME2 DEFAULT GETDATE(),
                    ip_address NVARCHAR(45),
                    status NVARCHAR(20)
                )
            `);

            // Create products table
            await this.pool.request().query(`
                CREATE TABLE products (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    name NVARCHAR(100),
                    price DECIMAL(10,2),
                    category NVARCHAR(50),
                    description NVARCHAR(500)
                )
            `);

            console.log('✅ Tables created successfully');
        } catch (err) {
            console.error('❌ Error creating tables:', err);
        }
    }

    async insertSampleData() {
        try {
            // Insert users
            const users = [
                ['alice_wonder', 'rabbit_hole123', 'user', 'alice@wonderland.com'],
                ['bob_builder', 'canwefixit456', 'user', 'bob@construction.com'],
                ['charlie_brown', 'snoopy789', 'user', 'charlie@peanuts.com'],
                ['diana_prince', 'lasso_truth999', 'moderator', 'diana@justice.com'],
                ['eve_hacker', 'crypto_queen2024', 'user', 'eve@security.com'],
                ['frank_admin', 'not_the_real_admin', 'admin', 'frank@fake.com']
            ];

            for (const user of users) {
                await this.pool.request()
                    .input('username', sql.NVarChar, user[0])
                    .input('password', sql.NVarChar, user[1])
                    .input('role', sql.NVarChar, user[2])
                    .input('email', sql.NVarChar, user[3])
                    .query('INSERT INTO users (username, password, role, email) VALUES (@username, @password, @role, @email)');
            }

            // Insert admin secrets (including the flag)
            const secrets = [
                ['FAKE_KEY_001', 'H7CTF{this_is_not_the_real_flag}', 1, 'Decoy flag to confuse attackers'],
                ['SUPER_SECRET_ADMIN_KEY_2024', 'H7CTF{W1LD_C4RD5_4R3_D4NG3R0U5_1N_5QL_S3RV3R}', 9, 'The real flag - highly classified'],
                ['BACKUP_KEY_999', 'H7CTF{backup_systems_are_important}', 5, 'Backup system access key']
            ];

            for (const secret of secrets) {
                await this.pool.request()
                    .input('secret_key', sql.NVarChar, secret[0])
                    .input('flag', sql.NVarChar, secret[1])
                    .input('access_level', sql.Int, secret[2])
                    .input('description', sql.NVarChar, secret[3])
                    .query('INSERT INTO admin_secrets (secret_key, flag, access_level, description) VALUES (@secret_key, @flag, @access_level, @description)');
            }

            console.log('✅ Sample data inserted successfully');
        } catch (err) {
            console.error('❌ Error inserting sample data:', err);
        }
    }

    // VULNERABLE: Search function using wildcards
    async searchUsers(query, callback) {
        try {
            // Intentionally vulnerable - direct string concatenation
            const sqlQuery = `SELECT username, email, role, created_at FROM users WHERE username LIKE '%${query}%' OR email LIKE '%${query}%'`;
            
            console.log('🔍 Executing search query:', sqlQuery);
            
            const result = await this.pool.request().query(sqlQuery);
            callback(null, result.recordset);
        } catch (err) {
            console.error('❌ Search error:', err.message);
            callback(err, null);
        }
    }

    // VULNERABLE: User details endpoint
    async getUserDetails(username, callback) {
        try {
            const sqlQuery = `SELECT id, username, email, role, created_at, last_login FROM users WHERE username = '${username}'`;
            
            console.log('👤 Fetching user details:', sqlQuery);
            
            const result = await this.pool.request().query(sqlQuery);
            callback(null, result.recordset[0]);
        } catch (err) {
            console.error('❌ User details error:', err.message);
            callback(err, null);
        }
    }

    // VULNERABLE: Login function with wildcards
    async authenticateUser(username, password, callback) {
        try {
            const sqlQuery = `SELECT * FROM users WHERE username LIKE '${username}' AND password LIKE '${password}'`;
            
            console.log('🔐 Authentication attempt:', sqlQuery);
            
            const result = await this.pool.request().query(sqlQuery);
            callback(null, result.recordset[0]);
        } catch (err) {
            console.error('❌ Authentication error:', err.message);
            callback(err, null);
        }
    }

    async close() {
        try {
            await sql.close();
            console.log('✅ Database connection closed');
        } catch (err) {
            console.error('❌ Error closing database:', err.message);
        }
    }
}

module.exports = SQLServerDatabase;