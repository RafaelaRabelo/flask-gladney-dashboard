# -----------------------------
# ETAPA 1: Build do frontend (Next.js)
# -----------------------------
FROM node:18 AS frontend-builder

# Diretório de trabalho para o frontend
WORKDIR /app/frontend

# Copiar os arquivos do frontend
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ ./

# Instalar dependências e buildar o Next
RUN npm install
RUN npm run build
RUN npm run export

# -----------------------------
# ETAPA 2: Build da aplicação Flask
# -----------------------------
FROM python:3.10-slim

# Instalar dependências básicas do sistema
RUN apt-get update && apt-get install -y build-essential

# Diretório de trabalho para o Flask
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos os arquivos do projeto Flask
COPY . .

# Copiar os arquivos exportados do Next (pasta out) para o static/next/
RUN mkdir -p static/next
COPY --from=frontend-builder /app/frontend/out/ static/next/

# Variável de ambiente para produção
ENV FLASK_ENV=production
ENV PORT=8080

# Expor porta (Cloud Run ignora, mas pode deixar)
EXPOSE 8080

# Comando para rodar o Flask
CMD ["python", "app.py"]
