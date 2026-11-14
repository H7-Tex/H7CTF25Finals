#!/bin/bash
set -e

echo "[*] Setting up admin Unix socket..."

# Create /etc/sudoers.d/cpr-admin for future users
touch /etc/sudoers.d/cpr-admin
chmod 440 /etc/sudoers.d/cpr-admin

# Start the admin service (will create socket)
echo "[*] Starting CPR admin service..."
systemctl enable cpr-admin.service
systemctl start cpr-admin.service

# Wait for socket to be created
sleep 2

# Verify socket exists and has correct permissions
if [ -S /var/run/cpr-admin.sock ]; then
    echo "[✓] Admin socket created: /var/run/cpr-admin.sock"
    ls -la /var/run/cpr-admin.sock
else
    echo "[!] Warning: Admin socket not found"
fi

echo "[✓] Admin socket service configured"
echo "    - Socket: /var/run/cpr-admin.sock"
echo "    - Permissions: root:platform-admins (770)"
echo "    - Service: cpr-admin.service"
