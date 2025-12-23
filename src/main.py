import asyncio
import logging
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.append(str(root))

from src.sync.synchronizer import CalendarSynchronizer
from src.integrations.google import GoogleCalendarAPI
from src.integrations.yandex import YandexCalendarAPI
from src.integrations.notion import NotionAPI
from src.database.db import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(levelname)-8s [%(asctime)s] %(message)s')
log = logging.getLogger(__name__)

async def run_pipeline():
    storage_dir = root / "data"
    storage_dir.mkdir(exist_ok=True)
    
    db = DatabaseManager(db_path=str(storage_dir / "calendar_sync.db"))
    
    try:
        await db.init_database()
        
        sync_engine = CalendarSynchronizer(
            db_manager=db,
            google_client=GoogleCalendarAPI(),
            notion_client=NotionAPI(use_mock=True),
            yandex_client=YandexCalendarAPI(use_mock=False)
        )
        
        log.info("Starting synchronization cycle...")
        report = await sync_engine.sync(days=7)
        
        log.info(
            "Sync complete. Created: %d, Skipped: %d, Errors: %d",
            report.get('created', 0), 
            report.get('skipped', 0), 
            report.get('errors', 0)
        )
        
        db_info = await db.get_sync_statistics()
        log.info("Database state: %d total events tracked", db_info.get('total_synced'))

    except Exception:
        log.exception("Unexpected pipeline failure")
    finally:
        log.info("Shutdown.")

if __name__ == "__main__":
    try:
        asyncio.run(run_pipeline())
    except KeyboardInterrupt:
        pass 
