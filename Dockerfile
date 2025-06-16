# Etapa 1: Build do frontend (Next.js + Tailwind)
FROM node:18 AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend ./
RUN npm run build
RUN npm run export

# Etapa 2: Backend Flask com frontend embutido
FROM python:3.10-slim

# Instala dependências do Python
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o backend Flask
COPY . .

# Copia o frontend gerado para dentro da pasta static
COPY --from=frontend-build /app/frontend/out /app/static/next

# Variável de ambiente obrigatória para Flask no Google Cloud
ENV PORT 8080

# Comando final para rodar Flask
CMD ["gunicorn", "-b", ":8080", "app:app"]
