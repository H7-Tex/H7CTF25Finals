#!/bin/bash
set -e

echo "[*] Installing Python and gRPC dependencies..."

export DEBIAN_FRONTEND=noninteractive

# Install Python 3.11
echo "[*] Installing Python 3.11..."
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv

# Upgrade pip
echo "[*] Upgrading pip..."
python3 -m pip install --upgrade pip setuptools wheel -q

# Install gRPC and dependencies globally
echo "[*] Installing gRPC packages..."
python3 -m pip install -q \
    grpcio==1.60.0 \
    grpcio-tools==1.60.0 \
    grpcio-reflection==1.60.0 \
    protobuf==4.25.1 \
    psutil==5.9.6

# Verify installation
echo "[*] Verifying gRPC installation..."
python3 -c "import grpc; print(f'gRPC version: {grpc.__version__}')"

# Install grpcurl for testing
echo "[*] Installing grpcurl..."
GRPCURL_VERSION="1.8.9"
wget -q https://github.com/fullstorydev/grpcurl/releases/download/v${GRPCURL_VERSION}/grpcurl_${GRPCURL_VERSION}_linux_x86_64.tar.gz
tar -xzf grpcurl_${GRPCURL_VERSION}_linux_x86_64.tar.gz -C /usr/local/bin
rm grpcurl_${GRPCURL_VERSION}_linux_x86_64.tar.gz
chmod +x /usr/local/bin/grpcurl

echo "[✓] gRPC installation complete"
