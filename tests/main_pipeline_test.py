import pytest
import types

@pytest.mark.asyncio
async def test_run_pipeline_smoke(monkeypatch, tmp_path):
    import src.main as main_mod
    monkeypatch.setattr(main_mod, "root", tmp_path)
    class FakeDB:
        def __init__(self, db_path): pass
        async def init_database(self): return None
        async def get_sync_statistics(self): return {"total_synced": 0}

    class FakeSync:
        def __init__(self, **kwargs): pass
        async def sync(self, days=7):
            return {"created": 0, "skipped": 0, "errors": 0}

    monkeypatch.setattr(main_mod, "DatabaseManager", FakeDB)
    monkeypatch.setattr(main_mod, "CalendarSynchronizer", FakeSync)

    monkeypatch.setattr(main_mod, "GoogleCalendarAPI", lambda: object())
    monkeypatch.setattr(main_mod, "NotionAPI", lambda *a, **k: object())
    monkeypatch.setattr(main_mod, "YandexCalendarAPI", lambda *a, **k: object())

    await main_mod.run_pipeline()