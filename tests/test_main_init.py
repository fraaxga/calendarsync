import pytest
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path
import src.main

@pytest.mark.asyncio
async def test_run_pipeline_execution(monkeypatch):
    mock_db = AsyncMock()
    mock_db.get_sync_statistics.return_value = {'total_synced': 10}
    mock_db.init_database = AsyncMock()
    
    mock_sync = AsyncMock()
    mock_sync.sync.return_value = {'created': 1, 'skipped': 0, 'errors': 0}
    monkeypatch.setattr("src.main.DatabaseManager", lambda **k: mock_db)
    monkeypatch.setattr("src.main.CalendarSynchronizer", lambda **k: mock_sync)
    monkeypatch.setattr("src.main.GoogleCalendarAPI", MagicMock())
    monkeypatch.setattr("src.main.YandexCalendarAPI", MagicMock())
    monkeypatch.setattr("src.main.NotionAPI", MagicMock())
    monkeypatch.setattr("src.main.Path.mkdir", MagicMock())
    await src.main.run_pipeline()
    assert mock_db.init_database.called, "База данных не была инициализирована"
    assert mock_sync.sync.called, "Метод синхронизации не был вызван"
    assert mock_db.get_sync_statistics.called, "Статистика БД не была запрошена"

def test_imports_and_constants():
    assert hasattr(src.main, 'run_pipeline')
    assert hasattr(src.main, 'GoogleCalendarAPI')
    assert hasattr(src.main, 'YandexCalendarAPI')
    assert hasattr(src.main, 'NotionAPI')
