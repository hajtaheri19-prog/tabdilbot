import time
from typing import Any, Dict, Tuple

_cache_store: Dict[str, Tuple[Any, float]] = {}

def set_cache(key: str, value: Any, ttl_seconds: int) -> None:
    expire_time = time.time() + ttl_seconds
    _cache_store[key] = (value, expire_time)

def get_cache(key: str) -> Any | None:
    if key in _cache_store:
        value, expire_time = _cache_store[key]
        if time.time() < expire_time:
            return value
        del _cache_store[key]
    return None










