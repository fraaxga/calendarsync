import pytest
import pytest_asyncio
import os
from pathlib import Path
from src.database.db import DatabaseManager

@pytest_asyncio.fixture
async def db_manager():
    test_db_path = "data/test_sync.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        
    manager = DatabaseManager(db_path=test_db_path)
    await manager.init_database()
    
    yield manager

    await manager.engine.dispose()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.mark.asyncio
async def test_save_and_verify_link(db_manager):
    source_id = "google_123"
    yandex_id = "yandex_456"
    source_name = "google"
    title = "Meeting with Team"
    success = await db_manager.save_event_link(
        source_id=source_id,
        yandex_id=yandex_id,
        source_name=source_name,
        title=title
    )
    assert success is True
    is_synced = await db_manager.is_event_synced(source_id)
    assert is_synced is True
    is_synced_fake = await db_manager.is_event_synced("non_existent_id")
    assert is_synced_fake is False

@pytest.mark.asyncio
async def test_get_statistics(db_manager):
    await db_manager.save_event_link("s1", "y1", "google", "Title 1")
    await db_manager.save_event_link("s2", "y2", "notion", "Title 2")
    stats = await db_manager.get_sync_statistics()
    
    assert stats['total_synced'] == 2
    assert any(k in stats for k in ['db_size_kb', 'database_size_mb'])

@pytest.mark.asyncio
async def test_duplicate_yandex_id_error(db_manager):
    source_id = "orig_1"
    yandex_id = "shared_yandex_id"
    await db_manager.save_event_link(source_id, yandex_id, "google")

    success = await db_manager.save_event_link("orig_2", yandex_id, "notion")
    assert success is False
