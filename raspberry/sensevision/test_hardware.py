"""
SenseVision - Script de Diagnóstico e Teste Individual de Hardware
Permite validar Buzzer, Botão, Câmera e Áudio isoladamente.
"""
import time
import sys
from pathlib import Path

from config import BUTTON_PIN, BUZZER_PIN, CAPTURES_DIR
from fruit_converter import FruitMathConverter
from tts_engine import TTSEngine

def test_buzzer():
    print(f"\n--- Testando Buzzer (GPIO {BUZZER_PIN} - Pino Físico 32) ---")
    try:
        from gpiozero import Buzzer
        bz = Buzzer(BUZZER_PIN)
        print("Emitindo bip de 100ms...")
        bz.on()
        time.sleep(0.1)
        bz.off()
        time.sleep(0.1)

        print("Emitindo bip duplo de sucesso...")
        for _ in range(2):
            bz.on()
            time.sleep(0.06)
            bz.off()
            time.sleep(0.06)

        print("✅ Buzzer testado com sucesso!")
    except Exception as e:
        print(f"❌ Falha ao acionar buzzer: {e}")

def test_button():
    print(f"\n--- Testando Botão de Disparo (GPIO {BUTTON_PIN} - Pino Físico 36) ---")
    try:
        from gpiozero import Button
        btn = Button(BUTTON_PIN, pull_up=True, bounce_time=0.1)
        print("Pressione o botão físico nos óculos agora (aguardando 10 segundos)...")
        pressed = btn.wait_for_press(timeout=10)
        if pressed:
            print("✅ BOTÃO PRESSIONADO COM SUCESSO!")
        else:
            print("⚠️ Tempo esgotado. Verifique se as conexões nos pinos 36 e 34 (GND) estão firmes.")
    except Exception as e:
        print(f"❌ Falha no teste do botão: {e}")

def test_camera():
    print("\n--- Testando Câmera OV5647 (5MP) ---")
    import subprocess
    test_img = CAPTURES_DIR / "test_camera.jpg"
    cmd = ["rpicam-still", "-t", "800", "-o", str(test_img), "--width", "1280", "--height", "720", "-n"]
    print(f"Executando: {' '.join(cmd)}...")
    try:
        subprocess.run(cmd, check=True)
        if test_img.exists() and test_img.stat().st_size > 0:
            print(f"✅ Foto capturada com sucesso: {test_img} ({test_img.stat().st_size // 1024} KB)")
        else:
            print("❌ Arquivo gerado está vazio.")
    except Exception as e:
        print(f"❌ Falha na câmera: {e}")
        print("Dica: Verifique se a fita flat está bem encaixada com a parte azul virada para a porta USB/Rede.")

def test_audio():
    print("\n--- Testando Áudio / Voz (TTS) ---")
    tts = TTSEngine()
    frase = "Olá, bem-vindo ao SenseVision. O sistema de suporte à matemática está funcionando perfeitamente!"
    print(f"Falando: \"{frase}\"")
    tts.speak(frase)
    print("✅ Teste de áudio concluído!")

def test_fruit_converter():
    print("\n--- Testando Conversor Pedagógico de Frutas ---")
    conv = FruitMathConverter()
    exemplos = [(3, "+", 2), (8, "-", 3), (3, "*", 3), (10, "/", 2)]
    for a, op, b in exemplos:
        res = conv.solve_and_convert(a, op, b)
        print(f"\nOperação: {res['math_expression']}")
        print(f"Visual:    {res['visual_formula']}")
        print(f"Narração:  {res['explanation_speech']}")
    print("\n✅ Conversor de frutas testado com sucesso!")

def menu():
    while True:
        print("\n" + "="*45)
        print("   SENSEVISION - DIAGNÓSTICO DE HARDWARE")
        print("="*45)
        print("1. Testar Buzzer (Bips sonoros)")
        print("2. Testar Botão (Clique físico)")
        print("3. Testar Câmera OV5647 (Foto teste)")
        print("4. Testar Áudio / Narração TTS")
        print("5. Testar Conversor de Frutas (Discalculia)")
        print("6. Sair")
        escolha = input("\nEscolha uma opção (1-6): ").strip()

        if escolha == "1":
            test_buzzer()
        elif escolha == "2":
            test_button()
        elif escolha == "3":
            test_camera()
        elif escolha == "4":
            test_audio()
        elif escolha == "5":
            test_fruit_converter()
        elif escolha == "6":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()
