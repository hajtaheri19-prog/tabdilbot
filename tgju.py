"""
TGJU Price Scraper
Fetches various asset prices from tgju.org website
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class TGJUPriceScraper:
    """Class to scrape prices from tgju.org"""
    
    def __init__(self):
        self.base_url = "https://www.tgju.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Mapping of asset names to their selectors
        self.asset_selectors = {
            "دلار": "l-price_dollar_rl",
            "یورو": "l-price_eur", 
            "پوند": "l-price_gbp",
            "تتر": "l-crypto-tether-irr",
            "بیت کوین": "l-crypto-bitcoin",
            "طلا": "l-price_ounce",
            "سکه": "l-price_coin",
            "نقره": "l-price_silver"
        }
    
    def _clean_price(self, price_text: str) -> Optional[float]:
        """Clean and convert price text to float"""
        if not price_text:
            return None
        
        # Remove commas and convert to float
        try:
            cleaned = price_text.replace(",", "").replace("٬", "").strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def _clean_change(self, change_text: str) -> str:
        """Clean change text"""
        if not change_text:
            return "نامشخص"
        return change_text.strip()
    
    def fetch_mofid_basket(self) -> Dict[str, Any]:
        """Fetch various asset prices from TGJU"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {}
            
            for asset_name, selector in self.asset_selectors.items():
                try:
                    # Find the element by ID
                    element = soup.find(id=selector)
                    if element:
                        # Extract price
                        price_element = element.find(class_="info-price")
                        price_text = price_element.get_text(strip=True) if price_element else None
                        price = self._clean_price(price_text)
                        
                        # Extract change
                        change_element = element.find(class_="info-change")
                        change_text = change_element.get_text(strip=True) if change_element else None
                        change = self._clean_change(change_text)
                        
                        data[asset_name] = {
                            "price": price,
                            "change": change,
                            "raw_price": price_text,
                            "raw_change": change_text
                        }
                    else:
                        logger.warning(f"Element not found for {asset_name} with selector {selector}")
                        data[asset_name] = {
                            "price": None,
                            "change": "نامشخص",
                            "raw_price": None,
                            "raw_change": None
                        }
                        
                except Exception as e:
                    logger.error(f"Error processing {asset_name}: {e}")
                    data[asset_name] = {
                        "price": None,
                        "change": "خطا",
                        "raw_price": None,
                        "raw_change": None
                    }
            
            return {
                "success": True,
                "status": "success",
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "source": "tgju.org"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error in fetch_mofid_basket: {e}")
            return {
                "success": False,
                "status": "error",
                "error": f"Network error: {str(e)}",
                "data": {},
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error in fetch_mofid_basket: {e}")
            return {
                "success": False,
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "data": {},
                "timestamp": datetime.now().isoformat()
            }

def fetch_mofid_basket() -> Dict[str, Any]:
    """Convenience function to fetch TGJU basket data"""
    scraper = TGJUPriceScraper()
    return scraper.fetch_mofid_basket()

if __name__ == "__main__":
    # Test the function
    result = fetch_mofid_basket()
    print(json.dumps(result, indent=2, ensure_ascii=False))
