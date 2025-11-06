#!/bin/sh

# Generate unique flag with UUID
UUID=$(uuidgen)
FLAG_VALUE="H7CTF{pwn_4_d4y_keeps_4_d0ct0r_aw4y_${UUID}}"

echo "========================================"
echo "PWN Challenge 1 Starting"
echo "========================================"
echo "Dynamic flag generated for this session"
echo "========================================"

# Write flag to a randomly named file in /tmp (writable by ctf user)
FLAGPATH="/tmp/flag-${UUID}.txt"
echo "$FLAG_VALUE" > "$FLAGPATH"

echo "Flag written to: $FLAGPATH"
echo "Starting challenge on port 1337..."

# Change to the challenge directory and start with socat
cd /home/ctf
exec socat tcp-l:1337,reuseaddr,fork EXEC:./challenge
