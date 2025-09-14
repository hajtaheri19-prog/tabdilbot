import os
from typing import Dict, Any

class Config:
    """Configuration settings for the bot"""
    
    # Bot token (replace with your actual token)
    BOT_TOKEN = "8308943984:AAGpg52VoSSpuwWRpVrDRZ-4SDA52__ybqQ"
    
    # Database settings
    DATABASE_URL = "sqlite:///bot.db"
    
    # API Keys (you'll need to get these from respective services)
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY", "")
    GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")
    
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
    UNIT_CATEGORIES = {
        "length": {
            "mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
            "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mile": 1609.34
        },
        "weight": {
            "mg": 0.001, "g": 1, "kg": 1000, "ton": 1000000,
            "oz": 28.3495, "lb": 453.592, "stone": 6350.29
        },
        "temperature": {
            "celsius": "C", "fahrenheit": "F", "kelvin": "K"
        },
        "volume": {
            "ml": 0.001, "l": 1, "gal": 3.78541,
            "qt": 0.946353, "pt": 0.473176, "cup": 0.236588
        }
    }
    
    # Calendar systems
    CALENDAR_SYSTEMS = ["gregorian", "persian", "hijri", "hebrew", "chinese"]
    
    # Weather units
    WEATHER_UNITS = {
        "metric": "°C",
        "imperial": "°F",
        "kelvin": "K"
    }
    
    # Admin settings
    ADMIN_USER_IDS = [123456789]  # Add your Telegram user ID here (replace with actual ID)
    
    # Glass UI settings
    GLASS_THEME = "modern"  # classic, modern, neon, dark, golden, rainbow
    GLASS_ANIMATIONS = True
    GLASS_SOUNDS = False
    
    # Bot settings
    BOT_NAME = "تبدیلا"
    BOT_VERSION = "2.0.0"
    BOT_DESCRIPTION = "ربات پیشرفته تبدیل واحدها، ارز، تاریخ و قیمت‌گذاری"
    
    # Performance settings
    CACHE_TTL = 300  # 5 minutes
    MAX_CONVERSIONS_PER_USER = 1000
    MAX_ALERTS_PER_USER = 10
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 30
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "bot.log"

