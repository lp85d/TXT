#!/bin/bash

# -----------------------------
# Generate UUID and X25519 keys
# -----------------------------
UUID=$(/usr/local/bin/xray uuid)
KEYS=$(/usr/local/bin/xray x25519)

# Extract private and public keys safely using grep and cut
PRIVATE_KEY=$(echo "$KEYS" | grep "Private key:" | cut -d ' ' -f 3)
PUBLIC_KEY=$(echo "$KEYS" | grep "Public key:" | cut -d ' ' -f 3)

# Check if keys were extracted
if [ -z "$PRIVATE_KEY" ] || [ -z "$PUBLIC_KEY" ]; then
    echo "Error: Failed to extract PrivateKey or PublicKey"
    exit 1
fi

# Generate random ShortID
SHORT_ID=$(openssl rand -hex 8)

# Domain
DOMAIN="joyfultank.aeza.network"

# -----------------------------
# Create Xray config directory if it doesn't exist
# -----------------------------
mkdir -p /usr/local/etc/xray/

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

# -----------------------------
# Restart Xray service
# -----------------------------
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
