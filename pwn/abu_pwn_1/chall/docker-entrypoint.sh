#!/bin/sh

UUID=$(uuidgen)
FLAG_VALUE="H7CTF{pwn_4_d4y_keeps_4_d0ct0r_aw4y_${UUID}}"

FLAGPATH="/tmp/flag-${UUID}.txt"
echo "$FLAG_VALUE" > "$FLAGPATH"

echo "Flag written to: $FLAGPATH"
echo "Starting challenge on port 1337..."

cd /home/ctf
exec socat tcp-l:1337,reuseaddr,fork EXEC:./challenge