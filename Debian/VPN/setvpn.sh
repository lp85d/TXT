#!/bin/bash

# Generate UUID and X25519 keys
UUID=$(/usr/local/bin/xray uuid)
KEYS=$(/usr/local/bin/xray x25519)

# Extract private and public keys using sed (works for any format with colon)
PRIVATE_KEY=$(echo "$KEYS" | sed -n 's/^Private key: //p')
PUBLIC_KEY=$(echo "$KEYS" | sed -n 's/^Public key: //p')

# Generate random ShortID
SHORT_ID=$(openssl rand -hex 8)

# Domain
DOMAIN="joyfultank.aeza.network"

# Write Xray config
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

# Restart Xray
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
