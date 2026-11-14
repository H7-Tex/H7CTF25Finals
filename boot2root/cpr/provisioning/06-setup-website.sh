#!/bin/bash
set -e

echo "[*] Setting up website..."

# Create website directory
mkdir -p /var/www/html

# Copy website files
echo "[*] Copying website files..."
cp -r /vagrant/website/* /var/www/html/

# Set permissions
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html

# Configure nginx
echo "[*] Configuring nginx..."
cat > /etc/nginx/sites-available/h7corp << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    root /var/www/html;
    index index.html;
    
    server_name _;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Misconfiguration: .git directory exposed (forgot to block it!)
    # location ~ /\.git {
    #     deny all;
    # }
    
    # Disable directory listing
    autoindex off;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

# Enable site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/h7corp /etc/nginx/sites-enabled/

# Test nginx configuration
nginx -t

# Restart nginx
systemctl restart nginx
systemctl enable nginx

echo "[✓] Website configured"
echo "    - Document root: /var/www/html"
echo "    - URL: http://192.168.56.11"
