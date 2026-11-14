use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint::ProgramResult,
    msg,
    program::invoke_signed,
    program_error::ProgramError,
    pubkey::Pubkey,
    system_instruction,
    sysvar::{rent::Rent, Sysvar},
};

use crate::{TokenAccount, TokenInstruction};

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = TokenInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;

    match instruction {
        TokenInstruction::Initialize => {
            msg!("Instruction: Initialize");
            process_initialize(program_id, accounts)
        }
        TokenInstruction::Mint { amount } => {
            msg!("Instruction: Mint");
            process_mint(program_id, accounts, amount)
        }
        TokenInstruction::Burn { amount } => {
            msg!("Instruction: Burn");
            process_burn(program_id, accounts, amount)
        }
        TokenInstruction::Transfer { amount } => {
            msg!("Instruction: Transfer");
            process_transfer(program_id, accounts, amount)
        }
    }
}

fn process_initialize(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let token_account = next_account_info(account_info_iter)?;
    let owner_account = next_account_info(account_info_iter)?;
    let system_program = next_account_info(account_info_iter)?;

    if !owner_account.is_signer {
        msg!("Owner must be signer for initialization");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Derive PDA using owner's pubkey
    let (token_pda, bump) = Pubkey::find_program_address(
        &[b"TOKEN", owner_account.key.as_ref()],
        program_id,
    );

    if token_pda != *token_account.key {
        msg!("Invalid token account PDA");
        return Err(ProgramError::InvalidAccountData);
    }

    // Create token account
    let rent = Rent::get()?;
    let account_size = std::mem::size_of::<TokenAccount>();
    let rent_lamports = rent.minimum_balance(account_size);

    invoke_signed(
        &system_instruction::create_account(
            owner_account.key,
            token_account.key,
            rent_lamports,
            account_size as u64,
            program_id,
        ),
        &[
            owner_account.clone(),
            token_account.clone(),
            system_program.clone(),
        ],
        &[&[b"TOKEN", owner_account.key.as_ref(), &[bump]]],
    )?;

    let token_data = TokenAccount {
        owner: *owner_account.key,
        balance: 0,
    };

    token_data.serialize(&mut &mut token_account.data.borrow_mut()[..])?;

    msg!("Token account initialized for owner: {}", owner_account.key);
    Ok(())
}

fn process_mint(program_id: &Pubkey, accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let token_account = next_account_info(account_info_iter)?;
    let authority_account = next_account_info(account_info_iter)?;

    if !authority_account.is_signer {
        msg!("Authority must be signer for minting");
        return Err(ProgramError::MissingRequiredSignature);
    }

    if token_account.owner != program_id {
        msg!("Token account not owned by program");
        return Err(ProgramError::InvalidAccountData);
    }

    let mut token_data = TokenAccount::try_from_slice(&token_account.data.borrow())?;

    // VULNERABILITY: Integer overflow in addition
    // If balance + amount > u64::MAX, this wraps around
    // But more importantly, the burn function has underflow vulnerability
    token_data.balance += amount;

    token_data.serialize(&mut &mut token_account.data.borrow_mut()[..])?;

    msg!("Minted {} tokens. New balance: {}", amount, token_data.balance);
    Ok(())
}

fn process_burn(program_id: &Pubkey, accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let token_account = next_account_info(account_info_iter)?;
    let owner_account = next_account_info(account_info_iter)?;

    if !owner_account.is_signer {
        msg!("Owner must be signer for burning");
        return Err(ProgramError::MissingRequiredSignature);
    }

    if token_account.owner != program_id {
        msg!("Token account not owned by program");
        return Err(ProgramError::InvalidAccountData);
    }

    let mut token_data = TokenAccount::try_from_slice(&token_account.data.borrow())?;

    if token_data.owner != *owner_account.key {
        msg!("Only token owner can burn tokens");
        return Err(ProgramError::InvalidAccountData);
    }

    // VULNERABILITY: Integer underflow!
    // If amount > balance, this wraps around to a huge positive number
    // Example: 100 - 200 = 18446744073709551516 (u64::MAX - 99)
    // The program compiles with overflow-checks = false in release mode
    // This allows the underflow to happen silently
    token_data.balance -= amount;

    token_data.serialize(&mut &mut token_account.data.borrow_mut()[..])?;

    msg!("Burned {} tokens. New balance: {}", amount, token_data.balance);
    Ok(())
}

fn process_transfer(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let source_account = next_account_info(account_info_iter)?;
    let dest_account = next_account_info(account_info_iter)?;
    let owner_account = next_account_info(account_info_iter)?;

    if !owner_account.is_signer {
        msg!("Owner must be signer for transfer");
        return Err(ProgramError::MissingRequiredSignature);
    }

    if source_account.owner != program_id || dest_account.owner != program_id {
        msg!("Token accounts not owned by program");
        return Err(ProgramError::InvalidAccountData);
    }

    let mut source_data = TokenAccount::try_from_slice(&source_account.data.borrow())?;
    let mut dest_data = TokenAccount::try_from_slice(&dest_account.data.borrow())?;

    if source_data.owner != *owner_account.key {
        msg!("Only token owner can transfer tokens");
        return Err(ProgramError::InvalidAccountData);
    }

    // Check sufficient balance (but burn function has underflow vuln anyway)
    if source_data.balance < amount {
        msg!("Insufficient balance");
        return Err(ProgramError::InsufficientFunds);
    }

    source_data.balance -= amount;
    dest_data.balance += amount;

    source_data.serialize(&mut &mut source_account.data.borrow_mut()[..])?;
    dest_data.serialize(&mut &mut dest_account.data.borrow_mut()[..])?;

    msg!("Transferred {} tokens", amount);
    Ok(())
}
