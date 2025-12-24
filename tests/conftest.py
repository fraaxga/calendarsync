import os
import pytest
from pathlib import Path

@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]

@pytest.fixture
def tmp_db_path(tmp_path: Path) -> str:
    return str(tmp_path / "test_calendar_sync.db")

@pytest.fixture
def set_env(monkeypatch):
    def _set(**kwargs):
        for k, v in kwargs.items():
            if v is None:
                monkeypatch.delenv(k, raising=False)
            else:
                monkeypatch.setenv(k, v)
    return _set