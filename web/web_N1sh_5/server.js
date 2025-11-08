const express = require('express');
const _ = require('lodash');

const app = express();
app.use(express.json());

// Application config with default guest role and a todo list
const config = {
  isGuest: true,
  flag: process.env.DYNAMIC_FLAG || 'H7CTF{pr0t0typ3_p0llut10n_15_d4ng3r0u5_default}',
  // tasks will be shown in the UI; start with an example
  tasks: [
    { id: 1, title: 'Welcome! Add tasks using the form below.' }
  ],
};

// Serve static frontend
app.use(express.static('public'));

// Legacy merge endpoint (keeps previous behavior for exploit scripts)
app.post('/merge', (req, res) => {
  try {
    // Vulnerable merge: merging untrusted input into config
    _.merge(config, req.body);
    // Log payload and debug state for debugging/CTF visibility
    try {
      const protoHas = Object.prototype.hasOwnProperty('isAdmin');
      const protoVal = Object.prototype.isAdmin === true;
      const configHasOwn = Object.prototype.hasOwnProperty.call(config, 'isAdmin');
      const configVal = !!config.isAdmin;
      console.log('=== REQUEST /merge ===');
      console.log('payload:', JSON.stringify(req.body));
      console.log('protoHas:', protoHas, 'protoVal:', protoVal, 'configHasOwn:', configHasOwn, 'configVal:', configVal);
      console.log('======================');
    } catch (e) {
      console.error('logging error', e);
    }

    // Do not expose full config to clients — return only tasks for the UI
    return res.json({ ok: true, tasks: config.tasks });
  } catch (err) {
    return res.status(500).json({ ok: false, error: String(err) });
  }
});

// Simulated "add task" endpoint used by the UI. It still performs a merge
// of the incoming JSON into the app config (vulnerable). After merge,
// if the request supplied a task we append it to the tasks array so the UI
// looks and feels like a real todo app.
app.post('/add', (req, res) => {
  try {
    // Vulnerable merge (intentional for CTF)
    // Merge the request body first (keeps legacy behavior)
    _.merge(config, req.body);

    // If the client provided a task as a string and it looks like JSON,
    // try to parse it and also merge the parsed object. This models a
    // real-world app that might accept JSON in a free-text field and
    // inadvertently merge it into server config. It allows a player to
    // type '{"__proto__": {"isAdmin": true}}' into the task input
    // (which the UI will send as a string) and trigger prototype pollution.
    if (req.body && req.body.userInput && typeof req.body.userInput.task === 'string') {
      const taskText = req.body.userInput.task.trim();
      if ((taskText.startsWith('{') && taskText.endsWith('}')) ||
          (taskText.startsWith('[') && taskText.endsWith(']'))) {
        try {
          const parsed = JSON.parse(taskText);
          // merge parsed object into config as well
          _.merge(config, parsed);
          // Intentional vulnerable behavior for the CTF: if the parsed
          // object contains a __proto__ key, also merge it into
          // Object.prototype so prototype pollution succeeds.
          if (parsed && typeof parsed === 'object' && parsed.__proto__ && typeof parsed.__proto__ === 'object') {
            _.merge(Object.prototype, parsed.__proto__);
          }
        } catch (e) {
          // ignore JSON parse errors — treat task as plain text
        }
      }

      // Append the original task text for UI friendliness so the list
      // appears normal to guest users.
      const nextId = config.tasks.length ? config.tasks[config.tasks.length - 1].id + 1 : 1;
      config.tasks.push({ id: nextId, title: req.body.userInput.task });
    }

      // Log payload and debug state for debugging/CTF visibility
      try {
        const protoHas = Object.prototype.hasOwnProperty('isAdmin');
        const protoVal = Object.prototype.isAdmin === true;
        const configHasOwn = Object.prototype.hasOwnProperty.call(config, 'isAdmin');
        const configVal = !!config.isAdmin;
        console.log('=== REQUEST /add ===');
        console.log('payload:', JSON.stringify(req.body));
        console.log('protoHas:', protoHas, 'protoVal:', protoVal, 'configHasOwn:', configHasOwn, 'configVal:', configVal);
        console.log('====================');
      } catch (e) {
        console.error('logging error', e);
      }

      // Return only tasks so the UI can render them without seeing internal flags
      return res.json({ ok: true, tasks: config.tasks });
  } catch (err) {
    return res.status(500).json({ ok: false, error: String(err) });
  }
});

