pub mod entrypoint;
pub mod processor;

use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::pubkey::Pubkey;

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum TokenInstruction {
    Initialize,
    Mint { amount: u64 },
    Burn { amount: u64 },
    Transfer { amount: u64 },
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct TokenAccount {
    pub owner: Pubkey,
    pub balance: u64,
}
