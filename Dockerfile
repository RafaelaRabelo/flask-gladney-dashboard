# Base image com Python
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y build-essential

# Copiar requirements e instalar dependências do Flask
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar tudo para dentro do container
COPY . .

# Variável de ambiente (caso queira usar produção)
ENV FLASK_ENV=production

# Expor a porta (caso queira forçar, mas o Cloud Run ignora e faz auto)
EXPOSE 8080

# Comando para rodar o Flask
CMD ["python", "app.py"]