app.get('/admin', (req, res) => {
  // Admin video page with the requested heading
   if (config.isAdmin) {
    return res.send(`<!doctype html>
<html><head><meta charset="utf-8"><title>root@server:~#</title>
<style>body{background:#001; color:#0f0; font-family:monospace; padding:2rem} .box{border:1px solid #0f0; padding:1rem; background:#002} video{width:100%; max-width:600px; margin:1rem 0}</style>
</head><body>
<h1>root@server:~# access granted</h1>
<div class="box">FLAG: <strong>${config.flag}</strong></div>
<h2>Ennathu Nagarjuna va?</h2>
<video controls autoplay>
  <source src="/video/suma.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
</body></html>`);
  }
  else{
    return res.send(`<!doctype html>
<html><head><meta charset="utf-8"><title>Admin Panel</title>
<style>
body{background:#001; color:#0f0; font-family:monospace; margin:0; padding:0; overflow:hidden} 
h2{color:#0f0; position:absolute; top:10px; left:20px; z-index:10; margin:0}
video{width:100vw; height:100vh; object-fit:contain}
</style>
</head><body>

<h2>Ennthu Nagaarjuna va?</h2>

<h2> <h2>
<video id="adminVideo" controls>
  <source src="/video/suma.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
<script>
document.addEventListener('DOMContentLoaded', function() {
  const video = document.getElementById('adminVideo');
  video.muted = false;
  video.play().catch(e => {
    console.log('Autoplay failed:', e);
    // Fallback: try with muted first, then unmute after play starts
    video.muted = true;
    video.play().then(() => {
      setTimeout(() => { video.muted = false; }, 100);
    });
  });
});
</script>
//TODO 
// need to set isAdmin Flase
// need to redesign todo
// need to style PP....
</body></html>`);
  }

  // Forbidden: show an access denied page
//   return res.status(403).send(`<!doctype html>
// <html><head><meta charset="utf-8"><title>access denied</title>
// <style>body{background:#111; color:#f33; font-family:monospace; padding:2rem}</style>
// </head><body>
// <h1>access denied</h1>
// <p>Insufficient privileges. Try again.</p>
// </body></html>`);
});

app.get('/admin/flag', (req, res) => {
  // Render a simple hacker-themed page. If admin, show the flag in a styled box.
  if (config.isAdmin) {
    return res.send(`<!doctype html>
<html><head><meta charset="utf-8"><title>root@server:~#</title>
<style>body{background:#001; color:#0f0; font-family:monospace; padding:2rem} .box{border:1px solid #0f0; padding:1rem; background:#002} video{width:100%; max-width:600px; margin:1rem 0}</style>
</head><body>
<h1>root@server:~# access granted</h1>
<div class="box">FLAG: <strong>${config.flag}</strong></div>
<h2>Ennthu Nagaarjuna va?</h2>
<video controls autoplay>
  <source src="/video/suma.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
</body></html>`);
  }

  // Forbidden: show an access denied hacker-themed page (do not reveal flag)
  return res.status(403).send(`<!doctype html>
<html><head><meta charset="utf-8"><title>access denied</title>
<style>body{background:#111; color:#f33; font-family:monospace; padding:2rem} .box{border:1px solid #f33; padding:1rem; background:#220}</style>
</head><body>
<h1>access denied</h1>
<p>Insufficient privileges. Try again.</p>
</body></html>`);
});

// Temporary debug endpoint to inspect prototype and config state.
// Returns whether Object.prototype has isAdmin and whether config has own isAdmin.
app.get('/debug', (req, res) => {
  try {
    const protoHas = Object.prototype.hasOwnProperty('isAdmin');
    const protoVal = Object.prototype.isAdmin === true;
    const configHasOwn = Object.prototype.hasOwnProperty.call(config, 'isAdmin');
    const configVal = !!config.isAdmin;
    return res.json({ protoHas, protoVal, configHasOwn, configVal });
  } catch (e) {
    return res.status(500).json({ ok: false, error: String(e) });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log('UI available at http://localhost:' + PORT);
});
