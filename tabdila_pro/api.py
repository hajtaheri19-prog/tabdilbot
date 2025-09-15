from typing import Dict, Any
from .prices import get_tgju_prices, get_tsetmc_raw
from .weather import get_weather
from .translate import translate


def get_tabdila_data(city: str = "Tehran", lang: str = "fa",
                      text_to_translate: str | None = None, translate_to: str = "en") -> Dict[str, Any]:
    return {
        "prices": get_tgju_prices(),
        "market_raw": get_tsetmc_raw(),
        "weather": get_weather(city, lang),
        "translation": translate(text_to_translate, src=lang, dest=translate_to) if text_to_translate else None,
    }










