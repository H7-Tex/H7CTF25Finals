# Prototype Pollution CTF Challenge (lodash < 4.17.11)

Overview
- This is a small CTF challenge demonstrating classic prototype pollution via vulnerable lodash versions (e.g. 4.17.10). The app merges user JSON into server config using `_.merge()` which allows an attacker to set properties on `Object.prototype` via `__proto__`.

Goal
- Use a JSON payload to pollute the prototype and cause `config.isAdmin` to become `true`, then access `/admin/flag` to retrieve the flag.

How it works
- The server runs `_.merge(config, req.body)` on incoming JSON at `/merge` (and also at `/add` in the UI flow).
- In vulnerable lodash releases, merging `{ "__proto__": { "isAdmin": true } }` will set `Object.prototype.isAdmin = true`, making `config.isAdmin` evaluate to `true` for all objects that read the property.

Files
- `server.js` — Express app with `/merge`, `/add` (UI uses `/add`) and `/admin/flag`.
- `public/` — static frontend (index.html + app.js) that looks like a todo list where guests can add tasks.
- `exploit.js` — Node script demonstrating the attack.
- `package.json` — pins `lodash@4.17.10` (vulnerable) and `express`.

Run (locally)
1. Install dependencies:

```powershell
npm install
```

2. Start the server:

```powershell
npm start
```

3. Open the UI in your browser at http://127.0.0.1:3000, or run the exploit script in another shell:

```powershell
node exploit.js
# OR using curl to craft the prototype payload manually:
curl -X POST -H "Content-Type: application/json" -d "{\"__proto__\":{\"isAdmin\":true}}" http://127.0.0.1:3000/merge
curl http://127.0.0.1:3000/admin/flag
```

UI behavior
- The site serves a small todo-list UI at `/`. Guests can type a task and click Add; the UI sends a JSON payload of the form `{ "userInput": { "task": "..." } }` to `/add`.
- The server intentionally uses `_.merge(config, req.body)` before appending the provided task to the todo list so the UI behaves like a normal webapp while remaining vulnerable to crafted prototype pollution requests.

Expected result
- After sending the payload, `/admin/flag` will respond with `CTF{prototype_pollution_success}` when prototype pollution sets `isAdmin` to `true`.

Mitigations
- Upgrade lodash to >= 4.17.11 (patch added to prevent merging into prototype properties).
- Validate or whitelist allowed properties before merging user input.
- Use safe merge libraries that ignore `__proto__`, `constructor`, or `prototype` keys.

Notes on challenge realism
- The UI intentionally looks like an ordinary todo application. Regular users will add tasks normally and see them in the list. An attacker or CTF player can craft a POST to `/add` (or `/merge`) with `{"__proto__":{"isAdmin":true}}` to pollute the prototype and gain admin access, but that vector is not visible in the UI.

CTF notes
- Score suggestion: 50-150 points depending on contest difficulty.
- Hints: "Think about Object.prototype and __proto__". The vulnerability is in the merge step.
# Prototype Pollution CTF Challenge (lodash < 4.17.11)

Overview
- This is a small CTF challenge demonstrating classic prototype pollution via vulnerable lodash versions (e.g. 4.17.10). The app merges user JSON into server config using `_.merge()` which allows an attacker to set properties on `Object.prototype` via `__proto__`.

Goal
- Use a JSON payload to pollute the prototype and cause `config.isAdmin` to become `true`, then access `/admin/flag` to retrieve the flag.

How it works
- The server runs `_.merge(config, req.body)` on incoming JSON at `/merge`.
- In vulnerable lodash releases, merging `{ "__proto__": { "isAdmin": true } }` will set `Object.prototype.isAdmin = true`, making `config.isAdmin` evaluate to `true` for all objects that read the property.

Files
- `server.js` — Express app with `/merge` and `/admin/flag`.
- `exploit.js` — Node script demonstrating the attack.
- `package.json` — pins `lodash@4.17.10` (vulnerable) and `express`.

Run (locally)
1. Install dependencies:

```powershell
npm install
```

2. Start the server:

```powershell
npm start
```

3. In another shell, run the exploit (or use curl):

```powershell
node exploit.js
# OR using curl:
curl -X POST -H "Content-Type: application/json" -d "{\"__proto__\":{\"isAdmin\":true}}" http://127.0.0.1:3000/merge
curl http://127.0.0.1:3000/admin/flag
```

Expected result
- After sending the payload, `/admin/flag` will respond with `CTF{prototype_pollution_success}`.

Mitigations
- Upgrade lodash to >= 4.17.11 (patch added to prevent merging into prototype properties).
- Validate or whitelist allowed properties before merging user input.
- Use safe merge libraries that ignore `__proto__`, `constructor`, or `prototype` keys.

CTF notes
- Score suggestion: 50-150 points depending on contest difficulty.
- Hints: "Think about Object.prototype and __proto__". The vulnerability is in the merge step.

docker build --no-cache -t web_n1sh_5:latest .
