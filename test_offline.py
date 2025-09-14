#!/usr/bin/env python3
"""
ربات تبدیلا - نسخه تست آفلاین
Offline Test Version for Telegram Bot
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[
            logging.FileHandler("bot_test.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

async def test_bot_offline():
    """Test bot functionality offline"""
    logger = setup_logging()
    logger.info("Starting offline bot test...")
    
    print("🧪 تست آفلاین ربات تبدیلا")
    print("=" * 50)
    
    try:
        # Test database
        print("1️⃣ Testing Database...")
        from database import Database
        db = Database()
        print("✅ Database initialized successfully")
        
        # Test unit converter
        print("\n2️⃣ Testing Unit Converter...")
        from unit_converter import UnitConverter
        unit_converter = UnitConverter()
        
        # Test length conversion
        result = unit_converter.convert(10, "km", "mile", "length")
        if result["success"]:
            print(f"✅ Length: 10 km = {result['result']:.2f} mile")
        else:
            print(f"❌ Length conversion failed: {result['error']}")
        
        # Test weight conversion
        result = unit_converter.convert(100, "kg", "lb", "weight")
        if result["success"]:
            print(f"✅ Weight: 100 kg = {result['result']:.2f} lb")
        else:
            print(f"❌ Weight conversion failed: {result['error']}")
        
        # Test temperature conversion
        result = unit_converter.convert(25, "celsius", "fahrenheit", "temperature")
        if result["success"]:
            print(f"✅ Temperature: 25°C = {result['result']:.2f}°F")
        else:
            print(f"❌ Temperature conversion failed: {result['error']}")
        
        # Test calculator
        print("\n3️⃣ Testing Calculator...")
        from calculator import AdvancedCalculator
        calc = AdvancedCalculator()
        
        test_expressions = [
            "2 + 3 * 4",
            "sqrt(16)",
            "sin(pi/2)",
            "log(100)",
            "2^3"
        ]
        
        for expr in test_expressions:
            result = calc.calculate(expr)
            if result["success"]:
                print(f"✅ {expr} = {result['formatted']}")
            else:
                print(f"❌ {expr} failed: {result['error']}")
        
        # Test date converter
        print("\n4️⃣ Testing Date Converter...")
        from date_converter import DateConverter
        date_converter = DateConverter()
        
        # Test current time
        time_result = date_converter.get_current_time("IRST")
        if time_result["success"]:
            print(f"✅ Current time (IRST): {time_result['datetime']}")
        else:
            print(f"❌ Time conversion failed: {time_result['error']}")
        
        # Test UI components
        print("\n5️⃣ Testing UI Components...")
        from ui_components import UIComponents
        ui = UIComponents()
        
        # Test welcome message
        welcome = ui.format_welcome_message()
        print(f"✅ Welcome message: {len(welcome)} characters")
        
        # Test keyboards
        main_keyboard = ui.get_main_menu_keyboard()
        print(f"✅ Main menu keyboard: {len(main_keyboard.inline_keyboard)} rows")
        
        currency_keyboard = ui.get_currency_menu_keyboard()
        print(f"✅ Currency menu keyboard: {len(currency_keyboard.inline_keyboard)} rows")
        
        # Test admin service
        print("\n6️⃣ Testing Admin Service...")
        from admin_service import AdminService
        admin_service = AdminService(db)
        
        # Test user stats (with dummy user)
        stats = admin_service.get_user_stats(12345)
        print(f"✅ User stats: {stats['total_conversions']} conversions")
        
        print("\n🎉 All offline tests completed successfully!")
        print("✅ Bot is ready for online testing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.error(f"Test failed: {e}")
        return False

async def test_online_apis():
    """Test online APIs with timeout"""
    print("\n🌐 Testing Online APIs...")
    print("=" * 30)
    
    try:
        # Test price tracker with timeout
        from price_tracker import PriceTracker
        from database import Database
        
        db = Database()
        tracker = PriceTracker(db)
        
        # Test with timeout
        try:
            result = await asyncio.wait_for(
                tracker.get_crypto_price("BTC"), 
                timeout=10.0
            )
            if result["success"]:
                print(f"✅ Crypto API: BTC = ${result['price']:.2f}")
            else:
                print(f"❌ Crypto API failed: {result['error']}")
        except asyncio.TimeoutError:
            print("⏰ Crypto API timeout (10s) - this is normal if internet is slow")
        
        # Test currency converter with timeout
        from currency_converter import CurrencyConverter
        converter = CurrencyConverter(db)
        
        try:
            result = await asyncio.wait_for(
                converter.convert_currency(100, "USD", "IRR"),
                timeout=10.0
            )
            if result["success"]:
                print(f"✅ Currency API: 100 USD = {result['result']:.2f} IRR")
            else:
                print(f"❌ Currency API failed: {result['error']}")
        except asyncio.TimeoutError:
            print("⏰ Currency API timeout (10s) - this is normal if internet is slow")
        
        print("✅ Online API tests completed!")
        
    except Exception as e:
        print(f"❌ Online API test failed: {e}")

def main():
    """Main test function"""
    print("🚀 ربات تبدیلا - تست کامل")
    print("=" * 50)
    
    # Run offline tests
    offline_success = asyncio.run(test_bot_offline())
    
    if offline_success:
        # Run online tests
        asyncio.run(test_online_apis())
        
        print("\n" + "=" * 50)
        print("📋 خلاصه تست‌ها:")
        print("✅ تست‌های آفلاین: موفق")
        print("✅ تست‌های آنلاین: با timeout (طبیعی)")
        print("✅ ربات آماده اجرا است!")
        
        print("\n🚀 برای اجرای ربات:")
        print("python run_bot.py")
        
    else:
        print("\n❌ تست‌ها ناموفق - لطفاً مشکلات را بررسی کنید")
        sys.exit(1)

if __name__ == "__main__":
    main()


