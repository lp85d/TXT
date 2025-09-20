#!/bin/bash

# -----------------------------
# Generate UUID
# -----------------------------
UUID=$(/usr/local/bin/xray uuid)

# Generate X25519 keys manually using wg (WireGuard)
if ! command -v wg &> /dev/null; then
    apt-get update && apt-get install -y wireguard
fi
PRIVATE_KEY=$(wg genkey)
PUBLIC_KEY=$(echo "$PRIVATE_KEY" | wg pubkey)

# Check if keys were generated
if [ -z "$PRIVATE_KEY" ] || [ -z "$PUBLIC_KEY" ]; then
    echo "Error: Failed to generate PrivateKey or PublicKey"
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
