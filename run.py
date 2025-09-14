#!/usr/bin/env python3
"""
🚀 Run Bot - اجرای ربات
فایل ساده برای اجرای ربات تبدیلا
"""

import sys
import os
import logging

# اضافه کردن مسیر فعلی به Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """بررسی وابستگی‌ها"""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'telegram',
        'requests',
        'jdatetime',
        'hijridate',
        'babel'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module}")
    
    if missing_modules:
        print(f"\n⚠️ Missing modules: {', '.join(missing_modules)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are available!")
    return True

def check_config():
    """بررسی تنظیمات"""
    print("\n🔧 Checking configuration...")
    
    try:
        from config import Config
        
        if not Config.BOT_TOKEN or Config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("❌ Bot token not set!")
            print("Please set your bot token in config.py")
            return False
        
        print("✅ Bot token is set")
        
        if not Config.ADMIN_USER_IDS:
            print("⚠️ No admin users configured")
            print("Add your Telegram user ID to ADMIN_USER_IDS in config.py")
        else:
            print(f"✅ Admin users configured: {len(Config.ADMIN_USER_IDS)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Config error: {e}")
        return False

def main():
    """تابع اصلی"""
    print("🤖 Telegram Bot Launcher")
    print("=" * 40)
    
    # بررسی وابستگی‌ها
    if not check_dependencies():
        sys.exit(1)
    
    # بررسی تنظیمات
    if not check_config():
        sys.exit(1)
    
    print("\n🚀 Starting bot...")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        # اجرای ربات
        from main import main as run_bot
        run_bot()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

