import os
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from notion_client import Client

log = logging.getLogger(__name__)

class NotionAPI:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not self.token or not self.database_id:
            log.warning("Notion credentials missing. Running in emulation mode.")
            self.enabled = False
            self.client = None
        else:
            self.enabled = True
            self.client = Client(auth=self.token)
            log.info("Notion API client initialized")

    def get_events(self, days: int = 7) -> List[Dict[str, Any]]:
        if not self.enabled:
            return self._get_emulated_events(days)
        now = datetime.now(timezone.utc)
        until = now + timedelta(days=days)
        try:
            res = self.client.databases.query(
                database_id=self.database_id,
                page_size=100,
            )
            events: List[Dict[str, Any]] = []
            for page in res.get("results", []):
                props = page.get("properties", {})
                title_prop = next((v for v in props.values() if v.get("type") == "title"), None)
                title = (
                    title_prop["title"][0]["plain_text"]
                    if title_prop and title_prop.get("title")
                    else "Untitled"
                )
                date_prop = props.get("Date")
                if not date_prop or not date_prop.get("date"):
                    continue

                start_raw = date_prop["date"].get("start")
                end_raw = date_prop["date"].get("end") or start_raw
                if not start_raw:
                    continue

                start = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
                end = datetime.fromisoformat(end_raw.replace("Z", "+00:00"))
                if end <= start:
                    end = start + timedelta(hours=1)
                if end < now or start > until:
                    continue

                events.append({
                    "id": page["id"],
                    "title": title,
                    "start": start,
                    "end": end,
                    "description": "Imported from Notion",
                    "source": "notion",
                    "source_name": "notion",
                })

            return events

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