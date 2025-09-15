#!/usr/bin/env python3
"""
Simple bot runner with error handling
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ContextTypes, filters, InlineQueryHandler
)

# Import our modules
from config import Config
from database import Database
from currency_converter import CurrencyConverter
from unit_converter import UnitConverter
from date_converter import DateConverter
from price_tracker import PriceTracker
from weather_service import WeatherService
from calculator import AdvancedCalculator
from translation_service import TranslationService
from notification_service import NotificationService
from admin_service import AdminService
from ui_components import UIComponents

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.LOG_LEVEL),
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleTelegramBot:
    """Simplified Telegram Bot with basic features"""
    
    def __init__(self):
        self.db = Database()
        self.currency_converter = CurrencyConverter(self.db)
        self.unit_converter = UnitConverter()
        self.date_converter = DateConverter()
        self.price_tracker = PriceTracker(self.db)
        self.weather_service = WeatherService(self.db)
        self.calculator = AdvancedCalculator()
        self.translation_service = TranslationService(self.db)
        self.admin_service = AdminService(self.db)
        self.ui = UIComponents()
        
        # User states for conversation flow
        self.user_states = {}
        
    # Command handlers
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Add user to database
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code or "fa"
        )
        
        # Update user activity
        self.db.update_user_activity(user.id)
        
        # Send welcome message
        welcome_text = self.ui.format_welcome_message()
        keyboard = self.ui.get_main_menu_keyboard()
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = self.ui.format_help_message()
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /menu command"""
        keyboard = self.ui.get_main_menu_keyboard()
        await update.message.reply_text(
            "🏠 **منوی اصلی**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    # Callback query handlers
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        # Update user activity
        self.db.update_user_activity(user_id)
        
        # Route to appropriate handler
        if data == "back_to_main":
            await self.show_main_menu(query)
        elif data.startswith("currency"):
            await self.handle_currency_menu(query, data)
        elif data.startswith("unit"):
            await self.handle_unit_menu(query, data)
        elif data.startswith("date"):
            await self.handle_date_menu(query, data)
        elif data.startswith("price"):
            await self.handle_price_menu(query, data)
        elif data.startswith("weather"):
            await self.handle_weather_menu(query, data)
        elif data.startswith("calculator"):
            await self.handle_calculator_menu(query, data)
        elif data.startswith("translate"):
            await self.handle_translate_menu(query, data)
        elif data.startswith("settings"):
            await self.handle_settings_menu(query, data)
        elif data.startswith("alerts"):
            await self.handle_alerts_menu(query, data)
        else:
            await self.handle_general_callback(query, data)
    
    async def show_main_menu(self, query):
        """Show main menu"""
        keyboard = self.ui.get_main_menu_keyboard()
        await query.edit_message_text(
            "🏠 **منوی اصلی**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    async def handle_currency_menu(self, query, data):
        """Handle currency menu callbacks"""
        if data == "currency":
            keyboard = self.ui.get_currency_menu_keyboard()
            await query.edit_message_text(
                "💱 **تبدیل ارز**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        elif data == "currency_convert":
            await query.edit_message_text(
                "💱 **تبدیل ارز**\n\nمثال: `100 USD to IRR`\n\nمتن خود را ارسال کنید:",
                parse_mode="Markdown"
            )
            self.user_states[query.from_user.id] = "currency_convert"
        elif data == "crypto_prices":
            await query.edit_message_text(
                "₿ **قیمت ارزهای دیجیتال**\n\nنام ارز دیجیتال را ارسال کنید:\nمثال: `BTC`, `ETH`, `DOGE`",
                parse_mode="Markdown"
            )
            self.user_states[query.from_user.id] = "crypto_price"
    
    async def handle_unit_menu(self, query, data):
        """Handle unit menu callbacks"""
        if data == "unit":
            keyboard = self.ui.get_unit_menu_keyboard()
            await query.edit_message_text(
                "📏 **تبدیل واحد**\n\nیکی از دسته‌بندی‌های زیر را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        elif data.startswith("unit_"):
            unit_type = data.split("_")[1]
            await query.edit_message_text(
                f"📏 **تبدیل {unit_type}**\n\nمثال: `10 km to mile`\n\nمتن خود را ارسال کنید:",
                parse_mode="Markdown"
            )
            self.user_states[query.from_user.id] = f"unit_{unit_type}"
    
    async def handle_date_menu(self, query, data):
        """Handle date menu callbacks"""
        if data == "date_convert":
            keyboard = self.ui.get_date_menu_keyboard()
            await query.edit_message_text(
                "📅 **تبدیل تاریخ**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        elif data == "date_convert":
            await query.edit_message_text(
                "📅 **تبدیل تاریخ**\n\nمثال: `2024-01-15`\n\nتاریخ خود را ارسال کنید:",
                parse_mode="Markdown"
            )
            self.user_states[query.from_user.id] = "date_convert"
        elif data == "current_time":
            await self.show_current_time(query)
    
    async def handle_price_menu(self, query, data):
        """Handle price menu callbacks"""
        if data == "price":
            keyboard = self.ui.get_price_menu_keyboard()
            await query.edit_message_text(
                "💰 **قیمت لحظه‌ای**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        elif data == "stock_price":
            await query.edit_message_text(
                "📈 **قیمت سهام**\n\nنماد سهام را ارسال کنید:\nمثال: `AAPL`, `GOOGL`, `TSLA`",
                parse_mode="Markdown"
            )
            self.user_states[query.from_user.id] = "stock_price"
        elif data == "crypto_price":
            await query.edit_message_text(
                "₿ **قیمت ارز دیجیتال**\n\nنام ارز دیجیتال را ارسال کنید:\nمثال: `BTC`, `ETH`, `DOGE`\n\n💡 **نکته:** می‌توانید چندین ارز را با کاما جدا کنید:\n`BTC,ETH,DOGE`",
                parse_mode="Markdown"
            )
            self.user_states[query.from_user.id] = "crypto_price"
        elif data == "top_crypto":
            await self.show_top_crypto(query)
        elif data == "crypto_list":
            await self.show_crypto_list(query)
    
    async def handle_weather_menu(self, query, data):
        """Handle weather menu callbacks"""
        if data == "weather":
            keyboard = self.ui.get_weather_menu_keyboard()
            await query.edit_message_text(
                "🌤️ **آب و هوا**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        elif data == "current_weather":
            await query.edit_message_text(
                "🌤️ **آب و هوای فعلی**\n\nنام شهر را ارسال کنید:\nمثال: `تهران`, `London`, `New York`",
                parse_mode="Markdown"
            )
            self.user_states[query.from_user.id] = "current_weather"
    
    async def handle_calculator_menu(self, query, data):
        """Handle calculator menu callbacks"""
        if data == "calculator":
            keyboard = self.ui.get_calculator_menu_keyboard()
            await query.edit_message_text(
                "🧮 **ماشین حساب**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        elif data == "calculate":
            await query.edit_message_text(
                "🧮 **محاسبه**\n\nعبارت ریاضی خود را ارسال کنید:\nمثال: `2 + 3 * 4`, `sin(pi/2)`, `sqrt(16)`",
                parse_mode="Markdown"
            )
            self.user_states[query.from_user.id] = "calculate"
    
    async def handle_translate_menu(self, query, data):
        """Handle translation menu callbacks"""
        if data == "translate":
            keyboard = self.ui.get_translate_menu_keyboard()
            await query.edit_message_text(
                "🌐 **ترجمه**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        elif data == "translate_text":
            await query.edit_message_text(
                "🌐 **ترجمه متن**\n\nمتن خود را ارسال کنید:\nمثال: `Hello world` یا `سلام دنیا`",
                parse_mode="Markdown"
            )
            self.user_states[query.from_user.id] = "translate_text"
    
    async def handle_settings_menu(self, query, data):
        """Handle settings menu callbacks"""
        if data == "settings":
            keyboard = self.ui.get_settings_menu_keyboard()
            await query.edit_message_text(
                "⚙️ **تنظیمات**\n\nتنظیمات خود را تغییر دهید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        elif data == "set_language":
            keyboard = self.ui.get_language_selection_keyboard()
            await query.edit_message_text(
                "🌍 **انتخاب زبان**\n\nزبان مورد نظر خود را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
    
    async def handle_alerts_menu(self, query, data):
        """Handle alerts menu callbacks"""
        if data == "alerts":
            keyboard = self.ui.get_alerts_menu_keyboard()
            await query.edit_message_text(
                "🚨 **هشدارها**\n\nمدیریت هشدارها و یادآوری‌ها:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        elif data == "my_alerts":
            await self.show_user_alerts(query)
    
    async def handle_general_callback(self, query, data):
        """Handle general callbacks"""
        if data == "my_stats":
            await self.show_user_stats(query)
        elif data.startswith("lang_"):
            await self.set_user_language(query, data)
        else:
            await query.edit_message_text("❌ گزینه انتخابی پشتیبانی نمی‌شود.")
    
    # Message handlers
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        # Update user activity
        self.db.update_user_activity(user_id)
        
        # Check if user has an active state
        if user_id in self.user_states:
            await self.handle_state_message(update, text)
        else:
            await self.handle_smart_message(update, text)
    
    async def handle_state_message(self, update: Update, text: str):
        """Handle messages when user is in a specific state"""
        user_id = update.effective_user.id
        state = self.user_states[user_id]
        
        try:
            if state == "currency_convert":
                await self.process_currency_conversion(update, text)
            elif state.startswith("unit_"):
                await self.process_unit_conversion(update, text, state)
            elif state == "date_convert":
                await self.process_date_conversion(update, text)
            elif state == "stock_price":
                await self.process_stock_price(update, text)
            elif state == "crypto_price":
                await self.process_crypto_price(update, text)
            elif state == "current_weather":
                await self.process_weather_request(update, text)
            elif state == "calculate":
                await self.process_calculation(update, text)
            elif state == "translate_text":
                await self.process_translation(update, text)
            
            # Clear user state after processing
            del self.user_states[user_id]
            
        except Exception as e:
            logger.error(f"Error processing state message: {e}")
            await update.message.reply_text(f"❌ خطا در پردازش: {str(e)}")
            if user_id in self.user_states:
                del self.user_states[user_id]
    
    async def handle_smart_message(self, update: Update, text: str):
        """Handle messages with smart detection"""
        try:
            # Try to detect what the user wants
            if any(keyword in text.lower() for keyword in ["to", "تبدیل", "convert"]):
                if any(curr in text.upper() for curr in ["USD", "EUR", "IRR", "BTC", "ETH"]):
                    await self.process_currency_conversion(update, text)
                elif any(unit in text.lower() for unit in ["km", "mile", "kg", "lb", "celsius", "fahrenheit"]):
                    await self.process_unit_conversion(update, text, "auto")
                else:
                    await update.message.reply_text(
                        "🤔 نمی‌توانم نوع تبدیل را تشخیص دهم.\nلطفاً از منو استفاده کنید.",
                        reply_markup=self.ui.get_main_menu_keyboard()
                    )
            elif text.replace(".", "").replace("-", "").isdigit() and len(text) <= 10:
                # Looks like a date
                await self.process_date_conversion(update, text)
            elif any(keyword in text.lower() for keyword in ["price", "قیمت", "stock", "crypto"]):
                await self.process_price_request(update, text)
            elif any(keyword in text.lower() for keyword in ["weather", "هوا", "آب"]):
                await self.process_weather_request(update, text)
            elif any(op in text for op in ["+", "-", "*", "/", "(", ")", "sin", "cos", "sqrt"]):
                await self.process_calculation(update, text)
            else:
                await update.message.reply_text(
                    "🤔 نمی‌توانم درخواست شما را تشخیص دهم.\nلطفاً از منو استفاده کنید یا متن واضح‌تری ارسال کنید.",
                    reply_markup=self.ui.get_main_menu_keyboard()
                )
        except Exception as e:
            logger.error(f"Error in smart message handling: {e}")
            await update.message.reply_text("❌ خطا در پردازش پیام.")
    
    # Processing methods
    async def process_currency_conversion(self, update: Update, text: str):
        """Process currency conversion"""
        try:
            parts = text.split()
            if len(parts) >= 4 and parts[2].lower() == "to":
                amount = float(parts[0])
                from_curr = parts[1].upper()
                to_curr = parts[3].upper()
                
                result = await self.currency_converter.convert_currency(amount, from_curr, to_curr)
                
                if result["success"]:
                    # Save to history
                    self.db.add_conversion_history(
                        update.effective_user.id,
                        "currency",
                        text,
                        f"{result['result']:.2f} {to_curr}"
                    )
                    
                    await update.message.reply_text(
                        f"💱 **تبدیل ارز**\n\n"
                        f"💰 {amount} {from_curr} = {result['result']:.2f} {to_curr}\n"
                        f"📊 نرخ: {result['rate']:.6f}\n"
                        f"🕐 زمان: {result['timestamp']}\n"
                        f"🔗 منبع: {result['source']}",
                        parse_mode="Markdown"
                    )
                else:
                    await update.message.reply_text(f"❌ {result['error']}")
            else:
                await update.message.reply_text("❌ فرمت اشتباه. مثال: `100 USD to IRR`")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در تبدیل ارز: {str(e)}")
    
    async def process_unit_conversion(self, update: Update, text: str, unit_type: str):
        """Process unit conversion"""
        try:
            parts = text.split()
            if len(parts) >= 4 and parts[2].lower() == "to":
                amount = float(parts[0])
                from_unit = parts[1].lower()
                to_unit = parts[3].lower()
                
                # Detect category if auto
                if unit_type == "auto":
                    categories = self.unit_converter.get_categories()
                    for category in categories:
                        if category != "temperature":
                            units = self.unit_converter.get_units_in_category(category)
                            if from_unit in units and to_unit in units:
                                unit_type = category
                                break
                
                result = self.unit_converter.convert(amount, from_unit, to_unit, unit_type)
                
                if result["success"]:
                    # Save to history
                    self.db.add_conversion_history(
                        update.effective_user.id,
                        f"unit_{unit_type}",
                        text,
                        f"{result['result']:.6f} {to_unit}"
                    )
                    
                    await update.message.reply_text(
                        f"📏 **تبدیل {unit_type}**\n\n"
                        f"📊 {amount} {from_unit} = {result['result']:.6f} {to_unit}",
                        parse_mode="Markdown"
                    )
                else:
                    await update.message.reply_text(f"❌ {result['error']}")
            else:
                await update.message.reply_text("❌ فرمت اشتباه. مثال: `10 km to mile`")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در تبدیل واحد: {str(e)}")
    
    async def process_date_conversion(self, update: Update, text: str):
        """Process date conversion"""
        try:
            result = self.date_converter.convert_date(text)
            
            if result["success"]:
                # Save to history
                self.db.add_conversion_history(
                    update.effective_user.id,
                    "date",
                    text,
                    str(result["conversions"])
                )
                
                formatted_result = self.date_converter.format_date_for_display(result)
                await update.message.reply_text(formatted_result, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در تبدیل تاریخ: {str(e)}")
    
    async def process_stock_price(self, update: Update, text: str):
        """Process stock price request"""
        try:
            symbol = text.upper().strip()
            result = await self.price_tracker.get_stock_price(symbol)
            
            if result["success"]:
                formatted_result = self.price_tracker.format_price_result(result)
                await update.message.reply_text(formatted_result, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت قیمت سهام: {str(e)}")
    
    async def process_crypto_price(self, update: Update, text: str):
        """Process crypto price request"""
        try:
            # Check if multiple symbols are requested
            if "," in text:
                symbols = [s.strip().upper() for s in text.split(",")]
                result = await self.price_tracker.get_multiple_crypto_prices(symbols)
                
                if result["success"]:
                    formatted_result = self.price_tracker.format_multiple_crypto_results(result)
                    await update.message.reply_text(formatted_result, parse_mode="Markdown")
                else:
                    await update.message.reply_text(f"❌ {result['error']}")
            else:
                symbol = text.upper().strip()
                result = await self.price_tracker.get_crypto_price(symbol)
                
                if result["success"]:
                    formatted_result = self.price_tracker.format_price_result(result)
                    await update.message.reply_text(formatted_result, parse_mode="Markdown")
                else:
                    await update.message.reply_text(f"❌ {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت قیمت ارز دیجیتال: {str(e)}")
    
    async def process_price_request(self, update: Update, text: str):
        """Process general price request"""
        try:
            symbol = text.upper().strip()
            
            # Try crypto first
            result = await self.price_tracker.get_crypto_price(symbol)
            if result["success"]:
                formatted_result = self.price_tracker.format_price_result(result)
                await update.message.reply_text(formatted_result, parse_mode="Markdown")
                return
            
            # Try stock
            result = await self.price_tracker.get_stock_price(symbol)
            if result["success"]:
                formatted_result = self.price_tracker.format_price_result(result)
                await update.message.reply_text(formatted_result, parse_mode="Markdown")
                return
            
            await update.message.reply_text(f"❌ نماد {symbol} پیدا نشد.")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت قیمت: {str(e)}")
    
    async def process_weather_request(self, update: Update, text: str):
        """Process weather request"""
        try:
            location = text.strip()
            result = await self.weather_service.get_current_weather(location)
            
            if result["success"]:
                formatted_result = self.weather_service.format_weather_result(result)
                await update.message.reply_text(formatted_result, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت آب و هوا: {str(e)}")
    
    async def process_calculation(self, update: Update, text: str):
        """Process calculation"""
        try:
            result = self.calculator.calculate(text)
            
            if result["success"]:
                # Save to history
                self.db.add_conversion_history(
                    update.effective_user.id,
                    "calculation",
                    text,
                    result["formatted"]
                )
                
                formatted_result = self.calculator.format_calculation_result(result)
                await update.message.reply_text(formatted_result, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در محاسبه: {str(e)}")
    
    async def process_translation(self, update: Update, text: str):
        """Process translation"""
        try:
            # Detect target language (default to Persian for English, English for Persian)
            lang_detection = self.translation_service.detect_language(text)
            source_lang = lang_detection["detected_language"]
            
            if source_lang == "fa":
                target_lang = "en"
            else:
                target_lang = "fa"
            
            result = await self.translation_service.translate_text(text, target_lang, source_lang)
            
            if result["success"]:
                formatted_result = self.translation_service.format_translation_result(result)
                await update.message.reply_text(formatted_result, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در ترجمه: {str(e)}")
    
    # Additional methods
    async def show_current_time(self, query):
        """Show current time in different timezones"""
        try:
            timezones = ["UTC", "IRST", "EST", "PST", "CET"]
            result_text = "🕐 **زمان فعلی در مناطق مختلف:**\n\n"
            
            for tz in timezones:
                time_result = self.date_converter.get_current_time(tz)
                if time_result["success"]:
                    result_text += f"🌍 **{tz}:** {time_result['datetime']}\n"
            
            await query.edit_message_text(result_text, parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(f"❌ خطا در دریافت زمان: {str(e)}")
    
    async def show_user_stats(self, query):
        """Show user statistics"""
        try:
            user_id = query.from_user.id
            stats = self.db.get_user_stats(user_id)
            
            stats_text = f"""
📊 **آمار شما**

🔄 کل تبدیلات: {stats['total_conversions']:,}
🚨 هشدارهای فعال: {stats['active_alerts']:,}
📈 محبوب‌ترین تبدیل: {stats['most_used_conversion'] or 'هیچ'} ({stats['most_used_count']:,} بار)

🕐 آخرین به‌روزرسانی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await query.edit_message_text(stats_text, parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(f"❌ خطا در دریافت آمار: {str(e)}")
    
    async def show_user_alerts(self, query):
        """Show user alerts"""
        try:
            user_id = query.from_user.id
            alerts = []  # Simplified for now
            
            if alerts:
                await query.edit_message_text("📋 هشدارهای شما:")
            else:
                await query.edit_message_text("📋 هیچ هشدار فعالی ندارید")
        except Exception as e:
            await query.edit_message_text(f"❌ خطا در دریافت هشدارها: {str(e)}")
    
    async def set_user_language(self, query, data):
        """Set user language"""
        try:
            lang_code = data.split("_")[1]
            user_id = query.from_user.id
            
            # Update user language in database
            self.db.add_user(
                user_id=user_id,
                username=query.from_user.username,
                first_name=query.from_user.first_name,
                last_name=query.from_user.last_name,
                language_code=lang_code
            )
            
            await query.edit_message_text(f"✅ زبان به {lang_code} تغییر یافت")
        except Exception as e:
            await query.edit_message_text(f"❌ خطا در تغییر زبان: {str(e)}")
    
    async def show_top_crypto(self, query):
        """Show top cryptocurrencies"""
        try:
            result = await self.price_tracker.get_top_crypto_prices(10)
            
            if result["success"]:
                formatted_result = self.price_tracker.format_top_crypto_results(result)
                await query.edit_message_text(formatted_result, parse_mode="Markdown")
            else:
                await query.edit_message_text(f"❌ {result['error']}")
        except Exception as e:
            await query.edit_message_text(f"❌ خطا در دریافت برترین ارزها: {str(e)}")
    
    async def show_crypto_list(self, query):
        """Show supported crypto list"""
        try:
            symbols = self.price_tracker.get_supported_crypto_symbols()
            
            output = "₿ **ارزهای دیجیتال پشتیبانی شده:**\n\n"
            
            # Group symbols in rows of 4
            for i in range(0, len(symbols), 4):
                row_symbols = symbols[i:i+4]
                output += " • ".join(row_symbols) + "\n"
            
            output += f"\n💡 **نکته:** می‌توانید هر کدام از این نمادها را برای دریافت قیمت ارسال کنید."
            
            await query.edit_message_text(output, parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(f"❌ خطا در دریافت لیست ارزها: {str(e)}")
    
    # Inline query handler
    async def handle_inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline queries"""
        query = update.inline_query.query
        
        if not query:
            return
        
        results = []
        
        try:
            # Try to detect what user is looking for
            if any(curr in query.upper() for curr in ["USD", "EUR", "IRR", "BTC", "ETH"]):
                # Currency conversion
                if "to" in query.lower():
                    parts = query.split()
                    if len(parts) >= 4:
                        amount = float(parts[0])
                        from_curr = parts[1].upper()
                        to_curr = parts[3].upper()
                        
                        result = await self.currency_converter.convert_currency(amount, from_curr, to_curr)
                        if result["success"]:
                            results.append({
                                "title": f"{amount} {from_curr} = {result['result']:.2f} {to_curr}",
                                "description": f"نرخ: {result['rate']:.6f}",
                                "message": f"💱 {amount} {from_curr} = {result['result']:.2f} {to_curr}"
                            })
            
            elif any(unit in query.lower() for unit in ["km", "mile", "kg", "lb"]):
                # Unit conversion
                if "to" in query.lower():
                    parts = query.split()
                    if len(parts) >= 4:
                        amount = float(parts[0])
                        from_unit = parts[1].lower()
                        to_unit = parts[3].lower()
                        
                        # Try different categories
                        categories = self.unit_converter.get_categories()
                        for category in categories:
                            if category != "temperature":
                                units = self.unit_converter.get_units_in_category(category)
                                if from_unit in units and to_unit in units:
                                    result = self.unit_converter.convert(amount, from_unit, to_unit, category)
                                    if result["success"]:
                                        results.append({
                                            "title": f"{amount} {from_unit} = {result['result']:.6f} {to_unit}",
                                            "description": f"تبدیل {category}",
                                            "message": f"📏 {amount} {from_unit} = {result['result']:.6f} {to_unit}"
                                        })
                                    break
            
            elif any(op in query for op in ["+", "-", "*", "/", "(", ")", "sin", "cos", "sqrt"]):
                # Calculation
                result = self.calculator.calculate(query)
                if result["success"]:
                    results.append({
                        "title": f"{query} = {result['formatted']}",
                        "description": "محاسبه ریاضی",
                        "message": f"🧮 {query} = {result['formatted']}"
                    })
            
            # Format results for inline query
            if results:
                inline_results = self.ui.get_inline_query_results(query, results)
                await update.inline_query.answer(inline_results)
            
        except Exception as e:
            logger.error(f"Error in inline query: {e}")
    
    def run(self):
        """Run the bot"""
        try:
            # Create application
            app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
            
            # Add handlers
            app.add_handler(CommandHandler("start", self.start_command))
            app.add_handler(CommandHandler("help", self.help_command))
            app.add_handler(CommandHandler("menu", self.menu_command))
            
            app.add_handler(CallbackQueryHandler(self.handle_callback_query))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            app.add_handler(InlineQueryHandler(self.handle_inline_query))
            
            # Start the bot
            logger.info("Starting Simple Telegram Bot...")
            app.run_polling()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            print(f"❌ خطا در شروع ربات: {e}")

if __name__ == "__main__":
    try:
        bot = SimpleTelegramBot()
        bot.run()
    except Exception as e:
        print(f"❌ خطا در اجرای ربات: {e}")
        sys.exit(1)






