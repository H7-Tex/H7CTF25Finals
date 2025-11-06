# Platform Nine and Three-Quarters

A minimalist webapp for validating 7 horcrux flags scattered across the Discord server.

**Challenge Name:** Insanity Check  
**Webapp Title:** Platform Nine and Three-Quarters (Platform 9¾)  
**Category:** MISC / OSINT  
**Difficulty:** Easy

## Challenge Description

Seven horcruxes are hidden throughout the H7CTF Discord server. Participants must find all 7 flags in any order. Only when all horcruxes are destroyed will the final flag be revealed.

## The Seven Horcruxes

The flags are scattered across various Discord channels, messages, and locations. Players must explore thoroughly to find them all.

## Features

- Validates flags in any order
- Tracks progress per session (browser-based)
- No flag spoilers in source code (hashed server-side)
- Dynamic final flag with UUID
- Minimalist, stoic interface

## Running Locally

```bash
npm install
node server.js
```

Access at `http://localhost:3000`

## Docker Build & Run

```bash
# Quick build and test
./build.sh

# Or manually
docker build -t platform-nine-three-quarters .
docker run -p 3000:3000 platform-nine-three-quarters
```

## Architecture

- **Backend**: Express.js server
- **Frontend**: Vanilla HTML/CSS/JS (no frameworks)
- **Storage**: In-memory sessions (upgrade to Redis for production)
- **Security**: Flags are SHA-256 hashed, never sent to client

## Notes

- Session persists via localStorage
- Final flag is dynamically generated with UUID on container start
- Completely stoic design - no emojis, minimal styling
- All 7 flags must be submitted before final flag is revealed
