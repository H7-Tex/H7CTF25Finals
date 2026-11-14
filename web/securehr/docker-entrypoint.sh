#!/bin/bash

# Generate dynamic flag following H7CTF format
FLAG="H7CTF{W1LD_C4RD5_4R3_D4NG3R0U5_1N_5QL_1NJ3CT10N_$(uuidgen)}"

# Set environment variables for the application
export PORT=${PORT:-3000}
export NODE_ENV=${NODE_ENV:-production}
export DYNAMIC_FLAG="${FLAG}"

echo "Dynamic flag generated: ${FLAG}"
echo "Application starting on port: ${PORT}"

# Execute the main command
exec "$@"