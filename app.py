import os
import csv
from flask import Flask, session, redirect, url_for, request, render_template
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from datetime import datetime
import gspread
import google.auth
from google.auth.transport.requests import Request
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

# 📌 Função para registrar acessos em CSV
def log_access(email, rota):
    with open("access_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), email, rota])

# 📤 Função para exportar CSV para Google Sheets (usando ADC, sem precisar de JSON)
def export_logs_to_sheets():
    SERVICE_ACCOUNT_FILE = "streamlit-auth-462617-dadfd3f80f52.json"
    SPREADSHEET_ID = "1kScMJP2Tx9KgGoMDYzkpYH1h4OZc0gaB-qKRCnqyoJI"
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)   # <-- Só isso, sem 'auth=app.auth'

    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    sheet.clear()
    sheet.append_row(["Timestamp", "Email", "Rota"])

    with open("access_log.csv", "r") as f:
        for line in f:
            row = line.strip().split(",")
            sheet.append_row(row)
            
# Página principal
@app.route('/')
def index():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    log_access(user["email"], "/")
    return render_template("dashboard.html", user=user)

# 🔑 Início do login
@app.route('/login')
def login():
    redirect_uri = url_for("authorize", _external=True, _scheme="https")
    return google.authorize_redirect(redirect_uri)

# ✅ Callback do Google
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

# 🔓 Logout
@app.route('/logout')
def logout():
    user = session.get("user")
    if user:
        log_access(user["email"], "/logout")
    session.clear()
    return redirect(url_for("index"))

# 📤 Exportar logs para o Google Sheets
@app.route('/export_logs')
def export_logs():
    try:
        export_logs_to_sheets()
        return "✅ Exportado com sucesso para o Google Sheets!"
    except Exception as e:
        return f"❌ Erro ao exportar: {e}", 500

# Rodar o app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
