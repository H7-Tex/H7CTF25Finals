#!/bin/sh

UUID=$(uuidgen)
FLAG_VALUE="H7CTF{y0u_h34p_wh4t_y0u_s0w_${UUID}"

FLAGPATH="/tmp/flag-${UUID}.txt"
echo "$FLAG_VALUE" > "$FLAGPATH"

echo "Flag written to: $FLAGPATH"
echo "Starting challenge on port 1337..."

cd /home/ctf
exec socat tcp-l:1337,reuseaddr,fork EXEC:./challenge