from datetime import datetime

from src.database.models import SyncRecord as DBSyncRecord, UserSettings as DBUserSettings
from src.sync.models import SyncRecord as SyncSyncRecord, UserSettings as SyncUserSettings

def test_db_models_to_dict():
    r = DBSyncRecord(source_id="s1", source_type="google", target_id="y1", event_title="Meet")
    d = r.to_dict()
    assert d["source_id"] == "s1"
    assert d["source_type"] == "google"
    assert d["target_id"] == "y1"
    assert d["target_type"] == "yandex"
    assert d["event_title"] == "Meet"
    u = DBUserSettings(user_id=123, sync_enabled=False, sync_days=14)
    ud = u.to_dict()
    assert ud["user_id"] == 123
    assert ud["sync_enabled"] == 0
    assert ud["sync_days"] == 14

def test_sync_models_defaults_and_to_dict():
    u = SyncUserSettings.default()
    assert u.user_id == "default"
    assert u.sync_enabled is True
    assert u.sync_days == 7
    r = SyncSyncRecord(source_id="a", target_id="b", source_type="notion", event_title="X")
    row = r.to_db_row()
    assert row["source_id"] == "a"
    assert row["target_id"] == "b"
    assert row["source_type"] == "notion"
    assert row["target_type"] == "yandex"
    assert isinstance(row["synced_at"], datetime)