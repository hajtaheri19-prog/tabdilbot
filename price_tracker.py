import requests
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Import new price sources
from binance_popular import get_popular_data
from tgju import fetch_mofid_basket
from crypto_prices import fetch_top_cryptos

logger = logging.getLogger(__name__)

class PriceTracker:
    """Real-time price tracking for stocks, crypto, and commodities"""
    
    def __init__(self, database):
        self.db = database
        self.api_keys = {
            "alpha_vantage": "",  # Add your API key
            "coinmarketcap": "",  # Add your API key
            "finnhub": "",  # Add your API key
            "polygon": ""  # Add your API key
        }
        
        # API endpoints
        self.endpoints = {
            "alpha_vantage": "https://www.alphavantage.co/query",
            "coinmarketcap": "https://pro-api.coinmarketcap.com/v1",
            "finnhub": "https://finnhub.io/api/v1",
            "polygon": "https://api.polygon.io/v2",
            "yahoo_finance": "https://query1.finance.yahoo.com/v8/finance/chart",
            "coingecko": "https://api.coingecko.com/api/v3",
            "binance": "https://api.binance.com/api/v3",
            "kucoin": "https://api.kucoin.com/api/v1",
            "cryptingup": "https://cryptingup.com/api"
        }
        
        # Supported asset types
        self.asset_types = {
            "stocks": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"],
            "crypto": ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE", "AVAX", "MATIC", 
                      "LTC", "BCH", "UNI", "LINK", "ATOM", "XLM", "VET", "FIL", "TRX", "ETC", "SHIB"],
            "commodities": ["GOLD", "SILVER", "OIL", "GAS", "COPPER", "WHEAT"],
            "forex": ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"]
        }
    
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock price"""
        symbol = symbol.upper()
        
        # Check cache first
        cache_key = f"stock_{symbol}_{datetime.now().strftime('%Y%m%d%H%M')}"
        cached_price = self.db.get_from_cache(cache_key)
        
        if cached_price:
            try:
                return json.loads(cached_price)
            except json.JSONDecodeError:
                pass
        
        # Try multiple APIs
        apis_to_try = [
            self._get_yahoo_finance_price,
            self._get_alpha_vantage_price,
            self._get_finnhub_price
        ]
        
        for api_func in apis_to_try:
            try:
                result = await api_func(symbol)
                if result["success"]:
                    # Cache for 5 minutes
                    self.db.add_to_cache(cache_key, json.dumps(result), 5)
                    return result
            except Exception as e:
                logger.warning(f"Stock API {api_func.__name__} failed: {e}")
                continue
        
        return {
            "success": False,
            "error": "All stock APIs failed",
            "symbol": symbol
        }
    
    async def _get_yahoo_finance_price(self, symbol: str) -> Dict[str, Any]:
        """Get stock price from Yahoo Finance"""
        url = f"{self.endpoints['yahoo_finance']}/{symbol}"
        params = {
            "range": "1d",
            "interval": "1m",
            "includePrePost": "true"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "chart" in data and "result" in data["chart"]:
                        result = data["chart"]["result"][0]
                        meta = result["meta"]
                        quote = result["indicators"]["quote"][0]
                        
                        # Get latest price
                        prices = quote["close"]
                        latest_price = next((p for p in reversed(prices) if p is not None), None)
                        
                        if latest_price:
                            return {
                                "success": True,
                                "symbol": symbol,
                                "price": latest_price,
                                "currency": meta.get("currency", "USD"),
                                "change": meta.get("regularMarketChange", 0),
                                "change_percent": meta.get("regularMarketChangePercent", 0),
                                "volume": meta.get("regularMarketVolume", 0),
                                "market_cap": meta.get("marketCap"),
                                "timestamp": datetime.now().isoformat(),
                                "source": "yahoo_finance"
                            }
        
        return {"success": False, "error": "Yahoo Finance API failed"}
    
    async def _get_alpha_vantage_price(self, symbol: str) -> Dict[str, Any]:
        """Get stock price from Alpha Vantage"""
        if not self.api_keys["alpha_vantage"]:
            return {"success": False, "error": "Alpha Vantage API key not configured"}
        
        url = self.endpoints["alpha_vantage"]
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_keys["alpha_vantage"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "Global Quote" in data:
                        quote = data["Global Quote"]
                        
                        return {
                            "success": True,
                            "symbol": symbol,
                            "price": float(quote["05. price"]),
                            "change": float(quote["09. change"]),
                            "change_percent": float(quote["10. change percent"].rstrip('%')),
                            "volume": int(quote["06. volume"]),
                            "timestamp": datetime.now().isoformat(),
                            "source": "alpha_vantage"
                        }
        
        return {"success": False, "error": "Alpha Vantage API failed"}
    
    async def _get_finnhub_price(self, symbol: str) -> Dict[str, Any]:
        """Get stock price from Finnhub"""
        if not self.api_keys["finnhub"]:
            return {"success": False, "error": "Finnhub API key not configured"}
        
        url = f"{self.endpoints['finnhub']}/quote"
        params = {
            "symbol": symbol,
            "token": self.api_keys["finnhub"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "c" in data:  # Current price
                        return {
                            "success": True,
                            "symbol": symbol,
                            "price": data["c"],
                            "change": data.get("d", 0),
                            "change_percent": data.get("dp", 0),
                            "high": data.get("h", 0),
                            "low": data.get("l", 0),
                            "open": data.get("o", 0),
                            "previous_close": data.get("pc", 0),
                            "timestamp": datetime.now().isoformat(),
                            "source": "finnhub"
                        }
        
        return {"success": False, "error": "Finnhub API failed"}
    
    async def get_crypto_price(self, symbol: str) -> Dict[str, Any]:
        """Get cryptocurrency price"""
        symbol = symbol.upper()
        
        # Check cache
        cache_key = f"crypto_{symbol}_{datetime.now().strftime('%Y%m%d%H%M')}"
        cached_price = self.db.get_from_cache(cache_key)
        
        if cached_price:
            try:
                return json.loads(cached_price)
            except json.JSONDecodeError:
                pass
        
        # Try multiple APIs (prioritize free APIs)
        apis_to_try = [
            self._get_binance_price,
            self._get_coingecko_price,
            self._get_kucoin_price,
            self._get_cryptingup_price,
            self._get_coinmarketcap_price
        ]
        
        for api_func in apis_to_try:
            try:
                result = await api_func(symbol)
                if result["success"]:
                    # Cache for 2 minutes
                    self.db.add_to_cache(cache_key, json.dumps(result), 2)
                    return result
            except Exception as e:
                logger.warning(f"Crypto API {api_func.__name__} failed: {e}")
                continue
        
        return {
            "success": False,
            "error": "All crypto APIs failed",
            "symbol": symbol
        }
    
    async def _get_coinmarketcap_price(self, symbol: str) -> Dict[str, Any]:
        """Get crypto price from CoinMarketCap"""
        if not self.api_keys["coinmarketcap"]:
            return {"success": False, "error": "CoinMarketCap API key not configured"}
        
        url = f"{self.endpoints['coinmarketcap']}/cryptocurrency/quotes/latest"
        headers = {
            "X-CMC_PRO_API_KEY": self.api_keys["coinmarketcap"],
            "Accept": "application/json"
        }
        params = {"symbol": symbol}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status", {}).get("error_code") == 0:
                        crypto_data = data["data"][symbol]
                        quote = crypto_data["quote"]["USD"]
                        
                        return {
                            "success": True,
                            "symbol": symbol,
                            "name": crypto_data["name"],
                            "price": quote["price"],
                            "change_24h": quote.get("percent_change_24h", 0),
                            "volume_24h": quote.get("volume_24h", 0),
                            "market_cap": quote.get("market_cap", 0),
                            "circulating_supply": crypto_data.get("circulating_supply", 0),
                            "max_supply": crypto_data.get("max_supply"),
                            "timestamp": datetime.now().isoformat(),
                            "source": "coinmarketcap"
                        }
        
        return {"success": False, "error": "CoinMarketCap API failed"}
    
    async def _get_binance_price(self, symbol: str, convert_to: str = "USDT") -> Dict[str, Any]:
        """Get crypto price from Binance API (free and fast)"""
        # Map symbols to Binance trading pairs
        symbol_map = {
            "BTC": "BTCUSDT", "ETH": "ETHUSDT", "BNB": "BNBUSDT",
            "XRP": "XRPUSDT", "ADA": "ADAUSDT", "SOL": "SOLUSDT",
            "DOT": "DOTUSDT", "DOGE": "DOGEUSDT", "AVAX": "AVAXUSDT",
            "MATIC": "MATICUSDT", "LTC": "LTCUSDT", "BCH": "BCHUSDT",
            "UNI": "UNIUSDT", "LINK": "LINKUSDT", "ATOM": "ATOMUSDT",
            "XLM": "XLMUSDT", "VET": "VETUSDT", "FIL": "FILUSDT",
            "TRX": "TRXUSDT", "ETC": "ETCUSDT", "SHIB": "SHIBUSDT"
        }
        
        trading_pair = symbol_map.get(symbol.upper())
        if not trading_pair:
            return {"success": False, "error": f"Symbol {symbol} not supported by Binance"}
        
        url = f"{self.endpoints['binance']}/ticker/price"
        params = {"symbol": trading_pair}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "symbol": symbol,
                        "price": float(data["price"]),
                        "currency": "USDT",
                        "trading_pair": trading_pair,
                        "timestamp": datetime.now().isoformat(),
                        "source": "binance"
                    }
        
        return {"success": False, "error": "Binance API failed"}
    
    async def _get_kucoin_price(self, symbol: str, convert_to: str = "USDT") -> Dict[str, Any]:
        """Get crypto price from KuCoin API (free alternative)"""
        # Map symbols to KuCoin trading pairs
        symbol_map = {
            "BTC": "BTC-USDT", "ETH": "ETH-USDT", "BNB": "BNB-USDT",
            "XRP": "XRP-USDT", "ADA": "ADA-USDT", "SOL": "SOL-USDT",
            "DOT": "DOT-USDT", "DOGE": "DOGE-USDT", "AVAX": "AVAX-USDT",
            "MATIC": "MATIC-USDT", "LTC": "LTC-USDT", "BCH": "BCH-USDT",
            "UNI": "UNI-USDT", "LINK": "LINK-USDT", "ATOM": "ATOM-USDT",
            "XLM": "XLM-USDT", "VET": "VET-USDT", "FIL": "FIL-USDT",
            "TRX": "TRX-USDT", "ETC": "ETC-USDT", "SHIB": "SHIB-USDT"
        }
        
        trading_pair = symbol_map.get(symbol.upper())
        if not trading_pair:
            return {"success": False, "error": f"Symbol {symbol} not supported by KuCoin"}
        
        url = f"{self.endpoints['kucoin']}/market/orderbook/level1"
        params = {"symbol": trading_pair}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("code") == "200000":  # KuCoin success code
                        order_data = data["data"]
                        
                        return {
                            "success": True,
                            "symbol": symbol,
                            "price": float(order_data["price"]),
                            "currency": "USDT",
                            "trading_pair": trading_pair,
                            "best_bid": float(order_data.get("bestBid", 0)),
                            "best_ask": float(order_data.get("bestAsk", 0)),
                            "timestamp": datetime.now().isoformat(),
                            "source": "kucoin"
                        }
        
        return {"success": False, "error": "KuCoin API failed"}
    
    async def _get_cryptingup_price(self, symbol: str, convert_to: str = "USD") -> Dict[str, Any]:
        """Get crypto price from CryptingUp API (free multi-exchange)"""
        url = f"{self.endpoints['cryptingup']}/markets"
        params = {"symbol": f"{symbol.upper()}-{convert_to.upper()}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "markets" in data and data["markets"]:
                        market = data["markets"][0]  # Get first market
                        
                        return {
                            "success": True,
                            "symbol": symbol,
                            "price": float(market["price"]),
                            "currency": convert_to,
                            "exchange": market.get("exchange", "Unknown"),
                            "volume_24h": float(market.get("volume_24h", 0)),
                            "change_24h": float(market.get("change_24h", 0)),
                            "timestamp": datetime.now().isoformat(),
                            "source": "cryptingup"
                        }
        
        return {"success": False, "error": "CryptingUp API failed"}
    
    async def _get_coingecko_price(self, symbol: str) -> Dict[str, Any]:
        """Get crypto price from CoinGecko (free API with comprehensive data)"""
        # Map symbols to CoinGecko IDs
        symbol_map = {
            "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin", 
            "XRP": "ripple", "ADA": "cardano", "SOL": "solana",
            "DOT": "polkadot", "DOGE": "dogecoin", "AVAX": "avalanche-2",
            "MATIC": "matic-network", "LTC": "litecoin", "BCH": "bitcoin-cash",
            "UNI": "uniswap", "LINK": "chainlink", "ATOM": "cosmos",
            "XLM": "stellar", "VET": "vechain", "FIL": "filecoin",
            "TRX": "tron", "ETC": "ethereum-classic", "SHIB": "shiba-inu"
        }
        
        coin_id = symbol_map.get(symbol.upper(), symbol.lower())
        
        url = f"{self.endpoints['coingecko']}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if coin_id in data:
                        crypto_data = data[coin_id]
                        
                        return {
                            "success": True,
                            "symbol": symbol,
                            "price": crypto_data["usd"],
                            "currency": "USD",
                            "market_cap": crypto_data.get("usd_market_cap"),
                            "volume_24h": crypto_data.get("usd_24h_vol"),
                            "percent_change_24h": crypto_data.get("usd_24h_change"),
                            "timestamp": datetime.now().isoformat(),
                            "source": "coingecko"
                        }
        
        return {"success": False, "error": "CoinGecko API failed"}
    
    async def get_multiple_crypto_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Get prices for multiple cryptocurrencies at once"""
        try:
            results = {}
            successful_count = 0
            
            # Use CoinGecko for multiple symbols (most efficient)
            symbol_map = {
                "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin", 
                "XRP": "ripple", "ADA": "cardano", "SOL": "solana",
                "DOT": "polkadot", "DOGE": "dogecoin", "AVAX": "avalanche-2",
                "MATIC": "matic-network", "LTC": "litecoin", "BCH": "bitcoin-cash",
                "UNI": "uniswap", "LINK": "chainlink", "ATOM": "cosmos",
                "XLM": "stellar", "VET": "vechain", "FIL": "filecoin",
                "TRX": "tron", "ETC": "ethereum-classic", "SHIB": "shiba-inu"
            }
            
            # Map symbols to CoinGecko IDs
            coin_ids = []
            symbol_to_id = {}
            for symbol in symbols:
                coin_id = symbol_map.get(symbol.upper(), symbol.lower())
                coin_ids.append(coin_id)
                symbol_to_id[coin_id] = symbol.upper()
            
            url = f"{self.endpoints['coingecko']}/simple/price"
            params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for coin_id, crypto_data in data.items():
                            symbol = symbol_to_id.get(coin_id, coin_id.upper())
                            results[symbol] = {
                                "success": True,
                                "symbol": symbol,
                                "price": crypto_data["usd"],
                                "currency": "USD",
                                "market_cap": crypto_data.get("usd_market_cap"),
                                "volume_24h": crypto_data.get("usd_24h_vol"),
                                "percent_change_24h": crypto_data.get("usd_24h_change"),
                                "timestamp": datetime.now().isoformat(),
                                "source": "coingecko"
                            }
                            successful_count += 1
            
            return {
                "success": True,
                "total_requested": len(symbols),
                "successful_count": successful_count,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting multiple crypto prices: {e}")
            return {
                "success": False,
                "error": f"Failed to get multiple crypto prices: {str(e)}",
                "symbols": symbols
            }
    
    async def get_top_crypto_prices(self, limit: int = 10) -> Dict[str, Any]:
        """Get top cryptocurrencies by market cap"""
        try:
            url = f"{self.endpoints['coingecko']}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": "false"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for coin in data:
                            results.append({
                                "rank": coin.get("market_cap_rank", 0),
                                "symbol": coin.get("symbol", "").upper(),
                                "name": coin.get("name", ""),
                                "price": coin.get("current_price", 0),
                                "market_cap": coin.get("market_cap", 0),
                                "volume_24h": coin.get("total_volume", 0),
                                "percent_change_24h": coin.get("price_change_percentage_24h", 0),
                                "timestamp": datetime.now().isoformat(),
                                "source": "coingecko"
                            })
                        
                        return {
                            "success": True,
                            "limit": limit,
                            "results": results,
                            "timestamp": datetime.now().isoformat()
                        }
            
            return {"success": False, "error": "Failed to get top crypto prices"}
            
        except Exception as e:
            logger.error(f"Error getting top crypto prices: {e}")
            return {
                "success": False,
                "error": f"Failed to get top crypto prices: {str(e)}"
            }
    
    async def get_commodity_price(self, commodity: str) -> Dict[str, Any]:
        """Get commodity price"""
        commodity = commodity.upper()
        
        # Check cache
        cache_key = f"commodity_{commodity}_{datetime.now().strftime('%Y%m%d%H%M')}"
        cached_price = self.db.get_from_cache(cache_key)
        
        if cached_price:
            try:
                return json.loads(cached_price)
            except json.JSONDecodeError:
                pass
        
        # Try Alpha Vantage for commodities
        if self.api_keys["alpha_vantage"]:
            try:
                result = await self._get_alpha_vantage_commodity(commodity)
                if result["success"]:
                    self.db.add_to_cache(cache_key, json.dumps(result), 10)
                    return result
            except Exception as e:
                logger.warning(f"Commodity API failed: {e}")
        
        return {
            "success": False,
            "error": "Commodity price not available",
            "commodity": commodity
        }
    
    async def _get_alpha_vantage_commodity(self, commodity: str) -> Dict[str, Any]:
        """Get commodity price from Alpha Vantage"""
        # Map commodity symbols to Alpha Vantage symbols
        commodity_map = {
            "GOLD": "GC=F",
            "SILVER": "SI=F",
            "OIL": "CL=F",
            "GAS": "NG=F",
            "COPPER": "HG=F",
            "WHEAT": "ZW=F"
        }
        
        symbol = commodity_map.get(commodity, commodity)
        
        url = self.endpoints["alpha_vantage"]
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_keys["alpha_vantage"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "Global Quote" in data:
                        quote = data["Global Quote"]
                        
                        return {
                            "success": True,
                            "commodity": commodity,
                            "symbol": symbol,
                            "price": float(quote["05. price"]),
                            "change": float(quote["09. change"]),
                            "change_percent": float(quote["10. change percent"].rstrip('%')),
                            "volume": int(quote["06. volume"]),
                            "timestamp": datetime.now().isoformat(),
                            "source": "alpha_vantage"
                        }
        
        return {"success": False, "error": "Alpha Vantage commodity API failed"}
    
    async def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary with major indices and crypto"""
        try:
            # Get major stock indices
            indices = ["^GSPC", "^DJI", "^IXIC", "^VIX"]  # S&P 500, Dow, NASDAQ, VIX
            index_prices = {}
            
            for index in indices:
                try:
                    price_data = await self._get_yahoo_finance_price(index)
                    if price_data["success"]:
                        index_prices[index] = price_data
                except Exception as e:
                    logger.warning(f"Failed to get {index}: {e}")
            
            # Get top crypto prices
            top_crypto = ["BTC", "ETH", "BNB", "XRP", "ADA"]
            crypto_prices = {}
            
            for crypto in top_crypto:
                try:
                    price_data = await self.get_crypto_price(crypto)
                    if price_data["success"]:
                        crypto_prices[crypto] = price_data
                except Exception as e:
                    logger.warning(f"Failed to get {crypto}: {e}")
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "indices": index_prices,
                "crypto": crypto_prices,
                "market_status": self._get_market_status()
            }
            
        except Exception as e:
            logger.error(f"Market summary error: {e}")
            return {
                "success": False,
                "error": f"Market summary failed: {str(e)}"
            }
    
    def _get_market_status(self) -> str:
        """Get current market status"""
        now = datetime.now()
        weekday = now.weekday()
        hour = now.hour
        
        # US market hours (9:30 AM - 4:00 PM EST, Monday-Friday)
        if weekday < 5 and 9.5 <= hour <= 16:
            return "Open"
        elif weekday < 5:
            return "Closed"
        else:
            return "Weekend"
    
    async def get_price_history(self, symbol: str, period: str = "1d") -> Dict[str, Any]:
        """Get historical price data"""
        symbol = symbol.upper()
        
        # Check cache
        cache_key = f"history_{symbol}_{period}_{datetime.now().strftime('%Y%m%d%H')}"
        cached_history = self.db.get_from_cache(cache_key)
        
        if cached_history:
            try:
                return json.loads(cached_history)
            except json.JSONDecodeError:
                pass
        
        # Try Yahoo Finance for historical data
        try:
            result = await self._get_yahoo_finance_history(symbol, period)
            if result["success"]:
                # Cache for 1 hour
                self.db.add_to_cache(cache_key, json.dumps(result), 60)
                return result
        except Exception as e:
            logger.warning(f"Historical data API failed: {e}")
        
        return {
            "success": False,
            "error": "Historical data not available",
            "symbol": symbol,
            "period": period
        }
    
    async def _get_yahoo_finance_history(self, symbol: str, period: str) -> Dict[str, Any]:
        """Get historical data from Yahoo Finance"""
        url = f"{self.endpoints['yahoo_finance']}/{symbol}"
        params = {
            "range": period,
            "interval": "1d" if period in ["1mo", "3mo", "6mo", "1y", "2y", "5y"] else "1m",
            "includePrePost": "true"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "chart" in data and "result" in data["chart"]:
                        result = data["chart"]["result"][0]
                        timestamps = result["timestamp"]
                        quotes = result["indicators"]["quote"][0]
                        
                        # Process historical data
                        history = []
                        for i, timestamp in enumerate(timestamps):
                            if quotes["close"][i] is not None:
                                history.append({
                                    "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
                                    "open": quotes["open"][i],
                                    "high": quotes["high"][i],
                                    "low": quotes["low"][i],
                                    "close": quotes["close"][i],
                                    "volume": quotes["volume"][i]
                                })
                        
                        return {
                            "success": True,
                            "symbol": symbol,
                            "period": period,
                            "history": history,
                            "data_points": len(history),
                            "source": "yahoo_finance"
                        }
        
        return {"success": False, "error": "Yahoo Finance history API failed"}
    
    def format_price_result(self, result: Dict[str, Any]) -> str:
        """Format price result for display"""
        if not result["success"]:
            return f"❌ {result['error']}"
        
        if "symbol" in result:
            symbol = result["symbol"]
            price = result["price"]
            change = result.get("change", result.get("percent_change_24h", 0))
            change_percent = result.get("change_percent", result.get("percent_change_24h", 0))
            
            # Format change with appropriate emoji
            change_emoji = "📈" if change >= 0 else "📉"
            change_sign = "+" if change >= 0 else ""
            
            output = f"💰 **{symbol}**\n"
            output += f"💵 قیمت: ${price:.2f}\n"
            
            if change != 0:
                output += f"{change_emoji} تغییر 24h: {change_sign}{change:.2f}% ({change_sign}{change_percent:.2f}%)\n"
            
            if "volume" in result or "volume_24h" in result:
                volume = result.get("volume", result.get("volume_24h", 0))
                output += f"📊 حجم 24h: ${volume:,.0f}\n"
            
            if "market_cap" in result:
                market_cap = result["market_cap"]
                if market_cap:
                    output += f"🏢 ارزش بازار: ${market_cap:,.0f}\n"
            
            if "trading_pair" in result:
                output += f"🔄 جفت معاملاتی: {result['trading_pair']}\n"
            
            if "exchange" in result:
                output += f"🏪 صرافی: {result['exchange']}\n"
            
            if "rank" in result:
                output += f"🏆 رتبه: #{result['rank']}\n"
            
            output += f"🕐 زمان: {result['timestamp']}\n"
            output += f"🔗 منبع: {result['source']}"
            
            return output
        
        return "❌ Invalid price result format"
    
    def get_supported_crypto_symbols(self) -> List[str]:
        """Get list of supported cryptocurrency symbols"""
        return [
            "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE", 
            "AVAX", "MATIC", "LTC", "BCH", "UNI", "LINK", "ATOM", 
            "XLM", "VET", "FIL", "TRX", "ETC", "SHIB"
        ]
    
    def format_multiple_crypto_results(self, result: Dict[str, Any]) -> str:
        """Format multiple crypto prices for display"""
        if not result["success"]:
            return f"❌ {result['error']}"
        
        output = f"💰 **قیمت‌های ارزهای دیجیتال**\n\n"
        output += f"📊 تعداد درخواستی: {result['total_requested']}\n"
        output += f"✅ تعداد موفق: {result['successful_count']}\n\n"
        
        for symbol, data in result["results"].items():
            if data["success"]:
                price = data["price"]
                change = data.get("percent_change_24h", 0)
                change_emoji = "📈" if change >= 0 else "📉"
                change_sign = "+" if change >= 0 else ""
                
                output += f"**{symbol}**: ${price:.2f} {change_emoji} {change_sign}{change:.2f}%\n"
        
        output += f"\n🕐 زمان: {result['timestamp']}"
        
        return output
    
    def format_top_crypto_results(self, result: Dict[str, Any]) -> str:
        """Format top crypto prices for display"""
        if not result["success"]:
            return f"❌ {result['error']}"
        
        output = f"🏆 **برترین ارزهای دیجیتال** (بر اساس ارزش بازار)\n\n"
        
        for i, crypto in enumerate(result["results"], 1):
            symbol = crypto["symbol"]
            name = crypto["name"]
            price = crypto["price"]
            change = crypto["percent_change_24h"]
            rank = crypto["rank"]
            
            change_emoji = "📈" if change >= 0 else "📉"
            change_sign = "+" if change >= 0 else ""
            
            output += f"{i}. **{symbol}** ({name})\n"
            output += f"   💵 قیمت: ${price:.2f}\n"
            output += f"   {change_emoji} تغییر: {change_sign}{change:.2f}%\n"
            output += f"   🏆 رتبه: #{rank}\n\n"
        
        output += f"🕐 زمان: {result['timestamp']}"
        
        return output
    
    # New methods for integrated price sources
    
    async def get_integrated_price_data(self) -> Dict[str, Any]:
        """Get comprehensive price data from all sources"""
        try:
            # Get data from all sources concurrently
            tasks = [
                self._get_binance_popular_data(),
                self._get_tgju_data(),
                self._get_crypto_irr_data()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            binance_data, tgju_data, crypto_irr_data = results
            
            # Handle exceptions
            if isinstance(binance_data, Exception):
                binance_data = {"success": False, "error": str(binance_data)}
            if isinstance(tgju_data, Exception):
                tgju_data = {"success": False, "error": str(tgju_data)}
            if isinstance(crypto_irr_data, Exception):
                crypto_irr_data = {"success": False, "error": str(crypto_irr_data)}
            
            return {
                "success": True,
                "binance_popular": binance_data,
                "tgju_assets": tgju_data,
                "crypto_irr": crypto_irr_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in get_integrated_price_data: {e}")
            return {
                "success": False,
                "error": f"Failed to get integrated price data: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_binance_popular_data(self) -> Dict[str, Any]:
        """Get popular crypto data from Binance/CoinGecko"""
        try:
            # Check cache first
            cache_key = f"binance_popular_{datetime.now().strftime('%Y%m%d%H%M')}"
            cached_data = self.db.get_from_cache(cache_key)
            
            if cached_data:
                try:
                    return json.loads(cached_data)
                except json.JSONDecodeError:
                    pass
            
            # Get fresh data
            result = get_popular_data()
            
            if result["success"]:
                # Cache for 5 minutes
                self.db.add_to_cache(cache_key, json.dumps(result), 5)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting Binance popular data: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_tgju_data(self) -> Dict[str, Any]:
        """Get TGJU asset data"""
        try:
            # Check cache first
            cache_key = f"tgju_assets_{datetime.now().strftime('%Y%m%d%H%M')}"
            cached_data = self.db.get_from_cache(cache_key)
            
            if cached_data:
                try:
                    return json.loads(cached_data)
                except json.JSONDecodeError:
                    pass
            
            # Get fresh data
            result = fetch_mofid_basket()
            
            if result["success"]:
                # Cache for 10 minutes
                self.db.add_to_cache(cache_key, json.dumps(result), 10)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting TGJU data: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_crypto_irr_data(self) -> Dict[str, Any]:
        """Get crypto prices in IRR from TGJU"""
        try:
            # Check cache first
            cache_key = f"crypto_irr_{datetime.now().strftime('%Y%m%d%H%M')}"
            cached_data = self.db.get_from_cache(cache_key)
            
            if cached_data:
                try:
                    return json.loads(cached_data)
                except json.JSONDecodeError:
                    pass
            
            # Get fresh data
            result = fetch_top_cryptos(limit=10)
            
            if result["success"]:
                # Cache for 5 minutes
                self.db.add_to_cache(cache_key, json.dumps(result), 5)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting crypto IRR data: {e}")
            return {"success": False, "error": str(e)}
    
    def format_integrated_price_message(self, data: Dict[str, Any]) -> str:
        """Format comprehensive price message"""
        if not data["success"]:
            return f"❌ {data['error']}"
        
        message = "📈 **قیمت‌های لحظه‌ای جامع**\n\n"
        
        # Binance Popular (USD)
        binance_data = data["binance_popular"]
        if binance_data["success"] and binance_data.get("popular"):
            message += "💰 **ارزهای دیجیتال محبوب (USD)**:\n"
            for coin in binance_data["popular"]:
                change_emoji = "📈" if coin["change_percent_24h"] >= 0 else "📉"
                change_sign = "+" if coin["change_percent_24h"] >= 0 else ""
                message += (
                    f"• {coin['name']} ({coin['symbol']}): ${coin['price_usd']:,.2f} "
                    f"{change_emoji} {change_sign}{coin['change_percent_24h']:.2f}%\n"
                )
            message += "\n"
        
        # TGJU Assets (IRR)
        tgju_data = data["tgju_assets"]
        if tgju_data["success"] and tgju_data.get("data"):
            message += "🏦 **دارایی‌ها (IRR)**:\n"
            for title, asset_data in tgju_data["data"].items():
                price = asset_data["price"]
                change = asset_data["change"]
                if price is not None:
                    message += f"• {title}: {price:,.0f} ({change})\n"
                else:
                    message += f"• {title}: نامشخص ({change})\n"
            message += "\n"
        
        # Crypto IRR
        crypto_irr_data = data["crypto_irr"]
        if crypto_irr_data["success"] and crypto_irr_data.get("data"):
            message += "🌐 **ارزهای دیجیتال (IRR)**:\n"
            for name, crypto_data in crypto_irr_data["data"].items():
                price = crypto_data["price_rial"]
                change_percent = crypto_data["change_percent"]
                change_value = crypto_data["change_value_tether"]
                
                if price is not None:
                    change_emoji = "📈" if change_percent and change_percent >= 0 else "📉"
                    change_sign = "+" if change_percent and change_percent >= 0 else ""
                    change_text = f"{change_sign}{change_percent:.2f}%" if change_percent is not None else "نامشخص"
                    message += f"• {name}: {price:,.0f} {change_emoji} {change_text} ({change_value})\n"
                else:
                    message += f"• {name}: نامشخص ({change_value})\n"
        
        message += f"\n🕐 زمان: {data['timestamp']}"
        return message
    
    def create_price_selection_keyboard(self):
        """Create keyboard for price source selection"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("💰 ارزهای دیجیتال (USD)", callback_data="price_crypto_usd"),
                InlineKeyboardButton("🌐 ارزهای دیجیتال (IRR)", callback_data="price_crypto_irr")
            ],
            [
                InlineKeyboardButton("🏦 دارایی‌ها (TGJU)", callback_data="price_tgju"),
                InlineKeyboardButton("📊 همه قیمت‌ها", callback_data="price_all")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
