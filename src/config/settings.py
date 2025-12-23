import os
import logging
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

class Config:
    ROOT = BASE_DIR
    DATA_DIR = ROOT / "data"
    AUTH_DIR = ROOT / "src" / "config"
    YANDEX_CLIENT_ID = os.getenv('YANDEX_CLIENT_ID')
    YANDEX_CLIENT_SECRET = os.getenv('YANDEX_CLIENT_SECRET')
    YANDEX_TOKEN_PATH = AUTH_DIR / 'yandex_token.json'

    GOOGLE_CREDS_PATH = AUTH_DIR / 'google_credentials.json'
    GOOGLE_TOKEN_PATH = AUTH_DIR / 'token.json'

    SYNC_DAYS = int(os.getenv('SYNC_DAYS_AHEAD', 7))

    DB_PATH = DATA_DIR / "calendar_sync.db"
    DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

    @property
    def is_yandex_ready(self) -> bool:
        return all([self.YANDEX_CLIENT_ID, self.YANDEX_CLIENT_SECRET])

    def setup_environment(self):
        self.DATA_DIR.mkdir(exist_ok=True)
        self.AUTH_DIR.mkdir(parents=True, exist_ok=True)

settings = Config()
