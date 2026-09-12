import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import datetime
from dotenv import load_dotenv

load_dotenv()

# In-memory store for fallback / simulated calendar mode
SIMULATED_EVENTS = []

def parse_iso_datetime(date_str: str) -> datetime.datetime:
    """Robust ISO datetime parsing across Python versions."""
    try:
        return datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        clean_str = date_str.split('.')[0].split('+')[0].split('-')[0]
        if len(clean_str) > 10:
            return datetime.datetime.strptime(clean_str[:19], "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.datetime.strptime(clean_str[:10], "%Y-%m-%d")

def get_calendar_service():
    if not os.path.exists('token.json'):
        return None
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar.events'])
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"⚠️ Could not load Google Calendar API: {e}")
        return None

def check_availability(date_iso: str) -> str:
    """Checks Google Calendar (or Smart Simulated Calendar) for busy slots on a specific date."""
    dt = parse_iso_datetime(date_iso)
    date_formatted = dt.strftime('%Y-%m-%d')
    
    service = get_calendar_service()
    if service:
        try:
            start_of_day = dt.replace(hour=0, minute=0, second=0).isoformat()
            end_of_day = dt.replace(hour=23, minute=59, second=59).isoformat()
            calendar_id = os.getenv("HOST_CALENDAR_ID", "primary")
            
            events_result = service.events().list(
                calendarId=calendar_id, timeMin=start_of_day, timeMax=end_of_day, 
                singleEvents=True, orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            if not events:
                return f"The calendar is completely free on {date_formatted}."
                
            busy_times = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                summary = event.get('summary', 'Busy')
                busy_times.append(f"- Blocked from {start} to {end} ({summary})")
                
            return f"Existing Google Calendar events on {date_formatted}:\n" + "\n".join(busy_times)
        except Exception as e:
            print(f"⚠️ Live Google Calendar error, switching to Simulated Mode: {e}")

    # Fallback / Simulated Mode
    print(f"📅 [SIMULATED CALENDAR] Checking availability for {date_formatted}")
    matching_events = [e for e in SIMULATED_EVENTS if e['date'] == date_formatted]
    
    default_busy = [
        f"- Blocked from 10:00 AM to 10:30 AM (Team Standup)",
        f"- Blocked from 02:00 PM to 02:30 PM (Product Sync)"
    ]
    
    for ev in matching_events:
        default_busy.append(f"- Blocked from {ev['start_time']} to {ev['end_time']} ({ev['title']})")
        
    return f"Calendar schedule on {date_formatted}:\n" + "\n".join(default_busy) + "\nOther time slots (e.g. 11:00 AM, 03:00 PM) are available for booking."

def book_meeting(date_time_iso: str, name: str = "User") -> str:
    """Creates a 30-minute Google Calendar meeting (or registers it in Simulated Mode)."""
    start_time = parse_iso_datetime(date_time_iso)
    end_time = start_time + datetime.timedelta(minutes=30)
    date_formatted = start_time.strftime('%Y-%m-%d')
    time_str = start_time.strftime('%I:%M %p')
    end_time_str = end_time.strftime('%I:%M %p')
    
    service = get_calendar_service()
    if service:
        try:
            calendar_id = os.getenv("HOST_CALENDAR_ID", "primary")
            event = {
                'summary': f'JARVIS AI Meeting: {name}',
                'description': 'Automated booking created via JARVIS AI Voice Assistant.',
                'start': {'dateTime': start_time.isoformat()},
                'end': {'dateTime': end_time.isoformat()},
            }
            event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"✅ REAL CALENDAR BOOKING SUCCESS: {event_result.get('htmlLink')}")
            return f"Success! Meeting booked on Google Calendar for {name} on {date_formatted} at {time_str}."
        except Exception as e:
            print(f"⚠️ Live Google Calendar booking error, using Simulated Mode: {e}")

    # Fallback / Simulated Mode
    booking = {
        'title': f'JARVIS AI Meeting: {name}',
        'date': date_formatted,
        'start_time': time_str,
        'end_time': end_time_str
    }
    SIMULATED_EVENTS.append(booking)
    print(f"✅ [SIMULATED CALENDAR] Booked meeting: {booking['title']} at {time_str} on {date_formatted}")
    return f"Success! Meeting '{booking['title']}' has been booked for {date_formatted} from {time_str} to {end_time_str}."