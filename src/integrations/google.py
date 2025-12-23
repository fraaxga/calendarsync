import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

try:
    from .google_auth import GoogleAuth
except ImportError:
    GoogleAuth = None

log = logging.getLogger(__name__)

class GoogleCalendarAPI:
    def __init__(self):
        if not GoogleAuth:
            log.error("GoogleAuth module not found. Check your project structure.")
            self.service = None
            return

        try:
            self.service = GoogleAuth().get_service()
        except Exception:
            log.exception("Failed to initialize Google Calendar service")
            self.service = None

    def get_events(self, days: int = 7) -> List[Dict[str, Any]]:
        if not self.service:
            log.warning("Google service not initialized, skipping fetch")
            return []
        
        try:
            time_min = datetime.now(timezone.utc).isoformat()
            time_max = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
            
            result = self.service.events().list(
                calendarId='primary', 
                timeMin=time_min, 
                timeMax=time_max,
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            
            raw_items = result.get('items', [])
            
            events = [self._transform(item) for item in raw_items]
            return [e for e in events if e is not None]

        except Exception:
            log.exception("Error during Google events fetching")
            return []

    def _transform(self, g_event: Dict) -> Dict | None:
        try:
            return {
                "id": g_event['id'],
                "title": g_event.get('summary') or 'Untitled Event',
                "start": self._parse_dt(g_event.get('start')),
                "end": self._parse_dt(g_event.get('end')),
                "description": g_event.get('description', ''),
                "source": 'google'
            }
        except (KeyError, ValueError) as e:
            log.debug("Skipping malformed event %s: %s", g_event.get('id'), e)
            return None

    def _parse_dt(self, dt_data: Dict) -> datetime | None:
        if not dt_data:
            return None
            
        dt_str = dt_data.get('dateTime') or dt_data.get('date')
        if not dt_str:
            return None
            
        iso_str = dt_str.replace('Z', '+00:00')
        try:
            return datetime.fromisoformat(iso_str)
        except ValueError:
            return None
        