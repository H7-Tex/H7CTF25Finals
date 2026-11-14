#!/bin/bash
set -e

echo "[*] Placing flags..."

# Flag 1: Embedded in gRPC response (admin-only field in UserService.GetUserDetails)
# H7CTF{d1d_y0u_l3arn_ab0ut_pr0t0buf_inject10ns}

# Flag 2: In svc-runtime home (after pickle RCE)
mkdir -p /home/svc-runtime
cat > /home/svc-runtime/flag.txt << 'EOF'
H7CTF{need_oorugai_f0r_curd_r1c3}
EOF
chown svc-runtime:svc-runtime /home/svc-runtime/flag.txt
chmod 600 /home/svc-runtime/flag.txt

# Flag 3: In abu home (after pivot from svc-runtime)
mkdir -p /home/abu
cat > /home/abu/flag.txt << 'EOF'
H7CTF{p1vot_1s_4_ch4nge_1n_strategy_w1th0ut_ch4nge_1n_vision}
EOF
chown abu:platform-admins /home/abu/flag.txt
chmod 600 /home/abu/flag.txt

# Flag 4: In root home (after Unix socket privilege escalation)
cat > /root/flag.txt << 'EOF'
H7CTF{w3_really_w3nt_fr0m_oorugai_t0_un1x_s0ckets}
EOF
chmod 600 /root/flag.txt

echo "[✓] Flags placed:"
echo "    - Flag 1: Returned by UserService.GetUserDetails (admin only)"
echo "    - Flag 2: /home/svc-runtime/flag.txt"
echo "    - Flag 3: /home/abu/flag.txt"
echo "    - Flag 4: /root/flag.txt"

# Start the gRPC services
echo "[*] Starting CPR services..."
systemctl enable cpr-runtime.service
systemctl start cpr-runtime.service
systemctl enable cpr-admin.service
systemctl start cpr-admin.service

# Wait for services to start
sleep 3

# Verify services are running
if systemctl is-active --quiet cpr-runtime.service; then
    echo "[✓] CPR runtime service is running"
else
    echo "[!] Warning: CPR runtime service failed to start"
    systemctl status cpr-runtime.service
fi

if systemctl is-active --quiet cpr-admin.service; then
    echo "[✓] CPR admin service is running"
else
    echo "[!] Warning: CPR admin service failed to start"
    systemctl status cpr-admin.service
fi

# Clear history
history -c
cat /dev/null > /root/.bash_history

echo "[✓] Challenge setup complete!"
