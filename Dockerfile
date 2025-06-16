# ============================
# ETAPA 1: Build do Next.js Frontend
# ============================
FROM node:18 AS frontend-build

WORKDIR /app/frontend

# Copia apenas o frontend
COPY ./frontend/package.json ./frontend/package-lock.json* ./frontend/

# Instala dependências do frontend
RUN npm install

# Copia o resto dos arquivos do frontend (pages, components, styles etc)
COPY ./frontend .

# Build de produção do Next.js
RUN npm run build && npm run export

# ============================
# ETAPA 2: Backend Flask + Servir Next.js Exportado
# ============================
FROM python:3.10-slim

# Instala dependências básicas do sistema
RUN apt-get update && apt-get install -y build-essential && apt-get clean

WORKDIR /app

# Copia o backend Flask
COPY . .

# Copia o build estático exportado do Next.js
COPY --from=frontend-build /app/frontend/out ./static/next/

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Flask
EXPOSE 8080

# Define a variável de ambiente para o Flask
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV PORT=8080

# Comando de inicialização
CMD ["python", "app.py"]
