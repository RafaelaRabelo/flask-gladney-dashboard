# Usar imagem oficial leve do Python
FROM python:3.11-slim

# Variáveis para evitar .pyc e problemas de buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir diretório de trabalho
WORKDIR /app

# Copiar o arquivo de requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do projeto (app.py, templates, etc)
COPY . .

# Variável de ambiente padrão do Cloud Run
ENV PORT=8080

# Expor a porta
EXPOSE 8080

# Comando de start (produção usa gunicorn)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
