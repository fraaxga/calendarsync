import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
import sys
import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)-8s [%(asctime)s] %(message)s")
log = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
load_dotenv(ROOT / ".env")
from src.sync.synchronizer import CalendarSynchronizer
from src.integrations.google import GoogleCalendarAPI
from src.integrations.notion import NotionAPI
from src.integrations.yandex import YandexCalendarAPI
from src.database.db import DatabaseManager
last_report: dict | None = None
sync_lock = asyncio.Lock()
async def build_sync_engine() -> CalendarSynchronizer:
    storage_dir = ROOT / "data"
    storage_dir.mkdir(exist_ok=True)

    db = DatabaseManager(db_path=str(storage_dir / "calendar_sync.db"))
    await db.init_database()

    return CalendarSynchronizer(
        db_manager=db,
        google_client=GoogleCalendarAPI(),
        notion_client=NotionAPI(),
        yandex_client=YandexCalendarAPI(),
    )
router = Router()
@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Это бот-синхронизатор календарей. \n"
                         "/sync - для запуска синхронизации календарей Notion, Google и Yandex \n"
                         "/status - для просмотра созданных, пропущенных событий и ошибок.")

async def main():
    token = os.getenv("CSYNC_TELEGRAM_TOKEN")
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)
@router.message(Command("status"))
async def status_handler(message: Message):
    global last_report
    if not last_report:
        await message.answer("синхронизации еще не было (/sync)")
        return
    await message.answer(
        "Последняя синхронизация:\n"
        f"Создано новых событий: {last_report.get('created', 0)}\n"
        f"Пропущено из-за конфликтов: {last_report.get('skipped', 0)}\n"
        f"Ошибки: {last_report.get('errors', 0)}"
    )
@router.message(Command("sync"))
async def sync_handler(message: Message):
    global last_report
    if sync_lock.locked():
        await message.answer("Ожидайте, идет процесс синхронизации")
        return
    async with sync_lock:
        await message.answer("Синхронизирую на 7 дней вперед")
        try:
            engine = await build_sync_engine()
            last_report = await engine.sync(days=7)
            await message.answer(
                "done\n"
                f"Создано новых событий: {last_report.get('created', 0)}\n"
                f"Пропущено из-за конфликтов: {last_report.get('skipped', 0)}\n"
                f"Ошибки: {last_report.get('errors', 0)}"
            )
        except Exception:
            log.exception("Ошибка синхронизации")
            last_report = {"created": 0, "skipped": 0, "errors": 1}
            await message.answer("error during sync")
        return last_report

if __name__ == "__main__":
    asyncio.run(main())
