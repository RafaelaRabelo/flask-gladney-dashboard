from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
from datetime import datetime

# Load env vars
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# OAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    authorize_params={'access_type': 'offline', 'prompt': 'consent'},
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/')
def index():
    user = session.get('user')
    if user:
        return render_template('dashboard.html', user=user)
    return redirect(url_for('login'))

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session['user'] = {
        'name': user_info['name'],
        'email': user_info['email'],
        'picture': user_info['picture'],
        'login_time': datetime.now().isoformat()
    }
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
