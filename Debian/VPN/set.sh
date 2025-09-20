#!/bin/bash

# -----------------------------
# Install required packages
# -----------------------------
apt-get update && apt-get install -y wireguard

# -----------------------------
# Generate UUID using xray
# -----------------------------
if ! command -v /usr/local/bin/xray &>/dev/null; then
    echo "Error: xray binary not found at /usr/local/bin/xray"
    exit 1
fi

UUID=$(/usr/local/bin/xray uuid)
if [ -z "$UUID" ]; then
    echo "Error: Failed to generate UUID"
    exit 1
fi

# -----------------------------
# Set fixed keys
# -----------------------------
PRIVATE_KEY="0IGs6kuXsWu21FPts6/swP7b+bhKmSk1dJcCDe3xzFE="
PUBLIC_KEY="uGoGgr77hBaEvROan6r2ve1pU8zb7nbvMZsw/m7zRWg="

if [ -z "$PRIVATE_KEY" ] || [ -z "$PUBLIC_KEY" ]; then
    echo "Error: PrivateKey or PublicKey not set"
    exit 1
fi

# -----------------------------
# Generate random ShortID
# -----------------------------
SHORT_ID=$(openssl rand -hex 8)

# -----------------------------
# IP address
# -----------------------------
IP="77.110.98.186"

# -----------------------------
# Create Xray config directory with proper permissions
# -----------------------------
mkdir -p /usr/local/etc/xray
chmod 755 /usr/local/etc/xray

# -----------------------------
# Write Xray config
# -----------------------------
cat << EOF > /usr/local/etc/xray/config.json
{
  "log": { "loglevel": "info" },
  "inbounds": [{
    "listen": "0.0.0.0",
    "port": 443,
    "protocol": "vless",
    "settings": {
      "clients": [{
        "id": "$UUID"
      }],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "tcp",
      "security": "none"
    }
  }],
  "outbounds": [{
    "protocol": "freedom"
  }]
}
EOF

if [ ! -f /usr/local/etc/xray/config.json ]; then
    echo "Error: Failed to create config.json"
    exit 1
fi

# -----------------------------
# Create systemd service for Xray
# -----------------------------
cat << EOF > /etc/systemd/system/xray.service
[Unit]
Description=Xray Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/xray -config /usr/local/etc/xray/config.json
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to register new service
systemctl daemon-reload

# Enable and start Xray service
systemctl enable xray
systemctl restart xray

# -----------------------------
# Output connection data
# -----------------------------
echo ""
echo "=== Connection data ==="
echo "UUID:       $UUID"
echo "PrivateKey: $PRIVATE_KEY"
echo "PublicKey:  $PUBLIC_KEY"
echo "ShortID:    $SHORT_ID"
echo ""
echo "VLESS link:"
echo "vless://${UUID}@${IP}:443?encryption=none&type=tcp#${IP}"
