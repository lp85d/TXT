#!/bin/bash

# Install required packages
apt-get update && apt-get install -y wireguard

# Generate UUID
if ! command -v /usr/local/bin/xray &>/dev/null; then
    echo "Error: xray binary not found"
    exit 1
fi
UUID=$(/usr/local/bin/xray uuid)
if [ -z "$UUID" ]; then
    echo "Error: Failed to generate UUID"
    exit 1
fi

# Set fixed keys
PRIVATE_KEY="0IGs6kuXsWu21FPts6/swP7b+bhKmSk1dJcCDe3xzFE="
PUBLIC_KEY="uGoGgr77hBaEvROan6r2ve1pU8zb7nbvMZsw/m7zRWg="
if [ -z "$PRIVATE_KEY" ] || [ -z "$PUBLIC_KEY" ]; then
    echo "Error: PrivateKey or PublicKey not set"
    exit 1
fi

# Generate random ShortID
SHORT_ID=$(openssl rand -hex 8)

# Domain
DOMAIN="joyfultank.aeza.network"

# Create Xray config directory
mkdir -p /usr/local/etc/xray
chmod 755 /usr/local/etc/xray

# Write Xray config with REALITY
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
      "security": "reality",
      "realitySettings": {
        "show": false,
        "dest": "$DOMAIN:443",
        "xver": 0,
        "serverNames": ["$DOMAIN"],
        "privateKey": "$PRIVATE_KEY",
        "shortIds": ["$SHORT_ID"]
      }
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

# Create systemd service
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

# Reload and start service
systemctl daemon-reload
systemctl enable xray
systemctl restart xray

# Output connection data
echo ""
echo "=== Connection data ==="
echo "UUID:       $UUID"
echo "PrivateKey: $PRIVATE_KEY"
echo "PublicKey:  $PUBLIC_KEY"
echo "ShortID:    $SHORT_ID"
echo ""
echo "VLESS link:"
echo "vless://${UUID}@${DOMAIN}:443?security=reality&encryption=none&pbk=${PUBLIC_KEY}&type=tcp&sni=${DOMAIN}&sid=${SHORT_ID}#${DOMAIN}"
