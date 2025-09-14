#!/usr/bin/env python3
"""
Setup script for Advanced Telegram Bot
This script helps with initial setup and configuration
"""

import os
import sys
import sqlite3
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_config():
    """Create configuration file if it doesn't exist"""
    config_file = Path("config.py")
    if config_file.exists():
        print("✅ Configuration file already exists")
        return True
    
    print("⚙️ Creating configuration file...")
    
    bot_token = input("Enter your Telegram bot token: ").strip()
    if not bot_token:
        print("❌ Bot token is required!")
        return False
    
    # Optional API keys
    openweather_key = input("Enter OpenWeather API key (optional): ").strip()
    alpha_vantage_key = input("Enter Alpha Vantage API key (optional): ").strip()
    coinmarketcap_key = input("Enter CoinMarketCap API key (optional): ").strip()
    google_translate_key = input("Enter Google Translate API key (optional): ").strip()
    
    admin_user_id = input("Enter your Telegram user ID for admin access (optional): ").strip()
    
    config_content = f'''import os
from typing import Dict, Any

class Config:
    """Configuration settings for the bot"""
    
    # Bot token
    BOT_TOKEN = "{bot_token}"
    
    # Database settings
    DATABASE_URL = "sqlite:///bot.db"
    
    # API Keys
    OPENWEATHER_API_KEY = "{openweather_key}"
    ALPHA_VANTAGE_API_KEY = "{alpha_vantage_key}"
    COINMARKETCAP_API_KEY = "{coinmarketcap_key}"
    GOOGLE_TRANSLATE_API_KEY = "{google_translate_key}"
    
    # Supported currencies
    SUPPORTED_CURRENCIES = [
        "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "CNY", "SEK", "NZD",
        "MXN", "SGD", "HKD", "NOK", "TRY", "RUB", "INR", "BRL", "ZAR", "KRW",
        "IRR", "AED", "SAR", "QAR", "KWD", "BHD", "OMR", "JOD", "LBP", "EGP"
    ]
    
    # Supported crypto currencies
    SUPPORTED_CRYPTO = [
        "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE", "AVAX", "MATIC",
        "LTC", "BCH", "UNI", "LINK", "ATOM", "XLM", "VET", "FIL", "TRX", "ETC"
    ]
    
    # Unit conversion categories
    UNIT_CATEGORIES = {{
        "length": {{
            "mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
            "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mile": 1609.34
        }},
        "weight": {{
            "mg": 0.001, "g": 1, "kg": 1000, "ton": 1000000,
            "oz": 28.3495, "lb": 453.592, "stone": 6350.29
        }},
        "temperature": {{
            "celsius": "C", "fahrenheit": "F", "kelvin": "K"
        }},
        "volume": {{
            "ml": 0.001, "l": 1, "gal": 3.78541,
            "qt": 0.946353, "pt": 0.473176, "cup": 0.236588
        }}
    }}
    
    # Calendar systems
    CALENDAR_SYSTEMS = ["gregorian", "persian", "hijri", "hebrew", "chinese"]
    
    # Weather units
    WEATHER_UNITS = {{
        "metric": "°C",
        "imperial": "°F",
        "kelvin": "K"
    }}
    
    # Admin settings
    ADMIN_USER_IDS = {[int(admin_user_id)] if admin_user_id.isdigit() else []}
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 30
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "bot.log"
'''
    
    try:
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ Configuration file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create configuration file: {e}")
        return False

def initialize_database():
    """Initialize the database"""
    print("🗄️ Initializing database...")
    try:
        from database import Database
        db = Database()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    modules = [
        "config",
        "database", 
        "currency_converter",
        "unit_converter",
        "date_converter",
        "price_tracker",
        "weather_service",
        "calculator",
        "translation_service",
        "notification_service",
        "admin_service",
        "ui_components"
    ]
    
    failed_imports = []
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"❌ Failed to import: {{', '.join(failed_imports)}}")
        return False
    
    print("✅ All modules imported successfully!")
    return True

def main():
    """Main setup function"""
    print("🚀 Advanced Telegram Bot Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create configuration
    if not create_config():
        return False
    
    # Initialize database
    if not initialize_database():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your API keys in config.py if needed")
    print("2. Run the bot: python advanced_bot.py")
    print("3. Start chatting with your bot on Telegram!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

