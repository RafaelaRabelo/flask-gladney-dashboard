# Etapa 1: Build do frontend
FROM node:18 AS frontend-build

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend ./
RUN npm run build
RUN npm run export

# Etapa 2: Backend Flask com frontend embutido
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=frontend-build /app/frontend/out /app/static/next

ENV PORT 8080

CMD ["gunicorn", "-b", ":8080", "app:app"]
