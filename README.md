# SenseVision

Óculos inteligentes que capturam exercícios de matemática e os transformam em frutas e blocos,
para pessoas com discalculia. Projeto de TCC (3º ano), Colégio UNASP, 2026.

## Estrutura

| Pasta | O que é |
|---|---|
| `front/` | O site (HTML, CSS, JS, imagens e o jogo). **É aqui que o design é feito.** |

Para quem vai mexer no visual: leia **`front/LEIA-ME-FRONT.md`** antes de alterar qualquer coisa.
Ele lista o que pode mudar à vontade e o que o JavaScript precisa que continue existindo.

## Ver o front no computador

```
cd front
python -m http.server 5173
```

Abra http://localhost:5173. Sem o servidor, login, histórico, câmera ao vivo e leitura de foto não funcionam
(o simulador funciona normalmente).

## Regras

- Nenhuma chave, senha ou token no front.
- Não adicionar CDNs nem serviços externos novos (a rede da escola só libera endereços específicos).
- Ao mudar um `.css` ou `.js`, mude o número em `?v=` do link para o navegador carregar o arquivo novo.
