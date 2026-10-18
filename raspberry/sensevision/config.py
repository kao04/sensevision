"""
SenseVision - Arquivo de Configuração Central
Contém os parâmetros de hardware, rede, áudio e OCR.
"""
import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent
CAPTURES_DIR = BASE_DIR / "capturas"
CAPTURES_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------
# Configurações de Hardware (GPIO)
# -------------------------------------------------------------
# Botão de captura: Pino 36 físico (GPIO 16) com GND no Pino 34
BUTTON_PIN = 16

# Buzzer piezoelétrico: Pino 32 físico (GPIO 12) com GND no Pino 30
BUZZER_PIN = 12

# Bip de feedback do Buzzer (em segundos)
BEEP_SHORT = 0.08
BEEP_SUCCESS_REPEAT = 2
BEEP_ERROR_DURATION = 0.4

# -------------------------------------------------------------
# Configurações da Câmera OV5647 5MP
# -------------------------------------------------------------
# Largura e altura da captura
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
# Tempo de aquecimento do sensor em ms antes de disparar
CAMERA_TIMEOUT_MS = 600
# Rotação da imagem se a câmera estiver montada invertida (0, 90, 180, 270)
CAMERA_ROTATION = 0

# -------------------------------------------------------------
# Configurações de Áudio / Text-To-Speech (TTS)
# -------------------------------------------------------------
# Voz em Português do Brasil
TTS_LANG = "pt-br"
# Velocidade de fala (palavras por minuto)
TTS_SPEED = 145

# -------------------------------------------------------------
# Integração com o Site / Backend Web
# -------------------------------------------------------------
# URL do Worker na nuvem que recebe as fotos (ex.: https://sensevision.SEU-USUARIO.workers.dev/api/upload)
WEB_API_URL = os.getenv("SENSEVISION_API_URL", "")
# Senha que autoriza o upload (mesmo valor do secret UPLOAD_TOKEN no Worker)
WEB_UPLOAD_TOKEN = os.getenv("SENSEVISION_TOKEN", "")
WEB_TIMEOUT_SECONDS = 15

# -------------------------------------------------------------
# Google Cloud Vision API
# -------------------------------------------------------------
# Caminho para o arquivo de credenciais JSON do Google Cloud (se for usar)
# Se não for fornecido, o sistema usa OCR Local / Math Parser com fallback automático
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", str(BASE_DIR / "google_credentials.json"))
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
