---
title: "LaTeX to PDF API"
emoji: 😜
colorFrom: blue
colorTo: purple
sdk: docker
sdk_version: ""
python_version: "3.x"
app_file: main.py
pinned: false
---

# LaTeX to PDF API (FastAPI + Docker)

Esta é uma API simples construída com FastAPI que recebe conteúdo LaTeX via POST e retorna um arquivo PDF compilado.

## Como rodar com Docker

1. Certifique-se de ter o Docker instalado.
2. No diretório do projeto, construa a imagem:
   ```bash
   docker build -t latex-api .
   ```
3. Inicie o container:
   ```bash
   docker run -p 8000:7860 latex-api
   ```

## Como usar a API

### Endpoint: `POST /compile`

Envia o conteúdo LaTeX para compilação.

**Corpo da Requisição (JSON):**
```json
{
  "content": "\\documentclass{article}\\begin{document}Olá, este é um teste do LaTeX!\\end{document}"
}
```

**Resposta:**
Um arquivo binário PDF (`application/pdf`).

### Exemplo com `curl`:

```bash
curl -X POST "http://localhost:8000/compile" \
     -H "Content-Type: application/json" \
     -d '{"content": "\\documentclass{article}\\begin{document}Hello World!\\end{document}"}' \
     --output document.pdf
```

## Estrutura do Projeto

- `main.py`: Código da API FastAPI.
- `Dockerfile`: Configuração para criar a imagem Docker com Python e TeX Live.
- `requirements.txt`: Dependências Python.