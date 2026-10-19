# SenseVision: guia do front-end (para quem vai mexer no design)

Este pacote é **só o front** (HTML, CSS, JS, imagens e o jogo). O servidor (login, histórico, leitura da foto) fica em outra pasta e **não vem aqui**. Você pode mudar o visual à vontade, desde que respeite a seção **"O que não pode quebrar"**.

## Como ver o site no seu computador

```
python -m http.server 5173
```
Abra `http://localhost:5173`. Sem o servidor, estas partes **não funcionam** (isso é normal): login/cadastro, histórico, "Câmera Ao Vivo" e leitura de foto.
O simulador funciona normalmente, e dá para abrir uma conta direto pelo endereço:
`http://localhost:5173/simulador.html?conta=(4+2)*3`

## Estrutura

| Arquivo / pasta | O que é |
|---|---|
| `index.html`, `instrucoes.html`, `produto.html`, `equipe.html`, `referencias.html` | Páginas de apresentação |
| `simulador.html` | Simulador (digita a conta e vê em frutas, passo a passo) |
| `jogo.html`, `jogar.html` | Página do jogo e a página que roda o jogo |
| `historico.html` | Histórico de contas de quem está logado |
| `css/design.css` | Base do design: tokens (cores, espaçamentos), cabeçalho, rodapé, grid e páginas de conteúdo |
| `css/features.css` | Simulador, pop-ups de conta, histórico e estados de interface |
| `css/refinement.css` | Ajustes finos de contraste, foco e responsividade (carregado por último) |
| `css/visual.css` | Frutas, blocos e quadros do passo a passo (gerados pelo JS) |
| `css/icons.css` | Ícones SVG locais |
| `css/style.css`, `css/responsive.css`, `css/dark.css`, `css/simulador.css`, `css/auth.css`, `css/jogar.css`, `css/produto.css`, `css/instrucoes.css`, `css/ux-review.css`, `parte2.css` | **Sem uso** nas páginas atuais (design anterior, mantidos como histórico) |
| `js/theme.js` | Modo escuro (lembra a escolha no navegador) |
| `js/script.js` | Menu do celular |
| `js/simulador.js`, `js/visual.js` | Motor do simulador e desenho das frutas |
| `js/auth.js`, `js/historico.js` | Login, cadastro, histórico |
| `parte2.js` | Formulário de contato |
| `game/` | O jogo (arquivos gerados pelo GameMaker). **Não editar.** |
| `assets/` | Ícones e imagens |

## O que não pode quebrar (o JavaScript depende disso)

O JS procura estes elementos pelo `id` ou pela classe. Pode **mudar o estilo, a posição e as tags ao redor**, mas o elemento precisa continuar existindo com o mesmo nome.

**`id`s usados pelo JS**
`mathInput`, `btnCalc`, `btnLiveMode`, `livePanel`, `liveStatus`, `btnSpeak`, `speakLabel`, `speedToggle`, `narrationText`, `stepsList`, `fruitsDisplay`, `equationOriginal`, `historyNote`, `testBuzzerBtn`, `header`, `menuToggle`, `histBox`, `histClear`, `histSub`

**Classes usadas pelo JS**
- Simulador: `.key-btn` (com `data-key`), `.fruit-btn` (com `data-fruit`), `.preset-chip` (com `data-expr`), `.steps-box`
- Menu e cabeçalho: `.header__inner`, `.header__cta`, `.nav`, `.nav__link`, `.menu-toggle`, `.theme-switch`, `.desktop-theme-switch`, `.menu-theme`. O `auth.js` junta Entrar + modo escuro + Jogar dentro de `.header__actions`.
- Formulário de contato: `.contact-form`, `.form-status`, campos `nome`, `email`, `mensagem` e o campo escondido `_honey` (anti-spam, não remover).

**Estados que o JS liga e desliga com classes** (precisam ter estilo): `body.theme-dark` (modo escuro), `.nav-open` (menu aberto no celular), `.live-active`, `.is-speaking`, `.is-active`, `.is-visible`, `body.auth-open`.

**Gerado pelo JS (não existe no HTML):** o pop-up de login (`.auth-*`), as frutas e os blocos (`.fv-*`) e a lista do histórico (`.hist-*`). Para mudar o visual deles, edite `css/features.css` (pop-ups e histórico) e `css/visual.css` (frutas).

**Ordem dos scripts:** `visual.js` antes de `simulador.js`; `theme.js` antes de `auth.js`. Mantenha `<script>` no fim do `<body>`.

**Rotas de API que o site chama** (mesma origem, não mudar):
`/api/status`, `/api/ocr`, `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`, `/api/history`.

## Regras do projeto (importante para a apresentação)

1. **Sem números nas áreas de resultado.** O público tem discalculia: quantidades aparecem como frutas e blocos, não dígitos. Manter assim.
2. **Não adicionar serviços externos novos.** A rede da escola só vai liberar os endereços da lista: o próprio site, `fonts.googleapis.com`, `fonts.gstatic.com` e `formsubmit.co`. **Não use CDN** (Bootstrap, Tailwind CDN, Font Awesome CDN, Google Analytics etc.). Se precisar de uma biblioteca ou fonte, **coloque o arquivo dentro da pasta** do projeto.
3. **Nenhuma chave, senha ou token no front.** Tudo que é segredo fica no servidor.
4. **Responsivo e modo escuro:** teste em 375, 820, 1280 e 1440 px, nos dois temas. O celular usa o menu "hambúrguer".
5. **Acessibilidade:** manter contraste, foco visível e tamanhos de toque grandes nos botões.
6. **Cache:** ao mudar um `.css` ou `.js`, mude o número em `?v=` do link para o navegador carregar o arquivo novo.

## Como devolver

- Mande a pasta inteira em `.zip`, com a **mesma estrutura**.
- Não precisa enviar `game/` se não mexeu (mas pode, sem problema).
- Anote numa lista os **arquivos que você alterou**, e se criou arquivos novos.
- Se precisar mudar algum `id`, classe ou rota da seção "O que não pode quebrar", **avise antes**, porque o JS precisa acompanhar.

Dúvidas sobre o que pode ou não mexer: pergunte antes de renomear.
