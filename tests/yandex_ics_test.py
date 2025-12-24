from datetime import datetime, timezone
from src.integrations.yandex import YandexCalendarAPI

def test_build_ics_contains_required_fields(monkeypatch):
    monkeypatch.setenv("YANDEX_EMAIL", "u@yandex.ru")
    monkeypatch.setenv("YANDEX_APP_PASSWORD", "pass")
    monkeypatch.setenv("YANDEX_CALENDAR_ID", "events-1")

    api = YandexCalendarAPI()

    event = {
        "title": "Hello",
        "description": "Desc",
        "start": datetime(2025, 12, 24, 10, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 12, 24, 11, 0, tzinfo=timezone.utc),
    }
    ics = api._build_ics(event, "UID-123")
    assert "BEGIN:VCALENDAR" in ics
    assert "BEGIN:VEVENT" in ics
    assert "UID:UID-123" in ics
    assert "SUMMARY:Hello" in ics
    assert "DESCRIPTION:Desc" in ics
    assert "DTSTART:20251224T100000Z" in ics
    assert "DTEND:20251224T110000Z" in ics
    assert ics.endswith("\r\n")
