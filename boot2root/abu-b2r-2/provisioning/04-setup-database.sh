#!/bin/bash
set -e

echo "[*] Setting up database..."

# Create data directory
mkdir -p /opt/cpr/data
chown svc-runtime:svc-runtime /opt/cpr/data

# Create Python script to initialize database with seeded users
cat > /tmp/init_db.py << 'DBEOF'
import sqlite3
import hashlib
import secrets

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id():
    return 'usr_' + secrets.token_hex(6)

# Create database
conn = sqlite3.connect('/opt/cpr/data/users.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        name TEXT DEFAULT '',
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        bio TEXT DEFAULT '',
        is_admin INTEGER DEFAULT 0,
        privilege_level INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Seed with example users showing privilege hierarchy
# These reveal the privilege level system without being obvious
users = [
    {
        'user_id': generate_user_id(),
        'username': 'svc-metrics',
        'password': hash_password('M3tr1cs!2024'),
        'name': 'Metrics Service',
        'email': 'metrics@cpr.internal',
        'bio': 'Automated metrics collection service',
        'is_admin': 0,
        'privilege_level': 10
    },
    {
        'user_id': generate_user_id(),
        'username': 'svc-backup',
        'password': hash_password('B4ckup!2024'),
        'name': 'Backup Service',
        'email': 'backup@cpr.internal',
        'bio': 'Automated backup service account',
        'is_admin': 0,
        'privilege_level': 50
    },
    {
        'user_id': generate_user_id(),
        'username': 'admin',
        'password': hash_password(secrets.token_hex(32)),  # Random unguessable password
        'name': 'Platform Administrator',
        'email': 'admin@cpr.internal',
        'bio': 'Platform administrator account',
        'is_admin': 1,
        'privilege_level': 100
    }
]

for user in users:
    cursor.execute('''
        INSERT INTO users (user_id, username, password_hash, name, email, bio, is_admin, privilege_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user['user_id'],
        user['username'],
        user['password'],
        user['name'],
        user['email'],
        user['bio'],
        user['is_admin'],
        user['privilege_level']
    ))

conn.commit()
conn.close()

print("Database initialized with seeded users")
DBEOF

# Run the initialization script
python3 /tmp/init_db.py
rm /tmp/init_db.py

# Create a dummy file so tar has something to back up
echo "CPR Data Directory" > /opt/cpr/data/.placeholder

# Set ownership
chown -R svc-runtime:svc-runtime /opt/cpr/data

echo "[✓] Database configuration complete"
echo "    - Database path: /opt/cpr/data/users.db"
echo "    - Owner: svc-runtime:svc-runtime"
echo "    - Seeded with service accounts showing privilege hierarchy"
