import os
from typing import Dict, Any

class Config:
    """Configuration settings for the bot"""
    
    # Bot token (replace with your actual token)
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    # Database settings
    DATABASE_URL = "sqlite:///bot.db"
    
    # API Keys (optional - add your keys here)
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
            "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mile": 1609.34,
            "nautical_mile": 1852, "light_year": 9.461e15,
            "parsec": 3.086e16, "angstrom": 1e-10, "micron": 1e-6
        },
        "weight": {
            "mg": 0.001, "g": 1, "kg": 1000, "ton": 1000000,
            "oz": 28.3495, "lb": 453.592, "stone": 6350.29,
            "carat": 0.2, "grain": 0.0647989, "dram": 1.77185,
            "troy_oz": 31.1035, "troy_pound": 373.242
        },
        "temperature": {
            "celsius": "C", "fahrenheit": "F", "kelvin": "K"
        },
        "volume": {
            "ml": 0.001, "l": 1, "gal": 3.78541,
            "qt": 0.946353, "pt": 0.473176, "cup": 0.236588,
            "barrel": 158.987, "cubic_meter": 1000, "cubic_cm": 0.001, "cubic_inch": 0.0163871
        },
        "area": {
            "mm²": 1e-6, "cm²": 1e-4, "m²": 1, "km²": 1e6,
            "in²": 6.4516e-4, "ft²": 0.092903, "yd²": 0.836127,
            "acre": 4046.86, "hectare": 10000, "square_mile": 2.59e6
        },
        "time": {
            "ns": 1e-9, "μs": 1e-6, "ms": 1e-3, "s": 1,
            "min": 60, "h": 3600, "day": 86400, "week": 604800,
            "month": 2629746, "year": 31556952, "decade": 315569520,
            "century": 3155695200
        },
        "speed": {
            "m/s": 1, "km/h": 0.277778, "mph": 0.44704,
            "ft/s": 0.3048, "knot": 0.514444, "mach": 343,
            "light_speed": 299792458
        },
        "pressure": {
            "pa": 1, "kpa": 1000, "mpa": 1e6, "bar": 1e5,
            "atm": 101325, "torr": 133.322, "psi": 6894.76,
            "mmhg": 133.322, "inhg": 3386.39
        },
        "energy": {
            "j": 1, "kj": 1000, "mj": 1e6, "cal": 4.184,
            "kcal": 4184, "btu": 1055.06, "kwh": 3.6e6,
            "wh": 3600, "therm": 1.055e8, "quad": 1.055e18
        },
        "power": {
            "w": 1, "kw": 1000, "mw": 1e6, "gw": 1e9,
            "hp": 745.7, "btu/h": 0.293071, "cal/s": 4.184,
            "ft-lb/s": 1.35582
        },
        "data": {
            "bit": 0.125, "byte": 1, "kb": 1024, "mb": 1024**2,
            "gb": 1024**3, "tb": 1024**4, "pb": 1024**5,
            "kib": 1024, "mib": 1024**2, "gib": 1024**3,
            "tib": 1024**4, "pib": 1024**5
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
    
    # Admin settings (add your Telegram user ID here)
    ADMIN_USER_IDS = []  # Example: [123456789, 987654321]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 30
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "bot.log"

