#!/bin/bash

# Ensure pip installed binaries are in PATH
export PATH="/usr/local/bin:$PATH"

# Generate dynamic flag with random UUID
DYNAMIC_UUID=$(uuidgen)
DYNAMIC_FLAG="H7CTF{r4nd0m_UU1DV3rsi0n1_15_d4mn_vu1nerabl3_${DYNAMIC_UUID}}"

# Create .env file with dynamic flag
cat > /app/.env << EOF
FLAG=${DYNAMIC_FLAG}
SECRET_KEY=${SECRET_KEY:-8a0ba8f0ebf595523890df6d3fcc4f2b}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-abbb92c4acaded401ea0a9b5c4adeec9}
RELAYMAILGRID_PASSWORD=${RELAYMAILGRID_PASSWORD:-3809ff76aed9d461795f93f343b8a1d3}
EOF

echo "Dynamic flag generated: ${DYNAMIC_FLAG}"

# Execute the main command
exec "$@"
