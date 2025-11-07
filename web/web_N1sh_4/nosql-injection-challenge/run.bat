@echo off

echo Starting web_N1sh_4 NoSQL Injection Challenge...
echo This will start both MongoDB and the web application...

REM Build and start with docker-compose
docker-compose up -d --build

echo.
echo 🚀 Challenge started successfully!
echo 📱 Application: http://localhost:3000
echo 🔍 Login page: http://localhost:3000/login.html
echo 📊 MongoDB: localhost:27017
echo.
echo Use 'docker-compose logs web_n1sh_4' to view application logs
echo Use 'docker-compose logs mongodb' to view database logs
echo Use 'docker-compose down' to stop all services

pause