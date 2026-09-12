"""
JARVIS AI — Local API Bridge Server
Handles function call requests from Gemini Live API for calendar operations.
"""

import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify
from flask_cors import CORS
from calendar_tool import book_meeting, check_availability

app = Flask(__name__)
CORS(app)

@app.route('/api/book_meeting', methods=['POST'])
def handle_booking():
    """Endpoint for booking a calendar meeting."""
    data = request.json or {}
    title = data.get('title', 'JARVIS AI Meeting')
    date_time = data.get('date_time', '')
    guest_email = data.get('guest_email', 'User')

    print(f"\n🔔 [JARVIS API] Booking meeting '{title}' for {guest_email} at {date_time}")
    result = book_meeting(date_time_iso=date_time, name=guest_email)
    print(f"✅ [JARVIS API RESPONSE] {result}")
    return jsonify({"result": result})

@app.route('/api/check_availability', methods=['POST'])
def handle_availability():
    """Endpoint for checking calendar availability for a given date."""
    data = request.json or {}
    date = data.get('date', '')

    print(f"\n📅 [JARVIS API] Checking availability for date: {date}")
    result = check_availability(date_iso=date)
    print(f"✅ [JARVIS API RESPONSE] {result}")
    return jsonify({"result": result})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "active", "service": "JARVIS AI API Bridge"})

if __name__ == '__main__':
    print("🚀 JARVIS AI Local API Bridge running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000)