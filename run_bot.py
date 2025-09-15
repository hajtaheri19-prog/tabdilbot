#!/usr/bin/env python3
"""
ربات تبدیلا - نسخه نهایی و بهبود یافته
Advanced Telegram Bot - Final Improved Version
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
            logging.FileHandler("bot.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        "telegram", "requests", "aiohttp", "jdatetime", 
        "hijridate", "babel", "pytz"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing dependencies: {', '.join(missing_modules)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main function to run the bot"""
    print("🚀 ربات تبدیلا - نسخه بهبود یافته")
    print("=" * 50)
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Telegram Bot...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Import bot modules
        from simple_bot import SimpleTelegramBot
        
        print("✅ Dependencies loaded successfully")
        print("✅ Bot modules imported successfully")
        print("🔄 Starting bot...")
        
        # Create and run bot
        bot = SimpleTelegramBot()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        logger.info("Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()















