#!/bin/bash

FLAG="H7CTF{ENj0Y_YOU4_S3CR3T_C0FFE3_$(uuidgen)}"

echo "$FLAG" > /home/ctfuser/flag.txt
chmod 644 /home/ctfuser/flag.txt

cd /home/ctfuser

exec su ctfuser -c "python3 server.py"
