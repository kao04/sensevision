"""
SenseVision - Motor de Narração em Áudio (Text-to-Speech)
Sintetiza em voz alta a explicação pedagógica em Português Brasileiro.
"""
import subprocess
import shutil
import logging
from typing import Optional

logger = logging.getLogger("SenseVision.TTS")

class TTSEngine:
    def __init__(self, lang: str = "pt-br", speed: int = 140):
        self.lang = lang
        self.speed = speed
        self._detect_backend()

    def _detect_backend(self):
        """Identifica qual sintetizador de voz está disponível no sistema."""
        if shutil.which("espeak-ng"):
            self.backend = "espeak-ng"
        elif shutil.which("espeak"):
            self.backend = "espeak"
        elif shutil.which("pico2wave"):
            self.backend = "pico2wave"
        else:
            self.backend = "simulated"
            logger.warning("Nenhum sintetizador TTS nativo (espeak-ng/pico2wave) encontrado. Modo silencioso ativado.")

    def speak(self, text: str) -> bool:
        """
        Reproduz o texto em voz alta através da saída de áudio do Raspberry Pi.
        Retorna True em caso de sucesso.
        """
        if not text or not text.strip():
            return False

        logger.info(f"Narrando: \"{text}\"")

        try:
            if self.backend == "espeak-ng":
                # espeak-ng com voz em português brasileiro e ajuste de velocidade
                cmd = ["espeak-ng", "-v", self.lang, "-s", str(self.speed), text]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True

            elif self.backend == "espeak":
                cmd = ["espeak", "-v", self.lang, "-s", str(self.speed), text]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True

            elif self.backend == "pico2wave":
                temp_wav = "/tmp/sensevision_tts.wav"
                subprocess.run(["pico2wave", "-l", "pt-BR", "-w", temp_wav, text], check=True)
                subprocess.run(["aplay", temp_wav], check=True)
                return True

            else:
                # Simulação (apenas imprime no terminal)
                print(f"\n[ÁUDIO SENSEVISION]: {text}\n")
                return True

        except Exception as e:
            logger.error(f"Erro ao sintetizar voz: {e}")
            print(f"\n[ÁUDIO FALHOU]: {text}\n")
            return False
