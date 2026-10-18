# SenseVision: endereços para liberar na rede (apresentação do TCC)

Documento para o responsável pela rede/firewall da escola.
O projeto SenseVision (óculos com câmera + site) usa a internet apenas por **HTTPS (porta 443)**.
Nenhuma porta diferente da 443 é necessária.

## Resumo: o que liberar (lista curta)

**Obrigatório** (sem isso o site não funciona):

| Domínio | Porta | Para quê |
|---|---|---|
| `sensevision.sensevision.workers.dev` | 443 (HTTPS) | O site inteiro e a API (todas as rotas abaixo) |

**Recomendado** (o site abre sem eles, mas perde a fonte e o formulário de contato):

| Domínio | Porta | Para quê |
|---|---|---|
| `fonts.googleapis.com` | 443 | Fonte do site (CSS) |
| `fonts.gstatic.com` | 443 | Fonte do site (arquivos) |
| `formsubmit.co` | 443 | Envio do formulário de contato por e-mail |

**Liberar pelo nome do domínio, não por IP.** O endereço fica na Cloudflare e os IPs mudam.
É preciso permitir os métodos **GET, POST e DELETE** (alguns filtros bloqueiam POST/DELETE sem avisar).
O site usa **cookies próprios** (`sv_session`, só do mesmo domínio): não bloquear cookies de primeira parte.

---

## 1. Computador da apresentação (navegador)

Tudo em `https://sensevision.sensevision.workers.dev`

### Páginas e arquivos (GET)
| Rota | O que é |
|---|---|
| `/` , `/index.html` | Página inicial |
| `/simulador.html` | Simulador de matemática com frutas |
| `/jogo.html`, `/jogar.html` | Página do jogo e o jogo |
| `/game/*` | Arquivos do jogo (imagens, sons .mp3, scripts) |
| `/instrucoes.html`, `/produto.html`, `/equipe.html`, `/referencias.html` | Demais páginas |
| `/historico.html` | Histórico de contas do usuário |
| `/css/*`, `/js/*`, `/assets/*` | Estilos, scripts e imagens |

### API (todas sob `/api/`)
| Método | Rota | Para quê |
|---|---|---|
| GET | `/api/status` | O site pergunta a cada 2 segundos se chegou uma foto nova dos óculos |
| POST | `/api/ocr` | Lê a conta da última foto (pode levar até alguns segundos) |
| POST | `/api/auth/register` | Criar conta |
| POST | `/api/auth/login` | Entrar |
| POST | `/api/auth/logout` | Sair |
| GET | `/api/auth/me` | Ver quem está logado |
| GET, POST, DELETE | `/api/history` | Listar, salvar e apagar o histórico |
| DELETE | `/api/history/{id}` | Apagar uma conta do histórico |

> Se o filtro permitir só o domínio inteiro, melhor ainda: basta liberar `sensevision.sensevision.workers.dev` com todos os caminhos.

### Outros endereços usados pelo navegador
| Domínio | Rota | Obrigatório? |
|---|---|---|
| `fonts.googleapis.com` | `GET /css2` | Recomendado |
| `fonts.gstatic.com` | `GET /s/*` | Recomendado |
| `formsubmit.co` | `POST /ajax/*` | Só para o formulário de contato |

**Narração por voz:** usa as vozes do próprio computador. Se o navegador for o Chrome e a voz em português for "Google português do Brasil", ela é carregada pela internet e pode exigir liberar domínios `google.com`. Em caso de dúvida, usar a voz "Microsoft Maria", que funciona sem internet.

---

## 2. Óculos (Raspberry Pi)

Na apresentação o Raspberry usará o **hotspot do celular**, então **não passa pela rede da escola**.
Se mesmo assim for ligado na rede da escola, ele precisa:

| Destino | Porta | Para quê |
|---|---|---|
| `sensevision.sensevision.workers.dev` — `POST /api/upload` | 443 | Enviar a foto tirada pelo botão |
| DNS (servidor da rede) | 53 UDP/TCP | Resolver o nome do site |
| `time.cloudflare.com` ou `pool.ntp.org` | 123 UDP | Acertar a hora (sem a hora certa o HTTPS falha) |

Observação: redes que pedem usuário e senha em página de login (portal cativo) ou autenticação corporativa **não funcionam no Raspberry**. Por isso o plano é o hotspot do celular.

---

## 3. Servidores (informativo — não passam pela rede da escola)

Estas conexões saem da nuvem, não do computador da apresentação:

| Origem | Destino | Para quê |
|---|---|---|
| Cloudflare Worker | `generativelanguage.googleapis.com` (443) | Leitura da foto por IA (Gemini) |
| Cloudflare Worker | `<servidor da escola onde roda o PHP>` (443) | Banco de dados de contas e histórico |

---

## 4. Links de consulta (opcionais, só se alguém clicar)

A página "Referências" tem links para sites externos. Não são necessários para o funcionamento:
`github.com`, `doi.org`, `arxiv.org`, `www.cast.org`, `cloud.google.com`, `docs.espressif.com`, `gdevelop.io`.

---

## 5. Como o responsável pode testar a liberação

Do computador da apresentação, abrir no navegador:

1. `https://sensevision.sensevision.workers.dev` — o site deve abrir com fonte e imagens.
2. `https://sensevision.sensevision.workers.dev/api/status` — deve mostrar um texto parecido com:
   `{"status":"ok","has_photo":true,"timestamp":...,"filename":"..."}`
   Se aparecer página de bloqueio, a rota `/api/` ainda está sendo barrada.
3. Abrir o simulador, digitar `3 + 2` e clicar em **Converter em Frutas**: devem aparecer as frutas.

Pelo terminal (opcional):
```
curl -I https://sensevision.sensevision.workers.dev
curl -X POST https://sensevision.sensevision.workers.dev/api/auth/login -H "Content-Type: application/json" -d "{}"
```
O segundo comando deve responder **401** com texto em JSON (isso mostra que o POST passa pelo filtro). Resposta de bloqueio da rede ou erro de conexão indica que ainda falta liberar.

---

## 6. Se não for possível liberar

Plano B: usar o hotspot do celular também no computador da apresentação (ou abrir o site no próprio celular). O site funciona em qualquer rede com acesso ao endereço da seção "Obrigatório".

*Projeto SenseVision — TCC 2026.*
