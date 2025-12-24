from src.integrations.notion import NotionAPI

def test_page_to_event_parses_title_and_date(monkeypatch):
    monkeypatch.setenv("NOTION_TOKEN", "secret_x")
    monkeypatch.setenv("NOTION_DATABASE_ID", "dbid")

    api = NotionAPI()
    page = {
        "id": "page1",
        "properties": {
            "Name": {"type": "title", "title": [{"plain_text": "Task 1"}]},
            "Date": {
                "type": "date",
                "date": {
                    "start": "2025-12-24T10:00:00Z",
                    "end": "2025-12-24T11:00:00Z"
                }
            },
        },
    }
    ev = api._page_to_event(page, date_prop_name="Date")
    assert ev is not None
    assert ev["id"] == "page1"
    assert ev["title"] == "Task 1"
    assert ev["source"] == "notion"