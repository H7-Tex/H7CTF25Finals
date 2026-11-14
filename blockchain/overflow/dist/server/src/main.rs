use sol_ctf_framework::ChallengeBuilder;
use solana_program::system_program;
use solana_sdk::{
    account::Account,
    pubkey::Pubkey,
    signature::{Keypair, Signer},
};
use borsh::BorshSerialize;
use std::{
    error::Error,
    fs,
    io::Write,
    net::{TcpListener, TcpStream},
};

const STARTING_BALANCE: u64 = 5_000_000_000;
const STARTING_TOKENS: u64 = 100;
const WIN_THRESHOLD: u64 = 1_000_000;
const SERVER_PORT: u16 = 5004;

#[derive(BorshSerialize)]
struct TokenAccount {
    owner: Pubkey,
    balance: u64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let listener = TcpListener::bind(format!("0.0.0.0:{}", SERVER_PORT))?;
    println!("[*] Listening on 0.0.0.0:{}", SERVER_PORT);
    
    loop {
        let (stream, addr) = listener.accept()?;
        println!("[+] New connection from: {}", addr);
        
        tokio::spawn(async move {
            if let Err(e) = handle_connection(stream).await {
                eprintln!("[!] Handler error: {}", e);
            }
        });
    }
}

async fn handle_connection(mut socket: TcpStream) -> Result<(), Box<dyn Error>> {
    writeln!(socket, "╔════════════════════════════════════════════════╗")?;
    writeln!(socket, "║        H7CTF 2025 - Stack Overflow             ║")?;
    writeln!(socket, "╚════════════════════════════════════════════════╝\n")?;
    
    writeln!(socket, "Initializing challenge instance...\n")?;
    
    let mut builder = ChallengeBuilder::try_from(socket.try_clone().unwrap()).unwrap();

    let user = Keypair::new();
    
    let program_id = builder
        .add_program("./token_overflow.so", None)
        .expect("Failed to add token program");

    builder.builder.add_account(
        user.pubkey(),
        Account::new(STARTING_BALANCE, 0, &system_program::ID),
    );
    
    let (user_token_pda, _) = Pubkey::find_program_address(
        &[b"TOKEN", user.pubkey().as_ref()],
        &program_id,
    );
    
    let user_token_data = TokenAccount {
        owner: user.pubkey(),
        balance: STARTING_TOKENS,
    };
    
    let serialized_data = user_token_data.try_to_vec().unwrap();
    let mut user_token_account = Account::new(1_000_000_000, serialized_data.len(), &program_id);
    user_token_account.data = serialized_data;
    
    builder.builder.add_account(user_token_pda, user_token_account);
    
    writeln!(socket, "Instance ready.\n")?;
    
    writeln!(socket, "═══════════════════════════════════════════════")?;
    writeln!(socket, "Player Account:")?;
    writeln!(socket, "  Address: {}", user.pubkey())?;
    writeln!(socket, "  Balance: {} SOL", STARTING_BALANCE / 1_000_000_000)?;
    
    let privkey_hex = user.to_bytes()
        .iter()
        .map(|b| format!("{:02x}", b))
        .collect::<String>();
    writeln!(socket, "  Private Key: {}\n", privkey_hex)?;
    
    writeln!(socket, "Token System:")?;
    writeln!(socket, "  Program ID: {}", program_id)?;
    writeln!(socket, "  Your Token Account: {}", user_token_pda)?;
    writeln!(socket, "  Current Token Balance: {}\n", STARTING_TOKENS)?;
    
    writeln!(socket, "Objective:")?;
    writeln!(socket, "  Increase your token balance to >= {}", WIN_THRESHOLD)?;
    writeln!(socket, "═══════════════════════════════════════════════\n")?;
    
    let flag = fs::read_to_string("/home/ctfuser/flag.txt")
        .unwrap_or_else(|_| "H7CTF{test_flag}".to_string());
    
    writeln!(socket, "[*] Ready for your exploit.")?;
    writeln!(socket, "[*] Send your solve program to begin.\n")?;

    let ret = builder.input_program().unwrap();
    
    writeln!(socket, "\n[*] Running your exploit program...\n")?;

    builder
        .builder
        .execute_user_code_instruction(user.insecure_clone(), &ret)
        .expect("Failed to execute user instruction");
    
    writeln!(socket, "[*] Exploit execution complete.")?;
    writeln!(socket, "[*] Checking win condition...\n")?;

    let final_user_token_account = builder
        .builder
        .get_account(&user_token_pda)
        .expect("Failed to get user token account");
    
    let final_token_data = TokenAccount::try_from_slice(&final_user_token_account.data)
        .expect("Failed to deserialize token account");
    
    writeln!(socket, "═══════════════════════════════════════════════")?;
    writeln!(socket, "Final State:")?;
    writeln!(socket, "  Token Balance: {}", final_token_data.balance)?;
    writeln!(socket, "  Required: {}", WIN_THRESHOLD)?;
    writeln!(socket, "═══════════════════════════════════════════════\n")?;

    if final_token_data.balance >= WIN_THRESHOLD {
        writeln!(socket, "[+] Success! You exploited the vulnerability.")?;
        writeln!(socket, "[+] Flag: {}", flag.trim())?;
    } else {
        writeln!(socket, "[-] Failed. Token balance too low.")?;
    }
    
    Ok(())
}
