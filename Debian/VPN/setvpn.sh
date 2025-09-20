```bash
#!/bin/bash

# -----------------------------
# Install required packages
# -----------------------------
apt-get update && apt-get install -y wireguard

# -----------------------------
# Generate UUID and set fixed keys
# -----------------------------
UUID=$(/usr/local/bin/xray uuid)
PRIVATE_KEY="0IGs6kuXsWu21FPts6/swP7b+bhKmSk1dJcCDe3xzFE="
PUBLIC_KEY="uGoGgr77hBaEvROan6r2ve1pU8zb7nbvMZsw/m7zRWg="

# Check if keys are set
if [ -z "$PRIVATE_KEY" ] || [ -z "$PUBLIC_KEY" ]; then
    echo "Error: PrivateKey or PublicKey not set"
    exit 1
fi

# Generate random ShortID
SHORT_ID=$(openssl rand -hex 8)

# Domain
DOMAIN="joyfultank.aeza.network"

# -----------------------------
# Create Xray config directory with proper permissions
# -----------------------------
mkdir -p /usr/local/etc/xray/
chmod 755 /usr/local/etc/xray/

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

# Check if config was created
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
echo "vless://${UUID}@${DOMAIN}:443?security=reality&encryption=none&pbk=${PUBLIC_KEY}&type=tcp&sni=${DOMAIN}&sid=${SHORT_ID}#${DOMAIN}"
