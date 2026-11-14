#!/bin/bash
set -euo pipefail

# Generate dynamic flag with UUID
FLAG="H7CTF{cp1_auth_byp4ss_n0_s1gn3r_ch3ck_$(uuidgen)}"

# Write flag and restrict permissions
printf '%s\n' "$FLAG" > /home/ctfuser/flag.txt
chown ctfuser:ctfuser /home/ctfuser/flag.txt
chmod 400 /home/ctfuser/flag.txt

cd /home/ctfuser

# Run server as ctfuser
exec su ctfuser -c "./escrow-bypass-server"
