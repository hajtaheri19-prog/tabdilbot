import requests
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class CurrencyConverter:
    """Advanced currency conversion with multiple APIs and crypto support"""
    
    def __init__(self, database):
        self.db = database
        self.base_urls = {
            "exchangerate": "https://api.exchangerate.host",
            "fixer": "https://api.fixer.io",
            "currencylayer": "https://api.currencylayer.com",
            "coinmarketcap": "https://pro-api.coinmarketcap.com/v1"
        }
        
        # Exchange rate APIs (free tier limits)
        self.api_keys = {
            "fixer": "",  # Add your API key
            "currencylayer": "",  # Add your API key
            "coinmarketcap": ""  # Add your API key
        }
    
    async def convert_currency(self, amount: float, from_currency: str, 
                             to_currency: str) -> Dict[str, any]:
        """Convert currency with fallback APIs"""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Check cache first
        cache_key = f"currency_{from_currency}_{to_currency}_{datetime.now().strftime('%Y%m%d%H')}"
        cached_rate = self.db.get_from_cache(cache_key)
        
        if cached_rate:
            try:
                rate_data = json.loads(cached_rate)
                result = amount * rate_data.get('rate', 0)
                return {
                    "success": True,
                    "amount": amount,
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "rate": rate_data.get('rate', 0),
                    "result": result,
                    "timestamp": rate_data.get('timestamp'),
                    "source": "cache"
                }
            except json.JSONDecodeError:
                pass
        
        # Try multiple APIs
        apis_to_try = [
            self._get_exchangerate_rate,
            self._get_fixer_rate,
            self._get_currencylayer_rate
        ]
        
        for api_func in apis_to_try:
            try:
                result = await api_func(amount, from_currency, to_currency)
                if result["success"]:
                    # Cache the result
                    cache_data = {
                        "rate": result["rate"],
                        "timestamp": result.get("timestamp", datetime.now().isoformat())
                    }
                    self.db.add_to_cache(cache_key, json.dumps(cache_data), 60)
                    return result
            except Exception as e:
                logger.warning(f"API {api_func.__name__} failed: {e}")
                continue
        
        return {
            "success": False,
            "error": "All currency APIs failed",
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency
        }
    
    async def _get_exchangerate_rate(self, amount: float, from_currency: str, 
                                   to_currency: str) -> Dict[str, any]:
        """Get exchange rate from exchangerate.host"""
        url = f"{self.base_urls['exchangerate']}/convert"
        params = {
            "from": from_currency,
            "to": to_currency,
            "amount": amount
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        return {
                            "success": True,
                            "amount": amount,
                            "from_currency": from_currency,
                            "to_currency": to_currency,
                            "rate": data["info"]["rate"],
                            "result": data["result"],
                            "timestamp": data["date"],
                            "source": "exchangerate.host"
                        }
        
        return {"success": False, "error": "exchangerate.host API failed"}
    
    async def _get_fixer_rate(self, amount: float, from_currency: str, 
                            to_currency: str) -> Dict[str, any]:
        """Get exchange rate from Fixer.io"""
        if not self.api_keys["fixer"]:
            return {"success": False, "error": "Fixer API key not configured"}
        
        url = f"{self.base_urls['fixer']}/latest"
        params = {
            "access_key": self.api_keys["fixer"],
            "base": from_currency,
            "symbols": to_currency
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        rate = data["rates"].get(to_currency, 0)
                        return {
                            "success": True,
                            "amount": amount,
                            "from_currency": from_currency,
                            "to_currency": to_currency,
                            "rate": rate,
                            "result": amount * rate,
                            "timestamp": data["date"],
                            "source": "fixer.io"
                        }
        
        return {"success": False, "error": "Fixer API failed"}
    
    async def _get_currencylayer_rate(self, amount: float, from_currency: str, 
                                    to_currency: str) -> Dict[str, any]:
        """Get exchange rate from CurrencyLayer"""
        if not self.api_keys["currencylayer"]:
            return {"success": False, "error": "CurrencyLayer API key not configured"}
        
        url = f"{self.base_urls['currencylayer']}/live"
        params = {
            "access_key": self.api_keys["currencylayer"],
            "currencies": f"{from_currency},{to_currency}",
            "source": "USD"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        # CurrencyLayer returns rates relative to USD
                        from_rate = data["quotes"].get(f"USD{from_currency}", 1)
                        to_rate = data["quotes"].get(f"USD{to_currency}", 1)
                        rate = to_rate / from_rate
                        
                        return {
                            "success": True,
                            "amount": amount,
                            "from_currency": from_currency,
                            "to_currency": to_currency,
                            "rate": rate,
                            "result": amount * rate,
                            "timestamp": datetime.fromtimestamp(data["timestamp"]).isoformat(),
                            "source": "currencylayer"
                        }
        
        return {"success": False, "error": "CurrencyLayer API failed"}
    
    async def get_crypto_price(self, symbol: str, convert_to: str = "USD") -> Dict[str, any]:
        """Get cryptocurrency price"""
        symbol = symbol.upper()
        convert_to = convert_to.upper()
        
        # Check cache
        cache_key = f"crypto_{symbol}_{convert_to}_{datetime.now().strftime('%Y%m%d%H%M')}"
        cached_price = self.db.get_from_cache(cache_key)
        
        if cached_price:
            try:
                price_data = json.loads(cached_price)
                return {
                    "success": True,
                    "symbol": symbol,
                    "price": price_data["price"],
                    "currency": convert_to,
                    "timestamp": price_data["timestamp"],
                    "source": "cache"
                }
            except json.JSONDecodeError:
                pass
        
        # Try CoinMarketCap API
        if self.api_keys["coinmarketcap"]:
            try:
                result = await self._get_coinmarketcap_price(symbol, convert_to)
                if result["success"]:
                    # Cache for 5 minutes
                    cache_data = {
                        "price": result["price"],
                        "timestamp": result["timestamp"]
                    }
                    self.db.add_to_cache(cache_key, json.dumps(cache_data), 5)
                    return result
            except Exception as e:
                logger.warning(f"CoinMarketCap API failed: {e}")
        
        # Fallback to free API
        try:
            result = await self._get_coingecko_price(symbol, convert_to)
            if result["success"]:
                cache_data = {
                    "price": result["price"],
                    "timestamp": result["timestamp"]
                }
                self.db.add_to_cache(cache_key, json.dumps(cache_data), 5)
                return result
        except Exception as e:
            logger.warning(f"CoinGecko API failed: {e}")
        
        return {
            "success": False,
            "error": "All crypto APIs failed",
            "symbol": symbol,
            "currency": convert_to
        }
    
    async def _get_coinmarketcap_price(self, symbol: str, convert_to: str) -> Dict[str, any]:
        """Get crypto price from CoinMarketCap"""
        url = f"{self.base_urls['coinmarketcap']}/cryptocurrency/quotes/latest"
        headers = {
            "X-CMC_PRO_API_KEY": self.api_keys["coinmarketcap"],
            "Accept": "application/json"
        }
        params = {
            "symbol": symbol,
            "convert": convert_to
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status", {}).get("error_code") == 0:
                        crypto_data = data["data"][symbol]
                        quote = crypto_data["quote"][convert_to]
                        
                        return {
                            "success": True,
                            "symbol": symbol,
                            "name": crypto_data["name"],
                            "price": quote["price"],
                            "currency": convert_to,
                            "market_cap": quote.get("market_cap"),
                            "volume_24h": quote.get("volume_24h"),
                            "percent_change_24h": quote.get("percent_change_24h"),
                            "timestamp": datetime.now().isoformat(),
                            "source": "coinmarketcap"
                        }
        
        return {"success": False, "error": "CoinMarketCap API failed"}
    
    async def _get_coingecko_price(self, symbol: str, convert_to: str) -> Dict[str, any]:
        """Get crypto price from CoinGecko (free API)"""
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": symbol.lower(),
            "vs_currencies": convert_to.lower(),
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if symbol.lower() in data:
                        crypto_data = data[symbol.lower()]
                        
                        return {
                            "success": True,
                            "symbol": symbol,
                            "price": crypto_data[convert_to.lower()],
                            "currency": convert_to,
                            "market_cap": crypto_data.get(f"{convert_to.lower()}_market_cap"),
                            "volume_24h": crypto_data.get(f"{convert_to.lower()}_24h_vol"),
                            "percent_change_24h": crypto_data.get(f"{convert_to.lower()}_24h_change"),
                            "timestamp": datetime.now().isoformat(),
                            "source": "coingecko"
                        }
        
        return {"success": False, "error": "CoinGecko API failed"}
    
    async def get_currency_list(self) -> Dict[str, List[str]]:
        """Get list of supported currencies"""
        return {
            "fiat": [
                "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "CNY", "SEK", "NZD",
                "MXN", "SGD", "HKD", "NOK", "TRY", "RUB", "INR", "BRL", "ZAR", "KRW",
                "IRR", "AED", "SAR", "QAR", "KWD", "BHD", "OMR", "JOD", "LBP", "EGP"
            ],
            "crypto": [
                "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE", "AVAX", "MATIC",
                "LTC", "BCH", "UNI", "LINK", "ATOM", "XLM", "VET", "FIL", "TRX", "ETC"
            ]
        }
    
    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict[str, any]:
        """Get all exchange rates for a base currency"""
        cache_key = f"rates_{base_currency}_{datetime.now().strftime('%Y%m%d%H')}"
        cached_rates = self.db.get_from_cache(cache_key)
        
        if cached_rates:
            try:
                return json.loads(cached_rates)
            except json.JSONDecodeError:
                pass
        
        url = f"{self.base_urls['exchangerate']}/latest"
        params = {"base": base_currency}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.db.add_to_cache(cache_key, json.dumps(data), 60)
                        return data
        
        return {"success": False, "error": "Failed to get exchange rates"}

