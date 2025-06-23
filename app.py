import os
import json
import uuid
from flask import Flask, session, redirect, url_for, request, render_template, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=30)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

@app.before_request
def make_session_permanent():
    session.permanent = True

# ====== IFRAmes (antes de qualquer rota) ======
expectant_iframes = {
    'overview': 'https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_8mak6z20rd',
    'recent-perspective': 'https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_obrfzkburd',
    'google-ads-performance': 'https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_oi42nj80rd',
    'campaign-breakdown': 'https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_7hlear4wsd',
    'funnel-comparison': 'https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_sg6j2t9wsd',
    'campaign-cost': 'https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_7pjh7o80rd',
    'contact-vs-cost': 'https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_drggvx80rd',
    'day-of-week': 'https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_kybyw8icrd',
    'campaign-ratios': 'https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_adv1u280rd',
    'contact-breakdown': 'https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_2b3vzq1wsd'
}

gladney_business_performance_iframes = {
    'domestic-adoptive-performance': 'https://lookerstudio.google.com/embed/reporting/704ba1ac-c624-464f-a9f5-4f0f7ecadbfc/page/p_0cruxnlesd',
    # ... os outros tabs (mantenha o restante igual)
}

page_traffic_monitor_iframes = {
    'cover-page': 'https://lookerstudio.google.com/embed/reporting/186ac7bf-c1de-463f-9fe7-c4eeef98acdb/page/p_z2i9rcdktd',
    # ... os outros tabs (mantenha igual)
}

# ====== Função: Credenciais Google Sheets ======
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
    last_action_time = session.get("last_action_time")
    last_route = session.get("last_route")
    last_tab = session.get("last_extra_action")

    if last_action_time and last_tab:
        try:
            time_diff = (datetime.now() - datetime.fromisoformat(last_action_time)).total_seconds()
            SPREADSHEET_ID = "1PtGM-CLkru5jWytYZfDW9ay-tFDJhHiIWSBGjL32Vbk"
            creds = get_google_credentials()
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SPREADSHEET_ID).sheet1

            if sheet.row_count == 0 or sheet.cell(1, 1).value != "Timestamp":
                sheet.clear()
                sheet.append_row(["Timestamp", "Email", "Rota", "Extra Action", "IP", "User-Agent", "Session ID", "Time Since Last Action (s)"])

            sheet.append_row([
                timestamp, email, last_route or "", last_tab, ip, user_agent, session_id, round(time_diff, 2)
            ])
        except Exception as e:
            print(f"❌ Erro ao salvar log: {e}")

    session["last_action_time"] = timestamp
    session["last_route"] = rota
    session["last_extra_action"] = extra_action or ""

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
    return render_template("welcome.html")

@app.route('/expectant_mother')
def expectant_mother():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    iframe_url = expectant_iframes['overview']
    log_access(user["email"], "/expectant_mother")
    return render_template("expectant_mother.html", user=user, iframe_url=iframe_url, active_tab='overview')

@app.route('/expectant_mother/expectant/<tab>')
def expectant_expectant_mother(tab):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    iframe_url = expectant_iframes.get(tab, expectant_iframes['overview'])
    log_access(user["email"], f"/expectant_mother/expectant/{tab}")
    return render_template("expectant_mother.html", user=user, iframe_url=iframe_url, active_tab=tab)

@app.route('/gladney_business_performance')
def gladney_business_performance():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    default_tab = list(gladney_business_performance_iframes.keys())[0]
    iframe_url = gladney_business_performance_iframes[default_tab]
    log_access(user["email"], "/gladney_business_performance")
    return render_template("gladney_business_performance.html", user=user, iframe_url=iframe_url, active_tab=default_tab)

@app.route('/gladney_business_performance/<tab>')
def gladney_business_performance_tab(tab):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    iframe_url = gladney_business_performance_iframes.get(tab)
    if not iframe_url:
        iframe_url = list(gladney_business_performance_iframes.values())[0]
    log_access(user["email"], f"/gladney_business_performance/{tab}")
    return render_template("gladney_business_performance.html", user=user, iframe_url=iframe_url, active_tab=tab)

@app.route('/page_traffic_monitor')
def page_traffic_monitor():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    log_access(user["email"], "/page_traffic_monitor")
    return render_template("page_traffic_monitor.html", user=user)

@app.route('/page_traffic_monitor/<tab>')
def page_traffic_monitor_tab(tab):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    iframe_url = page_traffic_monitor_iframes.get(tab)
    if not iframe_url:
        iframe_url = list(page_traffic_monitor_iframes.values())[0]
    log_access(user["email"], f"/page_traffic_monitor/{tab}")
    return render_template("page_traffic_monitor.html", user=user, iframe_url=iframe_url, active_tab=tab)

@app.route('/dashboard_details')
def dashboard_details():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    log_access(user["email"], "/dashboard_details")
    return render_template("dashboard_details.html", user=user)

@app.route('/notification')
def notification():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    log_access(user["email"], "/notification")
    return render_template("notification.html", user=user)

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

        ALLOWED_EMAILS = ["rafaelabernardesrabelo@gmail.com"]
        ALLOWED_DOMAIN = "@upstart13.com"

        if not (user_email.endswith(ALLOWED_DOMAIN) or user_email in ALLOWED_EMAILS):
            log_access(user_email, "/unauthorized", extra_action="Unauthorized Access Attempt")
            return render_template("unauthorized.html", user=user_info), 403

        session.permanent = True
        session["session_id"] = str(uuid.uuid4())
        session["user"] = {
            "name": user_info.get("name"),
            "email": user_email,
            "picture": user_info.get("picture"),
            "login_time": datetime.now().isoformat()
        }

        log_access(user_email, "/authorize")
        return redirect(url_for("expectant_mother"))

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

# ====== Run App ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
