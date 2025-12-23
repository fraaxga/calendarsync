from datetime import datetime
from typing import Optional
from dataclasses import dataclass

@dataclass
class SyncRecord:
    id: Optional[int] = None
    source_id: str = ""
    source_type: str = ""
    target_id: str = ""
    target_type: str = "yandex"
    event_title: Optional[str] = None
    synced_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'source_id': self.source_id,
            'source_type': self.source_type,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'event_title': self.event_title
        }

@dataclass
class UserSettings:
    user_id: int
    sync_enabled: bool = True
    sync_days: int = 7
    created_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'sync_enabled': 1 if self.sync_enabled else 0,
            'sync_days': self.sync_days
        }

if __name__ == "__main__":
    record = SyncRecord(
        source_id="google_123",
        source_type="google",
        target_id="yandex_456",
        event_title="Встреча с командой"
    )
    print(f"Пример записи: {record}")
    print(f"Для SQLite: {record.to_dict()}")
    
    settings = UserSettings(user_id=12345, sync_days=14)
    print(f"\nНастройки пользователя: {settings}")
    print(f"Для SQLite: {settings.to_dict()}")
