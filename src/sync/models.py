from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

@dataclass(frozen=True)
class SyncRecord:
    source_id: str
    target_id: str
    source_type: str
    event_title: Optional[str] = None
    target_type: str = "yandex"
    synced_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_db_row(self) -> dict:
        return asdict(self)

@dataclass
class UserSettings:
    user_id: str
    sync_enabled: bool = True
    sync_days: int = 7

    @classmethod
    def default(cls) -> "UserSettings":
        return cls(user_id="default")

    def to_dict(self) -> dict:
        return asdict(self)
    