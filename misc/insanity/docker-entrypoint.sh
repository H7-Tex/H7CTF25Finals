#!/bin/sh

# Generate unique flag with UUID
UUID=$(uuidgen)
FLAG_VALUE="H7CTF{dumbled0re_w0uld_b3_very_pr0ud_${UUID}}"

echo "========================================"
echo "Platform Nine and Three-Quarters"
echo "========================================"
echo "Dynamic flag generated for this session"
echo "========================================"

# Export flag as environment variable
export FLAG="$FLAG_VALUE"

echo "Starting platform on port 3000..."

# Start Node.js server
exec node server.js
