const express = require('express');
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Store the 7 horcrux flags (hashed for security)
const HORCRUXES = [
  'H7CTF{c4ll_0ut_my_name}',
  'H7CTF{always_check_the_discord_start_messages_of_a_ctf_i_have_seen_it_a_number_of_times}',
  'H7CTF{h1d1ng_fl4gs_1n_d1sc0rd_1s_cr4zy}',
  'H7CTF{never_gonna_give_you_up_never_gonna_let_you_down}',
  'H7CTF{keeping_this_small_to_make_life_easier}',
  'H7CTF{do_you_believe_in_love_at_first_sight}',
  'H7CTF{https://pbs.twimg.com/media/F43XxNAb0AAugH3?format=jpg&name=small}'
].map(flag => crypto.createHash('sha256').update(flag).digest('hex'));

// Store session data (in production, use Redis or similar)
const sessions = new Map();

// Validate a single flag
app.post('/api/validate', (req, res) => {
  const { flag, sessionId } = req.body;
  
  if (!flag || !sessionId) {
    return res.json({ valid: false, message: 'Invalid request' });
  }
  
  // Hash the submitted flag
  const flagHash = crypto.createHash('sha256').update(flag).digest('hex');
  
  // Check if it matches any horcrux
  const horcruxIndex = HORCRUXES.indexOf(flagHash);
  
  if (horcruxIndex === -1) {
    return res.json({ valid: false, message: 'Invalid horcrux' });
  }
  
  // Get or create session
  if (!sessions.has(sessionId)) {
    sessions.set(sessionId, new Set());
  }
  
  const foundHorcruxes = sessions.get(sessionId);
  
  // Check if already found
  if (foundHorcruxes.has(horcruxIndex)) {
    return res.json({ 
      valid: true, 
      duplicate: true,
      found: foundHorcruxes.size,
      total: 7,
      message: 'Horcrux already destroyed'
    });
  }
  
  // Add to found horcruxes
  foundHorcruxes.add(horcruxIndex);
  
  const allFound = foundHorcruxes.size === 7;
  
  res.json({
    valid: true,
    duplicate: false,
    found: foundHorcruxes.size,
    total: 7,
    complete: allFound,
    message: allFound ? 'All horcruxes destroyed' : `Horcrux ${foundHorcruxes.size} destroyed`
  });
});

// Get final flag (only if all 7 found)
app.post('/api/final', (req, res) => {
  const { sessionId } = req.body;
  
  if (!sessionId || !sessions.has(sessionId)) {
    return res.json({ error: 'Invalid session' });
  }
  
  const foundHorcruxes = sessions.get(sessionId);
  
  if (foundHorcruxes.size !== 7) {
    return res.json({ 
      error: 'Not all horcruxes destroyed',
      found: foundHorcruxes.size,
      remaining: 7 - foundHorcruxes.size
    });
  }
  
  // Return the final flag from environment variable
  const finalFlag = process.env.FLAG || 'H7CTF{flag_not_set}';
  
  res.json({
    success: true,
    flag: finalFlag,
    message: 'The final secret revealed'
  });
});

// Get progress
app.post('/api/progress', (req, res) => {
  const { sessionId } = req.body;
  
  if (!sessionId) {
    return res.json({ found: 0, total: 7 });
  }
  
  const foundHorcruxes = sessions.get(sessionId) || new Set();
  
  res.json({
    found: foundHorcruxes.size,
    total: 7,
    complete: foundHorcruxes.size === 7
  });
});

app.listen(PORT, () => {
  console.log(`Platform Nine and Three-Quarters running on port ${PORT}`);
  console.log(`Final flag loaded: ${process.env.FLAG ? 'Yes' : 'No'}`);
});
