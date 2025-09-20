bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
UUID=$(xray uuid)
echo $UUID

cat << EOF > /usr/local/etc/xray/config.json
{
  "log": {
    "access": "/var/log/xray/access.log",
    "error": "/var/log/xray/error.log",
    "loglevel": "info"
  },
  "inbounds": [
    {
      "port": 443,
      "protocol": "vless",
      "settings": {
        "clients": [
          { "id": "---------------------" }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "none"
      }
    }
  ],
  "outbounds": [
    { "protocol": "freedom" }
  ]
}
EOF

systemctl daemon-reload
systemctl enable xray
systemctl restart xray
systemctl status xray

IP=$(curl -s ifconfig.me)
echo "vless://1bfa8391-e56b-4715-929e-99a31109f6ca@${IP}:443?encryption=none&type=tcp#${IP}"
