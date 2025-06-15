import os
import csv
import json
from flask import Flask, session, redirect, url_for, request, render_template
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

# ------------------ Função para pegar as credenciais via ENV ------------------
def get_google_credentials():
    credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not credentials_json:
        raise Exception("❌ Variável de ambiente GOOGLE_APPLICATION_CREDENTIALS_JSON não encontrada.")
    info = json.loads(credentials_json)
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    return Credentials.from_service_account_info(info, scopes=scopes)

# ------------------ Configurar OAuth com Google ------------------
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

# ------------------ Função para registrar acessos ------------------
def log_access(email, rota):
    timestamp = datetime.now().isoformat()

    # (Opcional) Log local no CSV
    with open("access_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, email, rota])

# ------------------ Exportar logs para Google Sheets ------------------
    # Log direto no Google Sheets
    try:
        SPREADSHEET_ID = "1kScMJP2Tx9KgGoMDYzkpYH1h4OZc0gaB-qKRCnqyoJI"
        creds = get_google_credentials()
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        sheet.append_row([timestamp, email, rota])
    except Exception as e:
        print(f"❌ Erro ao salvar no Sheets: {e}")


# ------------------ Rotas Flask ------------------

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

        session["user"] = {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "picture": user_info.get("picture"),
            "login_time": datetime.now().isoformat()
        }

        log_access(user_info.get("email"), "/authorize")
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

# ------------------ Rodar o App ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
