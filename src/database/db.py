from pathlib import Path
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy import Column, Integer, String, TIMESTAMP, select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError

log = logging.getLogger(__name__)
Base = declarative_base()

class EventLink(Base):
    __tablename__ = 'event_links'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(String, nullable=False, index=True) 
    source_name = Column(String, nullable=False)
    yandex_id = Column(String, nullable=False, unique=True) 
    event_title = Column(String)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

class DatabaseManager:
    
    def __init__(self, db_path: str = 'data/sync.db'):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
        self.session_factory = async_sessionmaker(
            self.engine, 
            expire_on_commit=False
        )

    async def init_database(self):
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            log.info("Database initialized at %s", self.db_path)
        except SQLAlchemyError as e:
            log.error("Failed to initialize database: %s", e)
            raise

    async def save_event_link(self, source_id: str, yandex_id: str, 
                             source_name: str, title: Optional[str] = None) -> bool:
        async with self.session_factory() as session:
            try:
                link = EventLink(
                    source_id=source_id,
                    source_name=source_name,
                    yandex_id=yandex_id,
                    event_title=title
                )
                session.add(link)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                log.error("Database save failed for %s: %s", source_id, e)
                await session.rollback()
                return False

    async def is_event_synced(self, source_id: str) -> bool:
        async with self.session_factory() as session:
            try:
                stmt = select(EventLink).where(EventLink.source_id == source_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none() is not None
            except SQLAlchemyError as e:
                log.error("Query failed for source_id %s: %s", source_id, e)
                return False

    async def get_sync_statistics(self) -> Dict[str, Any]:
        async with self.session_factory() as session:
            try:
                count_stmt = select(func.count(EventLink.id))
                count_res = await session.execute(count_stmt)
                total = count_res.scalar() or 0
                
                size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    'total_synced': total,
                    'db_size_kb': round(size / 1024, 1)
                }
            except (SQLAlchemyError, OSError):
                return {'total_synced': 0, 'db_size_kb': 0}
            