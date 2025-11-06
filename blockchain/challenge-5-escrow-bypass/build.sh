#!/bin/bash
set -e

echo "[*] Building challenge-5-escrow-bypass..."

# Build program
echo "[+] Building program..."
cd program
cargo build-sbf
cd ..

# Build server
echo "[+] Building server..."
cd server
cargo build --release
cd ..

# Build solve
echo "[+] Building solve..."
cd solve
cargo build-sbf
cd ..

echo "[+] Build complete!"
echo ""
echo "To run locally:"
echo "  ./server/target/release/escrow-bypass-server"
echo ""
echo "To test exploit:"
echo "  python3 solve.py localhost 5005"
echo ""
echo "To build Docker image:"
echo "  cd challenge && docker build -t escrow-bypass ."
echo "  docker run -p 5005:5005 escrow-bypass"
