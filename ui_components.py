from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
)
from telegram.ext import ContextTypes
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class UIComponents:
    """Enhanced UI components for the bot"""
    
    @staticmethod
    def get_main_menu_keyboard() -> InlineKeyboardMarkup:
        """Get main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("💱 تبدیل ارز", callback_data="currency"),
                InlineKeyboardButton("📏 تبدیل واحد", callback_data="unit")
            ],
            [
                InlineKeyboardButton("📅 تبدیل تاریخ", callback_data="date_convert"),
                InlineKeyboardButton("💰 قیمت لحظه‌ای", callback_data="price")
            ],
            [
                InlineKeyboardButton("🌤️ آب و هوا", callback_data="weather"),
                InlineKeyboardButton("🧮 ماشین حساب", callback_data="calculator")
            ],
            [
                InlineKeyboardButton("🌐 ترجمه", callback_data="translate"),
                InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")
            ],
            [
                InlineKeyboardButton("📊 آمار من", callback_data="my_stats"),
                InlineKeyboardButton("🚨 هشدارها", callback_data="alerts")
            ],
            [
                InlineKeyboardButton("Open", web_app=WebAppInfo(
                    url="https://bot-nine-ochre.vercel.app/"
                ))
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_currency_menu_keyboard() -> InlineKeyboardMarkup:
        """Get currency conversion menu"""
        keyboard = [
            [
                InlineKeyboardButton("💱 تبدیل ارز", callback_data="currency_convert"),
                InlineKeyboardButton("📈 ارزهای دیجیتال", callback_data="crypto_prices")
            ],
            [
                InlineKeyboardButton("📊 نرخ ارز", callback_data="exchange_rates"),
                InlineKeyboardButton("📋 لیست ارزها", callback_data="currency_list")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_unit_menu_keyboard() -> InlineKeyboardMarkup:
        """Get unit conversion menu"""
        keyboard = [
            [
                InlineKeyboardButton("📏 طول", callback_data="unit_length"),
                InlineKeyboardButton("⚖️ وزن", callback_data="unit_weight")
            ],
            [
                InlineKeyboardButton("🌡️ دما", callback_data="unit_temperature"),
                InlineKeyboardButton("📦 حجم", callback_data="unit_volume")
            ],
            [
                InlineKeyboardButton("📐 مساحت", callback_data="unit_area"),
                InlineKeyboardButton("⏰ زمان", callback_data="unit_time")
            ],
            [
                InlineKeyboardButton("💨 سرعت", callback_data="unit_speed"),
                InlineKeyboardButton("💾 داده", callback_data="unit_data")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_date_menu_keyboard() -> InlineKeyboardMarkup:
        """Get date conversion menu"""
        keyboard = [
            [
                InlineKeyboardButton("📅 تبدیل تقویم", callback_data="date_convert"),
                InlineKeyboardButton("🌍 منطقه زمانی", callback_data="timezone_convert")
            ],
            [
                InlineKeyboardButton("📊 تفاوت تاریخ", callback_data="date_difference"),
                InlineKeyboardButton("📆 اطلاعات هفته", callback_data="week_info")
            ],
            [
                InlineKeyboardButton("➕/➖ روز", callback_data="date_arithmetic"),
                InlineKeyboardButton("🕐 زمان فعلی", callback_data="current_time")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_price_menu_keyboard() -> InlineKeyboardMarkup:
        """Get price tracking menu"""
        keyboard = [
            [
                InlineKeyboardButton("📈 سهام", callback_data="stock_price"),
                InlineKeyboardButton("₿ ارز دیجیتال", callback_data="crypto_price")
            ],
            [
                InlineKeyboardButton("🏆 برترین ارزها", callback_data="top_crypto"),
                InlineKeyboardButton("📋 لیست ارزها", callback_data="crypto_list")
            ],
            [
                InlineKeyboardButton("🥇 کالا", callback_data="commodity_price"),
                InlineKeyboardButton("📊 خلاصه بازار", callback_data="market_summary")
            ],
            [
                InlineKeyboardButton("📈 نمودار قیمت", callback_data="price_chart"),
                InlineKeyboardButton("🚨 هشدار قیمت", callback_data="price_alert")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_weather_menu_keyboard() -> InlineKeyboardMarkup:
        """Get weather menu"""
        keyboard = [
            [
                InlineKeyboardButton("🌤️ آب و هوای فعلی", callback_data="current_weather"),
                InlineKeyboardButton("📅 پیش‌بینی", callback_data="weather_forecast")
            ],
            [
                InlineKeyboardButton("🌍 شهرهای محبوب", callback_data="popular_cities"),
                InlineKeyboardButton("📍 موقعیت من", callback_data="my_location")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_calculator_menu_keyboard() -> InlineKeyboardMarkup:
        """Get calculator menu"""
        keyboard = [
            [
                InlineKeyboardButton("🧮 محاسبه", callback_data="calculate"),
                InlineKeyboardButton("📊 آمار", callback_data="statistics")
            ],
            [
                InlineKeyboardButton("🔢 تبدیل مبنا", callback_data="base_convert"),
                InlineKeyboardButton("📐 توابع", callback_data="functions")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_translate_menu_keyboard() -> InlineKeyboardMarkup:
        """Get translation menu"""
        keyboard = [
            [
                InlineKeyboardButton("🌐 ترجمه متن", callback_data="translate_text"),
                InlineKeyboardButton("🔍 تشخیص زبان", callback_data="detect_language")
            ],
            [
                InlineKeyboardButton("📝 عبارات رایج", callback_data="common_phrases"),
                InlineKeyboardButton("🌍 زبان‌های پشتیبانی", callback_data="supported_languages")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_settings_menu_keyboard() -> InlineKeyboardMarkup:
        """Get settings menu"""
        keyboard = [
            [
                InlineKeyboardButton("🌍 زبان", callback_data="set_language"),
                InlineKeyboardButton("🌡️ واحد دما", callback_data="set_temperature_unit")
            ],
            [
                InlineKeyboardButton("📏 واحد طول", callback_data="set_length_unit"),
                InlineKeyboardButton("💰 ارز پیش‌فرض", callback_data="set_default_currency")
            ],
            [
                InlineKeyboardButton("🔔 اعلان‌ها", callback_data="notification_settings"),
                InlineKeyboardButton("📊 حریم خصوصی", callback_data="privacy_settings")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_alerts_menu_keyboard() -> InlineKeyboardMarkup:
        """Get alerts menu"""
        keyboard = [
            [
                InlineKeyboardButton("📋 هشدارهای من", callback_data="my_alerts"),
                InlineKeyboardButton("➕ هشدار جدید", callback_data="add_alert")
            ],
            [
                InlineKeyboardButton("⏰ یادآوری", callback_data="add_reminder"),
                InlineKeyboardButton("📊 آمار هشدارها", callback_data="alert_stats")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_language_selection_keyboard() -> InlineKeyboardMarkup:
        """Get language selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
                InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
            ],
            [
                InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
                InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh")
            ],
            [
                InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
                InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_temperature_unit_keyboard() -> InlineKeyboardMarkup:
        """Get temperature unit selection"""
        keyboard = [
            [
                InlineKeyboardButton("🌡️ سانتی‌گراد", callback_data="temp_celsius"),
                InlineKeyboardButton("🌡️ فارنهایت", callback_data="temp_fahrenheit")
            ],
            [
                InlineKeyboardButton("🌡️ کلوین", callback_data="temp_kelvin"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_length_unit_keyboard() -> InlineKeyboardMarkup:
        """Get length unit selection"""
        keyboard = [
            [
                InlineKeyboardButton("📏 متر", callback_data="length_meter"),
                InlineKeyboardButton("📏 فوت", callback_data="length_foot")
            ],
            [
                InlineKeyboardButton("📏 اینچ", callback_data="length_inch"),
                InlineKeyboardButton("📏 کیلومتر", callback_data="length_kilometer")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_currency_selection_keyboard() -> InlineKeyboardMarkup:
        """Get currency selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("💵 USD", callback_data="currency_usd"),
                InlineKeyboardButton("💶 EUR", callback_data="currency_eur")
            ],
            [
                InlineKeyboardButton("💷 GBP", callback_data="currency_gbp"),
                InlineKeyboardButton("💴 JPY", callback_data="currency_jpy")
            ],
            [
                InlineKeyboardButton("💸 IRR", callback_data="currency_irr"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_quick_actions_keyboard() -> ReplyKeyboardMarkup:
        """Get quick actions keyboard"""
        keyboard = [
            [
                KeyboardButton("💱 ارز"),
                KeyboardButton("📏 واحد"),
                KeyboardButton("📅 تاریخ")
            ],
            [
                KeyboardButton("💰 قیمت"),
                KeyboardButton("🌤️ هوا"),
                KeyboardButton("🧮 حساب")
            ],
            [
                KeyboardButton("🌐 ترجمه"),
                KeyboardButton("⚙️ تنظیمات"),
                KeyboardButton("📊 آمار")
            ]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
        """Get confirmation keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("✅ تأیید", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ لغو", callback_data=f"cancel_{action}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_pagination_keyboard(current_page: int, total_pages: int, 
                              callback_prefix: str) -> InlineKeyboardMarkup:
        """Get pagination keyboard"""
        keyboard = []
        
        # Previous/Next buttons
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ قبلی", 
                                                   callback_data=f"{callback_prefix}_page_{current_page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", 
                                              callback_data="page_info"))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton("بعدی ➡️", 
                                                   callback_data=f"{callback_prefix}_page_{current_page+1}"))
        
        keyboard.append(nav_buttons)
        
        # Page numbers (if not too many)
        if total_pages <= 10:
            page_buttons = []
            for page in range(1, total_pages + 1):
                if page == current_page:
                    page_buttons.append(InlineKeyboardButton(f"•{page}•", 
                                                           callback_data="current_page"))
                else:
                    page_buttons.append(InlineKeyboardButton(str(page), 
                                                           callback_data=f"{callback_prefix}_page_{page}"))
            
            # Split into rows of 5
            for i in range(0, len(page_buttons), 5):
                keyboard.append(page_buttons[i:i+5])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_inline_query_results(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format results for inline query"""
        formatted_results = []
        
        for i, result in enumerate(results[:10]):  # Limit to 10 results
            formatted_results.append({
                "type": "article",
                "id": str(i),
                "title": result.get("title", "نتیجه"),
                "description": result.get("description", ""),
                "input_message_content": {
                    "message_text": result.get("message", ""),
                    "parse_mode": "Markdown"
                },
                "reply_markup": result.get("reply_markup")
            })
        
        return formatted_results
    
    @staticmethod
    def format_help_message() -> str:
        """Format help message"""
        return """
🤖 **راهنمای ربات تبدیلا**

**🔧 دستورات اصلی:**
• `/start` - شروع ربات
• `/help` - راهنما
• `/menu` - منوی اصلی
• `/settings` - تنظیمات

**💱 تبدیل ارز:**
• مثال: `100 USD to IRR`
• پشتیبانی از ارزهای دیجیتال
• نرخ لحظه‌ای

**📏 تبدیل واحد:**
• طول: `10 km to mile`
• وزن: `5 kg to lb`
• دما: `25 celsius to fahrenheit`
• حجم، مساحت، زمان و...

**📅 تبدیل تاریخ:**
• مثال: `2024-01-15`
• تقویم شمسی، قمری، میلادی
• منطقه زمانی

**💰 قیمت لحظه‌ای:**
• سهام، ارز دیجیتال، کالا
• مثال: `BTC`, `AAPL`, `GOLD`

**🌤️ آب و هوا:**
• آب و هوای فعلی
• پیش‌بینی 5 روزه

**🧮 ماشین حساب:**
• توابع علمی
• آمار و محاسبات پیشرفته

**🌐 ترجمه:**
• ترجمه متن
• تشخیص زبان

**🚨 هشدارها:**
• هشدار قیمت
• یادآوری

برای شروع `/start` را بزنید! 🚀
        """
    
    @staticmethod
    def format_welcome_message() -> str:
        """Format welcome message"""
        return """
🎉 **خوش آمدید به ربات تبدیلا!**

من یک ربات پیشرفته برای تبدیل واحدها، ارز، تاریخ و خیلی چیزهای دیگه هستم! 

**✨ قابلیت‌های من:**
• 💱 تبدیل ارز و ارز دیجیتال
• 📏 تبدیل واحدهای مختلف
• 📅 تبدیل تاریخ و تقویم
• 💰 قیمت لحظه‌ای سهام و کالا
• 🌤️ آب و هوا و پیش‌بینی
• 🧮 ماشین حساب پیشرفته
• 🌐 ترجمه متن
• 🚨 هشدارها و یادآوری

**🚀 برای شروع:**
روی دکمه‌های زیر کلیک کنید یا از منوی اصلی استفاده کنید!

**💡 نکته:** می‌تونید مستقیماً متن رو بفرستید و من خودکار تشخیص می‌دم که چه کاری می‌خواید انجام بدید!
        """
