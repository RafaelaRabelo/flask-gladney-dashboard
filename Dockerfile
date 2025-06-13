# Usar imagem oficial do Python
FROM python:3.11-slim

# Criar diretório de trabalho
WORKDIR /app

# Copiar dependências
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos
COPY . .

# Definir variável de ambiente obrigatória
ENV PORT=8080

# Expor porta que o Cloud Run usa
EXPOSE 8080

# Comando para rodar o app Flask
CMD ["python", "app.py"]
