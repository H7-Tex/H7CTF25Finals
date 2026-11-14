#!/bin/bash

# Generate dynamic flag following H7CTF format
FLAG="H7CTF{n05ql_1nj3ct10n_15_d4ng3r0u5_$(uuidgen)}"

# Set environment variables
export DYNAMIC_FLAG="${FLAG}"
export NODE_ENV=${NODE_ENV:-production}
export PORT=${PORT:-3000}
export MONGODB_URI="mongodb://localhost:27017/nosql_ctf"

echo "Dynamic flag generated: ${FLAG}"
echo "Starting MongoDB..."

# Start MongoDB in background
mongod --dbpath /data/db --bind_ip_all --port 27017 --fork --logpath /var/log/mongodb.log

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to be ready..."
sleep 10

# Check if MongoDB is actually running
if pgrep mongod > /dev/null; then
    echo "MongoDB started successfully"
else
    echo "Failed to start MongoDB"
    exit 1
fi

# Seed the database
echo "Seeding database..."
cd /app
node seed.js

echo "Starting the application on port: ${PORT}"

# Start the application
exec "$@"