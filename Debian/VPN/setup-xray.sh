#!/bin/bash

# Версия Xray: v25.8.3

set -e

JSON_PATH="/usr/local/etc/xray"
USERS_FILE="/root/users.json"
CONFIG_FILE="$JSON_PATH/config.json"
INSTALL_USER="www-data"
INSTALL_VERSION="v25.8.3"
DAT_PATH="/usr/local/share/xray"
TMP_DIRECTORY=$(mktemp -d)
ZIP_FILE="${TMP_DIRECTORY}/Xray-linux-64.zip"

identify_the_operating_system_and_architecture() {
  if [[ "$(uname -m)" == 'x86_64' ]]; then
    MACHINE='64'
  else
    echo "error: Unsupported architecture"
    exit 1
  fi
  if [[ ! -f '/etc/os-release' ]]; then
    echo "error: Unsupported OS"
    exit 1
  fi
}

download_xray() {
  local DOWNLOAD_LINK="https://github.com/XTLS/Xray-core/releases/download/${INSTALL_VERSION}/Xray-linux-${MACHINE}.zip"
  echo "Downloading Xray archive: $DOWNLOAD_LINK"
  if curl -f -L -o "$ZIP_FILE" "$DOWNLOAD_LINK"; then
    echo "ok."
  else
    echo 'error: Download failed!'
    exit 1
  fi
  echo "Verification skipped (no sha256sum)."
}

decompression() {
  if ! unzip -q "$1" -d "$TMP_DIRECTORY"; then
    echo 'error: Decompression failed.'
    rm -r "$TMP_DIRECTORY"
    exit 1
  fi
}

install_file() {
  NAME="$1"
  if [[ "$NAME" == 'xray' ]]; then
    install -m 755 "${TMP_DIRECTORY}/$NAME" "/usr/local/bin/$NAME"
  elif [[ "$NAME" == 'geoip.dat' ]] || [[ "$NAME" == 'geosite.dat' ]]; then
    install -m 644 "${TMP_DIRECTORY}/$NAME" "${DAT_PATH}/$NAME"
  fi
}

install_xray() {
  identify_the_operating_system_and_architecture
  if [[ ! -f '/usr/local/bin/xray' ]]; then
    apt update && apt install curl unzip -y
    download_xray
    decompression "$ZIP_FILE"
    install_file xray
    mkdir -p "$DAT_PATH"
    install_file geoip.dat
    install_file geosite.dat
    rm -r "$TMP_DIRECTORY"
  fi

  cat > /etc/systemd/system/xray.service << EOF
[Unit]
Description=Xray Service
Documentation=https://github.com/xtls
After=network.target nss-lookup.target

[Service]
User=$INSTALL_USER
Group=$INSTALL_USER
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/local/bin/xray run -config $CONFIG_FILE
Restart=on-failure
RestartPreventExitStatus=23
LimitNPROC=10000
LimitNOFILE=1000000

[Install]
WantedBy=multi-user.target
EOF

  mkdir -p /etc/systemd/system/xray.service.d
  cat > /etc/systemd/system/xray.service.d/10-donot_touch_single_conf.conf << EOF
[Service]
ExecStart=
ExecStart=/usr/local/bin/xray run -config $CONFIG_FILE
EOF

  systemctl daemon-reload
  systemctl enable xray
  systemctl start xray

  add_user ""
  chown -R "$INSTALL_USER:$INSTALL_USER" /usr/local/bin/xray "$DAT_PATH"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "Запускать от root"
        exit 1
    fi
}

install_jq_if_needed() {
    if ! command -v jq &>/dev/null; then
        apt update && apt install jq -y
    fi
}

create_user_if_needed() {
    if ! id "$INSTALL_USER" &>/dev/null; then
        useradd -r -s /bin/false "$INSTALL_USER"
    fi
}

init_users() {
    mkdir -p "$JSON_PATH"
    if [ ! -f "$USERS_FILE" ]; then
        echo "{}" > "$USERS_FILE"
    fi
    chown -R "$INSTALL_USER:$INSTALL_USER" "$JSON_PATH"
}

load_users() {
    jq -r 'to_entries[] | "\(.key) \(.value)"' "$USERS_FILE" 2>/dev/null || echo ""
}

