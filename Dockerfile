# Etapa 1: Build do frontend Next.js
FROM node:18 AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend ./
RUN npm run build
RUN npm run export

# Etapa 2: Backend Flask
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código do Flask
COPY . .

# Copiar o build pronto do frontend
COPY --from=frontend-build /app/frontend/out /app/static/next

# Variáveis obrigatórias
ENV PORT 8080

CMD ["gunicorn", "-b", ":8080", "app:app"]
