"""
Binance Popular Cryptocurrency Prices
Fetches popular cryptocurrency prices from CoinGecko API
"""

import requests
import json
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class BinancePopular:
    """Class to fetch popular cryptocurrency prices from CoinGecko"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.popular_coins = [
            {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
            {"id": "ethereum", "symbol": "ETH", "name": "Ethereum"},
            {"id": "binancecoin", "symbol": "BNB", "name": "Binance Coin"},
            {"id": "ripple", "symbol": "XRP", "name": "XRP"},
            {"id": "solana", "symbol": "SOL", "name": "Solana"}
        ]
    
    def get_popular_data(self) -> Dict[str, Any]:
        """Get popular cryptocurrency prices from CoinGecko"""
        try:
            # Prepare coin IDs for API call
            coin_ids = [coin["id"] for coin in self.popular_coins]
            
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Format the data
            popular_coins = []
            for coin_info in self.popular_coins:
                coin_id = coin_info["id"]
                if coin_id in data:
                    coin_data = data[coin_id]
                    popular_coins.append({
                        "symbol": coin_info["symbol"],
                        "name": coin_info["name"],
                        "price_usd": coin_data.get("usd", 0),
                        "change_percent_24h": coin_data.get("usd_24h_change", 0),
                        "market_cap": coin_data.get("usd_market_cap", 0),
                        "volume_24h": coin_data.get("usd_24h_vol", 0),
                        "image": f"https://cryptologos.cc/logos/{coin_info['name'].lower().replace(' ', '-')}-{coin_info['symbol'].lower()}-logo.png"
                    })
            
            return {
                "success": True,
                "status": "success",
                "popular": popular_coins,
                "timestamp": datetime.now().isoformat(),
                "source": "coingecko"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error in get_popular_data: {e}")
            return {
                "success": False,
                "status": "error",
                "error": f"Network error: {str(e)}",
                "popular": [],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error in get_popular_data: {e}")
            return {
                "success": False,
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "popular": [],
                "timestamp": datetime.now().isoformat()
            }

def get_popular_data() -> Dict[str, Any]:
    """Convenience function to get popular cryptocurrency data"""
    binance_popular = BinancePopular()
    return binance_popular.get_popular_data()

if __name__ == "__main__":
    # Test the function
    result = get_popular_data()
    print(json.dumps(result, indent=2, ensure_ascii=False))
