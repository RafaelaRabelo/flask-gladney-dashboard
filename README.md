
# 📊 Dashboard Access Tracker

Aplicação web em Flask com autenticação Google OAuth2, controle de acesso por domínio ou e-mail, rastreamento de ações de usuários e exportação de logs para Google Sheets.

---

## 🚀 Funcionalidades

- ✅ Login seguro com Google OAuth2  
- ✅ Controle de permissão por domínio (`@upstart13.com`) e/ou lista de e-mails  
- ✅ Registro detalhado de acessos e ações no Google Sheets  
- ✅ Exportação de logs com: timestamp, e-mail, rota acessada, IP, user-agent e tempo entre ações  
- ✅ Frontend com menu lateral, design responsivo  
- ✅ Dockerfile pronto para deploy no Google Cloud Run  

---

## 🗂️ Estrutura de Pastas

```
📁 /static
├── fundo.mp4
├── dashboard.css
├── unauthorized.png
├── access_denied_mascot.png
└── assets/
    ├── css/
    ├── fonts/
    ├── images/
    │   ├── icons/
    │   └── logo/
    └── js/

📁 /templates
├── index.html
├── dashboard.html
├── business.html
├── alerts.html
├── notification.html
├── traffic.html
└── unauthorized.html

📄 app.py
📄 Dockerfile
📄 requirements.txt
📄 README.md
📄 .env.example
```

---

## ✅ Exemplo `.env.example`

```
SECRET_KEY=sua_chave_segura
GOOGLE_CLIENT_ID=sua_client_id
GOOGLE_CLIENT_SECRET=seu_client_secret
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type": "service_account", ...}
```
> No Cloud Run, defina essas variáveis diretamente via painel web.

---

## ✅ Como Fazer o Deploy no Google Cloud Run

### 1) Build da imagem Docker:

```bash
gcloud builds submit --tag gcr.io/SEU_PROJETO_ID/gladney-dashboard
```

### 2) Deploy na Cloud Run:

```bash
gcloud run deploy gladney-dashboard \
  --image gcr.io/SEU_PROJETO_ID/gladney-dashboard \
  --platform managed \
  --region southamerica-east1 \
  --allow-unauthenticated
```

---

## ✅ Estrutura de Logs no Google Sheets

| Timestamp | Email | Rota | Extra Action | IP | User-Agent | Session ID | Time Since Last Action (s) |
|---|---|---|---|---|---|---|---|

---

## ✅ Tecnologias Usadas

- Python 3.11
- Flask
- Authlib (Google OAuth2)
- GSpread + Google Sheets API
- Bootstrap + Custom CSS
- Docker + Gunicorn
- Google Cloud Run
