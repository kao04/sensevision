#!/bin/bash
# Instala o SenseVision como serviço: inicia sozinho ao ligar o Raspberry.
# Uso (no Raspberry):  cd ~/sensevision && bash install_service.sh
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
USER_NAME="$(whoami)"
ENV_FILE="/etc/sensevision.env"
UNIT="/etc/systemd/system/sensevision.service"

read -r -p "URL do upload [https://sensevision.sensevision.workers.dev/api/upload]: " URL
URL="${URL:-https://sensevision.sensevision.workers.dev/api/upload}"
read -r -s -p "Senha de upload (UPLOAD_TOKEN, não aparece ao digitar): " TOKEN
echo
[ -n "$TOKEN" ] || { echo "Senha vazia. Abortado."; exit 1; }

# Arquivo de ambiente legível só pelo root (a senha não fica no projeto)
printf 'SENSEVISION_API_URL=%s\nSENSEVISION_TOKEN=%s\n' "$URL" "$TOKEN" | sudo tee "$ENV_FILE" >/dev/null
sudo chmod 600 "$ENV_FILE"

sudo tee "$UNIT" >/dev/null <<EOF
[Unit]
Description=SenseVision (botao -> foto -> site)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER_NAME
WorkingDirectory=$DIR
EnvironmentFile=$ENV_FILE
ExecStart=/usr/bin/python3 $DIR/sensevision_core.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now sensevision.service
echo
echo "Pronto. Status:   systemctl status sensevision --no-pager"
echo "Logs ao vivo:     journalctl -u sensevision -f"
echo "Parar/iniciar:    sudo systemctl stop|start sensevision"
