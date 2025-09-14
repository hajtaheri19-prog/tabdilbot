#!/usr/bin/env python3
"""
Test script for the enhanced crypto price APIs
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from price_tracker import PriceTracker

async def test_crypto_apis():
    """Test the new crypto APIs"""
    print("🚀 Testing Enhanced Crypto Price APIs")
    print("=" * 50)
    
    # Initialize database and price tracker
    db = Database()
    tracker = PriceTracker(db)
    
    # Test symbols
    test_symbols = ["BTC", "ETH", "DOGE", "SHIB"]
    
    print("\n1️⃣ Testing Single Crypto Price (BTC):")
    print("-" * 40)
    try:
        result = await tracker.get_crypto_price("BTC")
        if result["success"]:
            print(f"✅ Success: {result['symbol']} = ${result['price']:.2f}")
            print(f"📊 Source: {result['source']}")
            print(f"📈 Change 24h: {result.get('percent_change_24h', 0):.2f}%")
        else:
            print(f"❌ Failed: {result['error']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n2️⃣ Testing Multiple Crypto Prices:")
    print("-" * 40)
    try:
        result = await tracker.get_multiple_crypto_prices(test_symbols)
        if result["success"]:
            print(f"✅ Success: {result['successful_count']}/{result['total_requested']} symbols")
            for symbol, data in result["results"].items():
                if data["success"]:
                    print(f"  {symbol}: ${data['price']:.2f} ({data['source']})")
        else:
            print(f"❌ Failed: {result['error']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n3️⃣ Testing Top Crypto Prices:")
    print("-" * 40)
    try:
        result = await tracker.get_top_crypto_prices(5)
        if result["success"]:
            print(f"✅ Success: Top {len(result['results'])} cryptocurrencies")
            for i, crypto in enumerate(result["results"], 1):
                print(f"  {i}. {crypto['symbol']}: ${crypto['price']:.2f} (Rank #{crypto['rank']})")
        else:
            print(f"❌ Failed: {result['error']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n4️⃣ Testing Supported Symbols:")
    print("-" * 40)
    try:
        symbols = tracker.get_supported_crypto_symbols()
        print(f"✅ Supported symbols: {len(symbols)}")
        print(f"📋 Symbols: {', '.join(symbols[:10])}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n5️⃣ Testing Different APIs:")
    print("-" * 40)
    apis_to_test = [
        ("Binance", tracker._get_binance_price),
        ("CoinGecko", tracker._get_coingecko_price),
        ("KuCoin", tracker._get_kucoin_price),
        ("CryptingUp", tracker._get_cryptingup_price)
    ]
    
    for api_name, api_func in apis_to_test:
        try:
            result = await api_func("BTC")
            if result["success"]:
                print(f"✅ {api_name}: ${result['price']:.2f}")
            else:
                print(f"❌ {api_name}: {result['error']}")
        except Exception as e:
            print(f"❌ {api_name}: Error - {e}")
    
    print("\n🎉 Test completed!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_crypto_apis())

