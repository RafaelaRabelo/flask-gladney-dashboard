# Usar imagem oficial leve do Python
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do projeto
COPY . .

# Definir variável de ambiente padrão do Cloud Run
ENV PORT=8080

# Expor a porta
EXPOSE 8080

# Rodar com gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
