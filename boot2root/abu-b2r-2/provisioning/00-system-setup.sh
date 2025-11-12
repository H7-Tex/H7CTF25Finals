#!/bin/bash
set -e

echo "[*] Starting system setup..."

export DEBIAN_FRONTEND=noninteractive

# Update system
echo "[*] Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

# Install basic tools
echo "[*] Installing system utilities..."
apt-get install -y -qq \
    curl \
    wget \
    git \
    vim \
    nano \
    net-tools \
    build-essential \
    sqlite3 \
    nginx \
    ufw \
    software-properties-common

# Disable AppArmor for CTF
echo "[*] Disabling AppArmor..."
systemctl disable apparmor --now 2>/dev/null || true

# Configure firewall (allow all for CTF)
echo "[*] Configuring firewall..."
ufw --force enable
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 50051/tcp

echo "[✓] System setup complete"
