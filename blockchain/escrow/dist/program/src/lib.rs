pub mod entrypoint;
pub mod processor;

use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::pubkey::Pubkey;

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum EscrowInstruction {
    Initialize { amount: u64 },
    Release,
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
