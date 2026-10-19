"""
SenseVision - Aplicação Principal para Raspberry Pi 3
Orquestra o botão de disparo, buzzer de feedback, câmera OV5647 5MP,
OCR matemático, conversor pedagógico em frutas, áudio TTS e envio para o site.
"""
import time
import os
import sys
import subprocess
import logging
import signal
import threading
from pathlib import Path
from typing import Optional
import requests

from config import (
    BUTTON_PIN, BUZZER_PIN, BEEP_SHORT, BEEP_SUCCESS_REPEAT, BEEP_ERROR_DURATION,
    CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_TIMEOUT_MS, CAMERA_ROTATION,
    CAPTURES_DIR, WEB_API_URL, WEB_UPLOAD_TOKEN, WEB_TIMEOUT_SECONDS
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("SenseVision.Core")

class SenseVisionDevice:
    def __init__(self):
        logger.info("Inicializando SenseVision Óculos Inteligentes...")

        self._busy = threading.Lock()  # ignora cliques durante um ciclo em andamento
        self._init_gpio()

    def _init_gpio(self):
        """Inicializa botão e buzzer com tratamento seguro para testes."""
        self.button = None
        self.buzzer = None

        try:
            from gpiozero import Button, Buzzer
            self.buzzer = Buzzer(BUZZER_PIN)
            self.button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.1)
            logger.info(f"Hardware GPIO carregado com sucesso: Botão (GPIO {BUTTON_PIN}), Buzzer (GPIO {BUZZER_PIN}).")
        except Exception as e:
            logger.warning(f"GPIO não disponível ou simulado: {e}")

    # ---------------------------------------------------------
    # Feedbacks Sonoros (Buzzer)
    # ---------------------------------------------------------
    def beep(self, duration: float = BEEP_SHORT, repeat: int = 1, interval: float = 0.08):
        if not self.buzzer:
            return
        try:
            for i in range(repeat):
                self.buzzer.on()
                time.sleep(duration)
                self.buzzer.off()
                if i < repeat - 1:
                    time.sleep(interval)
        except Exception as e:
            logger.error(f"Erro no acionamento do buzzer: {e}")

    def sound_ready(self):
        """Dois bips suaves indicando que o sistema está pronto."""
        self.beep(0.04, 2, 0.05)

    def sound_capture(self):
        """Um bip de clique para indicar disparo da foto."""
        self.beep(0.08, 1)

    def sound_success(self):
        """Dois bips alegres indicando cálculo concluído com sucesso."""
        self.beep(0.06, 2, 0.07)

    def sound_error(self):
        """Um bip mais longo para avisar que precisa tentar novamente."""
        self.beep(BEEP_ERROR_DURATION, 1)

    # ---------------------------------------------------------
    # Captura de Imagem (Câmera OV5647)
    # ---------------------------------------------------------
    def capture_photo(self) -> Path:
        """
        Dispara a câmera do Raspberry Pi para fotografar a expressão matemática.
        """
        timestamp = int(time.time())
        output_file = CAPTURES_DIR / f"capture_{timestamp}.jpg"

        logger.info(f"Capturando foto com câmera OV5647: {output_file.name}")

        # Comando oficial do Raspberry Pi OS para câmeras CSI
        cmd = [
            "rpicam-still",
            "-t", str(CAMERA_TIMEOUT_MS),
            "-o", str(output_file),
            "--width", str(CAMERA_WIDTH),
            "--height", str(CAMERA_HEIGHT),
            "-n"  # Sem tela cheia de preview
        ]

        if CAMERA_ROTATION > 0:
            cmd.extend(["--rotation", str(CAMERA_ROTATION)])

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Foto capturada com sucesso!")
            return output_file
        except Exception as e:
            logger.warning(f"rpicam-still falhou ou câmera não conectada: {e}")
            
            # Criar imagem sintética para teste caso a câmera física ainda não esteja plugada
            from PIL import Image, ImageDraw
            img = Image.new("RGB", (640, 480), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            draw.text((150, 200), "3 + 2 =", fill=(0, 0, 0))
            img.save(output_file)
            logger.info("Imagem de demonstração gerada para teste.")
            return output_file

    # ---------------------------------------------------------
    # Envio para o Site / API Web
    # ---------------------------------------------------------
    def dispatch_to_website(self, image_path: Path) -> bool:
        """Envia a foto (JPEG cru) ao Worker na nuvem. Retorna True se o site recebeu."""
        if not WEB_API_URL:
            logger.warning("SENSEVISION_API_URL não configurada: foto não enviada ao site.")
            return False
        logger.info(f"Enviando foto para o site ({WEB_API_URL})...")

        try:
            with open(image_path, "rb") as f:
                img_bytes = f.read()

            resp = requests.post(
                WEB_API_URL,
                data=img_bytes,
                headers={
                    "Content-Type": "image/jpeg",
                    "X-Filename": image_path.name,
                    "X-Token": WEB_UPLOAD_TOKEN,
                },
                timeout=WEB_TIMEOUT_SECONDS,
            )
            if resp.status_code in (200, 201):
                logger.info("Site recebeu a foto com sucesso!")
                return True
            logger.warning(f"Site respondeu com status {resp.status_code}: {resp.text[:120]}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Não foi possível conectar ao site agora ({e}).")
        return False

    # ---------------------------------------------------------
    # Ciclo Completo de Processamento
    # ---------------------------------------------------------
    def trigger_cycle(self):
        """Botão: tira a foto, bipa, envia ao site e bipa o resultado."""
        if not self._busy.acquire(blocking=False):
            logger.info("Ciclo em andamento, clique ignorado.")
            return
        try:
            logger.info("🔵 DISPARO ACIONADO!")

            # 1. Foto
            image_path = self.capture_photo()

            # 2. Bip: foto tirada
            self.sound_capture()

            # 3. Envio ao site (o OCR e as frutas são feitos lá)
            if self.dispatch_to_website(image_path):
                self.sound_success()   # 2 bips: enviada
                logger.info("🟢 Foto enviada. Aguardando novo disparo...")
            else:
                self.sound_error()     # 1 bip longo: falhou
                logger.warning("🔴 Falha no envio. Tente de novo.")
        finally:
            self._busy.release()

    def run(self):
        """Inicia o laço principal de escuta."""
        self.sound_ready()
        logger.info("👓 SenseVision pronto. Aperte o botão (GPIO %s).", BUTTON_PIN)
        if not WEB_API_URL:
            logger.warning("SENSEVISION_API_URL vazia: as fotos não serão enviadas.")

        if self.button:
            self.button.when_pressed = self.trigger_cycle

        try:
            if sys.stdin.isatty():
                print("  * ENTER aqui simula o botão | Ctrl+C sai")
                while True:
                    input()
                    self.trigger_cycle()
            else:
                signal.pause()  # sem terminal (serviço): fica esperando o botão
        except (KeyboardInterrupt, EOFError):
            print("Encerrando SenseVision com segurança...")
        finally:
            if self.buzzer:
                self.buzzer.off()

if __name__ == "__main__":
    device = SenseVisionDevice()
    device.run()
