#!/bin/bash
# 1. Обновление системы
apt update && apt upgrade -y

# 2. Установка необходимых утилит
apt install -y curl uuid-runtime

# 3. Установка XRay
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# 4. Генерация UUID и ключей Reality
UUID=$(uuidgen)
KEYS=$(xray x25519)
PRIVATE_KEY=$(echo "$KEYS" | grep "Private key" | awk '{print $3}')
PUBLIC_KEY=$(echo "$KEYS" | grep "Public key" | awk '{print $3}')

# 5. Создание конфигурационного файла XRay
cat << EOF > /usr/local/etc/xray/config.json
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "port": 443,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "$UUID",
            "flow": "xtls-rprx-vision"
          }
        ],
        "decryption": "none",
        "fallbacks": [
          {
            "dest": "www.google.com:443"
          }
        ]
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "www.google.com:443",
          "xver": 0,
          "serverNames": ["www.google.com"],
          "privateKey": "$PRIVATE_KEY",
          "publicKey": "$PUBLIC_KEY",
          "minClientVer": "",
          "maxClientVer": "",
          "maxTimeDiff": 0,
          "shortIds": ["", "12345678"]
        }
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom"
    }
  ]
}
EOF

# 6. Перезапуск и включение XRay
systemctl restart xray
systemctl enable xray

# 7. Получение IP сервера
SERVER_IP=$(curl -s ifconfig.me)

# 8. Создание VLESS-ссылки (профиля)
VLESS_LINK="vless://$UUID@$SERVER_IP:443?security=reality&encryption=none&pbk=$PUBLIC_KEY&headerType=none&fp=chrome&type=tcp&sni=www.google.com#xray-vless"

# 9. Сохранение профиля в файл
echo "$VLESS_LINK" > /root/vless_profile.txt

# 10. Вывод профиля на экран
echo "Ваш профиль для Hiddify-Next сохранён в /root/vless_profile.txt:"
cat /root/vless_profile.txt
