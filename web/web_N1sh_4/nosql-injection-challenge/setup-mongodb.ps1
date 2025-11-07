# H7CTF NoSQL Injection Challenge - MongoDB Setup Script
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  H7CTF NoSQL Injection Challenge - Setup" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if MongoDB is installed
Write-Host "[1/4] Checking MongoDB installation..." -ForegroundColor Green
if (Get-Command mongod -ErrorAction SilentlyContinue) {
    Write-Host "✓ MongoDB is installed" -ForegroundColor Green
} else {
    Write-Host "✗ MongoDB is not installed!" -ForegroundColor Red
    Write-Host "Please install MongoDB from: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
    exit
}

# Create data directory
Write-Host "`n[2/4] Creating MongoDB data directory..." -ForegroundColor Green
$dataPath = "C:\data\db"
if (!(Test-Path $dataPath)) {
    New-Item -ItemType Directory -Path $dataPath -Force | Out-Null
    Write-Host "✓ Created directory: $dataPath" -ForegroundColor Green
} else {
    Write-Host "✓ Directory already exists: $dataPath" -ForegroundColor Green
}

# Start MongoDB in background
Write-Host "`n[3/4] Starting MongoDB server..." -ForegroundColor Green
$mongoProcess = Start-Process -FilePath "mongod" -ArgumentList "--dbpath=$dataPath" -PassThru -WindowStyle Minimized
Start-Sleep -Seconds 3

if ($mongoProcess -and !$mongoProcess.HasExited) {
    Write-Host "✓ MongoDB server started (PID: $($mongoProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to start MongoDB server" -ForegroundColor Red
    exit
}

# Create test user
Write-Host "`n[4/4] Creating test user..." -ForegroundColor Green
Start-Sleep -Seconds 2

$mongoScript = @"
use nosql_ctf
db.users.insertOne({ 
    username: "admin", 
    password: "SuperSecret123!", 
    createdAt: new Date(), 
    updatedAt: new Date() 
})
db.users.find().pretty()
exit
"@

$mongoScript | mongosh --quiet

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✓ Setup Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "MongoDB is running on: mongodb://localhost:27017" -ForegroundColor Yellow
Write-Host "Database: nosql_ctf" -ForegroundColor Yellow
Write-Host "Test user: admin / SuperSecret123!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: npm start" -ForegroundColor White
Write-Host "  2. Visit: http://localhost:3000/login.html" -ForegroundColor White
Write-Host ""
Write-Host "To stop MongoDB: Stop-Process -Id $($mongoProcess.Id)" -ForegroundColor Gray
Write-Host ""
