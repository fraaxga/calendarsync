синхронизация событий из Google Calendar и Notion в Яндекс.Календарь  
---
## 1. цель проекта

События часто распределены по разным системам:
- Google Calendar
- Notion

При этом Яндекс.Календарь используется как единая точка планирования.

Ручной перенос событий:
- не 


Цель проекта — автоматизировать этот процесс с обработкой дублей

---

## 2. Общая архитектура

Основные компоненты проекта:
- Telegram-бот
- CalendarSynchronizer
- Integrations:
  - Google Calendar
  - Notion
  - Yandex Calendar
- Database

Поток данных:
Telegram → Synchronizer → Sources → Yandex → Database

---

## 3. bot.py
точка входа пользователя

Функции:
- /sync
- /status
- защита от параллельных запусков

```python
sync_lock = asyncio.Lock()

@router.message(Command("sync"))
async def sync_handler(message: Message):
    if sync_lock.locked():
        await message.answer("Ожидайте, идет процесс синхронизации")
        return
    async with sync_lock:
        ...
```

---

## 4. Инициализация синхронизатора

```python
async def build_sync_engine() -> CalendarSynchronizer:
    db = DatabaseManager(db_path="calendar_sync.db")
    await db.init_database()

    return CalendarSynchronizer(
        db_manager=db,
        google_client=GoogleCalendarAPI(),
        notion_client=NotionAPI(),
        yandex_client=YandexCalendarAPI(),
    )
```

---

## 5. Ядро проекта — CalendarSynchronizer

Файл: `synchronizer.py`

```python
async def sync(self, days: int = 7) -> Dict[str, Any]:
    stats = {"created": 0, "skipped": 0, "errors": 0}

    incoming_events = await self._collect_from_all_sources(days)
    unique_events = self._deduplicate(incoming_events)

    for event in unique_events:
        if await self.db.is_event_synced(event['id']):
            stats["skipped"] += 1
            continue

        yandex_id = self.yandex.create_event(event)
        if not yandex_id:
            stats["errors"] += 1
            continue

        await self.db.save_event_link(
            source_id=event['id'],
            yandex_id=yandex_id,
            source_name=event['source'],
            title=event['title']
        )
        stats["created"] += 1

    return stats
```

основной алгоритм синхронизации.

---

## 6. Сбор событий

```python
async def _collect_from_all_sources(self, days: int):
    all_events = []
    all_events.extend(self.google.get_events(days))
    all_events.extend(self.notion.get_events(days))
    return all_events
```

если один источник недоступен — синхронизация всё равно продолжается.

---

## 7. Дедупликация

```python
def _deduplicate(self, events):
    seen = set()
    return [e for e in events if not (e['id'] in seen or seen.add(e['id']))]
```

Удаляет повторы в рамках одного запуска синхронизации.

---

## 8. База данных (db.py)

база данных используется чтобы повторный запуск не создавал дубли

### Модель

```python
class EventLink(Base):
    __tablename__ = 'event_links'
    source_id = Column(String, index=True)
    yandex_id = Column(String, unique=True)
    source_name = Column(String)
    event_title = Column(String)
```

---

## 9. проверка, было ли событие синхронизировано
```python
async def is_event_synced(self, source_id: str) -> bool:
    stmt = select(EventLink).where(EventLink.source_id == source_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None
```
---
## 10. Google Calendar интеграция
Google API используется для чтения событий.
```python
return {
    "id": g_event['id'],
    "title": g_event.get('summary'),
    "start": start,
    "end": end,
    "description": g_event.get('description'),
    "source": "google"
}
```

Все события приводятся к одному формату.

---

## 11. Google OAuth2

```python
if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())
```

Токены автоматически обновляются.

---

## 12. Notion интеграция

```python
if not self.token:
    self.enabled = False
```

+проверка на токены (для оффлайн тестов)

---

## 13. Yandex Calendar

```python
response = requests.put(
    url,
    data=ics_content,
    auth=HTTPBasicAuth(user, password)
)
```

ICS — стандартный формат календарных событий.

---

## 14. отчёт пользователю
```python
Создано новых событий: сколько то
Пропущено: сколько то
Ошибки: сколько то
```


