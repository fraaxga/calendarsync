import pytest
from datetime import datetime
from src.sync.models import SyncRecord, UserSettings
from src.database.models import SyncRecord as DBSyncRecord

def test_db_model_init():
    record = DBSyncRecord(source_id="test", target_id="test", source_type="google")
    assert record.source_id == "test"

def test_sync_record_to_db_row():
    record = SyncRecord(
        source_id="g_123",
        target_id="y_456",
        source_type="google",
        event_title="Meeting"
    )
    
    row = record.to_db_row()
    
    assert row["source_id"] == "g_123"
    assert row["target_id"] == "y_456"
    assert row["event_title"] == "Meeting"
    assert isinstance(row["synced_at"], datetime)

def test_user_settings_logic():
    settings = UserSettings.default()
    assert settings.user_id == "default"
    assert settings.sync_enabled is True
    data = settings.to_dict()
    assert data["user_id"] == "default"
    assert data["sync_days"] == 7

def test_sync_record_repr():
    from src.database.models import SyncRecord
    record = SyncRecord(source_id="123", target_id="456", source_type="google")
    assert "123" in str(record)
    assert "456" in repr(record)

def test_sync_record_full_coverage():
    from src.database.models import SyncRecord
    record = SyncRecord(source_id="1", target_id="2", source_type="test")
    print(str(record))
    print(repr(record))
    assert record.source_id == "1"
