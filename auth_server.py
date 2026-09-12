"""
JARVIS AI — Google Calendar OAuth 2.0 Authorization Server
Runs a temporary authentication flow to generate token.json for Google Calendar access.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, request
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv

load_dotenv()

# Allow HTTP traffic for local localhost testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# Build the config dynamically from .env
client_config = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

# Set up OAuth 2.0 flow
flow = Flow.from_client_config(
    client_config,
    scopes=['https://www.googleapis.com/auth/calendar.events'],
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
)

HTML_STYLE = """
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
    .card { background: #1e293b; border: 1px solid #334155; padding: 2.5rem; border-radius: 16px; text-align: center; max-width: 420px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
    h1 { color: #60a5fa; margin-top: 0; font-size: 1.6rem; }
    p { color: #94a3b8; font-size: 0.95rem; line-height: 1.5; }
    a.btn { display: inline-block; background: #3b82f6; color: white; padding: 0.85rem 1.75rem; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 1.5rem; transition: background 0.2s; }
    a.btn:hover { background: #2563eb; }
</style>
"""

@app.route('/')
def index():
    try:
        auth_url, _ = flow.authorization_url(prompt='consent')
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>JARVIS AI — Google Authorization</title>{HTML_STYLE}</head>
        <body>
            <div class="card">
                <h1>🤖 JARVIS AI</h1>
                <p>Authorize JARVIS AI to access and manage your Google Calendar schedule securely.</p>
                <a class="btn" href="{auth_url}">Authorize Google Calendar</a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h3>OAuth Initialization Error:</h3><pre>{str(e)}</pre>"

@app.route('/auth/callback')
def callback():
    try:
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        
        # Save credentials for calendar operation
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
            
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>JARVIS AI — Authorization Successful</title>{HTML_STYLE}</head>
        <body>
            <div class="card">
                <h1 style="color: #10b981;">✅ Authorization Success!</h1>
                <p><strong>token.json</strong> has been successfully generated and saved.</p>
                <p>You can now close this window and start running JARVIS AI.</p>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h3>Authentication Callback Error:</h3><pre>{str(e)}</pre>"

if __name__ == '__main__':
    print("🚀 Starting JARVIS AI Authorization Server...")
    print("👉 Open http://localhost:8000 or http://127.0.0.1:8000 in your browser to log in.")
    app.run(host='0.0.0.0', port=8000)