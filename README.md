# SenseVision

Óculos inteligentes que capturam exercícios de matemática e os transformam em frutas e blocos,
para pessoas com discalculia. Projeto de TCC (3º ano), Colégio UNASP, 2026.

```
Raspberry Pi (botão + câmera)  --foto-->  Cloudflare Worker  <--consulta--  Site (front)
                                              |  \--> Gemini (lê a conta da foto)
                                              \--> API PHP + MySQL (contas e histórico)
```

## Estrutura

| Pasta | O que é |
|---|---|
| `front/` | **O site** (HTML, CSS, JS, imagens e o jogo). É aqui que o design é feito. |
| `backend/cloud/` | Servidor na Cloudflare (Worker): recebe a foto, lê a conta com IA, login e histórico. |
| `backend/db-api/` | API em PHP + tabelas SQL do banco de dados (MySQL). |
| `raspberry/` | Programa dos óculos (botão, câmera, buzzer e envio da foto). |
| `docs/` | Documentos (liberação de rede para a apresentação). |

**Quem vai mexer no visual:** só `front/`. Leia antes **`front/LEIA-ME-FRONT.md`**
(o que pode mudar e o que o JavaScript precisa que continue existindo).

## Segredos

Este repositório **não contém** senhas, tokens nem chaves de API. Eles ficam fora do código:

- Worker (Cloudflare): `GEMINI_API_KEY`, `UPLOAD_TOKEN`, `DB_API_URL`, `DB_API_SECRET`, gravados com `wrangler secret put`.
- PHP (servidor da escola): `config.php`, criado no servidor a partir de `backend/db-api/api/config.example.php`.
- Raspberry: variáveis `SENSEVISION_API_URL` e `SENSEVISION_TOKEN` (arquivo `/etc/sensevision.env`).

## Ver o front no computador

```
cd front
python -m http.server 5173
```

Abra http://localhost:5173. Sem o servidor, login, histórico, câmera ao vivo e leitura de foto não funcionam
(o simulador funciona normalmente).
