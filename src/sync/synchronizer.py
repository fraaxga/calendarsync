import logging
from typing import List, Dict, Any

log = logging.getLogger(__name__)

class CalendarSynchronizer:
    def __init__(self, google_client, notion_client, yandex_client, db_manager):
        self.google = google_client
        self.notion = notion_client
        self.yandex = yandex_client
        self.db = db_manager

    async def sync(self, days: int = 7) -> Dict[str, Any]:
        stats = {"created": 0, "skipped": 0, "errors": 0}
        
        incoming_events = await self._collect_from_all_sources(days)
        
        unique_events = self._deduplicate(incoming_events)
        
        for event in unique_events:
            try:
                if await self.db.is_event_synced(event['id']):
                    stats["skipped"] += 1
                    continue

                yandex_id = self.yandex.create_event(event)
                
                if not yandex_id:
                    log.warning("Failed to create event %s in Yandex", event['id'])
                    stats["errors"] += 1
                    continue

                await self.db.save_event_link(
                    source_id=event['id'],
                    yandex_id=yandex_id,
                    source_name=event.get('source', 'unknown'),
                    title=event.get('title')
                )
                stats["created"] += 1
                log.info("Synced: %s", event.get('title', 'No title'))


            except Exception as e:
                log.error("Error processing event %s: %s", event.get('id'), e)
                stats["errors"] += 1
        
        return stats

    async def _collect_from_all_sources(self, days: int) -> List[Dict]:
        all_events = []
        
        try:
            all_events.extend(self.google.get_events(days=days))
        except Exception as e:
            log.error("Google API unavailable: %s", e)

        try:
            all_events.extend(self.notion.get_events(days=days))
        except Exception as e:
            log.error("Notion API unavailable: %s", e)
            
        return all_events

    def _deduplicate(self, events: List[Dict]) -> List[Dict]:
        seen = set()
        return [e for e in events if not (e['id'] in seen or seen.add(e['id']))]
    