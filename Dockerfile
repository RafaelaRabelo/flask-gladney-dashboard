# Etapa 1: Build do Frontend (Next.js)
FROM node:18 AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend ./
RUN npm run build && npm run export

# Etapa 2: Backend Flask
FROM python:3.10-slim AS backend

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copiar código Flask
COPY app.py ./
COPY templates ./templates/
COPY static ./static/

# Copiar frontend buildado para o static
COPY --from=frontend-build /app/frontend/out /app/static/next

EXPOSE 8080

CMD ["python", "app.py"]
