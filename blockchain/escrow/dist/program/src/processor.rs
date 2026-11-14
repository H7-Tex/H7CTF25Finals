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

use crate::{Escrow, EscrowInstruction};

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = EscrowInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;

    match instruction {
        EscrowInstruction::Initialize { amount } => {
            msg!("Instruction: Initialize");
            process_initialize(program_id, accounts, amount)
        }
        EscrowInstruction::Release => {
            msg!("Instruction: Release");
            process_release(program_id, accounts)
        }
        EscrowInstruction::Cancel => {
            msg!("Instruction: Cancel");
            process_cancel(program_id, accounts)
        }
    }
}

fn process_initialize(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let escrow_account = next_account_info(account_info_iter)?;
    let depositor_account = next_account_info(account_info_iter)?;
    let recipient_account = next_account_info(account_info_iter)?;
    let system_program = next_account_info(account_info_iter)?;

    if !depositor_account.is_signer {
        msg!("Depositor must be signer");
        return Err(ProgramError::MissingRequiredSignature);
    }

    let (escrow_pda, bump) = Pubkey::find_program_address(
        &[b"ESCROW", depositor_account.key.as_ref()],
        program_id,
    );

    if escrow_pda != *escrow_account.key {
        msg!("Invalid escrow PDA");
        return Err(ProgramError::InvalidAccountData);
    }

    let rent = Rent::get()?;
    let escrow_size = std::mem::size_of::<Escrow>();
    let rent_lamports = rent.minimum_balance(escrow_size);

    invoke_signed(
        &system_instruction::create_account(
            depositor_account.key,
            escrow_account.key,
            rent_lamports + amount,
            escrow_size as u64,
            program_id,
        ),
        &[
            depositor_account.clone(),
            escrow_account.clone(),
            system_program.clone(),
        ],
        &[&[b"ESCROW", depositor_account.key.as_ref(), &[bump]]],
    )?;

    let escrow_data = Escrow {
        depositor: *depositor_account.key,
        recipient: *recipient_account.key,
        amount,
        authority_program: *program_id,
        is_released: false,
    };

    escrow_data.serialize(&mut &mut escrow_account.data.borrow_mut()[..])?;

    msg!("Escrow initialized with {} lamports", amount);
    Ok(())
}

fn process_release(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let escrow_account = next_account_info(account_info_iter)?;
    let recipient_account = next_account_info(account_info_iter)?;
    let authority_program = next_account_info(account_info_iter)?;

    if escrow_account.owner != program_id {
        msg!("Escrow account not owned by program");
        return Err(ProgramError::InvalidAccountData);
    }

    let mut escrow_data = Escrow::try_from_slice(&escrow_account.data.borrow())?;

    if escrow_data.is_released {
        msg!("Escrow already released");
        return Err(ProgramError::InvalidAccountData);
    }

    if escrow_data.recipient != *recipient_account.key {
        msg!("Invalid recipient");
        return Err(ProgramError::InvalidAccountData);
    }

    if escrow_data.authority_program != *authority_program.key {
        msg!("Unauthorized program");
        return Err(ProgramError::InvalidAccountData);
    }

    **escrow_account.lamports.borrow_mut() -= escrow_data.amount;
    **recipient_account.lamports.borrow_mut() += escrow_data.amount;

    escrow_data.is_released = true;
    escrow_data.serialize(&mut &mut escrow_account.data.borrow_mut()[..])?;

    msg!("Released {} lamports to recipient", escrow_data.amount);
    Ok(())
}

fn process_cancel(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let escrow_account = next_account_info(account_info_iter)?;
    let depositor_account = next_account_info(account_info_iter)?;

    if !depositor_account.is_signer {
        msg!("Depositor must be signer");
        return Err(ProgramError::MissingRequiredSignature);
    }

    if escrow_account.owner != program_id {
        msg!("Escrow account not owned by program");
        return Err(ProgramError::InvalidAccountData);
    }

    let escrow_data = Escrow::try_from_slice(&escrow_account.data.borrow())?;

    if escrow_data.is_released {
        msg!("Escrow already released");
        return Err(ProgramError::InvalidAccountData);
    }

    if escrow_data.depositor != *depositor_account.key {
        msg!("Only depositor can cancel");
        return Err(ProgramError::InvalidAccountData);
    }

    **escrow_account.lamports.borrow_mut() -= escrow_data.amount;
    **depositor_account.lamports.borrow_mut() += escrow_data.amount;

    msg!("Cancelled escrow and returned {} lamports", escrow_data.amount);
    Ok(())
}
