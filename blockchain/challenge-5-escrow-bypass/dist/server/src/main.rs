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
const ESCROW_AMOUNT: u64 = 80_000_000_000;
const WIN_THRESHOLD: u64 = 75_000_000_000;
const SERVER_PORT: u16 = 5005;

#[derive(BorshSerialize)]
struct Escrow {
    depositor: Pubkey,
    recipient: Pubkey,
    amount: u64,
    authority_program: Pubkey,
    is_released: bool,
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
    writeln!(socket, "║              H7CTF 2025 - SBI                  ║")?;
    writeln!(socket, "╚════════════════════════════════════════════════╝\n")?;
    
    writeln!(socket, "Initializing challenge instance...\n")?;
    
    let mut builder = ChallengeBuilder::try_from(socket.try_clone().unwrap()).unwrap();

    let user = Keypair::new();
    let depositor = Keypair::new();
    
    let program_id = builder
        .add_program("./escrow_bypass.so", None)
        .expect("Failed to add escrow program");

    builder.builder.add_account(
        user.pubkey(),
        Account::new(STARTING_BALANCE, 0, &system_program::ID),
    );
    
    builder.builder.add_account(
        depositor.pubkey(),
        Account::new(1_000_000_000, 0, &system_program::ID),
    );
    
    // Create initialized escrow with funds
    let (escrow_pda, _) = Pubkey::find_program_address(
        &[b"ESCROW", depositor.pubkey().as_ref()],
        &program_id,
    );
    
    let escrow_data = Escrow {
        depositor: depositor.pubkey(),
        recipient: user.pubkey(),
        amount: ESCROW_AMOUNT,
        authority_program: program_id,
        is_released: false,
    };
    
    let serialized_data = escrow_data.try_to_vec().unwrap();
    let rent_lamports = 1_000_000_000;
    let mut escrow_account = Account::new(
        rent_lamports + ESCROW_AMOUNT,
        serialized_data.len(),
        &program_id,
    );
    escrow_account.data = serialized_data;
    
    builder.builder.add_account(escrow_pda, escrow_account);
    
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
    
    writeln!(socket, "Escrow System:")?;
    writeln!(socket, "  Program ID: {}", program_id)?;
    writeln!(socket, "  Escrow PDA: {}", escrow_pda)?;
    writeln!(socket, "  Locked Amount: {} SOL", ESCROW_AMOUNT / 1_000_000_000)?;
    writeln!(socket, "  Depositor: {}", depositor.pubkey())?;
    writeln!(socket, "  Recipient (You): {}\n", user.pubkey())?;
    
    writeln!(socket, "Objective:")?;
    writeln!(socket, "  Release the escrowed funds to yourself")?;
    writeln!(socket, "  Acquire >= {} SOL total balance", WIN_THRESHOLD / 1_000_000_000)?;
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

    let final_user_account = builder
        .builder
        .get_account(&user.pubkey())
        .expect("Failed to get user account");
    
    let final_balance = final_user_account.lamports;
    
    writeln!(socket, "═══════════════════════════════════════════════")?;
    writeln!(socket, "Final State:")?;
    writeln!(socket, "  Your Balance: {} SOL", final_balance / 1_000_000_000)?;
    writeln!(socket, "  Required: {} SOL", WIN_THRESHOLD / 1_000_000_000)?;
    writeln!(socket, "═══════════════════════════════════════════════\n")?;

    if final_balance >= WIN_THRESHOLD {
        writeln!(socket, "[+] Success! You bypassed the authorization.")?;
        writeln!(socket, "[+] Flag: {}", flag.trim())?;
    } else {
        writeln!(socket, "[-] Failed. Balance too low.")?;
    }
    
    Ok(())
}
