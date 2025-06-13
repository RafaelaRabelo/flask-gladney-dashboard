import os
from flask import Flask, session, redirect, url_for, request, render_template
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

# Configurar OAuth com Google
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'openid email profile'},
    authorize_params={'access_type': 'offline', 'prompt': 'consent'}
)

# Página principal
@app.route('/')
def index():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user)

# 🔑 Início do login
@app.route('/login')
def login():
    redirect_uri = url_for("authorize", _external=True, _scheme="https")
    return google.authorize_redirect(redirect_uri)

# ✅ Callback do Google
@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session["user"] = {
        "name": user_info["name"],
        "email": user_info["email"],
        "picture": user_info["picture"],
        "login_time": datetime.now().isoformat()
    }
    return redirect(url_for("index"))

# 🔓 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

# Executar app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
