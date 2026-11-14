#!/bin/bash
set -e

echo "[*] Setting up privilege escalation path: svc-runtime -> abu..."

# Compile backup utility from C source
echo "[*] Compiling backup utility..."
gcc /vagrant/provisioning/cpr-backup.c -o /usr/local/bin/cpr-backup

# Remove source file from VM (forces reverse engineering)
# Source is in repo for reference but not on target system

# Set SUID+SGID bits and owner to abu:platform-admins
chown abu:platform-admins /usr/local/bin/cpr-backup
chmod 6755 /usr/local/bin/cpr-backup  # 6755 = SUID + SGID + rwxr-xr-x

# Strip debug symbols to make reversing slightly harder
strip /usr/local/bin/cpr-backup

echo "[✓] Backup utility installed with SUID"
ls -la /usr/local/bin/cpr-backup

# Create backups directory
mkdir -p /opt/cpr/backups
chown abu:platform-admins /opt/cpr/backups
chmod 775 /opt/cpr/backups

echo "[✓] Pivot path configured: svc-runtime -> abu via SUID binary"
