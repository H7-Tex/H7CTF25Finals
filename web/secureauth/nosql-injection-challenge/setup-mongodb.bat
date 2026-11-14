@echo off
echo ===============================================
echo   H7CTF NoSQL Injection Challenge - Setup
echo ===============================================
echo.

echo [1/3] Creating MongoDB data directory...
if not exist "C:\data\db" (
    mkdir "C:\data\db"
    echo Created directory: C:\data\db
) else (
    echo Directory already exists: C:\data\db
)

echo.
echo [2/3] Starting MongoDB server...
echo MongoDB will start in a new window - KEEP IT OPEN!
echo.
start "MongoDB Server" mongod --dbpath=C:\data\db

timeout /t 5 /nobreak > nul

echo.
echo [3/3] Creating test user...
mongosh --eval "use nosql_ctf; db.users.insertOne({ username: 'admin', password: 'SuperSecret123!', createdAt: new Date(), updatedAt: new Date() }); db.users.find().pretty();"

echo.
echo ===============================================
echo   Setup Complete!
echo ===============================================
echo.
echo MongoDB is running on: mongodb://localhost:27017
echo Database: nosql_ctf
echo Test user: admin / SuperSecret123!
echo.
echo Next steps:
echo   1. Run: npm start
echo   2. Visit: http://localhost:3000/login.html
echo.
pause
