# Usar uma imagem base leve de Python
FROM python:3.11-slim

# Evitar a geração de arquivos .pyc e habilitar o log em tempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependências do sistema, incluindo o compilador LaTeX
# texlive-latex-base contém o pdflatex básico
# texlive-fonts-recommended é necessário para fontes comuns
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY main.py .

# Expor a porta que o FastAPI usará
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
