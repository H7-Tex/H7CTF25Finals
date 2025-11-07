# 🚀 Quick Start Guide - H7CTF NoSQL Injection Challenge

## Option 1: Automated Setup (Recommended)

### Using PowerShell Script:
```powershell
.\setup-mongodb.ps1
npm start
```

### Using Batch File:
```cmd
setup-mongodb.bat
npm start
```

Then open: **http://localhost:3000/login.html**

---

## Option 2: Manual Setup

### Step 1: Start MongoDB
Open PowerShell and run:
```powershell
# Create data directory
mkdir C:\data\db

# Start MongoDB server (keep this terminal open!)
mongod --dbpath=C:\data\db
```

### Step 2: Create Test User
Open **another** PowerShell terminal:
```powershell
# Connect to MongoDB
mongosh

# In mongosh shell, run:
use nosql_ctf
db.users.insertOne({ 
    username: "admin", 
    password: "SuperSecret123!", 
    createdAt: new Date(), 
    updatedAt: new Date() 
})
exit
```

### Step 3: Start the Application
In your project directory:
```powershell
npm start
```

### Step 4: Access the Challenge
Open browser: **http://localhost:3000/login.html**

---

## 🎯 Testing the Challenge

Try logging in with:
- Username: `admin`
- Password: `SuperSecret123!`

This should work normally. Now try to exploit the NoSQL injection!

---

## 🔍 Exploitation Hints

1. Open browser DevTools (F12)
2. Go to Network tab
3. Try logging in and capture the request
4. Modify the JSON payload...
5. Think about MongoDB operators like `$ne`, `$gt`, `$regex`

---

## 🛑 Stop MongoDB

To stop MongoDB server:
```powershell
# Find the process
Get-Process mongod

# Stop it
Stop-Process -Name mongod
```

---

## 📝 Project Files

- `src/app.js` - Main application
- `src/routes/auth.js` - **VULNERABLE** login endpoint
- `src/models/User.js` - User model
- `public/login.html` - Login page
- `.env` - Environment configuration

---

## ⚠️ Troubleshooting

### MongoDB won't start?
```powershell
# Make sure no other MongoDB instance is running
Get-Process mongod | Stop-Process

# Try starting again
mongod --dbpath=C:\data\db
```

### Can't connect to database?
- Check if MongoDB is running
- Verify `.env` file exists with correct URI
- Make sure port 27017 is not blocked

### Port 3000 already in use?
Change the port in `.env`:
```
PORT=3001
```

---

Good luck with the challenge! 🎯
