from src.integrations.notion import NotionAPI

def test_notion_emulation_mode(monkeypatch):
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_DATABASE_ID", raising=False)
    api = NotionAPI()
    events = api.get_events(days=7)

    assert api.enabled is False
    assert len(events) > 0
    assert events[0]["source"] == "notion"