import os
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

log = logging.getLogger(__name__)

class NotionAPI:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not self.token or not self.database_id:
            log.warning("Notion credentials missing. Running in emulation mode.")
            self.enabled = False
        else:
            self.enabled = True
            log.info("Notion API client initialized")

    def get_events(self, days: int = 7) -> List[Dict[str, Any]]:
        if not self.enabled:
            return self._get_emulated_events(days)

        try:
            log.info("Fetching events from Notion database...")
            return [] 
        except Exception:
            log.exception("Failed to query Notion database")
            return []

    def _transform_page(self, page: Dict) -> Dict:
        props = page.get("properties", {})
        return {
            "id": page.get("id"),
            "title": props.get("Name", {}).get("title", [{}])[0].get("plain_text", "Untitled"),
            "start": None, 
            "end": None,
            "source": "notion"
        }

    def _get_emulated_events(self, days: int) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "id": f"notion_emu_{i}",
                "title": f"Notion Task #{i}",
                "start": now + timedelta(days=2, hours=i),
                "end": now + timedelta(days=2, hours=i + 1),
                "description": "Imported from Notion database",
                "source": "notion"
            }
            for i in range(2)
        ]