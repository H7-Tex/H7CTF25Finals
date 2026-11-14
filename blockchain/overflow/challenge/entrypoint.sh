#!/bin/bash
set -euo pipefail

# Use the Anvil-injected FLAG env var when running on the platform.
# Fall back to generating a dynamic flag for standalone / local testing.
if [ -z "${FLAG:-}" ]; then
    FLAG="H7CTF{1nt3ger_und3rf10w_1n_th1s_d4y_and_ag3_$(uuidgen)}"
fi

# Write flag and restrict permissions
printf '%s\n' "$FLAG" > /home/ctfuser/flag.txt
chown ctfuser:ctfuser /home/ctfuser/flag.txt
chmod 400 /home/ctfuser/flag.txt

cd /home/ctfuser

# Run server as ctfuser
exec su ctfuser -c "./token-overflow-server"
