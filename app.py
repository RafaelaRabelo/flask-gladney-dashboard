import os
import base64
import streamlit as st
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
from authlib.integrations.requests_client import OAuth2Session
from urllib.parse import urlencode

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SCOPE = "openid email profile"

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

# Session state
if "email" not in st.session_state:
    st.session_state.email = None

# Login URL
def build_login_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"{AUTH_URL}?{urlencode(params)}"

# Handle OAuth2
def handle_auth():
    query_params = st.query_params
    code = query_params.get("code", [None])[0] if isinstance(query_params.get("code"), list) else query_params.get("code")

    if code and not st.session_state.email:
        try:
            st.info("📨 Solicitando token...")
            client = OAuth2Session(CLIENT_ID, CLIENT_SECRET, redirect_uri=REDIRECT_URI)
            token = client.fetch_token(
                TOKEN_URL,
                code=code,
                include_client_id=True,
                redirect_uri=REDIRECT_URI,
            )
            client.token = token
            userinfo = client.get(USERINFO_URL).json()
            st.session_state.email = userinfo["email"]
            st.success(f"✅ Logado como: {userinfo['email']}")
            st.query_params.clear()
        except Exception as e:
            st.error("❌ Erro durante o login:")
            st.exception(e)

# Base64 conversion
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_image_as_base64(file):
    file_ = get_base64_of_bin_file(file)
    return f"data:image/png;base64,{file_}"

# Load logo
image_base64 = get_image_as_base64("gladney.png")

# Page config
st.set_page_config(
    page_title="Dashboard - Gladney",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown(
    f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stApp {{ background-color: #f5f5f5; }}
    .block-container {{
        background-color: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .fixed-header {{
        background-color: white;
        position: fixed;
        top: 0; left: 0; width: 100%;
        z-index: 1001;
        display: flex;
        align-items: center;
        padding: 15px 20px;
        padding-left: 400px;
        color: #008542;
        border-bottom: 3px solid #008542;
        transition: padding-left 0.3s ease;
    }}
    .fixed-header h2 {{
        margin: 0;
        font-size: 20px;
        color: #008542;
    }}
    .fixed-header img.logo {{
        position: absolute;
        height: 40px;
        right: 20px;
    }}
    section[data-testid="stSidebar"][aria-expanded="false"] ~ div .fixed-header {{
        padding-left: 80px !important;
    }}
    iframe {{
        width: 100%;
        height: 850px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.markdown(
    f"""
    <div class="fixed-header">
        <h2>Dashboard tool</h2>
        <img class="logo" src="{image_base64}" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True
)

# Auth flow
handle_auth()

# Content flow
if st.session_state.email:
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",  
            options=["Expectant Mother Dashboard", "Gladney Business Performance Dashboard", "About"],  
            icons=["speedometer", "graph-up-arrow", "info-circle"], 
            menu_icon="cast",  
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "#FFFFFF"},
                "icon": {"color": "#008542", "font-size": "18px"},
                "nav-link": {
                    "font-size": "17px",
                    "text-align": "left",
                    "margin": "5px",
                    "color": "#333333",
                    "border-radius": "10px",
                },
                "nav-link-selected": {
                    "background-color": "#00A651",
                    "color": "white",
                    "font-weight": "bold",
                },
            }
        )

    st.markdown("## ")

    if selected == "Expectant Mother Dashboard":
        st.markdown("---")
        st.markdown(
            """
            <iframe 
            src="https://lookerstudio.google.com/embed/reporting/018fe7d3-8e30-4a70-86e9-ac5b71bdb662/page/p_iv91iy4nsd" 
            frameborder="0" allowfullscreen 
            sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox">
            </iframe>
            """,
            unsafe_allow_html=True
        )

    elif selected == "Gladney Business Performance Dashboard":
        st.markdown("---")
        st.markdown(
            """
            <iframe width="100%" height="600" 
            src="https://lookerstudio.google.com/embed/reporting/704ba1ac-c624-464f-a9f5-4f0f7ecadbfc/page/p_0cruxnlesd" 
            frameborder="0" allowfullscreen 
            sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox">
            </iframe>
            """,
            unsafe_allow_html=True
        )

    elif selected == "About":
        st.markdown("---")
        st.markdown("""
        - 🚀 **Dashboard tool**
        - 💼 Developed by UpStart 13
        """)

    st.markdown("---")
    st.markdown(
        "<center><small>Developed by UpStart 13 • 2025 🚀</small></center>",
        unsafe_allow_html=True
    )

else:
    login_url = build_login_url()
    st.warning("Você não está logado.")
    st.markdown(f"[Clique aqui para login com Google]({login_url})")
