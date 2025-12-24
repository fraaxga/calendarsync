from datetime import datetime, timezone
import types

from src.integrations.yandex import YandexCalendarAPI

def test_yandex_create_event_success(monkeypatch):
    monkeypatch.setenv("YANDEX_EMAIL", "user@yandex.ru")
    monkeypatch.setenv("YANDEX_APP_PASSWORD", "app-pass")
    monkeypatch.setenv("YANDEX_CALENDAR_ID", "events-1")
    api = YandexCalendarAPI()
    class Resp:
        status_code = 201
        text = ""
    def fake_put(url, data=None, headers=None, auth=None, timeout=None):
        assert url.startswith("https://caldav.yandex.ru/")
        assert b"BEGIN:VCALENDAR" in data
        return Resp()
    import src.integrations.yandex as ymod
    monkeypatch.setattr(ymod.requests, "put", fake_put)

    event = {
        "title": "Test",
        "description": "Desc",
        "start": datetime(2025, 12, 24, 10, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 12, 24, 11, 0, tzinfo=timezone.utc),
    }

    uid = api.create_event(event)
    assert uid is not None
    assert len(uid) > 10