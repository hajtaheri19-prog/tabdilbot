"""
🎨 Glass UI Components - اجزای رابط کاربری شیشه‌ای
یک سیستم پیشرفته برای ایجاد کیبوردها و دکمه‌های شیشه‌ای زیبا و حرفه‌ای
"""

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
)
from telegram.ext import ContextTypes
from typing import Dict, List, Optional, Any, Tuple
import logging
import random

logger = logging.getLogger(__name__)

class GlassUI:
    """کلاس اصلی برای ایجاد رابط کاربری شیشه‌ای"""
    
    # نمادهای شیشه‌ای و حرفه‌ای
    GLASS_EMOJIS = {
        "currency": "💎", "unit": "🔮", "date": "✨", "price": "💫",
        "weather": "🌌", "calculator": "🧿", "translate": "🔮", 
        "settings": "⚡", "stats": "🌟", "alerts": "💥",
        "admin": "👑", "help": "💡", "back": "🔙", "next": "➡️",
        "prev": "⬅️", "confirm": "✅", "cancel": "❌", "info": "ℹ️",
        "warning": "⚠️", "error": "🚫", "success": "🎉", "loading": "⏳"
    }
    
    # رنگ‌های شیشه‌ای (با استفاده از emoji)
    GLASS_COLORS = {
        "primary": "🔵", "secondary": "🟣", "success": "🟢", 
        "warning": "🟡", "danger": "🔴", "info": "🔵", "light": "⚪"
    }
    
    @staticmethod
    def get_glass_button(text: str, callback_data: str = None, 
                        web_app: WebAppInfo = None, emoji: str = None) -> InlineKeyboardButton:
        """ایجاد دکمه شیشه‌ای"""
        if emoji:
            display_text = f"{emoji} {text}"
        else:
            display_text = text
            
        if web_app:
            return InlineKeyboardButton(display_text, web_app=web_app)
        else:
            return InlineKeyboardButton(display_text, callback_data=callback_data)
    
    @staticmethod
    def get_main_glass_keyboard() -> InlineKeyboardMarkup:
        """کیبورد اصلی شیشه‌ای"""
        keyboard = [
            [
                GlassUI.get_glass_button(
                    "Open",
                    web_app=WebAppInfo(url="https://bot-nine-ochre.vercel.app/")
                ),
                GlassUI.get_glass_button("شروع مجدد", "restart", emoji="🔄")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_currency_glass_keyboard() -> InlineKeyboardMarkup:
        """کیبورد تبدیل ارز شیشه‌ای"""
        keyboard = [
            [
                GlassUI.get_glass_button("💱 تبدیل ارز", "currency_convert", emoji="💎"),
                GlassUI.get_glass_button("₿ ارز دیجیتال", "crypto_prices", emoji="🔮")
            ],
            [
                GlassUI.get_glass_button("📈 نرخ ارز", "exchange_rates", emoji="✨"),
                GlassUI.get_glass_button("📋 لیست ارزها", "currency_list", emoji="💫")
            ],
            [
                GlassUI.get_glass_button("🏆 برترین ارزها", "top_currencies", emoji="🌟"),
                GlassUI.get_glass_button("📊 نمودار قیمت", "price_chart", emoji="💥")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت", "back_to_main", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_unit_glass_keyboard() -> InlineKeyboardMarkup:
        """کیبورد تبدیل واحد شیشه‌ای"""
        keyboard = [
            [
                GlassUI.get_glass_button("📏 طول", "unit_length", emoji="🔮"),
                GlassUI.get_glass_button("⚖️ وزن", "unit_weight", emoji="✨")
            ],
            [
                GlassUI.get_glass_button("🌡️ دما", "unit_temperature", emoji="💫"),
                GlassUI.get_glass_button("📦 حجم", "unit_volume", emoji="🌟")
            ],
            [
                GlassUI.get_glass_button("📐 مساحت", "unit_area", emoji="💥"),
                GlassUI.get_glass_button("⏰ زمان", "unit_time", emoji="🔮")
            ],
            [
                GlassUI.get_glass_button("💨 سرعت", "unit_speed", emoji="✨"),
                GlassUI.get_glass_button("💾 داده", "unit_data", emoji="💫")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت", "back_to_main", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_price_glass_keyboard() -> InlineKeyboardMarkup:
        """کیبورد قیمت‌گذاری شیشه‌ای"""
        keyboard = [
            [
                GlassUI.get_glass_button("💰 ارزهای دیجیتال (USD)", "price_crypto_usd", emoji="💎"),
                GlassUI.get_glass_button("🌐 ارزهای دیجیتال (IRR)", "price_crypto_irr", emoji="🔮")
            ],
            [
                GlassUI.get_glass_button("🏦 دارایی‌ها (TGJU)", "price_tgju", emoji="✨"),
                GlassUI.get_glass_button("📊 همه قیمت‌ها", "price_all", emoji="💫")
            ],
            [
                GlassUI.get_glass_button("📈 سهام", "stock_price", emoji="🌟"),
                GlassUI.get_glass_button("🥇 کالا", "commodity_price", emoji="💥")
            ],
            [
                GlassUI.get_glass_button("🏆 برترین ارزها", "top_crypto", emoji="🔮"),
                GlassUI.get_glass_button("📋 لیست ارزها", "crypto_list", emoji="✨")
            ],
            [
                GlassUI.get_glass_button("📈 نمودار قیمت", "price_chart", emoji="💫"),
                GlassUI.get_glass_button("🚨 هشدار قیمت", "price_alert", emoji="🌟")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت", "back_to_main", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_glass_keyboard() -> InlineKeyboardMarkup:
        """کیبورد مدیریت شیشه‌ای"""
        keyboard = [
            [
                GlassUI.get_glass_button("📊 آمار ربات", "admin_stats", emoji="👑"),
                GlassUI.get_glass_button("👥 کاربران", "admin_users", emoji="💎")
            ],
            [
                GlassUI.get_glass_button("📢 ارسال پیام", "admin_broadcast", emoji="🔮"),
                GlassUI.get_glass_button("🔧 تنظیمات", "admin_settings", emoji="✨")
            ],
            [
                GlassUI.get_glass_button("🚨 هشدارها", "admin_alerts", emoji="💫"),
                GlassUI.get_glass_button("📋 لاگ‌ها", "admin_logs", emoji="🌟")
            ],
            [
                GlassUI.get_glass_button("🛠️ تعمیرات", "admin_maintenance", emoji="💥"),
                GlassUI.get_glass_button("💾 کش", "admin_cache", emoji="🔮")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت", "back_to_main", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_settings_glass_keyboard() -> InlineKeyboardMarkup:
        """کیبورد تنظیمات شیشه‌ای"""
        keyboard = [
            [
                GlassUI.get_glass_button("🌍 زبان", "set_language", emoji="🔮"),
                GlassUI.get_glass_button("🌡️ واحد دما", "set_temperature_unit", emoji="✨")
            ],
            [
                GlassUI.get_glass_button("📏 واحد طول", "set_length_unit", emoji="💫"),
                GlassUI.get_glass_button("💰 ارز پیش‌فرض", "set_default_currency", emoji="🌟")
            ],
            [
                GlassUI.get_glass_button("🔔 اعلان‌ها", "notification_settings", emoji="💥"),
                GlassUI.get_glass_button("📊 حریم خصوصی", "privacy_settings", emoji="🔮")
            ],
            [
                GlassUI.get_glass_button("🎨 تم", "theme_settings", emoji="✨"),
                GlassUI.get_glass_button("⚡ عملکرد", "performance_settings", emoji="💫")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت", "back_to_main", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_confirmation_glass_keyboard(action: str) -> InlineKeyboardMarkup:
        """کیبورد تأیید شیشه‌ای"""
        keyboard = [
            [
                GlassUI.get_glass_button("✅ تأیید", f"confirm_{action}", emoji="✅"),
                GlassUI.get_glass_button("❌ لغو", f"cancel_{action}", emoji="❌")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
        """کیبورد فقط با دکمه بازگشت به منوی اصلی"""
        keyboard = [
            [
                GlassUI.get_glass_button("🔙 بازگشت به منوی اصلی", "back_to_main", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_pagination_glass_keyboard(current_page: int, total_pages: int, 
                                    callback_prefix: str) -> InlineKeyboardMarkup:
        """کیبورد صفحه‌بندی شیشه‌ای"""
        keyboard = []
        
        # دکمه‌های ناوبری
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(GlassUI.get_glass_button("⬅️ قبلی", 
                                                      f"{callback_prefix}_page_{current_page-1}", emoji="⬅️"))
        
        nav_buttons.append(GlassUI.get_glass_button(f"{current_page}/{total_pages}", 
                                                   "page_info", emoji="ℹ️"))
        
        if current_page < total_pages:
            nav_buttons.append(GlassUI.get_glass_button("بعدی ➡️", 
                                                      f"{callback_prefix}_page_{current_page+1}", emoji="➡️"))
        
        keyboard.append(nav_buttons)
        
        # شماره صفحات (اگر زیاد نباشد)
        if total_pages <= 10:
            page_buttons = []
            for page in range(1, total_pages + 1):
                if page == current_page:
                    page_buttons.append(GlassUI.get_glass_button(f"•{page}•", 
                                                               "current_page", emoji="🔮"))
                else:
                    page_buttons.append(GlassUI.get_glass_button(str(page), 
                                                               f"{callback_prefix}_page_{page}", emoji="✨"))
            
            # تقسیم به ردیف‌های 5 تایی
            for i in range(0, len(page_buttons), 5):
                keyboard.append(page_buttons[i:i+5])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_quick_glass_keyboard() -> ReplyKeyboardMarkup:
        """کیبورد سریع شیشه‌ای"""
        keyboard = [
            [
                KeyboardButton("💎 ارز"), KeyboardButton("🔮 واحد"), KeyboardButton("✨ تاریخ")
            ],
            [
                KeyboardButton("💫 قیمت"), KeyboardButton("🌌 هوا"), KeyboardButton("🧿 حساب")
            ],
            [
                KeyboardButton("🔮 ترجمه"), KeyboardButton("⚡ تنظیمات"), KeyboardButton("🌟 آمار")
            ],
            [
                KeyboardButton("🔄 شروع مجدد")
            ]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    @staticmethod
    def get_quick_keyboard_with_webapp() -> ReplyKeyboardMarkup:
        """کیبورد سریع با دکمه مینی‌اپ برای نمایش کنار نوار تایپ"""
        keyboard = [
            [
                KeyboardButton("🚀 مینی‌اپ", web_app=WebAppInfo(url="https://bot-nine-ochre.vercel.app/"))
            ],
            [
                KeyboardButton("💎 ارز"), KeyboardButton("🔮 واحد"), KeyboardButton("✨ تاریخ")
            ],
            [
                KeyboardButton("💫 قیمت"), KeyboardButton("🌌 هوا"), KeyboardButton("🧿 حساب")
            ],
            [
                KeyboardButton("🔄 شروع مجدد")
            ]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_language_selection_glass_keyboard() -> InlineKeyboardMarkup:
        """کیبورد انتخاب زبان شیشه‌ای"""
        keyboard = [
            [
                GlassUI.get_glass_button("🇮🇷 فارسی", "lang_fa", emoji="🔮"),
                GlassUI.get_glass_button("🇺🇸 English", "lang_en", emoji="✨")
            ],
            [
                GlassUI.get_glass_button("🇸🇦 العربية", "lang_ar", emoji="💫"),
                GlassUI.get_glass_button("🇨🇳 中文", "lang_zh", emoji="🌟")
            ],
            [
                GlassUI.get_glass_button("🇪🇸 Español", "lang_es", emoji="💥"),
                GlassUI.get_glass_button("🇫🇷 Français", "lang_fr", emoji="🔮")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت", "back_to_settings", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_theme_selection_glass_keyboard() -> InlineKeyboardMarkup:
        """کیبورد انتخاب تم شیشه‌ای"""
        keyboard = [
            [
                GlassUI.get_glass_button("💎 شیشه‌ای کلاسیک", "theme_classic_glass", emoji="💎"),
                GlassUI.get_glass_button("🔮 شیشه‌ای مدرن", "theme_modern_glass", emoji="🔮")
            ],
            [
                GlassUI.get_glass_button("✨ شیشه‌ای نئون", "theme_neon_glass", emoji="✨"),
                GlassUI.get_glass_button("💫 شیشه‌ای تاریک", "theme_dark_glass", emoji="💫")
            ],
            [
                GlassUI.get_glass_button("🌟 شیشه‌ای طلایی", "theme_golden_glass", emoji="🌟"),
                GlassUI.get_glass_button("💥 شیشه‌ای رنگین‌کمان", "theme_rainbow_glass", emoji="💥")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت", "back_to_settings", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_glass_welcome_message() -> str:
        """پیام خوش‌آمدگویی شیشه‌ای"""
        return """
🌟 به دنیای جادویی تبدیل‌ها خوش آمدید! 🌟
✨ تبدیلا؛ پیشرفته‌ترین ربات شیشه‌ای برای هر آنچه که به فکرش برسی!

💎 ابر قابلیت‌ها:
• 💰 تبدیل حرفه‌ای ارز و رمزارز با قیمت لحظه‌ای
• 📏 تبدیل انواع واحدها — از متر و کیلو گرفته تا بیت و بایت
• 📅 تبدیل تاریخ و تقویم (شمسی، میلادی، قمری)
• 📈 نمایش قیمت زنده سهام، طلا، سکه و کالا
• ☁️ آب و هوا و پیش‌بینی هوشمند روزهای آینده
• 🔢 ماشین‌حساب پیشرفته با تشخیص خودکار عملیات
• 🌍 ترجمه سریع و روان متن به زبان‌های مختلف
• 🚨 اعلان‌ها، هشدارها و یادآوری‌های هوشمند

🚀 شروع جادوی شما:
روی دکمه‌های شیشه‌ای پایین بزنید یا هر متن/سوالی رو بفرستید…
من خودم می‌فهمم چی می‌خواید! 😏
        """

    @staticmethod
    def get_tools_glass_keyboard() -> InlineKeyboardMarkup:
        """کیبورد ابزارهای شیشه‌ای"""
        keyboard = [
            [
                GlassUI.get_glass_button("💎 ارز", "currency_menu", emoji="💎"),
                GlassUI.get_glass_button("🔮 واحد", "unit_menu", emoji="🔮")
            ],
            [
                GlassUI.get_glass_button("✨ تاریخ", "date_menu", emoji="✨"),
                GlassUI.get_glass_button("💫 قیمت", "price_menu", emoji="💫")
            ],
            [
                GlassUI.get_glass_button("🌌 هوا", "weather_menu", emoji="🌌"),
                GlassUI.get_glass_button("🧿 حساب", "calculator_menu", emoji="🧿")
            ],
            [
                GlassUI.get_glass_button("🔮 ترجمه", "translate_menu", emoji="🔮"),
                GlassUI.get_glass_button("⚡ تنظیمات", "settings_menu", emoji="⚡")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_price_submenu_keyboard() -> InlineKeyboardMarkup:
        """کیبورد زیرمنوی قیمت‌گذاری"""
        keyboard = [
            [
                GlassUI.get_glass_button("₿ بیت کوین", "price_bitcoin", emoji="₿"),
                GlassUI.get_glass_button("🥇 طلای 18 عیار", "price_gold_18k", emoji="🥇")
            ],
            [
                GlassUI.get_glass_button("🥈 نقره", "price_silver", emoji="🥈"),
                GlassUI.get_glass_button("💎 انس طلا", "price_gold_ounce", emoji="💎")
            ],
            [
                GlassUI.get_glass_button("💰 ارزهای دیجیتال", "price_crypto_menu", emoji="💰"),
                GlassUI.get_glass_button("📈 سهام", "price_stocks", emoji="📈")
            ],
            [
                GlassUI.get_glass_button("🏦 دارایی‌ها (TGJU)", "price_tgju", emoji="🏦"),
                GlassUI.get_glass_button("📊 همه قیمت‌ها", "price_all", emoji="📊")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت به منو", "back_to_main", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_currency_submenu_keyboard() -> InlineKeyboardMarkup:
        """کیبورد زیرمنوی ارز"""
        keyboard = [
            [
                GlassUI.get_glass_button("💵 دلار آمریکا", "currency_usd", emoji="💵"),
                GlassUI.get_glass_button("💶 یورو", "currency_eur", emoji="💶")
            ],
            [
                GlassUI.get_glass_button("💷 پوند انگلیس", "currency_gbp", emoji="💷"),
                GlassUI.get_glass_button("💴 ین ژاپن", "currency_jpy", emoji="💴")
            ],
            [
                GlassUI.get_glass_button("₿ بیت کوین", "currency_btc", emoji="₿"),
                GlassUI.get_glass_button("Ξ اتریوم", "currency_eth", emoji="Ξ")
            ],
            [
                GlassUI.get_glass_button("💱 تبدیل ارز", "currency_convert", emoji="💱"),
                GlassUI.get_glass_button("📈 نرخ ارز", "exchange_rates", emoji="📈")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت به منو", "back_to_main", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_date_submenu_keyboard() -> InlineKeyboardMarkup:
        """کیبورد زیرمنوی تاریخ"""
        keyboard = [
            [
                GlassUI.get_glass_button("📅 امروز", "date_today", emoji="📅"),
                GlassUI.get_glass_button("📆 این ماه", "date_this_month", emoji="📆")
            ],
            [
                GlassUI.get_glass_button("🗓️ تقویم شمسی", "calendar_persian", emoji="🗓️"),
                GlassUI.get_glass_button("📅 تقویم میلادی", "calendar_gregorian", emoji="📅")
            ],
            [
                GlassUI.get_glass_button("🌙 تقویم قمری", "calendar_hijri", emoji="🌙"),
                GlassUI.get_glass_button("⏰ ساعت جهانی", "world_time", emoji="⏰")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت به منو", "back_to_main", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_unit_submenu_keyboard() -> InlineKeyboardMarkup:
        """کیبورد زیرمنوی واحد"""
        keyboard = [
            [
                GlassUI.get_glass_button("📏 طول", "unit_length", emoji="📏"),
                GlassUI.get_glass_button("⚖️ وزن", "unit_weight", emoji="⚖️")
            ],
            [
                GlassUI.get_glass_button("🌡️ دما", "unit_temperature", emoji="🌡️"),
                GlassUI.get_glass_button("📦 حجم", "unit_volume", emoji="📦")
            ],
            [
                GlassUI.get_glass_button("📐 مساحت", "unit_area", emoji="📐"),
                GlassUI.get_glass_button("⏰ زمان", "unit_time", emoji="⏰")
            ],
            [
                GlassUI.get_glass_button("💨 سرعت", "unit_speed", emoji="💨"),
                GlassUI.get_glass_button("💾 داده", "unit_data", emoji="💾")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت به منو", "back_to_main", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_feedback_glass_keyboard() -> InlineKeyboardMarkup:
        """کیبورد شیشه‌ای پیشنهادات و گزارش خرابی"""
        keyboard = [
            [
                GlassUI.get_glass_button("پیشنهادات و انتقادات", "feedback", emoji="📝"),
                GlassUI.get_glass_button("گزارش خرابی", "report_bug", emoji="🐞")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_glass_help_message() -> str:
        """پیام راهنما شیشه‌ای"""
        return """
🤖 **راهنمای ربات تبدیلا** 💎

🔧 **دستورات اصلی:**
• `/start` - شروع ربات
• `/help` - راهنما
• `/menu` - منوی اصلی
• `/settings` - تنظیمات
• `/admin` - پنل مدیریت (فقط ادمین)

💎 **تبدیل ارز:**
• مثال: `100 USD to IRR`
• پشتیبانی از ارزهای دیجیتال
• نرخ لحظه‌ای

🔮 **تبدیل واحد:**
• طول: `10 km to mile`
• وزن: `5 kg to lb`
• دما: `25 celsius to fahrenheit`
• حجم، مساحت، زمان و...

✨ **تبدیل تاریخ:**
• مثال: `2024-01-15`
• تقویم شمسی، قمری، میلادی
• منطقه زمانی

💫 **قیمت لحظه‌ای:**
• سهام، ارز دیجیتال، کالا
• مثال: `BTC`, `AAPL`, `GOLD`

🌌 **آب و هوا:**
• آب و هوای فعلی
• پیش‌بینی 5 روزه

🧿 **ماشین حساب:**
• توابع علمی
• آمار و محاسبات پیشرفته

🔮 **ترجمه:**
• ترجمه متن
• تشخیص زبان

💥 **هشدارها:**
• هشدار قیمت
• یادآوری

برای شروع `/start` را بزنید! 🚀
        """
    
    @staticmethod
    def get_glass_loading_message() -> str:
        """پیام بارگذاری شیشه‌ای"""
        loading_emojis = ["⏳", "🔄", "✨", "💫", "🌟", "🔮", "💎"]
        emoji = random.choice(loading_emojis)
        return f"{emoji} در حال پردازش..."
    
    @staticmethod
    def get_glass_success_message(message: str) -> str:
        """پیام موفقیت شیشه‌ای"""
        return f"✅ {message} ✨"
    
    @staticmethod
    def get_glass_error_message(message: str) -> str:
        """پیام خطا شیشه‌ای"""
        return f"❌ {message} 🚫"
    
    @staticmethod
    def get_glass_warning_message(message: str) -> str:
        """پیام هشدار شیشه‌ای"""
        return f"⚠️ {message} 💥"
    
    @staticmethod
    def get_glass_info_message(message: str) -> str:
        """پیام اطلاعات شیشه‌ای"""
        return f"ℹ️ {message} 💡"
    
    @staticmethod
    def get_permanent_reply_keyboard() -> ReplyKeyboardMarkup:
        """کیبورد دائمی با دو دکمه - مینی‌اپ و شروع مجدد"""
        keyboard = [
            [
                KeyboardButton("🚀 مینی‌اپ", web_app=WebAppInfo(url="https://bot-nine-ochre.vercel.app/")),
                KeyboardButton("🔄 شروع مجدد")
            ]
        ]
        return ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True, 
            one_time_keyboard=False,  # False = دائمی
            input_field_placeholder="پیام خود را بنویسید..."
        )

