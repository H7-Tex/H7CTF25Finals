#!/usr/bin/env python3
import socket
import random
import os
import sys
import threading
from wordlists import COFFEE_NAMES, TARGET_WORDS
from utils import dual_affine_encrypt, generate_random_keys


class CoffeeChallenge:
    def __init__(self, seed=None, flag_template=None):
        if seed is not None:
            random.seed(seed)
        
        self.a1, self.b1, self.a2, self.b2 = generate_random_keys(seed)

        self.target_word = random.choice(TARGET_WORDS).upper()

        self.flag_template = flag_template if flag_template else 'H7CTF{ENj0Y_YOU4_S3CR3T_C0FFE3}'
        
        print(f"[Server] Challenge initialized")
        print(f"[Server] Hidden word: {self.target_word}")
        print(f"[Server] Affine keys: (a1={self.a1}, b1={self.b1}), (a2={self.a2}, b2={self.b2})")
        print(f"[Server] Flag: {self.flag_template}")
    
    def encrypt_guess(self, guess: str) -> str:
        return dual_affine_encrypt(guess.upper(), self.a1, self.b1, self.a2, self.b2)
    
    def is_valid_coffee(self, guess: str) -> bool:
        return guess.lower() in COFFEE_NAMES
    
    def check_guess(self, guess: str) -> bool:
        return guess.upper() == self.target_word


def handle_client(conn, addr, challenge):
    print(f"[Server] Connection from {addr}")
    
    encrypted_target = challenge.encrypt_guess(challenge.target_word)
    
    welcome = f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                ☕ Coffee Would Be Nice! ☕                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Welcome, weary traveler, to the Hidden Café!

I am the Oracle of Beans, keeper of caffeinated secrets. A peculiar
customer left behind a mysterious note before vanishing into the 
morning mist. The note contains a single encrypted word:

                    ✨ {encrypted_target} ✨

If you can find this word, I will reward you with the legendary Ambrosiac Coffee.
My enchanted espresso machine will transform any coffee name you 
speak into its encrypted form.

Study the patterns. Understand the magic. But choose wisely - 
you have only ONE chance to guess the hidden word!

╭─────────────────────────────────────────────────────────────╮
│  Commands:                                                  │
│    ENCRYPT <coffee>  - See a coffee name encrypted         │
│    GUESS <word>      - Make your one and only guess!       │
╰─────────────────────────────────────────────────────────────╯

💡 Note: The hidden word can be anything

The Oracle awaits your questions...

