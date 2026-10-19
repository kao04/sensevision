# SenseVision: cópia COMPLETA do projeto (privada)

Esta branch é um espelho da pasta `TCC` do computador original, **incluindo senhas**
(`db-api/api/config.php`). **Nunca deixe este repositório público nem adicione colaboradores a ele.**

## Como restaurar em outro computador

```
git clone -b completo https://github.com/kao04/sensevision.git TCC
```

Depois:

1. **Repositório aninhado do site:** a pasta `sense-vision-website/_git-aninhado` é o `.git` original do site
   (o Git não aceita um `.git` dentro de outro). Para voltar a usá-lo:
   `cd TCC/sense-vision-website` e renomeie `_git-aninhado` para `.git`.
2. **Chave SSH privada (`tcc2026`):** NÃO foi enviada. Copie à mão (pen drive) ou gere outra.
3. **Programas necessários:** Git, Node.js 24 (para o Wrangler/Cloudflare), Python 3, FileZilla.
4. **Cloudflare:** `cd cloud` e `npx wrangler login`. Os secrets (`GEMINI_API_KEY`, `UPLOAD_TOKEN`,
   `DB_API_URL`, `DB_API_SECRET`) ficam na Cloudflare e **não** estão neste repositório; continuam valendo.
   Para publicar: `npx wrangler deploy`.
5. **Raspberry Pi:** continua com o programa e o serviço instalados; nada a fazer no computador novo.
6. **Banco e FTP:** as credenciais estão em `db-api/api/config.php` (servidor da escola).
