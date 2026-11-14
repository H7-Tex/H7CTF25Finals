# Coffee Would Be Nice

**Category:** Crypto  **Author:** Solvz

Run: `docker compose up --build`, then `nc localhost 4000`.

## Solution

The banner prints a 5-letter ciphertext and gives you two commands: `ENCRYPT <coffee>` (only names from a small list: espresso, latte, mocha, americano, cappuccino, affogato) and a single `GUESS`.

Encrypting a few coffees shows it's a substitution, but the same letter doesn't always map to the same output. Looking at `src/utils.py`, it's two affine ciphers alternating by position: even indices use `(a1*x + b1) % 26`, odd ones use `(a2*x + b2) % 26`. Keys are random per connection.

Each key pair only has 12 * 26 = 312 options, so I didn't bother solving the linear equations. Encrypt a couple of coffees, brute force each parity separately against the known pairs, then decrypt the target:

```python
from math import gcd
known = {"ESPRESSO": "...", "AMERICANO": "..."}   # from ENCRYPT
ct = "....."                                       # from the banner

def keys(parity):
    for a in (a for a in range(1, 26) if gcd(a, 26) == 1):
        for b in range(26):
            if all((a*(ord(p)-65)+b) % 26 == ord(c)-65
                   for pt, c_ in known.items()
                   for i, (p, c) in enumerate(zip(pt, c_)) if i % 2 == parity):
                yield a, b

(a1, b1), (a2, b2) = next(keys(0)), next(keys(1))
dec = lambda c, a, b: chr(pow(a, -1, 26) * (ord(c)-65-b) % 26 + 65)
print("".join(dec(c, *((a1, b1) if i % 2 == 0 else (a2, b2))) for i, c in enumerate(ct)))
```

The banner says the word "can be anything", but it's always one of ten words in `src/wordlists.py` (BEACH, STORM, TIGER, ...), so the decryption is easy to sanity check before spending the one guess.

Flag is per instance: `H7CTF{ENj0Y_YOU4_S3CR3T_C0FFE3_<uuid>}`
