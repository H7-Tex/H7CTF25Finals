# Challenge 4: Token Overflow - Integer Underflow

## Challenge Overview
**Difficulty:** Medium  
**Category:** Solana Smart Contract Security  
**Vulnerability:** Integer Underflow in Arithmetic Operations

## Description
A simple token program allows users to mint, burn, and transfer tokens. Players start with 100 tokens and must acquire at least 1,000,000 tokens to capture the flag.

## Vulnerability
The `Burn` instruction performs unchecked arithmetic subtraction. When burning more tokens than exist in an account, an integer underflow occurs, wrapping around to a massive positive value.

**Vulnerable Code Location:** `program/src/processor.rs` in `process_burn()`
```rust
// No overflow checking in release mode!
token_data.balance -= amount;
```

The program compiles with `overflow-checks = false` in release profile, allowing silent underflow:
```rust
// Example: 100 - 200 = 18446744073709551516 (wraps to u64::MAX - 99)
```

## Directory Structure

```
challenge-4-token-overflow/
├── challenge/          # Production deployment
│   ├── Dockerfile
│   ├── entrypoint.sh  # Generates dynamic flag
│   ├── program/       # Symlinked to ../program
│   └── server/        # Symlinked to ../server
│
├── dist/              # Player distribution
│   ├── Dockerfile
│   ├── program/       # Cleaned source
│   ├── server/        # Challenge server
│   └── solve/         # Empty template
│
├── program/           # Vulnerable token contract
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── processor.rs   # Contains vulnerability
│       └── entrypoint.rs
│
├── server/            # CTF framework server
│   ├── Cargo.toml
│   └── src/
│       └── main.rs    # Challenge setup & validation
│
└── solve/             # Reference solution
    ├── Cargo.toml
    └── src/
        ├── lib.rs
        └── processor.rs   # Working exploit
```

## Deployment

### Using Docker (Recommended)
```bash
cd challenge/
docker build -t token-overflow .
docker run -p 5004:5004 token-overflow
```

The entrypoint script automatically generates a dynamic flag with UUID.

### Manual Build
```bash
# Build program
cd program
cargo build-sbf

# Build server
cd ../server
cargo build --release

# Run server
cd ..
./server/target/release/token-overflow-server
```

## Configuration
- **Port:** 5004
- **Starting Balance:** 5 SOL
- **Starting Tokens:** 100
- **Win Threshold:** 1,000,000 tokens
- **Flag Format:** `H7CTF{1nt3ger_und3rf10w_1n_th1s_d4y_and_ag3_<UUID>}`

## Player Distribution

Create the player package:
```bash
cd dist/
tar -czf token-overflow-player.tar.gz Dockerfile program/ server/ solve/
```

Give players `token-overflow-player.tar.gz` containing:
- Full source code (cleaned, no vulnerability hints)
- Server binary
- Empty solve template
- Dockerfile for local testing

## Testing

Build and run locally:
```bash
chmod +x build.sh
./build.sh

# In terminal 1:
./server/target/release/token-overflow-server

# In terminal 2:
python3 solve.py localhost 5004
```

## Security Note

This challenge demonstrates why:
1. Overflow checking should be enabled in production
2. Arithmetic operations must use checked variants (`.checked_sub()`)
3. Input validation is critical for financial operations
4. Rust's default behavior differs between debug and release builds
