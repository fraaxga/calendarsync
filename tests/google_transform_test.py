from datetime import datetime, timezone
from src.integrations.google import GoogleCalendarAPI

def test_google_parse_dt_datetime():
    api = GoogleCalendarAPI.__new__(GoogleCalendarAPI)
    dt = api._parse_dt({"dateTime": "2025-12-24T10:00:00Z"})
    assert isinstance(dt, datetime)
    assert dt.tzinfo is not None

def test_google_parse_dt_date_all_day():
    api = GoogleCalendarAPI.__new__(GoogleCalendarAPI)
    dt = api._parse_dt({"date": "2025-12-24"})
    assert isinstance(dt, datetime)

def test_google_transform_minimal_event():
    api = GoogleCalendarAPI.__new__(GoogleCalendarAPI)
    g_event = {
        "id": "abc",
        "summary": "Meeting",
        "start": {"dateTime": "2025-12-24T10:00:00Z"},
        "end": {"dateTime": "2025-12-24T11:00:00Z"},
        "description": "Hello",
    }
    ev = api._transform(g_event)
    assert ev["id"] == "abc"
    assert ev["title"] == "Meeting"
    assert ev["source"] == "google"