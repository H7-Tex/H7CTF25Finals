pub mod entrypoint;
pub mod processor;

use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::pubkey::Pubkey;

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum EscrowInstruction {
    /// Initialize escrow with locked SOL
    /// 
    /// Accounts:
    /// 0. `[writable]` Escrow PDA account
    /// 1. `[signer, writable]` Depositor
    /// 2. `[]` Authorized recipient
    /// 3. `[]` System program
    Initialize { amount: u64 },

    /// Release funds to recipient (only callable by CPI from authorized program)
    /// 
    /// Accounts:
    /// 0. `[writable]` Escrow PDA account
    /// 1. `[writable]` Recipient
    /// 2. `[]` Authority program (must be the calling program)
    Release,

    /// Cancel escrow and return funds (only by depositor)
    /// 
    /// Accounts:
    /// 0. `[writable]` Escrow PDA account
    /// 1. `[signer, writable]` Depositor
    Cancel,
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct Escrow {
    pub depositor: Pubkey,
    pub recipient: Pubkey,
    pub amount: u64,
    pub authority_program: Pubkey,
    pub is_released: bool,
}
