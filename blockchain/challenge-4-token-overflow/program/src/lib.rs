pub mod entrypoint;
pub mod processor;

use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::pubkey::Pubkey;

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum TokenInstruction {
    /// Initialize a token account
    /// 
    /// Accounts:
    /// 0. `[writable]` Token account PDA
    /// 1. `[signer]` Owner
    /// 2. `[]` System program
    Initialize,

    /// Mint tokens to an account
    /// 
    /// Accounts:
    /// 0. `[writable]` Token account PDA
    /// 1. `[signer]` Mint authority
    Mint { amount: u64 },

    /// Burn tokens from an account
    /// 
    /// Accounts:
    /// 0. `[writable]` Token account PDA
    /// 1. `[signer]` Owner
    Burn { amount: u64 },

    /// Transfer tokens between accounts
    /// 
    /// Accounts:
    /// 0. `[writable]` Source token account
    /// 1. `[writable]` Destination token account
    /// 2. `[signer]` Owner of source account
    Transfer { amount: u64 },
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct TokenAccount {
    pub owner: Pubkey,
    pub balance: u64,
}
