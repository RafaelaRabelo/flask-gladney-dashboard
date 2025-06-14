import os
import csv
import json
import uuid
from flask import Flask, session, redirect, url_for, request, render_template, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

# ====== Função: Credenciais do Google Sheets ======
def get_google_credentials():
    credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not credentials_json:
        raise Exception("❌ GOOGLE_APPLICATION_CREDENTIALS_JSON não encontrada.")
    info = json.loads(credentials_json)
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    return Credentials.from_service_account_info(info, scopes=scopes)

# ====== Função: Log ======
def log_access(email, rota, extra_action=None):
    timestamp = datetime.now().isoformat()
    ip = request.remote_addr or "unknown"
    user_agent = request.headers.get('User-Agent') or "unknown"
    session_id = session.get("session_id", "unknown")

    last_action = session.get("last_action_time")
    if last_action:
        time_diff = (datetime.now() - datetime.fromisoformat(last_action)).total_seconds()
    else:
        time_diff = 0
    session["last_action_time"] = timestamp

    # CSV Local (opcional)
    with open("access_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp, email, rota, extra_action or "", ip, user_agent, session_id, round(time_diff, 2)
        ])

    # Google Sheets
    try:
        SPREADSHEET_ID = "1kScMJP2Tx9KgGoMDYzkpYH1h4OZc0gaB-qKRCnqyoJI"
        creds = get_google_credentials()
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1

        if sheet.row_count == 0 or sheet.cell(1, 1).value != "Timestamp":
            sheet.clear()
            sheet.append_row(["Timestamp", "Email", "Rota", "Extra Action", "IP", "User-Agent", "Session ID", "Time Since Last Action (s)"])

        sheet.append_row([
            timestamp, email, rota, extra_action or "", ip, user_agent, session_id, round(time_diff, 2)
        ])

    except Exception as e:
        print(f"❌ Erro ao salvar no Sheets: {e}")

# ====== OAuth Google ======
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile', 'prompt': 'consent', 'access_type': 'offline'}
)

# ====== Rotas ======

@app.route('/')
def landing_page():
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    log_access(user["email"], "/dashboard")
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

        # ====== Controle de permissão ======
        ALLOWED_EMAILS = ["rafaelabernardesrabelo@gmail.com"]
        ALLOWED_DOMAIN = "@upstart13.com"

        if not (user_email.endswith(ALLOWED_DOMAIN) or user_email in ALLOWED_EMAILS):
            log_access(user_email, "/unauthorized", extra_action="Unauthorized Access Attempt")
            return render_template("unauthorized.html", user=user_info), 403 


        # ====== Login e Session ======
        session["session_id"] = str(uuid.uuid4())
        session["user"] = {
            "name": user_info.get("name"),
            "email": user_email,
            "picture": user_info.get("picture"),
            "login_time": datetime.now().isoformat()
        }

        log_access(user_email, "/authorize")
        return redirect(url_for("dashboard"))

    except Exception as e:
        return f"❌ Erro durante autenticação: {str(e)}", 500

@app.route('/logout')
def logout():
    user = session.get("user")
    if user:
        log_access(user["email"], "/logout")
    session.clear()
    return redirect(url_for("landing_page"))

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
        return jsonify({"status": "error", "message": str(e)}), 500

# ====== Run ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
