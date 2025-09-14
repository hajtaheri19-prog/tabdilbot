import logging
import requests
import jdatetime
from hijridate import Gregorian
from babel.numbers import format_decimal

from telegram import (
    Update, InlineKeyboardButton,
    InlineKeyboardMarkup, WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# Import our glass UI components
from glass_ui import GlassUI
from admin_service import AdminService
from advanced_admin_panel import AdvancedAdminPanel
from database import Database

# ---- لاگ گیری ----
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---- وضعیت کاربران ----
user_states = {}  # user_id -> mode

# Initialize services
db = Database()
admin_service = AdminService(db)
advanced_admin = AdvancedAdminPanel(db)

# ---- استارت ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # Register user in database
    db.register_user(user_id, update.message.from_user.username, 
                     update.message.from_user.first_name, 
                     update.message.from_user.last_name)
    
    # Get glass keyboard
    reply_markup = GlassUI.get_main_glass_keyboard()
    
    # Send welcome message with glass UI
    welcome_text = GlassUI.format_glass_welcome_message()
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
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

    if choice == "currency":
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
            parse_mode='Markdown'
        )
    elif choice == "price":
        reply_markup = GlassUI.get_price_glass_keyboard()
        await query.edit_message_text(
            "💫 **قیمت لحظه‌ای**\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice == "weather":
        await query.edit_message_text(
            "🌌 **آب و هوا**\n\nنام شهر را ارسال کنید یا موقعیت خود را به اشتراک بگذارید",
            parse_mode='Markdown'
        )
    elif choice == "calculator":
        await query.edit_message_text(
            "🧿 **ماشین حساب**\n\nعبارت ریاضی را وارد کنید:\nمثال: `2 + 3 * 4` یا `sin(pi/2)`",
            parse_mode='Markdown'
        )
    elif choice == "translate":
        await query.edit_message_text(
            "🔮 **ترجمه**\n\nمتن مورد نظر را ارسال کنید",
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
            parse_mode='Markdown'
        )
    elif choice == "back_to_main":
        reply_markup = GlassUI.get_main_glass_keyboard()
        await query.edit_message_text(
            GlassUI.format_glass_welcome_message(),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif choice.startswith("admin_"):
        # Admin commands
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

# ---- هندل ورودی عادی ----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_states:
        await update.message.reply_text("اول از /start شروع کن 😊")
        return

    choice = user_states[user_id]
    text = update.message.text.strip()

    try:
        if choice == "currency":
            await convert_currency(update, text)
        elif choice == "unit":
            await convert_unit(update, text)
        elif choice == "date_convert":
            await convert_date(update, text)
        elif choice == "price":
            await get_price(update, text)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

# ---- تبدیل ارز ----
async def convert_currency(update: Update, text: str):
    try:
        amount, from_curr, _, to_curr = text.split()
        url = f"https://api.exchangerate.host/convert?from={from_curr.upper()}&to={to_curr.upper()}&amount={amount}"
        res = requests.get(url).json()

        if res.get("result"):
            formatted = format_decimal(res["result"], locale="fa")
            await update.message.reply_text(
                f"{amount} {from_curr.upper()} = {formatted} {to_curr.upper()}"
            )
        else:
            await update.message.reply_text("⚠️ داده پیدا نشد.")
    except Exception:
        await update.message.reply_text("❌ فرمت اشتباه. مثال: 100 USD to IRR")

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
            await update.message.reply_text(f"{amount} {from_unit} = {result} {to_unit}")
        else:
            await update.message.reply_text("⚠️ این واحد پشتیبانی نمی‌شود.")
    except Exception:
        await update.message.reply_text("❌ فرمت اشتباه. مثال: 10 km to mile")

# ---- تبدیل تاریخ ----
async def convert_date(update: Update, text: str):
    try:
        y, m, d = map(int, text.split("-"))
        greg = Gregorian(y, m, d)
        persian_date = jdatetime.date.fromgregorian(date=greg.to_gregorian())
        hijri_date = greg.to_hijri()
        await update.message.reply_text(
            f"📅 شمسی: {persian_date.strftime('%Y/%m/%d')}\n"
            f"🕋 قمری: {hijri_date}"
        )
    except Exception:
        await update.message.reply_text("❌ فرمت اشتباه. مثال: 2025-09-14")

# ---- قیمت لحظه‌ای ----
async def get_price(update: Update, text: str):
    await update.message.reply_text(
        f"🔍 داده قیمت برای '{text}' هنوز به API وصل نشده"
    )

# ---- داده ارسالی از مینی‌اپ ----
async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.message.web_app_data.data
    await update.message.reply_text(f"📦 داده از مینی‌اپ: {data}")

# ---- دستورات اضافی ----
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور راهنما"""
    help_text = GlassUI.format_glass_help_message()
    await update.message.reply_text(help_text, parse_mode='Markdown')

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

# ---- اجرای برنامه ----
def main():
    app = ApplicationBuilder().token("8308943984:AAGpg52VoSSpuwWRpVrDRZ-4SDA52__ybqQ").build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("admin", admin_command))
    
    # Callback and message handlers
    app.add_handler(CallbackQueryHandler(handle_menu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    
    app.run_polling()

if __name__ == "__main__":
    main()
