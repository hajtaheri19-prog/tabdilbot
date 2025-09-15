"""
Crypto Prices Scraper
Fetches cryptocurrency prices from TGJU crypto page
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class CryptoPriceScraper:
    """Class to scrape cryptocurrency prices from TGJU crypto page"""
    
    def __init__(self):
        self.crypto_url = "https://www.tgju.org/crypto"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _clean_price(self, price_text: str) -> Optional[float]:
        """Clean and convert price text to float"""
        if not price_text:
            return None
        
        try:
            # Remove commas, spaces, and convert to float
            cleaned = price_text.replace(",", "").replace("٬", "").replace(" ", "").strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def _clean_change_percent(self, change_text: str) -> Optional[float]:
        """Clean and convert change percentage to float"""
        if not change_text:
            return None
        
        try:
            # Remove % sign and convert to float
            cleaned = change_text.replace("%", "").replace("٪", "").strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def fetch_top_cryptos(self, limit: int = 10) -> Dict[str, Any]:
        """Fetch top cryptocurrency prices from TGJU crypto page"""
        try:
            response = requests.get(self.crypto_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find crypto table or list
            crypto_data = {}
            
            # Look for crypto price elements
            crypto_elements = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'crypto|coin|price'))
            
            if not crypto_elements:
                # Try alternative selectors
                crypto_elements = soup.find_all('div', {'data-symbol': True})
            
            count = 0
            for element in crypto_elements:
                if count >= limit:
                    break
                
                try:
                    # Extract crypto name
                    name_element = element.find(['span', 'div', 'td'], class_=re.compile(r'name|title|symbol'))
                    if not name_element:
                        name_element = element.find('a')
                    
                    if name_element:
                        crypto_name = name_element.get_text(strip=True)
                        
                        # Extract price in IRR
                        price_element = element.find(['span', 'div', 'td'], class_=re.compile(r'price|value'))
                        price_text = price_element.get_text(strip=True) if price_element else None
                        price_rial = self._clean_price(price_text)
                        
                        # Extract change percentage
                        change_element = element.find(['span', 'div', 'td'], class_=re.compile(r'change|percent'))
                        change_text = change_element.get_text(strip=True) if change_element else None
                        change_percent = self._clean_change_percent(change_text)
                        
                        # Extract change value in Tether
                        change_value_element = element.find(['span', 'div', 'td'], class_=re.compile(r'change.*value|tether'))
                        change_value_tether = change_value_element.get_text(strip=True) if change_value_element else "نامشخص"
                        
                        if crypto_name and price_rial is not None:
                            crypto_data[crypto_name] = {
                                "price_rial": price_rial,
                                "change_percent": change_percent,
                                "change_value_tether": change_value_tether,
                                "raw_price": price_text,
                                "raw_change": change_text
                            }
                            count += 1
                
                except Exception as e:
                    logger.error(f"Error processing crypto element: {e}")
                    continue
            
            # If no crypto data found, try to find any price elements
            if not crypto_data:
                logger.warning("No crypto data found, trying alternative approach")
                # Look for any elements with price-like content
                price_elements = soup.find_all(text=re.compile(r'[\d,]+'))
                for i, price_text in enumerate(price_elements[:limit]):
                    if price_text.strip():
                        crypto_data[f"ارز دیجیتال {i+1}"] = {
                            "price_rial": self._clean_price(price_text.strip()),
                            "change_percent": None,
                            "change_value_tether": "نامشخص",
                            "raw_price": price_text.strip(),
                            "raw_change": None
                        }
            
            return {
                "success": True,
                "status": "success",
                "data": crypto_data,
                "count": len(crypto_data),
                "limit": limit,
                "timestamp": datetime.now().isoformat(),
                "source": "tgju.org/crypto"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error in fetch_top_cryptos: {e}")
            return {
                "success": False,
                "status": "error",
                "error": f"Network error: {str(e)}",
                "data": {},
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error in fetch_top_cryptos: {e}")
            return {
                "success": False,
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "data": {},
                "timestamp": datetime.now().isoformat()
            }

def fetch_top_cryptos(limit: int = 10) -> Dict[str, Any]:
    """Convenience function to fetch top cryptocurrencies from TGJU"""
    scraper = CryptoPriceScraper()
    return scraper.fetch_top_cryptos(limit)

if __name__ == "__main__":
    # Test the function
    result = fetch_top_cryptos(5)
    print(json.dumps(result, indent=2, ensure_ascii=False))
