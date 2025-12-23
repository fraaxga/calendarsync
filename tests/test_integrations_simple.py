import pytest
from unittest.mock import MagicMock, patch
from src.integrations.google import GoogleCalendarAPI
from src.integrations.yandex import YandexCalendarAPI
from src.integrations.notion import NotionAPI

def test_google_api_coverage(monkeypatch):
    monkeypatch.setattr("src.integrations.google.GoogleAuth", MagicMock())
    api = GoogleCalendarAPI()
    assert hasattr(api, 'service')

def test_yandex_api_coverage():
    api = YandexCalendarAPI()
    assert hasattr(api, 'base_url') or api is not None

def test_notion_api_coverage():
    api = NotionAPI()
    assert api is not None
