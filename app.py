import os
import csv
import json
from flask import Flask, session, redirect, url_for, request, render_template, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

# ✅ Lista de e-mails permitidos
ALLOWED_USERS = [
    "rafaelabernardesrabelo@gmail.com",
    "email2@empresa.com"
]

# ✅ Domínio permitido
ALLOWED_DOMAIN = "@upstart13.com"

# --------- Função para pegar credenciais do Google (Service Account via env) ---------
def get_google_credentials():
    credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not credentials_json:
        raise Exception("❌ Variável GOOGLE_APPLICATION_CREDENTIALS_JSON não encontrada.")
    info = json.loads(credentials_json)
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    return Credentials.from_service_account_info(info, scopes=scopes)

# --------- Função de log ---------
def log_access(email, rota, extra_action=None):
    timestamp = datetime.now().isoformat()

    # Log local (opcional)
    with open("access_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, email, rota, extra_action or ""])

    # Log no Google Sheets
    try:
        SPREADSHEET_ID = "1kScMJP2Tx9KgGoMDYzkpYH1h4OZc0gaB-qKRCnqyoJI"
        creds = get_google_credentials()
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        sheet.append_row([timestamp, email, rota, extra_action or ""])
    except Exception as e:
        print(f"❌ Erro ao salvar no Sheets: {e}")

# --------- Configurar OAuth2 Google ---------
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'consent',
        'access_type': 'offline'
    }
)

# --------- Rotas ---------

@app.route('/')
def index():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    log_access(user["email"], "/")
    return render_template("dashboard.html", user=user)

@app.route('/login')
def login():
    redirect_uri = url_for("authorize", _external=True, _scheme="https")
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    try:
        token = google.authorize_access_token()
        resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
        user_info = resp.json()

        user_email = user_info.get("email")

        # ✅ Controle híbrido: e-mail específico ou domínio permitido
        if user_email not in ALLOWED_USERS and not user_email.endswith(ALLOWED_DOMAIN):
            print(f"❌ Acesso bloqueado para: {user_email}")
            return f"❌ Acesso não autorizado para {user_email}.", 403

        session["user"] = {
            "name": user_info.get("name"),
            "email": user_email,
            "picture": user_info.get("picture"),
            "login_time": datetime.now().isoformat()
        }

        log_access(user_email, "/authorize")
        return redirect(url_for("index"))

    except Exception as e:
        return f"❌ Erro durante autenticação: {str(e)}", 500

@app.route('/logout')
def logout():
    user = session.get("user")
    if user:
        log_access(user["email"], "/logout")
    session.clear()
    return redirect(url_for("index"))

@app.route('/track_action', methods=['POST'])
def track_action():
    try:
        user = session.get("user")
        if not user:
            return jsonify({"status": "unauthorized"}), 401

        data = request.get_json()
        action = data.get("action", "Ação desconhecida")
        log_access(user["email"], "/track_action", extra_action=action)
        return jsonify({"status": "ok"})

    except Exception as e:
        print(f"❌ Erro ao registrar ação: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --------- Rodar o App ---------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
