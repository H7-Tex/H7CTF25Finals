# Todo

**Category:** Web  **Author:** N1sh

Run: `./run.sh` (or `docker build -t web_n1sh_5 . && docker run -p 3000:3000 web_n1sh_5`)

## Solution

A guest todo list. Adding a task POSTs `{"userInput":{"task":"..."}}` to `/add`. `/admin` just plays a video and `/admin/flag` says access denied. The `/admin` page source has a leftover TODO about `isAdmin`, so the goal is to make `config.isAdmin` truthy.

`package.json` pins `lodash@4.17.10`, and the server does `_.merge(config, req.body)` on every `/add` and `/merge` request. That version of `_.merge` follows `__proto__`, so this is classic prototype pollution. `config` has no own `isAdmin`, so once `Object.prototype.isAdmin` is set the check passes.

The UI path works without any tooling: if the task text looks like JSON, the server parses it and merges that too. Type this into the task box:

```
{"__proto__":{"isAdmin":true}}
```

Or with curl:

```
curl -X POST http://localhost:3000/merge -H 'Content-Type: application/json' \
  -d '{"__proto__":{"isAdmin":true}}'
curl http://localhost:3000/admin/flag
```

`exploit.js` tries the same vectors in a loop.

Unintended: `/merge` with plain `{"isAdmin":true}` sets an own property on `config` and gets the flag without any pollution. There's also a `/debug` endpoint left in that shows whether the prototype got polluted.

Flag: `H7CTF{pr0t0typ3_p0llut10n_15_d4ng3r0u5_<uuid>}` (UUID generated per container)
