import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from typing import Dict, Any
from .cache import get_cache, set_cache
from .config import CACHE_TIME_SECONDS, DEFAULT_TIMEOUT, USER_AGENT


def _safe(ok: bool, payload: Dict[str, Any] | None = None, error: str | None = None) -> Dict[str, Any]:
    if ok:
        return {"ok": True, **(payload or {})}
    return {"ok": False, "error": error or "unknown_error"}


def translate(text: str, src: str = "auto", dest: str = "en") -> Dict[str, Any]:
    cache_key = f"translate_{src}_{dest}_{text}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    try:
        url = f"https://translate.google.com/m?sl={src}&tl={dest}&q={quote(text)}"
        headers = {"User-Agent": USER_AGENT}
        html = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT).text
        soup = BeautifulSoup(html, "html.parser")
        container = soup.find("div", class_="result-container")
        translated_text = container.text if container else None
        if not translated_text:
            return _safe(False, error="translate_result_not_found")
        wrapped = _safe(True, {"text": translated_text})
        set_cache(cache_key, wrapped, CACHE_TIME_SECONDS)
        return wrapped
    except Exception as e:
        return _safe(False, error=str(e))









