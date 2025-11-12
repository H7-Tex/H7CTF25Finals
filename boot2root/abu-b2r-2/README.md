# CPR - Boot2Root Challenge

A hard-difficulty boot2root challenge focused on modern microservices exploitation, protobuf vulnerabilities, and privilege escalation techniques.

![Difficulty](https://img.shields.io/badge/Difficulty-Hard-red)
![Type](https://img.shields.io/badge/Type-Boot2Root-red)
![Skills](https://img.shields.io/badge/Skills-gRPC%20%7C%20Protobuf%20%7C%20Deserialization%20%7C%20Privesc-blue)

## Challenge Information

**Difficulty**: Hard  
**Type**: Boot2Root  
**Estimated Time**: 3-5 hours  
**Flags**: 4

## Attack Vectors

1. **gRPC Reflection Enabled** - Enumerate all services and methods
2. **Broken Object Property Level Authorization (BOPLA)** - Exposed sensitive fields without authorization checks
3. **Insecure Pickle Deserialization** - RCE via malicious serialized objects
4. **SUID Binary Exploitation** - Command injection for lateral movement
5. **Unix Socket Privilege Escalation** - Unauthenticated access to root-level operations

## Challenge Description

H7Corp Technologies has deployed their Cloud Platform Runtime (CPR), a microservices-based infrastructure for managing enterprise applications. The platform exposes gRPC services for authentication, user management, backup operations, and system monitoring.

Your objective: Gain complete control of the system by exploiting vulnerabilities in the platform's service architecture. Capture all four flags.

## Setup

### Prerequisites

- VirtualBox installed
- Vagrant 2.4.x or higher
- 2GB RAM available for VM
- 20GB disk space
- Internet connection for initial setup

### Installation

```bash
# Navigate to challenge directory
cd boot2root/abu-b2r-2

# Start the VM (first run takes 10-15 minutes)
vagrant up
```

### Access

Once provisioned, the target is accessible at:

- **IP Address**: 192.168.56.11
- **Website**: http://192.168.56.11
- **gRPC Service**: 192.168.56.11:50051

## Required Tools

- `nmap` - Port scanning
- `grpcurl` - gRPC command-line client
- `grpcui` (optional) - gRPC web interface
- Python 3 - For exploit development
- `nc` (netcat) - For reverse shells
- **Binary analysis tools** (optional):
  - Ghidra / IDA Pro / Binary Ninja - For reverse engineering
  - `strings`, `file`, `ltrace`, `strace` - For binary analysis

Install grpcurl:
```bash
# Linux
wget https://github.com/fullstorydev/grpcurl/releases/download/v1.8.9/grpcurl_1.8.9_linux_x86_64.tar.gz
tar -xzf grpcurl_1.8.9_linux_x86_64.tar.gz
sudo mv grpcurl /usr/local/bin/

# macOS
brew install grpcurl
```

## Flags

- **Flag 1**: Gain administrative access to the platform
- **Flag 2**: Obtain service account shell access on the system
- **Flag 3**: Lateral movement to user account
- **Flag 4**: Escalate privileges to root

## Skills Required

- Network reconnaissance
- gRPC service enumeration and exploitation
- Protocol Buffer understanding
- Python exploitation techniques
- **Binary reverse engineering**
- Command injection exploitation
- Linux privilege escalation

## Troubleshooting

### VM Won't Start

```bash
# Check VirtualBox status
VBoxManage list vms

# Destroy and recreate
vagrant destroy -f
vagrant up
```

### Can't Connect to Services

```bash
# Check VM is running
vagrant status

# Verify port forwarding
vagrant port

# Test connectivity
ping 192.168.56.11
nc -zv 192.168.56.11 50051
```

### gRPC Service Not Responding

```bash
# SSH into VM
vagrant ssh

# Check service status
sudo systemctl status cpr-runtime.service

# View logs
sudo journalctl -u cpr-runtime.service -f
```

## Notes

- This is a CTF-style challenge designed for educational purposes
- Do not use these techniques against real systems without authorization
- The vulnerabilities are intentionally introduced for learning
- Take notes as you progress through the challenge

## Solution

A complete walkthrough is available in `SOLUTION.md` after you've attempted the challenge.

## Credits

Challenge created by AbuCTF for the H7CTF Finals 2025.

## License

This challenge is provided for educational purposes only.
