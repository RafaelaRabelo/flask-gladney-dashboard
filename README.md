
# 📊 Gladney Dashboard Access Tracker

Uma aplicação web em Flask com autenticação Google OAuth2, controle de acesso por domínio e e-mail, rastreamento de ações de usuários e exportação automática de logs para o Google Sheets.

---

## 🚀 Funcionalidades

✅ Login seguro com Google OAuth2  
✅ Controle de permissão por domínio (`@upstart13.com`) e/ou lista de e-mails permitidos  
✅ Tracking detalhado de acessos, cliques, IP, User-Agent e tempo entre ações  
✅ Exportação automática de logs para Google Sheets  
✅ Deploy otimizado no Google Cloud Run  
✅ Dockerfile pronto para produção  

---

## 🗂️ Estrutura de Pastas

```
📁 /app
├── app.py
├── requirements.txt
├── Dockerfile
├── templates/
│   ├── index.html          # Landing Page (Tela inicial)
│   └── dashboard.html      # Dashboard principal com menu
└── .env (somente para uso local - NÃO subir para o Git!)
```

---

## 🌐 Fluxo do Usuário

1. **Landing Page** (`/`) → Botão "Iniciar"
2. **Autenticação via Google OAuth**
3. **Acesso ao Dashboard com Menu lateral:**
   - Expectant Mother Dashboard
   - Business Dashboard
   - Filtros de Teste
   - Sobre a UpStart
4. **Cada clique em qualquer parte do sistema é rastreado e enviado ao Google Sheets**

---

## ✅ Variáveis de Ambiente Necessárias

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Uma string segura para sessão Flask |
| `GOOGLE_CLIENT_ID` | Client ID do OAuth Google |
| `GOOGLE_CLIENT_SECRET` | Client Secret do OAuth Google |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | O conteúdo JSON da Service Account (convertido em string única) |

Exemplo `.env` (localmente):

```
SECRET_KEY=uma_sua_chave
GOOGLE_CLIENT_ID=sua_client_id
GOOGLE_CLIENT_SECRET=seu_client_secret
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type": "service_account", ...}
```

**Obs:** No Cloud Run você deve cadastrar todas como Variáveis de Ambiente diretamente na interface web (não precisa de arquivo .env lá).

---

## ✅ Deploy no Google Cloud Run

### 1) Build da Imagem Docker:

```bash
gcloud builds submit --tag gcr.io/SEU_PROJETO_ID/nome-da-imagem
```

### 2) Deploy na Cloud Run:

```bash
gcloud run deploy nome-da-app \
  --image gcr.io/SEU_PROJETO_ID/nome-da-imagem \
  --platform managed \
  --region southamerica-east1 \
  --allow-unauthenticated
```

---

## ✅ Estrutura do Log no Google Sheets:

| Timestamp | Email | Rota | Extra Action | IP | User-Agent | Session ID | Time Since Last Action (s) |
|---|---|---|---|---|---|---|---|

Cada ação feita pelo usuário gera uma nova linha no Sheet.

---

## ✅ Tecnologias Utilizadas

- **Python 3.11**
- **Flask**
- **Authlib**
- **GSpread**
- **Google Sheets API**
- **Docker + Gunicorn**
- **Google Cloud Run**

---

## ✅ Possíveis Evoluções Futuras

- 📈 Dashboard de uso para visualização dos logs
- ✅ Controle de permissão via Google Sheets ou BigQuery
- 🚨 Configuração de Alertas por e-mail/Slack
- 📊 Exportação futura dos logs para o BigQuery (se houver grande volume)

---

## 🏆 Desenvolvido por:

**UpStart 13** 🚀  
2025
