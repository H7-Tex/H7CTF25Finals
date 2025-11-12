#!/bin/bash
set -e

echo "[*] Setting up gRPC services..."

# Create application directory structure
mkdir -p /opt/cpr/app/proto
mkdir -p /opt/cpr/{data,logs,backups}
mkdir -p /usr/local/lib/cpr

chown -R svc-runtime:svc-runtime /opt/cpr

# Copy proto files
echo "[*] Copying proto files..."
cp /vagrant/services/proto/*.proto /opt/cpr/app/proto/

# Generate Python code from proto files
echo "[*] Generating Python code from proto files..."
cd /opt/cpr/app/proto

python3 -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    auth.proto

python3 -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    user.proto

python3 -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    backup.proto

python3 -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    monitoring.proto

python3 -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    internal.proto

# Copy service implementations to appropriate locations
echo "[*] Copying service implementations..."
cp /vagrant/services/server.py /opt/cpr/app/
cp /vagrant/services/database.py /opt/cpr/app/
cp /vagrant/services/metrics.py /usr/local/lib/cpr/collector.py

# Set ownership and permissions
chown root:svc-runtime /opt/cpr/app/server.py /opt/cpr/app/database.py
chmod 550 /opt/cpr/app/server.py
chmod 440 /opt/cpr/app/database.py

chown root:svc-runtime /usr/local/lib/cpr/collector.py
chmod 550 /usr/local/lib/cpr/collector.py

# Proto directory accessible for service
chown -R svc-runtime:svc-runtime /opt/cpr/app/proto
chmod 755 /opt/cpr/app/proto

# Data/logs directory for service  
chown -R svc-runtime:svc-runtime /opt/cpr/data /opt/cpr/logs 2>/dev/null || true

# Copy systemd service files
echo "[*] Installing systemd services..."
cp /vagrant/services/systemd/cpr-runtime.service /etc/systemd/system/
cp /vagrant/services/systemd/cpr-admin.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

echo "[✓] gRPC services configured"
