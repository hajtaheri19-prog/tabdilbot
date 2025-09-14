#!/usr/bin/env python3
"""
Quick test to verify bot functionality
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from price_tracker import PriceTracker
from currency_converter import CurrencyConverter
from unit_converter import UnitConverter
from calculator import AdvancedCalculator

async def test_basic_functionality():
    """Test basic bot functionality"""
    print("🧪 Testing Basic Bot Functionality")
    print("=" * 50)
    
    try:
        # Test database
        print("1️⃣ Testing Database...")
        db = Database()
        print("✅ Database initialized successfully")
        
        # Test price tracker
        print("\n2️⃣ Testing Price Tracker...")
        tracker = PriceTracker(db)
        result = await tracker.get_crypto_price("BTC")
        if result["success"]:
            print(f"✅ Crypto price: BTC = ${result['price']:.2f}")
        else:
            print(f"❌ Crypto price failed: {result['error']}")
        
        # Test currency converter
        print("\n3️⃣ Testing Currency Converter...")
        converter = CurrencyConverter(db)
        result = await converter.convert_currency(100, "USD", "IRR")
        if result["success"]:
            print(f"✅ Currency conversion: 100 USD = {result['result']:.2f} IRR")
        else:
            print(f"❌ Currency conversion failed: {result['error']}")
        
        # Test unit converter
        print("\n4️⃣ Testing Unit Converter...")
        unit_converter = UnitConverter()
        result = unit_converter.convert(10, "km", "mile", "length")
        if result["success"]:
            print(f"✅ Unit conversion: 10 km = {result['result']:.2f} mile")
        else:
            print(f"❌ Unit conversion failed: {result['error']}")
        
        # Test calculator
        print("\n5️⃣ Testing Calculator...")
        calc = AdvancedCalculator()
        result = calc.calculate("2 + 3 * 4")
        if result["success"]:
            print(f"✅ Calculation: 2 + 3 * 4 = {result['formatted']}")
        else:
            print(f"❌ Calculation failed: {result['error']}")
        
        print("\n🎉 All basic tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    if success:
        print("\n✅ Bot is ready to run!")
    else:
        print("\n❌ Bot has issues that need to be fixed.")
        sys.exit(1)


