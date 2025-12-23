import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any

DISPLAY_TIME_FORMAT = "%d.%m.%Y %H:%M"

@dataclass(frozen=True)
class CalendarEvent:
    id: str                    
    source: str                
    title: str                 
    start: datetime            
    end: datetime              
    description: str = ""
    location: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.end < self.start:
            logging.getLogger(__name__).warning(f"Event '{self.title}' has invalid dates.")

    @property
    def summary(self) -> str:
        return f"[{self.source.upper()}] {self.title} ({self.start.strftime(DISPLAY_TIME_FORMAT)})"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['start'] = self.start.isoformat()
        d['end'] = self.end.isoformat()
        return d
    