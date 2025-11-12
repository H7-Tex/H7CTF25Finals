#!/bin/bash
set -e

echo "[*] Setting up git repository leak..."

# Work in website root directory
REPO_DIR="/var/www/html"

# Remove existing git repo if present (for idempotency)
rm -rf "$REPO_DIR/.git"

# Change to repo directory
cd "$REPO_DIR"

# Set git directory explicitly
export GIT_DIR="$REPO_DIR/.git"
export GIT_WORK_TREE="$REPO_DIR"

# Initialize git repo
git init -q

# Configure git (with explicit git dir)
GIT_DIR="$REPO_DIR/.git" git config user.email "devops@h7corp.local"
GIT_DIR="$REPO_DIR/.git" git config user.name "H7Corp DevOps"

# Copy proto files to repo (from vagrant directory - source files)
mkdir -p "$REPO_DIR/proto"
cp /vagrant/services/proto/*.proto "$REPO_DIR/proto/"

# Create minimal README (no hints, stoic)
cat > "$REPO_DIR/README.md" << 'EOF'
# CPR Internal RPC Architecture

Protocol Buffer definitions for Cloud Platform Runtime internal service communication.

## Services

- Authentication Service
- User Management Service  
- Backup Service
- Monitoring Service

EOF

# Create .gitignore
cat > "$REPO_DIR/.gitignore" << 'EOF'
*.pyc
__pycache__/
*.egg-info/
*_pb2.py
*_pb2_grpc.py
EOF

# Stage and commit (with explicit git dir)
GIT_DIR="$REPO_DIR/.git" GIT_WORK_TREE="$REPO_DIR" git add proto/ README.md .gitignore
GIT_DIR="$REPO_DIR/.git" GIT_WORK_TREE="$REPO_DIR" git commit -m "Initial commit: RPC protocol definitions"

# Make .git directory world-readable (misconfiguration)
chmod -R 755 "$REPO_DIR/.git"

echo "[✓] Git repository configured with exposed .git directory"
echo "    Repository: $REPO_DIR/.git"
echo "    Files: $(GIT_DIR="$REPO_DIR/.git" git ls-files | wc -l) tracked files"
