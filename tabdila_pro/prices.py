import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from .config import TGJU_URL, TSETMC_URL, CACHE_TIME_SECONDS, DEFAULT_TIMEOUT, USER_AGENT
from .cache import get_cache, set_cache


def _safe_result(ok: bool, payload: Dict[str, Any] | None = None, error: str | None = None) -> Dict[str, Any]:
    if ok:
        return {"ok": True, **(payload or {})}
    return {"ok": False, "error": error or "unknown_error"}


def get_tgju_prices() -> Dict[str, Any]:
    cache_key = "tgju_prices"
    cached = get_cache(cache_key)
    if cached:
        return cached
    try:
        res = requests.get(TGJU_URL, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": USER_AGENT})
        data = res.json().get("data", {})
        result = {
            "gold": data.get("mesghal_24", {}).get("p"),
            "coin": data.get("sekeb", {}).get("p"),
            "usd": data.get("price_dollar_rl", {}).get("p"),
            "eur": data.get("price_eur", {}).get("p"),
            "btc": data.get("crypto-bitcoin", {}).get("p"),
        }
        wrapped = _safe_result(True, {"prices": result})
        set_cache(cache_key, wrapped, CACHE_TIME_SECONDS)
        return wrapped
    except Exception as e:
        return _safe_result(False, error=str(e))


def get_tsetmc_raw() -> Dict[str, Any]:
    cache_key = "tsetmc_raw"
    cached = get_cache(cache_key)
    if cached:
        return cached
    try:
        res = requests.get(TSETMC_URL, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": USER_AGENT})
        wrapped = _safe_result(True, {"raw": res.text})
        set_cache(cache_key, wrapped, CACHE_TIME_SECONDS)
        return wrapped
    except Exception as e:
        return _safe_result(False, error=str(e))


# --- Mofid Basket (TGJU homepage specific ids) ---
_BASKET_IDS = {
    "بورس": "l-gc30",
    "انس طلا": "l-ons",
    "مثقال طلا": "l-mesghal",
    "طلا ۱۸": "l-geram18",
    "سکه": "l-sekee",
    "دلار": "l-price_dollar_rl",
    "نفت برنت": "l-oil_brent",
    "تتر": "l-crypto-tether-irr",
    "بیت کوین": "l-crypto-bitcoin",
}


def fetch_mofid_basket() -> Dict[str, Any]:
    cache_key = "mofid_basket"
    cached = get_cache(cache_key)
    if cached:
        return cached
    try:
        url = "https://www.tgju.org/"
        res = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=DEFAULT_TIMEOUT)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        result: Dict[str, Any] = {}
        for title, _id in _BASKET_IDS.items():
            element = soup.find("li", id=_id)
            if not element:
                continue
            value_el = element.select_one(".info-price")
            change_el = element.select_one(".info-change")
            price_txt = value_el.text.strip().replace(",", "") if value_el else None
            change_txt = change_el.text.strip() if change_el else None
            price_val: Any = price_txt
            try:
                price_val = float(price_txt) if price_txt is not None else None
            except Exception:
                pass
            result[title] = {"price": price_val, "change": change_txt}

        wrapped = _safe_result(True, {"data": result})
        set_cache(cache_key, wrapped, CACHE_TIME_SECONDS)
        return wrapped
    except Exception as e:
        return _safe_result(False, error=str(e))


# --- Popular cryptos via CoinGecko ---
_POPULAR_COINS = {
    "bitcoin": {
        "symbol": "BTC",
        "name": "Bitcoin",
        "image": "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
    },
    "ethereum": {
        "symbol": "ETH",
        "name": "Ethereum",
        "image": "https://cryptologos.cc/logos/ethereum-eth-logo.png",
    },
    "binancecoin": {
        "symbol": "BNB",
        "name": "BNB",
        "image": "https://cryptologos.cc/logos/binance-coin-bnb-logo.png",
    },
    "ripple": {
        "symbol": "XRP",
        "name": "XRP",
        "image": "https://cryptologos.cc/logos/xrp-xrp-logo.png",
    },
    "solana": {
        "symbol": "SOL",
        "name": "Solana",
        "image": "https://cryptologos.cc/logos/solana-sol-logo.png",
    },
}

_POPULAR_API = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum,binancecoin,ripple,solana"
    "&vs_currencies=usd"
    "&include_24hr_change=true"
)


def get_popular_crypto() -> Dict[str, Any]:
    cache_key = "popular_crypto"
    cached = get_cache(cache_key)
    if cached:
        return cached
    try:
        res = requests.get(_POPULAR_API, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": USER_AGENT})
        res.raise_for_status()
        data = res.json()

        popular_list = []
        for coin_id, info in data.items():
            if coin_id not in _POPULAR_COINS:
                continue
            coin_info = _POPULAR_COINS[coin_id]
            price = float(info.get("usd", 0))
            change_percent = float(info.get("usd_24h_change", 0))
            popular_list.append({
                "symbol": coin_info["symbol"],
                "name": coin_info["name"],
                "price_usd": round(price, 2),
                "change_percent_24h": round(change_percent, 2),
                "image": coin_info["image"],
            })

        wrapped = _safe_result(True, {"popular": popular_list})
        set_cache(cache_key, wrapped, CACHE_TIME_SECONDS)
        return wrapped
    except Exception as e:
        return _safe_result(False, error=str(e))