get_vpn_url() {
    local uuid="$1"
    local server_ip
    server_ip=$(curl -s ifconfig.me)
    local public_key=$(cat "$CONFIG_FILE" | jq -r '.inbounds[0].streamSettings.realitySettings.publicKey')
    echo "vless://$uuid@$server_ip:443?type=tcp&security=reality&pbk=$public_key&sni=www.google.com&fp=chrome&sid=&encryption=none#$(date +%Y%m%d)-User"
}

add_user() {
    local uuid="$1"
    if [ -z "$uuid" ]; then
        uuid=$(xray uuid)
        echo "Сгенерирован UUID: $uuid"
    fi
    local date=$(date -Iseconds)
    jq --arg uuid "$uuid" --arg date "$date" '.[$uuid] = $date' "$USERS_FILE" > "${USERS_FILE}.tmp" && mv "${USERS_FILE}.tmp" "$USERS_FILE"
    update_config
    local url=$(get_vpn_url "$uuid")
    echo "Добавлен: $uuid ($date)"
    echo "VPN URL: $url"
}

remove_user() {
    local uuid="$1"
    jq "del(.$uuid)" "$USERS_FILE" > "${USERS_FILE}.tmp" && mv "${USERS_FILE}.tmp" "$USERS_FILE"
    update_config
    echo "Удалён: $uuid"
}

list_users() {
    echo "Пользователи:"
    local public_key=$(cat "$CONFIG_FILE" | jq -r '.inbounds[0].streamSettings.realitySettings.publicKey')
    local server_ip=$(curl -s ifconfig.me)
    load_users | while read -r uuid date; do
        [ -n "$uuid" ] && {
            echo "- $uuid: $date"
            echo "  VPN URL: vless://$uuid@$server_ip:443?type=tcp&security=reality&pbk=$public_key&sni=www.google.com&fp=chrome&sid=&encryption=none#$(date +%Y%m%d)-User"
        }
    done
}

status() {
    echo "Статус Xray:"
    systemctl status xray --no-pager -l
    echo
    list_users
}

update_config() {
    local clients=$(jq -r 'to_entries[] | "{\"id\": \"\(.key)\"}"' "$USERS_FILE" | jq -s .)
    if [ "$clients" = "[]" ]; then
        echo "Нет пользователей"
        exit 1
    fi
    xray x25519 > /tmp/keys.txt
    local private_key=$(grep "Private key:" /tmp/keys.txt | awk '{print $3}')
    local public_key=$(grep "Public key:" /tmp/keys.txt | awk '{print $3}')
    rm /tmp/keys.txt

    cat > "$CONFIG_FILE" << EOF
{
    "log": {"loglevel": "warning"},
    "inbounds": [{
        "port": 443,
        "protocol": "vless",
        "settings": {
            "clients": $clients,
            "decryption": "none",
            "fallbacks": [{"dest": "www.google.com:443"}]
        },
        "streamSettings": {
            "network": "tcp",
            "security": "reality",
            "realitySettings": {
                "show": false,
                "dest": "www.google.com:443",
                "xver": 0,
                "serverNames": ["www.google.com"],
                "privateKey": "$private_key",
                "publicKey": "$public_key",
                "minClientVer": "",
                "maxClientVer": "",
                "maxTimeDiff": 0,
                "shortIds": ["", "12345678"]
            }
        }
    }],
    "outbounds": [{"protocol": "freedom"}]
}
EOF
    chown "$INSTALL_USER:$INSTALL_USER" "$CONFIG_FILE"
    systemctl restart xray
}

interactive_menu() {
    while true; do
        echo "Xray установлен. Выберите:"
        echo "1) Добавить пользователя"
        echo "2) Удалить пользователя"
        echo "3) Список пользователей"
        echo "4) Статус"
        echo "5) Выход"
        read -p "Ввод: " choice
        case $choice in
            1)
                read -p "UUID (Enter для генерации): " uuid
                add_user "$uuid"
                ;;
            2)
                list_users
                read -p "UUID для удаления: " uuid
                remove_user "$uuid"
                ;;
            3)
                list_users
                ;;
            4)
                status
                ;;
            5)
                exit 0
                ;;
            *)
                echo "Неверно"
                ;;
        esac
    done
}

main() {
    check_root
    install_jq_if_needed
    create_user_if_needed
    init_users

    if systemctl is-enabled xray &>/dev/null; then
        interactive_menu
    else
        echo "Xray не установлен. Устанавливаем..."
        install_xray
        echo "Установка завершена. Запустите скрипт снова для меню."
    fi
}

main "$@"
