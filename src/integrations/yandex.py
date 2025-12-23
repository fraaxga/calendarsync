import os
import requests
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__name__)

class YandexCalendarAPI:
    def __init__(self):
        self.user = os.getenv("YANDEX_EMAIL")
        self.password = os.getenv("YANDEX_APP_PASSWORD")
        self.calendar_id = os.getenv("YANDEX_CALENDAR_ID", "events")
        
        self.base_url = f"https://caldav.yandex.ru/calendars/{self.user}/{self.calendar_id}/"

    def create_event(self, event_data: Dict[str, Any]) -> str | None:
        if not all([self.user, self.password]):
            log.error("Yandex credentials missing in environment variables")
            return None

        event_uid = str(uuid.uuid4()).upper()
        url = f"{self.base_url}{event_uid}.ics"
        
        ics_content = self._build_ics(event_data, event_uid)

        try:
            response = requests.put(
                url,
                data=ics_content.encode('utf-8'),
                headers={
                    "Content-Type": "text/calendar; charset=utf-8",
                },
                auth=HTTPBasicAuth(self.user, self.password),
                timeout=15
            )
            
            if response.status_code in (201, 204):
                log.info("Successfully created Yandex event: %s", event_data.get('title'))
                return event_uid
            
            log.error("Yandex API error %d: %s", response.status_code, response.text)
            return None
            
        except requests.exceptions.RequestException as e:
            log.error("Network error while connecting to Yandex: %s", e)
            return None

    def _build_ics(self, data: Dict, uid: str) -> str:
        def format_date(dt):
            if not dt:
                return ""
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        description = data.get('description', '')
        summary = data.get('title', 'Untitled')

        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//CalendarSyncApp//RU",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{format_date(datetime.now())}",
            f"DTSTART:{format_date(data.get('start'))}",
            f"DTEND:{format_date(data.get('end'))}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
            "END:VCALENDAR"
        ]
        return "\r\n".join(ics_lines) + "\r\n"
    