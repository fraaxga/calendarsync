import pytest
from src.sync.synchronizer import CalendarSynchronizer

class FakeGoogle:
    def __init__(self, events):
        self._events = events
    def get_events(self, days=7):
        return self._events

class FakeNotion:
    def __init__(self, events):
        self._events = events
    def get_events(self, days=7):
        return self._events

class FakeYandex:
    def __init__(self):
        self.created = []
    def create_event(self, event_data):
        self.created.append(event_data)
        return f"y_{event_data['id']}"

class FakeDB:
    def __init__(self):
        self.synced = set()
        self.saved = []
    async def is_event_synced(self, source_id: str) -> bool:
        return source_id in self.synced
    async def save_event_link(self, source_id, yandex_id, source_name, title=None):
        self.synced.add(source_id)
        self.saved.append((source_id, yandex_id, source_name, title))
        return True

@pytest.mark.asyncio
async def test_sync_creates_new_and_skips_synced():
    events = [
        {"id": "e1", "title": "A", "start": "x", "end": "y", "source_name": "google"},
        {"id": "e2", "title": "B", "start": "x", "end": "y", "source_name": "notion"},
        {"id": "e2", "title": "B-dup", "start": "x", "end": "y", "source_name": "notion"},
    ]

    db = FakeDB()
    db.synced.add("e1")

    sync = CalendarSynchronizer(
        google_client=FakeGoogle([events[0]]),
        notion_client=FakeNotion(events[1:]),
        yandex_client=FakeYandex(),
        db_manager=db
    )

    report = await sync.sync(days=7)

    assert report["created"] == 1
    assert report["skipped"] == 1
    assert report["errors"] == 0
    assert len(db.saved) == 1
    assert db.saved[0][0] == "e2"
