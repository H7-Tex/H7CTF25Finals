#!/usr/bin/env python3
import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "/opt/cpr/data/users.db"

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def init_database():
    """Initialize the database schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
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
    """)
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id(username):
    """Generate user ID from username and timestamp"""
    timestamp = str(datetime.now().timestamp())
    data = f"{username}_{timestamp}"
    return "usr_" + hashlib.md5(data.encode()).hexdigest()[:12]

def register_user(username, email, password):
    """Register a new user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists", None
        
        # Create user
        user_id = generate_user_id(username)
        password_hash = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (user_id, username, email, password_hash)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, email, password_hash))
        
        conn.commit()
        conn.close()
        
        return True, "User registered successfully", user_id
    except Exception as e:
        return False, f"Registration failed: {str(e)}", None

def authenticate_user(username, password):
    """Authenticate user credentials"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute("""
            SELECT user_id FROM users 
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return True, "Authentication successful", result[0]
        else:
            return False, "Invalid credentials", None
    except Exception as e:
        return False, f"Authentication failed: {str(e)}", None

def get_user_details(user_id):
    """Get user details by user_id"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, name, email, bio, is_admin, privilege_level
            FROM users WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'name': result[2],
                'email': result[3],
                'bio': result[4],
                'is_admin': bool(result[5]),
                'privilege_level': result[6]
            }
        return None
    except Exception as e:
        print(f"Error getting user details: {e}")
        return None

def update_user_profile(user_id, name=None, email=None, bio=None, is_admin=None, privilege_level=None):
    """Update user profile information"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        
        if email:
            updates.append("email = ?")
            params.append(email)
        
        if bio is not None:
            updates.append("bio = ?")
            params.append(bio)
        
        if is_admin is not None:
            updates.append("is_admin = ?")
            params.append(1 if is_admin else 0)
        
        if privilege_level is not None:
            updates.append("privilege_level = ?")
            params.append(privilege_level)
        
        if not updates:
            conn.close()
            return False, "No fields to update"
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return True, "Profile updated successfully"
    except Exception as e:
        return False, f"Update failed: {str(e)}"

def is_user_admin(user_id):
    """Check if user has admin privileges"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return bool(result[0]) if result else False
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False

def list_all_users():
    """List all users (admin only)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, email, is_admin
            FROM users
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'username': row[1],
                'email': row[2],
                'role': 'admin' if row[3] else 'user'
            })
        
        conn.close()
        return users
    except Exception as e:
        print(f"Error listing users: {e}")
        return []

if __name__ == "__main__":
    # Initialize database
    init_database()
    print("Database initialized successfully")
