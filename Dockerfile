# Etapa 1 - Build Frontend
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend ./
RUN npm run build

# Etapa 2 - Backend + Copiando Frontend Build
FROM python:3.10-slim

WORKDIR /app
COPY . .

# Copia o build estático do Next para a pasta pública do Flask (exemplo)
COPY --from=frontend-build /app/frontend/.next /app/static/next

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
