#!/bin/bash
set -euo pipefail

# Generate dynamic flag with UUID
FLAG="H7CTF{1nt3ger_und3rf10w_1n_th1s_d4y_and_ag3_$(uuidgen)}"

# Write flag and restrict permissions
printf '%s\n' "$FLAG" > /home/ctfuser/flag.txt
chown ctfuser:ctfuser /home/ctfuser/flag.txt
chmod 400 /home/ctfuser/flag.txt

cd /home/ctfuser

# Run server as ctfuser
exec su ctfuser -c "./token-overflow-server"
