#!/bin/bash

# Generate dynamic flag following H7CTF format
FLAG="H7CTF{pr0t0typ3_p0llut10n_15_d4ng3r0u5_$(uuidgen)}"

# Set environment variables for the application
export PORT=${PORT:-3000}
export NODE_ENV=${NODE_ENV:-production}
export DYNAMIC_FLAG="${FLAG}"

echo "Dynamic flag generated: ${FLAG}"
echo "Application starting on port: ${PORT}"

# Execute the main command
exec "$@"