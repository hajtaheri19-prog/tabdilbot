import requests
from typing import Dict, Any
from .config import OPENWEATHER_API_KEY, CACHE_TIME_SECONDS, DEFAULT_TIMEOUT, USER_AGENT
from .cache import get_cache, set_cache


def _safe(ok: bool, payload: Dict[str, Any] | None = None, error: str | None = None) -> Dict[str, Any]:
    if ok:
        return {"ok": True, **(payload or {})}
    return {"ok": False, "error": error or "unknown_error"}


def get_weather(city: str = "Tehran", lang: str = "fa") -> Dict[str, Any]:
    cache_key = f"weather_{city}_{lang}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    try:
        if not OPENWEATHER_API_KEY:
            return _safe(False, error="OPENWEATHER_API_KEY not set")
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}"
            f"&lang={lang}&units=metric"
        )
        res = requests.get(url, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": USER_AGENT})
        data = res.json()
        result = {
            "city": data.get("name", city),
            "temp_c": data.get("main", {}).get("temp"),
            "condition": (data.get("weather") or [{}])[0].get("description"),
            "humidity": data.get("main", {}).get("humidity"),
            "wind_ms": data.get("wind", {}).get("speed"),
        }
        wrapped = _safe(True, {"current": result})
        set_cache(cache_key, wrapped, CACHE_TIME_SECONDS)
        return wrapped
    except Exception as e:
        return _safe(False, error=str(e))