"""
    conn.sendall(welcome.encode())
    
    guess_made = False
    
    try:
        while True:
            conn.sendall(b"> ")
            data = conn.recv(1024).decode().strip()
            
            if not data:
                break

            parts = data.split(None, 1)
            if len(parts) == 0:
                continue
            
            command = parts[0].upper()
            
            if command == "ENCRYPT":
                if len(parts) < 2:
                    conn.sendall(b"Usage: ENCRYPT <coffee_name>\n")
                    continue
                
                coffee = parts[1].strip()

                if not challenge.is_valid_coffee(coffee):
                    response = "\n🤔 The Oracle raises an eyebrow...\n"
                    response += f"\"'{coffee}'? That doesn't sound like any coffee I know!\"\n"
                    conn.sendall(response.encode())
                    continue

                encrypted = challenge.encrypt_guess(coffee)
                response = "\n✨ The espresso machine whirs and hums...\n"
                response += f"   {coffee.upper()} transforms into: {encrypted}\n"
                response += "✨ The Oracle nods knowingly.\n\n"
                conn.sendall(response.encode())
            
            elif command == "GUESS":
                if len(parts) < 2:
                    conn.sendall(b"Usage: GUESS <word>\n")
                    continue

                if guess_made:
                    response = "\n⚠️  The Oracle shakes their head slowly...\n"
                    response += "\"You've already made your guess, traveler. The magic only works once.\"\n"
                    response += "The connection fades to darkness...\n\n"
                    conn.sendall(response.encode())
                    break
                
                guess_made = True
                guess = parts[1].strip()

                if challenge.check_guess(guess):
                    response = "\n╔═══════════════════════════════════════════════════════════╗\n"
                    response += "║                                                           ║\n"
                    response += "║  ✨ The Oracle's eyes light up with ancient wisdom! ✨   ║\n"
                    response += "║                                                           ║\n"
                    response += "╚═══════════════════════════════════════════════════════════╝\n\n"
                    response += "\"Remarkable! You've deciphered the pattern and uncovered\n"
                    response += " the hidden word: " + challenge.target_word + "\"\n\n"
                    response += "The Oracle smiles and hands you a steaming cup. As you peer\n"
                    response += "into the foam, you see letters forming...\n\n"
                    flag_text = challenge.flag_template
                    
                    response += f"     🏆 FLAG: {flag_text} 🏆\n\n"
                    response += "\"May your future be as bright as a perfect morning brew!\"\n"
                    response += "═══════════════════════════════════════════════════════════\n"
                    conn.sendall(response.encode())
                    break
                else:
                    response = "\n╔═══════════════════════════════════════════════════════════╗\n"
                    response += "║                                                           ║\n"
                    response += "║              ☕ The Oracle sighs deeply... ☕            ║\n"
                    response += "║                                                           ║\n"
                    response += "╚═══════════════════════════════════════════════════════════╝\n\n"
                    response += f"\"Alas, '{guess}' is not the word I seek...\"\n\n"
                    response += "The Oracle's form begins to fade like morning steam.\n"
                    response += "\"You had but one chance, and the moment has passed.\"\n\n"
                    response += "The café grows dark. The mystery remains unsolved.\n"
                    response += "Perhaps next time, study the patterns more carefully...\n\n"
                    response += "💔 You leave the cafe to never find it again.\n"
                    response += "═══════════════════════════════════════════════════════════\n"
                    conn.sendall(response.encode())
                    break
            
            else:
                response = "\n❓ The Oracle looks confused...\n"
                response += "\"I don't understand that command, dear traveler.\"\n"
                response += "\"Try: ENCRYPT <coffee> or GUESS <word>\"\n\n"
                conn.sendall(response.encode())
    
    except Exception as e:
        print(f"[Server] Error handling client: {e}")
    finally:
        conn.close()
        print(f"[Server] Connection closed: {addr}")


def main():
    port = int(os.environ.get('PORT', 4000))
    seed = os.environ.get('SEED')
    if seed is not None:
        seed = int(seed)
    flag_file = os.environ.get('FLAG_FILE', '/home/ctfuser/flag.txt')
    if not os.path.exists(flag_file):
        flag_file = os.path.join(os.path.dirname(__file__), '..', 'flag.txt')

    flag_template = 'H7CTF{ENj0Y_YOU4_S3CR3T_C0FFE3}'
    try:
        with open(flag_file, 'r') as f:
            flag_template = f.read().strip()
        print(f"[Server] Loaded flag from {flag_file}")
    except Exception as e:
        print(f"[Server] Could not read flag file, using default: {e}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    
    print(f"[Server] Listening on port {port}")
    print(f"[Server] Multithreaded mode enabled")
    print(f"[Server] Press Ctrl+C to stop")
    
    conn_count = 0
    conn_count_lock = threading.Lock()
    
    def handle_connection(conn, addr, challenge):
        try:
            handle_client(conn, addr, challenge)
        except Exception as e:
            print(f"[Server] Thread error for {addr}: {e}")
    
    try:
        while True:
            conn, addr = server_socket.accept()
            
            with conn_count_lock:
                conn_count += 1
                current_count = conn_count

            if seed is not None:
                per_conn_seed = seed + current_count
            else:
                per_conn_seed = None

            challenge = CoffeeChallenge(seed=per_conn_seed, flag_template=flag_template)

            client_thread = threading.Thread(
                target=handle_connection,
                args=(conn, addr, challenge),
                daemon=True
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
