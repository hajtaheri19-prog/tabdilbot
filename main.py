import logging
import requests
import jdatetime
from hijridate import Gregorian
from babel.numbers import format_decimal
from typing import Dict, Any

from telegram import (
    Update, InlineKeyboardButton,
    InlineKeyboardMarkup, WebAppInfo, MenuButtonWebApp
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# Import our glass UI components
from glass_ui import GlassUI
from database import Database
from price_tracker import PriceTracker
from currency_converter import CurrencyConverter
from weather_service import WeatherService
from translation_service import TranslationService
from smart_text_processor import SmartTextProcessor
from tabdila_pro.prices import fetch_mofid_basket, get_popular_crypto

# Try to import admin services (optional)
try:
    from admin_service import AdminService
    from advanced_admin_panel import AdvancedAdminPanel
    ADMIN_AVAILABLE = True
except ImportError:
    ADMIN_AVAILABLE = False
    print("Admin services not available - running in basic mode")

# ---- لاگ گیری ----
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---- وضعیت کاربران ----
user_states = {}  # user_id -> mode

# Initialize services
db = Database()

# Initialize feature services
price_tracker = PriceTracker(db)
currency_converter = CurrencyConverter(db)
weather_service = WeatherService(db)
translation_service = TranslationService(db)
smart_processor = SmartTextProcessor()

# Initialize admin services if available
if ADMIN_AVAILABLE:
    admin_service = AdminService(db)
    advanced_admin = AdvancedAdminPanel(db)
else:
    admin_service = None
    advanced_admin = None

# ---- استارت ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # Register user in database
    db.register_user(user_id, update.message.from_user.username, 
                     update.message.from_user.first_name, 
                     update.message.from_user.last_name)
    
    # Show welcome message with tools keyboard
    welcome_text = GlassUI.format_glass_welcome_message()
    tools_keyboard = GlassUI.get_tools_glass_keyboard()
    await update.message.reply_text(welcome_text, reply_markup=tools_keyboard, parse_mode='Markdown')

    # Show permanent reply keyboard with mini app and restart
    permanent_keyboard = GlassUI.get_permanent_reply_keyboard()
    await update.message.reply_text(
        "🚀 برای دسترسی سریع:",
        reply_markup=permanent_keyboard
    )

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع مجدد"""
    # Reset user state if any
    user_id = update.effective_user.id
    if user_id in user_states:
        del user_states[user_id]
    
    # Register user in database
    db.register_user(user_id, update.message.from_user.username, 
                     update.message.from_user.first_name, 
                     update.message.from_user.last_name)
    
    # Show welcome message with tools keyboard
    welcome_text = GlassUI.format_glass_welcome_message()
    tools_keyboard = GlassUI.get_tools_glass_keyboard()
    await update.message.reply_text(welcome_text, reply_markup=tools_keyboard, parse_mode='Markdown')

    # Show permanent reply keyboard with mini app and restart
    permanent_keyboard = GlassUI.get_permanent_reply_keyboard()
    await update.message.reply_text(
        "🚀 برای دسترسی سریع:",
        reply_markup=permanent_keyboard
    )

# ---- هندل کلیک منو ----
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    user_id = query.from_user.id
    user_states[user_id] = choice

    # Update user activity
    db.update_user_activity(user_id)

    if choice == "restart":
        reply_markup = GlassUI.get_main_glass_keyboard()
        await query.edit_message_text(
            GlassUI.format_glass_welcome_message(),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        # Send feedback keyboard as a new message
        try:
            await query.message.reply_text(
                "اگر نظری داری یا مشکلی دیدی، از دکمه‌های زیر استفاده کن:",
                reply_markup=GlassUI.get_feedback_glass_keyboard()
            )
        except Exception:
            pass
    elif choice == "currency":
        reply_markup = GlassUI.get_currency_glass_keyboard()
        await query.edit_message_text(
            "💎 **تبدیل ارز**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "unit":
        reply_markup = GlassUI.get_unit_glass_keyboard()
        await query.edit_message_text(
            "🔮 **تبدیل واحد**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "date_convert":
        await query.edit_message_text(
            "✨ **تبدیل تاریخ**\n\nمثال: `2025-09-14` یا `15/01/2024`",
            reply_markup=GlassUI.get_back_to_main_keyboard(),
            parse_mode='Markdown'
        )
    elif choice == "price":
        reply_markup = GlassUI.get_price_glass_keyboard()
        await query.edit_message_text(
            "💫 **قیمت لحظه‌ای**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "price_crypto_usd":
        await show_crypto_usd_prices(query)
    elif choice == "price_crypto_irr":
        await show_crypto_irr_prices(query)
    elif choice == "price_tgju":
        await show_tgju_prices(query)
    elif choice == "price_all":
        await show_all_prices(query)
    elif choice == "price_bitcoin":
        await show_bitcoin_price(query)
    elif choice == "price_gold_18k":
        await show_gold_18k_price(query)
    elif choice == "price_silver":
        await show_silver_price(query)
    elif choice == "price_gold_ounce":
        await show_gold_ounce_price(query)
    elif choice == "price_crypto_menu":
        reply_markup = GlassUI.get_price_glass_keyboard()
        await query.edit_message_text(
            "💰 **ارزهای دیجیتال**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "price_stocks":
        await query.edit_message_text(
            "📈 **قیمت سهام**\n\nنماد سهام را ارسال کنید:\nمثال: `AAPL`, `TSLA`, `MSFT`",
            reply_markup=GlassUI.get_back_to_main_keyboard(),
            parse_mode='Markdown'
        )
    elif choice == "weather":
        await query.edit_message_text(
            "🌌 **آب و هوا**\n\nنام شهر را ارسال کنید یا موقعیت خود را به اشتراک بگذارید",
            reply_markup=GlassUI.get_back_to_main_keyboard(),
            parse_mode='Markdown'
        )
    elif choice == "calculator":
        await query.edit_message_text(
            "🧿 **ماشین حساب**\n\nعبارت ریاضی را وارد کنید:\nمثال: `2 + 3 * 4` یا `sin(pi/2)`",
            reply_markup=GlassUI.get_back_to_main_keyboard(),
            parse_mode='Markdown'
        )
    elif choice == "translate":
        await query.edit_message_text(
            "🔮 **ترجمه**\n\nمتن مورد نظر را ارسال کنید",
            reply_markup=GlassUI.get_back_to_main_keyboard(),
            parse_mode='Markdown'
        )
    elif choice == "settings":
        reply_markup = GlassUI.get_settings_glass_keyboard()
        await query.edit_message_text(
            "⚡ **تنظیمات**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "my_stats":
        stats = db.get_user_stats(user_id)
        stats_text = f"🌟 **آمار شما**\n\n"
        stats_text += f"📊 کل تبدیلات: {stats.get('total_conversions', 0)}\n"
        stats_text += f"🚨 هشدارهای فعال: {stats.get('active_alerts', 0)}\n"
        stats_text += f"📈 محبوب‌ترین تبدیل: {stats.get('most_used_conversion', 'هیچ')}\n"
        await query.edit_message_text(stats_text, parse_mode='Markdown')
    elif choice == "alerts":
        await query.edit_message_text(
            "💥 **هشدارها**\n\nبرای مدیریت هشدارها، نام ارز یا کالا را ارسال کنید",
            reply_markup=GlassUI.get_back_to_main_keyboard(),
            parse_mode='Markdown'
        )
    elif choice == "feedback":
        user_states[user_id] = "feedback"
        await query.edit_message_text(
            "📝 لطفاً پیشنهاد یا انتقاد خودت رو بنویس و بفرست.",
            parse_mode='Markdown'
        )
    elif choice == "report_bug":
        user_states[user_id] = "report_bug"
        await query.edit_message_text(
            "🐞 لطفاً مشکل یا باگ رو با جزئیات بنویس و بفرست.",
            parse_mode='Markdown'
        )
    elif choice == "back_to_main":
        reply_markup = GlassUI.get_tools_glass_keyboard()
        await query.edit_message_text(
            GlassUI.format_glass_welcome_message(),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "currency_menu":
        reply_markup = GlassUI.get_currency_submenu_keyboard()
        await query.edit_message_text(
            "💎 **تبدیل ارز**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "unit_menu":
        reply_markup = GlassUI.get_unit_submenu_keyboard()
        await query.edit_message_text(
            "🔮 **تبدیل واحد**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "date_menu":
        reply_markup = GlassUI.get_date_submenu_keyboard()
        await query.edit_message_text(
            "✨ **تبدیل تاریخ**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "price_menu":
        reply_markup = GlassUI.get_price_submenu_keyboard()
        await query.edit_message_text(
            "💫 **قیمت لحظه‌ای**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "weather_menu":
        await query.edit_message_text(
            "🌌 **آب و هوا**\n\nنام شهر را ارسال کنید یا موقعیت خود را به اشتراک بگذارید",
            reply_markup=GlassUI.get_back_to_main_keyboard(),
            parse_mode='Markdown'
        )
    elif choice == "calculator_menu":
        await query.edit_message_text(
            "🧿 **ماشین حساب**\n\nعبارت ریاضی را وارد کنید:\nمثال: `2 + 3 * 4` یا `sin(pi/2)`",
            reply_markup=GlassUI.get_back_to_main_keyboard(),
            parse_mode='Markdown'
        )
    elif choice == "translate_menu":
        await query.edit_message_text(
            "🔮 **ترجمه**\n\nمتن مورد نظر را ارسال کنید",
            reply_markup=GlassUI.get_back_to_main_keyboard(),
            parse_mode='Markdown'
        )
    elif choice == "settings_menu":
        reply_markup = GlassUI.get_settings_glass_keyboard()
        await query.edit_message_text(
            "⚡ **تنظیمات**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice.startswith("admin_"):
        # Admin commands
        if ADMIN_AVAILABLE and admin_service and advanced_admin:
            if await admin_service.is_admin(user_id):
                admin_choice = choice.replace("admin_", "")
                
                if admin_choice == "dashboard":
                    # نمایش داشبورد اصلی
                    dashboard_data = await advanced_admin.get_admin_dashboard(user_id)
                    dashboard_text = advanced_admin.format_dashboard_message(dashboard_data)
                    reply_markup = advanced_admin.get_admin_keyboard()
                    await query.edit_message_text(dashboard_text, reply_markup=reply_markup, parse_mode='Markdown')
                    
                elif admin_choice == "stats":
                    stats = await admin_service.get_bot_statistics()
                    stats_text = admin_service.format_statistics(stats)
                    await query.edit_message_text(stats_text, parse_mode='Markdown')
                    
                elif admin_choice == "users":
                    reply_markup = advanced_admin.get_user_management_keyboard()
                    await query.edit_message_text(
                        "👥 **مدیریت کاربران**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    
                elif admin_choice == "user_list":
                    user_data = await advanced_admin.manage_users("list", data={"page": 1, "limit": 10})
                    if user_data["success"]:
                        users_text = admin_service.format_user_list(user_data)
                        reply_markup = advanced_admin.get_user_management_keyboard(
                            user_data["pagination"]["current_page"],
                            user_data["pagination"]["total_pages"]
                        )
                        await query.edit_message_text(users_text, reply_markup=reply_markup, parse_mode='Markdown')
                    else:
                        await query.edit_message_text(f"❌ خطا: {user_data['error']}")
                        
                elif admin_choice == "broadcast":
                    reply_markup = advanced_admin.get_broadcast_keyboard()
                    await query.edit_message_text(
                        "📢 **ارسال پیام گروهی**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    
                elif admin_choice == "settings":
                    reply_markup = advanced_admin.get_system_settings_keyboard()
                    await query.edit_message_text(
                        "⚙️ **تنظیمات سیستم**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    
                elif admin_choice == "maintenance":
                    # تغییر حالت تعمیر
                    current_mode = advanced_admin.maintenance_mode
                    result = await advanced_admin.toggle_maintenance_mode(not current_mode)
                    if result["success"]:
                        status = "فعال" if result["maintenance_mode"] else "غیرفعال"
                        await query.edit_message_text(f"✅ حالت تعمیر {status} شد")
                    else:
                        await query.edit_message_text(f"❌ خطا: {result['error']}")
                        
                elif admin_choice == "cache":
                    # مدیریت کش
                    cache_stats = await advanced_admin.manage_cache("stats")
                    if cache_stats["success"]:
                        stats = cache_stats["cache_stats"]
                        cache_text = f"💾 **آمار کش**\n\n"
                        cache_text += f"📊 کل ورودی‌ها: {stats.get('total_entries', 0)}\n"
                        cache_text += f"✅ ورودی‌های فعال: {stats.get('active_entries', 0)}\n"
                        cache_text += f"📈 نرخ موفقیت: {stats.get('hit_rate', 0):.1%}\n"
                        
                        keyboard = [
                            [
                                GlassUI.get_glass_button("🗑️ پاک کردن کش منقضی", "admin_cache_clear", emoji="🗑️"),
                                GlassUI.get_glass_button("🗑️ پاک کردن تمام کش", "admin_cache_clear_all", emoji="🗑️")
                            ],
                            [
                                GlassUI.get_glass_button("🔙 بازگشت", "admin_settings", emoji="🔙")
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(cache_text, reply_markup=reply_markup, parse_mode='Markdown')
                    else:
                        await query.edit_message_text(f"❌ خطا: {cache_stats['error']}")
                        
                elif admin_choice == "cache_clear":
                    result = await advanced_admin.manage_cache("clear")
                    await query.edit_message_text(f"✅ {result['message']}")
                    
                elif admin_choice == "cache_clear_all":
                    result = await advanced_admin.manage_cache("clear_all")
                    await query.edit_message_text(f"✅ {result['message']}")
                    
                elif admin_choice == "alerts":
                    alerts = await admin_service.get_all_alerts()
                    alerts_text = f"🚨 **هشدارهای فعال**\n\n"
                    alerts_text += f"📊 کل هشدارها: {alerts.get('total_alerts', 0)}\n"
                    alerts_text += f"👥 کاربران دارای هشدار: {alerts.get('users_with_alerts', 0)}\n"
                    await query.edit_message_text(alerts_text, parse_mode='Markdown')
                    
                elif admin_choice == "logs":
                    logs = await admin_service.get_recent_logs()
                    logs_text = f"📋 **لاگ‌های اخیر**\n\n"
                    logs_text += logs.get("message", "لاگ‌گیری در این نسخه پیاده‌سازی نشده است")
                    await query.edit_message_text(logs_text, parse_mode='Markdown')
                    
                elif admin_choice == "back_to_admin":
                    # بازگشت به پنل اصلی ادمین
                    dashboard_data = await advanced_admin.get_admin_dashboard(user_id)
                    dashboard_text = advanced_admin.format_dashboard_message(dashboard_data)
                    reply_markup = advanced_admin.get_admin_keyboard()
                    await query.edit_message_text(dashboard_text, reply_markup=reply_markup, parse_mode='Markdown')
                    
                else:
                    await query.edit_message_text("🔧 این قابلیت در حال توسعه است")
            else:
                await query.edit_message_text("❌ شما دسترسی ادمین ندارید")
        else:
            await query.edit_message_text("❌ سرویس‌های مدیریت در دسترس نیست")

# ---- هندل ورودی عادی ----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    # به‌روزرسانی فعالیت کاربر
    db.update_user_activity(user_id)
    
    # Handle restart button press
    if text == "🔄 شروع مجدد":
        await restart_command(update, context)
        return
    
    # اگر کاربر در حالت خاصی نیست، سعی کن خودکار تشخیص بده
    if user_id not in user_states:
        # تشخیص هوشمند نوع درخواست
        detection_result = smart_processor.detect_request_type(text)
        
        if detection_result['type'] != 'unknown' and detection_result['confidence'] > 0.6:
            # پردازش بر اساس نوع تشخیص داده شده
            if detection_result['type'] == 'currency':
                await process_smart_currency_conversion(update, detection_result['data'])
            elif detection_result['type'] == 'unit':
                await process_smart_unit_conversion(update, detection_result['data'])
            elif detection_result['type'] == 'date':
                await process_smart_date_conversion(update, detection_result['data'])
            elif detection_result['type'] == 'price':
                await process_smart_price_request(update, detection_result['data'])
            elif detection_result['type'] == 'weather':
                await process_smart_weather_request(update, detection_result['data'])
            elif detection_result['type'] == 'calculation':
                await process_smart_calculation(update, detection_result['data'])
            elif detection_result['type'] == 'translation':
                await process_smart_translation(update, detection_result['data'])
        else:
            # اگر تشخیص داده نشد، راهنمایی نمایش بده
            await update.message.reply_text(
                "🔍 نمی‌تونم نوع درخواست شما رو تشخیص بدم!\n\n"
                "لطفاً از منوی اصلی استفاده کنید یا یکی از فرمت‌های زیر را امتحان کنید:\n\n"
                "💎 تبدیل ارز: `100 USD to IRR` یا `1 بیت کوین به دلار`\n"
                "🔮 تبدیل واحد: `10 km to mile` یا `5 کیلوگرم به پوند`\n"
                "✨ تبدیل تاریخ: `2024-01-15` یا `15/01/1403`\n"
                "💫 قیمت: `BTC` یا `طلا` یا `AAPL`\n"
                "🌤️ آب و هوا: `تهران` یا `آب و هوای اصفهان`\n"
                "🧮 محاسبه: `2 + 3 * 4` یا `sin(pi/2)`\n"
                "🌐 ترجمه: `Hello world` یا `سلام دنیا`",
                parse_mode='Markdown'
            )
        return

    choice = user_states[user_id]

    try:
        if choice == "currency":
            await convert_currency(update, text)
        elif choice == "unit":
            await convert_unit(update, text)
        elif choice == "date_convert":
            await convert_date(update, text)
        elif choice == "price":
            await get_price(update, text)
        elif choice == "weather":
            await get_weather(update, text)
        elif choice == "calculator":
            await calculate(update, text)
        elif choice == "translate":
            await translate_text(update, text)
        elif choice == "feedback":
            db.add_notification(user_id, "feedback", text, {"source": "inline"})
            await update.message.reply_text("✅ ممنون! بازخوردت ثبت شد.", reply_markup=GlassUI.get_back_to_main_keyboard())
            del user_states[user_id]
        elif choice == "report_bug":
            db.add_notification(user_id, "bug_report", text, {"source": "inline"})
            await update.message.reply_text("✅ گزارش خرابی دریافت شد. به‌زودی بررسی می‌کنیم.", reply_markup=GlassUI.get_back_to_main_keyboard())
            del user_states[user_id]
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")
        print(f"Error in handle_message: {e}")

# ---- پردازشگرهای هوشمند ----
async def process_smart_currency_conversion(update: Update, data: Dict[str, Any]):
    """پردازش هوشمند تبدیل ارز"""
    try:
        if data.get('amount') and data.get('from_currency') and data.get('to_currency'):
            result = await currency_converter.convert_currency(
                data['amount'], 
                data['from_currency'], 
                data['to_currency']
            )
            if result.get("success"):
                formatted = format_decimal(result["result"], locale="fa")
                await update.message.reply_text(
                    f"💱 **تبدیل ارز**\n\n"
                    f"💰 {data['amount']} {data['from_currency']} = {formatted} {data['to_currency']}\n"
                    f"📊 نرخ: {result['rate']:.6f}\n"
                    f"🕐 زمان: {result['timestamp']}",
                    parse_mode='Markdown',
                    reply_markup=GlassUI.get_permanent_reply_keyboard()
                )
            else:
                await update.message.reply_text(
                    f"❌ خطا در تبدیل ارز: {result.get('error', 'نامشخص')}",
                    reply_markup=GlassUI.get_permanent_reply_keyboard()
                )
        else:
            # اگر داده کامل نیست، پیام راهنما بده
            await update.message.reply_text(
                "💱 **تبدیل ارز**\n\n"
                "لطفاً فرمت صحیح را استفاده کنید:\n"
                "`100 USD to IRR`\n"
                "`1 BTC to USD`\n"
                "`500 یورو به ریال`",
                parse_mode='Markdown',
                reply_markup=GlassUI.get_permanent_reply_keyboard()
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در پردازش تبدیل ارز: {str(e)}",
            reply_markup=GlassUI.get_permanent_reply_keyboard()
        )

async def process_smart_unit_conversion(update: Update, data: Dict[str, Any]):
    """پردازش هوشمند تبدیل واحد"""
    try:
        if data.get('amount') and data.get('from_unit') and data.get('to_unit'):
            # اینجا باید از unit_converter استفاده کنی
            await update.message.reply_text(
                f"📏 **تبدیل {data['unit_type']}**\n\n"
                f"در حال پردازش: {data['amount']} {data['from_unit']} به {data['to_unit']}",
                parse_mode='Markdown',
                reply_markup=GlassUI.get_permanent_reply_keyboard()
            )
        else:
            await update.message.reply_text(
                f"📏 **تبدیل {data['unit_type']}**\n\n"
                "لطفاً فرمت صحیح را استفاده کنید:\n"
                "`10 km to mile`\n"
                "`5 کیلوگرم به پوند`",
                parse_mode='Markdown',
                reply_markup=GlassUI.get_permanent_reply_keyboard()
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در پردازش تبدیل واحد: {str(e)}",
            reply_markup=GlassUI.get_permanent_reply_keyboard()
        )

async def process_smart_date_conversion(update: Update, data: Dict[str, Any]):
    """پردازش هوشمند تبدیل تاریخ"""
    try:
        date_string = data.get('date_string', '')
        if date_string:
            await convert_date(update, date_string)
        else:
            await update.message.reply_text(
                "📅 **تبدیل تاریخ**\n\n"
                "لطفاً فرمت صحیح را استفاده کنید:\n"
                "`2024-01-15`\n"
                "`15/01/1403`\n"
                "`15 Jan 2024`",
                parse_mode='Markdown',
                reply_markup=GlassUI.get_permanent_reply_keyboard()
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در پردازش تبدیل تاریخ: {str(e)}",
            reply_markup=GlassUI.get_permanent_reply_keyboard()
        )

async def process_smart_price_request(update: Update, data: Dict[str, Any]):
    """پردازش هوشمند درخواست قیمت"""
    try:
        symbols = data.get('all_symbols', [])
        if symbols:
            # اولین نماد را برای قیمت درخواست کن
            await get_price(update, symbols[0])
        else:
            await update.message.reply_text(
                "💫 **قیمت لحظه‌ای**\n\n"
                "لطفاً نماد مورد نظر را وارد کنید:\n"
                "`BTC` - بیت کوین\n"
                "`طلا` - قیمت طلا\n"
                "`AAPL` - سهام اپل",
                parse_mode='Markdown',
                reply_markup=GlassUI.get_permanent_reply_keyboard()
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در پردازش درخواست قیمت: {str(e)}",
            reply_markup=GlassUI.get_permanent_reply_keyboard()
        )

async def process_smart_weather_request(update: Update, data: Dict[str, Any]):
    """پردازش هوشمند درخواست آب و هوا"""
    try:
        location = data.get('location', '')
        if location:
            await get_weather(update, location)
        else:
            await update.message.reply_text(
                "🌤️ **آب و هوا**\n\n"
                "لطفاً نام شهر را وارد کنید:\n"
                "`تهران`\n"
                "`آب و هوای اصفهان`\n"
                "`London`",
                parse_mode='Markdown',
                reply_markup=GlassUI.get_permanent_reply_keyboard()
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در پردازش درخواست آب و هوا: {str(e)}",
            reply_markup=GlassUI.get_permanent_reply_keyboard()
        )

async def process_smart_calculation(update: Update, data: Dict[str, Any]):
    """پردازش هوشمند محاسبه"""
    try:
        expression = data.get('expression', '')
        if expression:
            await calculate(update, expression)
        else:
            await update.message.reply_text(
                "🧮 **ماشین حساب**\n\n"
                "لطفاً عبارت ریاضی را وارد کنید:\n"
                "`2 + 3 * 4`\n"
                "`sin(pi/2)`\n"
                "`sqrt(16)`",
                parse_mode='Markdown',
                reply_markup=GlassUI.get_permanent_reply_keyboard()
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در پردازش محاسبه: {str(e)}",
            reply_markup=GlassUI.get_permanent_reply_keyboard()
        )

async def process_smart_translation(update: Update, data: Dict[str, Any]):
    """پردازش هوشمند ترجمه"""
    try:
        text_to_translate = data.get('text', '')
        if text_to_translate:
            await translate_text(update, text_to_translate)
        else:
            await update.message.reply_text(
                "🌐 **ترجمه**\n\n"
                "لطفاً متن مورد نظر را وارد کنید:\n"
                "`Hello world`\n"
                "`سلام دنیا`",
                parse_mode='Markdown',
                reply_markup=GlassUI.get_permanent_reply_keyboard()
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در پردازش ترجمه: {str(e)}",
            reply_markup=GlassUI.get_permanent_reply_keyboard()
        )

# ---- تبدیل ارز ----
async def convert_currency(update: Update, text: str):
    try:
        amount, from_curr, _, to_curr = text.split()
        amount_val = float(amount)
        result = await currency_converter.convert_currency(amount_val, from_curr, to_curr)
        if result.get("success"):
            formatted = format_decimal(result["result"], locale="fa")
            await update.message.reply_text(
                f"{amount} {from_curr.upper()} = {formatted} {to_curr.upper()}",
                reply_markup=GlassUI.get_permanent_reply_keyboard()
            )
        else:
            await update.message.reply_text(f"❌ {result.get('error','داده پیدا نشد')}", reply_markup=GlassUI.get_permanent_reply_keyboard())
    except Exception:
        await update.message.reply_text("❌ فرمت اشتباه. مثال: 100 USD to IRR", reply_markup=GlassUI.get_permanent_reply_keyboard())

# ---- تبدیل واحد ----
async def convert_unit(update: Update, text: str):
    units = {
        ("km", "mile"): 0.621371,
        ("mile", "km"): 1.60934
    }
    try:
        amount, from_unit, _, to_unit = text.split()
        key = (from_unit.lower(), to_unit.lower())
        if key in units:
            result = float(amount) * units[key]
            await update.message.reply_text(f"{amount} {from_unit} = {result} {to_unit}", reply_markup=GlassUI.get_back_to_main_keyboard())
        else:
            await update.message.reply_text("⚠️ این واحد پشتیبانی نمی‌شود.", reply_markup=GlassUI.get_back_to_main_keyboard())
    except Exception:
        await update.message.reply_text("❌ فرمت اشتباه. مثال: 10 km to mile", reply_markup=GlassUI.get_back_to_main_keyboard())

# ---- تبدیل تاریخ ----
async def convert_date(update: Update, text: str):
    try:
        y, m, d = map(int, text.split("-"))
        greg = Gregorian(y, m, d)
        persian_date = jdatetime.date.fromgregorian(date=greg.to_gregorian())
        hijri_date = greg.to_hijri()
        await update.message.reply_text(
            f"📅 شمسی: {persian_date.strftime('%Y/%m/%d')}\n"
            f"🕋 قمری: {hijri_date}",
            reply_markup=GlassUI.get_back_to_main_keyboard()
        )
    except Exception:
        await update.message.reply_text("❌ فرمت اشتباه. مثال: 2025-09-14", reply_markup=GlassUI.get_back_to_main_keyboard())

# ---- قیمت لحظه‌ای ----
async def get_price(update: Update, text: str):
    # Try to detect crypto tickers first (common ones), else show info text
    symbol = text.strip().upper()
    result = await price_tracker.get_crypto_price(symbol)
    if result.get("success"):
        msg = price_tracker.format_price_result(result)
        await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=GlassUI.get_back_to_main_keyboard())
        return
    await update.message.reply_text(
        f"💫 داده قیمت برای '{text}' در حال حاضر در دسترس نیست",
        reply_markup=GlassUI.get_back_to_main_keyboard()
    )

# ---- آب و هوا ----
async def get_weather(update: Update, text: str):
    result = await weather_service.get_current_weather(text)
    msg = weather_service.format_weather_result(result)
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=GlassUI.get_back_to_main_keyboard())

# ---- ماشین حساب ----
async def calculate(update: Update, text: str):
    import ast
    import operator as op

    # اپراتورهای مجاز
    allowed_operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: op.pow,
        ast.Mod: op.mod,
        ast.USub: op.neg,
        ast.UAdd: op.pos,
    }

    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            operator = allowed_operators.get(type(node.op))
            if operator is None:
                raise ValueError("operator_not_allowed")
            return operator(left, right)
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            operator = allowed_operators.get(type(node.op))
            if operator is None:
                raise ValueError("operator_not_allowed")
            return operator(operand)
        raise ValueError("expression_not_allowed")

    try:
        expr = ast.parse(text, mode='eval').body
        result = _eval(expr)
        await update.message.reply_text(
            f"🧿 **نتیجه محاسبه:**\n\n"
            f"`{text} = {result}`",
            parse_mode='Markdown',
            reply_markup=GlassUI.get_back_to_main_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در محاسبه: {e}\n\n"
            "💡 مثال‌های صحیح:\n"
            "• `2 + 3 * 4`\n"
            "• `10 / 2`\n"
            "• `2 ** 3`",
            reply_markup=GlassUI.get_back_to_main_keyboard()
        )

# ---- ترجمه ----
async def translate_text(update: Update, text: str):
    result = await translation_service.translate_text(text, target_lang="fa")
    msg = translation_service.format_translation_result(result)
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=GlassUI.get_back_to_main_keyboard())

# ---- داده ارسالی از مینی‌اپ ----
async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.message.web_app_data.data
    await update.message.reply_text(f"📦 داده از مینی‌اپ: {data}")

# ---- دستورات اضافی ----
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور راهنما"""
    help_text = GlassUI.format_glass_help_message()
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def basket_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش سبد گران مفید (TGJU)"""
    data = fetch_mofid_basket()
    if not data.get("ok") and data.get("status") != "success":
        # normalize both wrappers
        err = data.get("error") or data.get("message") or "خطای نامشخص"
        await update.message.reply_text(f"❌ خطا در دریافت داده: {err}")
        return

    # unify
    payload = data.get("data") if "data" in data else data
    if "data" in payload:
        payload = payload["data"]

    lines = ["📦 سبد گران مفید:"]
    for k, v in payload.items():
        price = v.get("price")
        change = v.get("change")
        lines.append(f"• {k}: {price} ({change})")

    await update.message.reply_text("\n".join(lines), reply_markup=GlassUI.get_back_to_main_keyboard())

async def popular_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قیمت محبوب‌ترین ارزهای دیجیتال"""
    data = get_popular_crypto()
    if not data.get("ok"):
        await update.message.reply_text(f"❌ خطا: {data.get('error', 'نامشخص')}")
        return
    coins = data.get("popular", [])
    if not coins:
        await update.message.reply_text("داده‌ای یافت نشد")
        return
    lines = ["💹 محبوب‌ترین رمزارزها (USD):"]
    for c in coins:
        lines.append(f"• {c['symbol']}: ${c['price_usd']} ({c['change_percent_24h']}%)")
    await update.message.reply_text("\n".join(lines), reply_markup=GlassUI.get_back_to_main_keyboard())

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور منو"""
    reply_markup = GlassUI.get_main_glass_keyboard()
    await update.message.reply_text(
        "🎯 **منوی اصلی**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور تنظیمات"""
    reply_markup = GlassUI.get_settings_glass_keyboard()
    await update.message.reply_text(
        "⚡ **تنظیمات**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور مدیریت"""
    user_id = update.message.from_user.id
    
    if ADMIN_AVAILABLE and admin_service and advanced_admin:
        if await admin_service.is_admin(user_id):
            # نمایش داشبورد اصلی ادمین
            dashboard_data = await advanced_admin.get_admin_dashboard(user_id)
            dashboard_text = advanced_admin.format_dashboard_message(dashboard_data)
            reply_markup = advanced_admin.get_admin_keyboard()
            await update.message.reply_text(
                dashboard_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید")
    else:
        await update.message.reply_text("❌ سرویس‌های مدیریت در دسترس نیست")

# New price handler functions
async def show_crypto_usd_prices(query):
    """Show crypto prices in USD"""
    try:
        result = await price_tracker._get_binance_popular_data()
        if result["success"] and result.get("popular"):
            message = "💰 **ارزهای دیجیتال محبوب (USD)**:\n\n"
            for coin in result["popular"]:
                change_emoji = "📈" if coin["change_percent_24h"] >= 0 else "📉"
                change_sign = "+" if coin["change_percent_24h"] >= 0 else ""
                message += (
                    f"• {coin['name']} ({coin['symbol']}): ${coin['price_usd']:,.2f} "
                    f"{change_emoji} {change_sign}{coin['change_percent_24h']:.2f}%\n"
                )
            message += f"\n🕐 زمان: {result['timestamp']}"
        else:
            message = f"❌ خطا در دریافت داده: {result.get('error', 'نامشخص')}"
        
        await query.edit_message_text(
            message,
            reply_markup=GlassUI.get_price_glass_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ خطا در دریافت قیمت‌ها: {str(e)}",
            reply_markup=GlassUI.get_price_glass_keyboard()
        )

async def show_crypto_irr_prices(query):
    """Show crypto prices in IRR"""
    try:
        result = await price_tracker._get_crypto_irr_data()
        if result["success"] and result.get("data"):
            message = "🌐 **ارزهای دیجیتال (IRR)**:\n\n"
            for name, crypto_data in result["data"].items():
                price = crypto_data["price_rial"]
                change_percent = crypto_data["change_percent"]
                change_value = crypto_data["change_value_tether"]
                
                if price is not None:
                    change_emoji = "📈" if change_percent and change_percent >= 0 else "📉"
                    change_sign = "+" if change_percent and change_percent >= 0 else ""
                    change_text = f"{change_sign}{change_percent:.2f}%" if change_percent is not None else "نامشخص"
                    message += f"• {name}: {price:,.0f} {change_emoji} {change_text} ({change_value})\n"
                else:
                    message += f"• {name}: نامشخص ({change_value})\n"
            message += f"\n🕐 زمان: {result['timestamp']}"
        else:
            message = f"❌ خطا در دریافت داده: {result.get('error', 'نامشخص')}"
        
        await query.edit_message_text(
            message,
            reply_markup=GlassUI.get_price_glass_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ خطا در دریافت قیمت‌ها: {str(e)}",
            reply_markup=GlassUI.get_price_glass_keyboard()
        )

async def show_tgju_prices(query):
    """Show TGJU asset prices"""
    try:
        result = await price_tracker._get_tgju_data()
        if result["success"] and result.get("data"):
            message = "🏦 **دارایی‌ها (IRR)**:\n\n"
            for title, asset_data in result["data"].items():
                price = asset_data["price"]
                change = asset_data["change"]
                if price is not None:
                    message += f"• {title}: {price:,.0f} ({change})\n"
                else:
                    message += f"• {title}: نامشخص ({change})\n"
            message += f"\n🕐 زمان: {result['timestamp']}"
        else:
            message = f"❌ خطا در دریافت داده: {result.get('error', 'نامشخص')}"
        
        await query.edit_message_text(
            message,
            reply_markup=GlassUI.get_price_glass_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ خطا در دریافت قیمت‌ها: {str(e)}",
            reply_markup=GlassUI.get_price_glass_keyboard()
        )

async def show_all_prices(query):
    """Show all integrated prices"""
    try:
        result = await price_tracker.get_integrated_price_data()
        message = price_tracker.format_integrated_price_message(result)
        
        await query.edit_message_text(
            message,
            reply_markup=GlassUI.get_price_glass_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ خطا در دریافت قیمت‌ها: {str(e)}",
            reply_markup=GlassUI.get_price_glass_keyboard()
        )

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور قیمت - نمایش همه قیمت‌ها"""
    try:
        result = await price_tracker.get_integrated_price_data()
        message = price_tracker.format_integrated_price_message(result)
        
        await update.message.reply_text(
            message,
            reply_markup=GlassUI.get_price_glass_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در دریافت قیمت‌ها: {str(e)}",
            reply_markup=GlassUI.get_back_to_main_keyboard()
        )

async def show_bitcoin_price(query):
    """Show Bitcoin price"""
    try:
        result = await price_tracker.get_crypto_price("BTC")
        if result["success"]:
            price = result["price"]
            change = result.get("change_24h", 0)
            change_emoji = "📈" if change >= 0 else "📉"
            change_sign = "+" if change >= 0 else ""
            
            message = f"₿ **بیت کوین (Bitcoin)**\n\n"
            message += f"💰 قیمت: ${price:,.2f}\n"
            message += f"📊 تغییر 24h: {change_emoji} {change_sign}{change:.2f}%\n"
            message += f"🕐 زمان: {result.get('timestamp', 'نامشخص')}"
        else:
            message = f"❌ خطا در دریافت قیمت بیت کوین: {result.get('error', 'نامشخص')}"
        
        await query.edit_message_text(
            message,
            reply_markup=GlassUI.get_price_submenu_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ خطا در دریافت قیمت بیت کوین: {str(e)}",
            reply_markup=GlassUI.get_price_submenu_keyboard()
        )

async def show_gold_18k_price(query):
    """Show 18k Gold price"""
    try:
        result = await price_tracker.get_commodity_price("GOLD")
        if result["success"]:
            price = result["price"]
            change = result.get("change_24h", 0)
            change_emoji = "📈" if change >= 0 else "📉"
            change_sign = "+" if change >= 0 else ""
            
            message = f"🥇 **طلای 18 عیار**\n\n"
            message += f"💰 قیمت: ${price:,.2f} per ounce\n"
            message += f"📊 تغییر 24h: {change_emoji} {change_sign}{change:.2f}%\n"
            message += f"🕐 زمان: {result.get('timestamp', 'نامشخص')}"
        else:
            message = f"❌ خطا در دریافت قیمت طلا: {result.get('error', 'نامشخص')}"
        
        await query.edit_message_text(
            message,
            reply_markup=GlassUI.get_price_submenu_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ خطا در دریافت قیمت طلا: {str(e)}",
            reply_markup=GlassUI.get_price_submenu_keyboard()
        )

async def show_silver_price(query):
    """Show Silver price"""
    try:
        result = await price_tracker.get_commodity_price("SILVER")
        if result["success"]:
            price = result["price"]
            change = result.get("change_24h", 0)
            change_emoji = "📈" if change >= 0 else "📉"
            change_sign = "+" if change >= 0 else ""
            
            message = f"🥈 **نقره (Silver)**\n\n"
            message += f"💰 قیمت: ${price:,.2f} per ounce\n"
            message += f"📊 تغییر 24h: {change_emoji} {change_sign}{change:.2f}%\n"
            message += f"🕐 زمان: {result.get('timestamp', 'نامشخص')}"
        else:
            message = f"❌ خطا در دریافت قیمت نقره: {result.get('error', 'نامشخص')}"
        
        await query.edit_message_text(
            message,
            reply_markup=GlassUI.get_price_submenu_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ خطا در دریافت قیمت نقره: {str(e)}",
            reply_markup=GlassUI.get_price_submenu_keyboard()
        )

async def show_gold_ounce_price(query):
    """Show Gold ounce price"""
    try:
        result = await price_tracker.get_commodity_price("GOLD")
        if result["success"]:
            price = result["price"]
            change = result.get("change_24h", 0)
            change_emoji = "📈" if change >= 0 else "📉"
            change_sign = "+" if change >= 0 else ""
            
            message = f"💎 **انس طلا (Gold Ounce)**\n\n"
            message += f"💰 قیمت: ${price:,.2f} per ounce\n"
            message += f"📊 تغییر 24h: {change_emoji} {change_sign}{change:.2f}%\n"
            message += f"🕐 زمان: {result.get('timestamp', 'نامشخص')}"
        else:
            message = f"❌ خطا در دریافت قیمت انس طلا: {result.get('error', 'نامشخص')}"
        
        await query.edit_message_text(
            message,
            reply_markup=GlassUI.get_price_submenu_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ خطا در دریافت قیمت انس طلا: {str(e)}",
            reply_markup=GlassUI.get_price_submenu_keyboard()
        )

# ---- اجرای برنامه ----
def main():
    app = ApplicationBuilder().token("8308943984:AAGpg52VoSSpuwWRpVrDRZ-4SDA52__ybqQ").build()

    async def setup_menu_button(app_):
        try:
            await app_.bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="🚀 مینی‌اپ",
                    web_app=WebAppInfo(url="https://bot-nine-ochre.vercel.app/")
                )
            )
        except Exception as e:
            logging.warning(f"Failed to set menu button: {e}")

    app.post_init = setup_menu_button
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", restart_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("basket", basket_command))
    app.add_handler(CommandHandler("popular", popular_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("price", price_command))
    
    # Callback and message handlers
    app.add_handler(CallbackQueryHandler(handle_menu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    
    app.run_polling()

if __name__ == "__main__":
    main()
