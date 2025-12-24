import pytest

from src.database.db import DatabaseManager

@pytest.mark.asyncio
async def test_db_init_and_save_and_check(tmp_db_path):
    db = DatabaseManager(db_path=tmp_db_path)
    await db.init_database()
    assert await db.is_event_synced("abc") is False
    ok = await db.save_event_link(
        source_id="abc",
        yandex_id="YANDEX-1",
        source_name="notion",
        title="Test"
    )
    assert ok is True
    assert await db.is_event_synced("abc") is True
    stats = await db.get_sync_statistics()
    assert stats["total_synced"] == 1
    assert stats["db_size_kb"] >= 0