import os
import csv
from flask import Flask, session, redirect, url_for, request, render_template
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

# Configurar OAuth com Google
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

# Função: Loga acesso tanto no CSV quanto no Google Sheets
def log_access(email, rota):
    timestamp = datetime.now().isoformat()

    # Log no CSV local (opcional, útil para backup)
    with open("access_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, email, rota])

    # Log direto no Google Sheets
    try:
        SERVICE_ACCOUNT_FILE = "streamlit-auth-462617-dadfd3f80f52.json"  # Nome real do seu JSON
        SPREADSHEET_ID = "1kScMJP2Tx9KgGoMDYzkpYH1h4OZc0gaB-qKRCnqyoJI"    # ID da sua planilha
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1

        # Adiciona uma linha nova no final da planilha
        sheet.append_row([timestamp, email, rota])

    except Exception as e:
        print(f"Erro ao gravar no Google Sheets: {e}")

# Página principal
@app.route('/')
def index():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    log_access(user["email"], "/")
    return render_template("dashboard.html", user=user)

# Login Google
@app.route('/login')
def login():
    redirect_uri = url_for("authorize", _external=True, _scheme="https")
    return google.authorize_redirect(redirect_uri)

# Callback do Google OAuth
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
        return f"Erro durante autenticação: {str(e)}", 500

# Logout
@app.route('/logout')
def logout():
    user = session.get("user")
    if user:
        log_access(user["email"], "/logout")
    session.clear()
    return redirect(url_for("index"))

# Rodar o app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
