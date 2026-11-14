#!/bin/bash
set -e

echo "[*] Creating users and groups..."

# Create svc-runtime user (service account)
if ! id "svc-runtime" &>/dev/null; then
    useradd -r -m -s /bin/bash -u 2001 svc-runtime
    echo "[✓] Created svc-runtime user"
fi

# Create platform-admins group
if ! getent group platform-admins > /dev/null; then
    groupadd -g 1100 platform-admins
    echo "[✓] Created platform-admins group"
fi

# Create abu user (regular user, gets compromised via RCE)
# Primary group is platform-admins (realistic for team-based orgs)
if ! id "abu" &>/dev/null; then
    useradd -m -s /bin/bash -u 2002 -g platform-admins abu
    echo "abu:h7corpCPR2025!" | chpasswd
    echo "[✓] Created abu user (primary group: platform-admins)"
fi

# Create home directories
mkdir -p /home/abu/{Documents,Downloads,.ssh}
chown -R abu:platform-admins /home/abu

mkdir -p /home/svc-runtime
chown -R svc-runtime:svc-runtime /home/svc-runtime

# Create some realistic files for abu
cat > /home/abu/Documents/readme.txt << 'EOF'
CPR Platform Notes
==================

Platform access:
- gRPC endpoint: localhost:50051
- Admin tools: Available via internal socket

For backup operations, contact platform team.

EOF

chown -R abu:platform-admins /home/abu/Documents

# Create bash history for realism
cat > /home/abu/.bash_history << 'EOF'
ls -la
cd Documents
cat readme.txt
python3 --version
grpcurl --help
exit
EOF

chown abu:platform-admins /home/abu/.bash_history

echo "[✓] Users and groups configured"
echo "    - svc-runtime: Service account (UID 1002)"
echo "    - abu: Regular user (UID 1001, password: h7corpCPR2025!)"
echo "    - platform-admins: Admin group (GID 1100)"
