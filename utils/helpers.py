from datetime import datetime
from typing import Any, Dict

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")

def safe_get(data: Dict, *keys, default: Any = None) -> Any:
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

if __name__ == "__main__":
    print("Тестирование утилит...")
    test_dict = {'a': {'b': {'c': 123}}}
    print(f"safe_get: {safe_get(test_dict, 'a', 'b', 'c')}")
    print(f"format_datetime: {format_datetime(datetime.now())}")
    print("Утилиты работают")
