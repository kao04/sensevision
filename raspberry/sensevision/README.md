# SenseVision 👓🍎
**Óculos Inteligentes para o Suporte à Aprendizagem Matemática de Estudantes com Discalculia**
*Colégio UNASP - III SIPIC*

---

## 📌 Visão Geral
O **SenseVision** é uma tecnologia assistiva vestível baseada em Raspberry Pi 3 que captura equações matemáticas através de visão computacional (OCR) e converte números abstratos em **representações visuais e sensoriais concretas com frutas** (🍎, 🍌, 🍊, 🍓, 🍇), acompanhadas de feedback sonoro (buzzer) e narração em áudio pedagógica (Text-To-Speech).

---

## 🔌 Pinagem e Conexões de Hardware

| Componente | Pino GPIO | Pino Físico no Raspberry Pi 3B+ | Conexão |
| :--- | :--- | :--- | :--- |
| **Câmera 5MP OV5647** | Conector CSI | Porta Flat CSI (entre HDMI e P2) | Fita flat azul virada para as portas USB/Rede |
| **Buzzer** | **GPIO 12** | **Pino 32** | Positivo (+) no **Pino 32**, Negativo (-) no **Pino 30 (GND)** |
| **Botão de Disparo** | **GPIO 16** | **Pino 36** | Um terminal no **Pino 36** e outro no **Pino 34 (GND)** |
| **Saída de Áudio** | Jack P2 / Bluetooth | Saída P2 da placa | Fone de ouvido ou mini speaker |

*Nota: O botão utiliza o resistor interno de pull-up da placa, dispensando resistores externos no circuito.*

---

## 📂 Estrutura do Código

```
sensevision/
├── config.py             # Configurações de pinos GPIO, câmera, áudio e URLs
├── fruit_converter.py    # Motor pedagógico de conversão matemática para frutas
├── ocr_engine.py         # OCR via Google Cloud Vision com analisador de fórmulas
├── tts_engine.py         # Síntese de voz em português brasileiro
├── sensevision_core.py   # Aplicação principal (loop do botão, buzzer, câmera e envio)
├── test_hardware.py      # Diagnóstico interativo para testar cada peça isoladamente
└── requirements.txt      # Dependências Python
```

---

## 💻 Conectando o Computador à Placa via SSH

Para controlar a placa diretamente do terminal do seu computador (Windows/Linux/Mac):

### 1. Requisitos Prévios
* O computador e o Raspberry Pi devem estar conectados na **mesma rede Wi-Fi** (ou ligados pelo mesmo roteador/cabo de rede).
* O serviço SSH deve estar ativo no Raspberry Pi (`sudo raspi-config` -> *Interface Options* -> *SSH* -> *Enable*).

> **Atenção:** Nunca use endereços `127.0.0.1` ou `127.0.1.1`. Esses endereços são de *loopback* (apontam para o seu próprio computador, não para a placa).

### 2. Opção A: Conectar pelo Nome do Host (Mais Fácil)
Geralmente o Raspberry Pi responde por mDNS na rede local. No terminal do seu computador, execute:
```powershell
ssh usuario@TCC.local
```
*(Ou `ssh usuario@raspberrypi.local` caso use a imagem padrão sem renomear a placa).*

### 3. Opção B: Conectar pelo Endereço IP Local
Se a conexão por `.local` não funcionar, descubra o IP da placa na rede local (costuma começar com `192.168...` ou `10.0...`):

* **Se você tem tela/teclado no Pi:** execute `hostname -I` no terminal da placa para ver o IP.
* **Pelo Windows (PowerShell):** você pode testar:
  ```powershell
  ping raspberrypi.local
  ```
  O terminal mostrará o IP correspondente (ex: `192.168.1.50`).
* **Conecte com o IP encontrado na sua rede:**
  ```powershell
  ssh usuario@192.168.1.50
  ```

### 4. Primeira Conexão
Na primeira vez que conectar, o terminal exibirá:
`Are you sure you want to continue connecting (yes/no/[fingerprint])?`
* Digite `yes` e pressione Enter.
* Digite a senha do usuário `usuario` (as letras não aparecem na tela por segurança, apenas digite e aperte Enter).

---

## 🚀 Como Executar no Raspberry Pi

### 1. Testar os componentes individualmente:
```bash
python3 test_hardware.py
```
*(Permite testar os bips do buzzer, o clique do botão, disparo de foto da câmera e a fala do áudio).*

### 2. Rodar o sistema principal dos óculos:
```bash
python3 sensevision_core.py
```
Ao pressionar o botão nos óculos:
1. O buzzer emite 1 bip confirmando o disparo.
2. A câmera fotografa a folha com a conta.
3. O OCR lê a operação matemática.
4. O conversor traduz a conta para grupos de frutas concretas.
5. O buzzer emite 2 bips de sucesso.
6. A narração explica a conta em voz alta pelo fone.
7. O sistema envia a imagem e o resultado estruturado em JSON para o site de vocês.

---

## 🌐 Formato do Payload Enviado ao Site (HTTP POST)

O SenseVision envia os dados via JSON para a URL definida em `config.py` (`WEB_API_URL`):

```json
{
  "timestamp": 1726533000,
  "math_expression": "3 + 2 = 5",
  "result": 5,
  "fruit": {
    "name_singular": "maçã",
    "name_plural": "maçãs",
    "emoji": "🍎",
    "gender": "f"
  },
  "visual_formula": "🍎🍎🍎 + 🍎🍎 = 🍎🍎🍎🍎🍎",
  "pedagogical_steps": [
    "Grupo 1: 🍎🍎🍎 (3)",
    "Adicionando: 🍎🍎 (2)",
    "Total reunido: 🍎🍎🍎🍎🍎 (5)"
  ],
  "explanation_speech": "Você tem 3 maçãs e ganhou mais 2 maçãs. Juntando todas, agora você tem 5 maçãs!",
  "image_base64": "data:image/jpeg;base64,..."
}
```
