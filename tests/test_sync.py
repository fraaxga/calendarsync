import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from src.sync.synchronizer import CalendarSynchronizer

@pytest.fixture
def sync_engine():
    mock_google = MagicMock()
    mock_notion = MagicMock()
    mock_yandex = MagicMock()
    mock_db = MagicMock()

    mock_db.is_event_synced = AsyncMock()
    mock_db.save_event_link = AsyncMock()

    engine = CalendarSynchronizer(
        google_client=mock_google,
        notion_client=mock_notion,
        yandex_client=mock_yandex,
        db_manager=mock_db
    )
    return engine

def test_deduplicate_events(sync_engine):
    events = [
        {'id': '1', 'source_name': 'google'},
        {'id': '1', 'source_name': 'google'},
        {'id': '2', 'source_name': 'notion'}
    ]
    unique = sync_engine._deduplicate(events)
    assert len(unique) == 2
    assert unique[0]['id'] == '1'
    assert unique[1]['id'] == '2'

@pytest.mark.asyncio
async def test_full_sync_flow_success(sync_engine):
    sync_engine.google.get_events.return_value = [
        {'id': 'g1', 'source_name': 'google', 'title': 'Test', 'start': datetime.now(), 'end': datetime.now()}
    ]
    sync_engine.notion.get_events.return_value = []
    sync_engine.db.is_event_synced.return_value = False
    sync_engine.yandex.create_event.return_value = 'yandex_123'

    stats = await sync_engine.sync(days=1)

    assert stats['created'] == 1
    assert stats['errors'] == 0
    sync_engine.db.save_event_link.assert_called_once()

@pytest.mark.asyncio
async def test_skip_already_synced(sync_engine):
    sync_engine.google.get_events.return_value = [{'id': 'g1', 'source_name': 'google'}]
    sync_engine.notion.get_events.return_value = []
    sync_engine.db.is_event_synced.return_value = True

    stats = await sync_engine.sync(days=1)
    assert stats['skipped'] == 1
    assert stats['created'] == 0