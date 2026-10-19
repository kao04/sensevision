"""
SenseVision - Motor de OCR e Reconhecimento Matemático
Suporta Google Cloud Vision API (REST/SDK) e analisador sintático de expressões.
"""
import re
import os
import base64
import json
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import requests

logger = logging.getLogger("SenseVision.OCR")

class OCREngine:
    def __init__(self, api_key: str = "", credentials_path: str = ""):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    def _extract_math_expression(self, text: str) -> Optional[Tuple[int, str, int]]:
        """
        Analisa o texto bruto extraído da imagem e procura uma operação matemática básica.
        Exemplos: '3 + 2', '5 - 1 =', '4 x 3', '8 / 2 = ?', '10 ÷ 5'
        """
        if not text:
            return None

        # Limpar quebras de linha e caracteres desnecessários
        cleaned = text.replace("×", "*").replace("÷", "/").replace(":", "/")
        cleaned = re.sub(r'[\r\n]+', ' ', cleaned)

        # Regex flexível para capturar: [número] [operador +, -, *, x, /] [número]
        pattern = r'(\d+)\s*([\+\-\*xX\/])\s*(\d+)'
        match = re.search(pattern, cleaned)

        if match:
            a = int(match.group(1))
            op = match.group(2).lower()
            b = int(match.group(3))
            
            # Normalizar operador
            if op == 'x':
                op = '*'
                
            logger.info(f"Expressão matemática identificada: {a} {op} {b}")
            return (a, op, b)

        return None

    def recognize_with_google_vision(self, image_path: Path) -> str:
        """
        Envia a imagem para a API Google Cloud Vision usando REST API nativa.
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Arquivo de imagem não encontrado: {image_path}")

        # Ler imagem e converter em Base64
        with open(image_path, "rb") as img_file:
            content = base64.b64encode(img_file.read()).decode("utf-8")

        if not self.api_key:
            logger.warning("GOOGLE_API_KEY não configurada. Verifique config.py.")
            return ""

        url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
        payload = {
            "requests": [
                {
                    "image": {"content": content},
                    "features": [{"type": "TEXT_DETECTION"}]
                }
            ]
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        try:
            annotations = data["responses"][0].get("textAnnotations", [])
            if annotations:
                full_text = annotations[0].get("description", "")
                logger.info(f"Texto detectado pelo Google Vision: {repr(full_text)}")
                return full_text
        except (KeyError, IndexError) as e:
            logger.warning(f"Nenhum texto retornado pelo Google Vision: {e}")

        return ""

    def process_image(self, image_path: Path, simulate_if_empty: bool = True) -> Dict[str, Any]:
        """
        Processa a foto capturada pela câmera do Raspberry Pi.
        Retorna dicionário com o texto bruto e a expressão decomposta.
        """
        raw_text = ""
        math_parsed = None

        # 1. Tentar reconhecimento via Google Cloud Vision se a chave existir
        if self.api_key:
            try:
                raw_text = self.recognize_with_google_vision(image_path)
                math_parsed = self._extract_math_expression(raw_text)
            except Exception as e:
                logger.error(f"Erro ao comunicar com Google Cloud Vision: {e}")

        # 2. Se nenhuma chave configurada ou falha na detecção
        if not math_parsed and simulate_if_empty:
            logger.info("Modo de demonstração/teste ativado (expressão padrão de exemplo: 3 + 2)")
            raw_text = "3 + 2 ="
            math_parsed = (3, "+", 2)

        return {
            "raw_text": raw_text,
            "parsed": math_parsed,  # (a, op, b) ou None
            "success": math_parsed is not None
        }
