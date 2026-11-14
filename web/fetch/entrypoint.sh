#!/bin/sh

# Generate a UUID
UUID=$(uuidgen)

# Create the flag with the UUID
FLAG="H7CTF{b4uh_y0u_br0k3_th3_c0d3_0r_th3_c0de_br0ke_y0u_${UUID}}"

# Export the flag as an environment variable
export FLAG

# Run the Next.js application
exec npm start
