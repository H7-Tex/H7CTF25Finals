# Challenge 5: Escrow Bypass - CPI Authorization Vulnerability

## Challenge Overview
**Difficulty:** Hard  
**Category:** Solana Smart Contract Security  
**Vulnerability:** Cross-Program Invocation (CPI) Authorization Bypass

## Description
An escrow program holds 50 SOL for controlled release. The release function is protected by an authority program requirement. Players start with 5 SOL and must steal at least 45 SOL from the escrow to capture the flag.

## Vulnerability
The `Release` instruction verifies that an authority program account matches the stored authority pubkey, but **fails to verify that the current instruction is actually being invoked via CPI from that program**. An attacker can directly call the release function and simply pass the authority program's pubkey as an account parameter.

**Vulnerable Code Location:** `program/src/processor.rs` in `process_release()`
```rust
// Checks if authority_program account matches, but NOT if we're called via CPI
if escrow_data.authority_program != *authority_program.key {
    msg!("Invalid authority program");
    return Err(ProgramError::InvalidAccountData);
}
// Missing: Verification that authority_program is the CALLER
```

## Directory Structure

```
challenge-5-escrow-bypass/
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
├── program/           # Vulnerable escrow contract
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
docker build -t escrow-bypass .
docker run -p 5005:5005 escrow-bypass
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
./server/target/release/escrow-bypass-server
```

## Configuration
- **Port:** 5005
- **Starting Balance:** 5 SOL
- **Escrow Balance:** 50 SOL
- **Win Threshold:** 45 SOL (player must steal ≥45 SOL)
- **Flag Format:** `H7CTF{cp1_4uth0r1z4t10n_byp4ss_n0_st4ck_ch3ck_<UUID>}`

## Player Distribution

Create the player package:
```bash
cd dist/
tar -czf escrow-bypass-player.tar.gz Dockerfile program/ server/ solve/
```

Give players `escrow-bypass-player.tar.gz` containing:
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
./server/target/release/escrow-bypass-server

# In terminal 2:
python3 solve.py localhost 5005
```

## Security Note

This challenge demonstrates why:
1. CPI caller validation must verify the actual call stack
2. Passing an account pubkey is not the same as being called by that program
3. Solana's `get_stack_height()` or similar mechanisms should be used
4. Authorization checks must validate program execution context
