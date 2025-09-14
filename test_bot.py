"""
🧪 Test Bot - تست ربات
فایل تست برای بررسی عملکرد ربات
"""

import asyncio
import logging
from database import Database
from glass_ui import GlassUI

# تنظیم لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database():
    """تست پایگاه داده"""
    print("🗄️ Testing database...")
    
    try:
        db = Database()
        print("✅ Database initialized successfully")
        
        # تست ثبت کاربر
        result = db.register_user(123456789, "test_user", "Test", "User")
        print(f"✅ User registration: {result}")
        
        # تست دریافت کاربر
        user = db.get_user(123456789)
        print(f"✅ User retrieval: {user is not None}")
        
        # تست آمار کاربر
        stats = db.get_user_stats(123456789)
        print(f"✅ User stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_glass_ui():
    """تست رابط کاربری شیشه‌ای"""
    print("🎨 Testing Glass UI...")
    
    try:
        # تست کیبورد اصلی
        main_keyboard = GlassUI.get_main_glass_keyboard()
        print(f"✅ Main keyboard: {len(main_keyboard.inline_keyboard)} rows")
        
        # تست کیبورد ارز
        currency_keyboard = GlassUI.get_currency_glass_keyboard()
        print(f"✅ Currency keyboard: {len(currency_keyboard.inline_keyboard)} rows")
        
        # تست پیام خوش‌آمدگویی
        welcome_message = GlassUI.format_glass_welcome_message()
        print(f"✅ Welcome message: {len(welcome_message)} characters")
        
        # تست پیام راهنما
        help_message = GlassUI.format_glass_help_message()
        print(f"✅ Help message: {len(help_message)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Glass UI test failed: {e}")
        return False

async def test_admin_services():
    """تست سرویس‌های ادمین"""
    print("👑 Testing Admin Services...")
    
    try:
        from admin_service import AdminService
        from advanced_admin_panel import AdvancedAdminPanel
        
        db = Database()
        admin_service = AdminService(db)
        advanced_admin = AdvancedAdminPanel(db)
        
        # تست بررسی ادمین
        is_admin = await admin_service.is_admin(123456789)
        print(f"✅ Admin check: {is_admin}")
        
        # تست آمار ربات
        stats = await admin_service.get_bot_statistics()
        print(f"✅ Bot statistics: {stats['success']}")
        
        # تست داشبورد ادمین
        dashboard = await advanced_admin.get_admin_dashboard(123456789)
        print(f"✅ Admin dashboard: {dashboard['success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Admin services test failed: {e}")
        return False

async def main():
    """تست اصلی"""
    print("🚀 Starting Bot Tests...\n")
    
    # تست پایگاه داده
    db_test = await test_database()
    print()
    
    # تست رابط کاربری
    ui_test = test_glass_ui()
    print()
    
    # تست سرویس‌های ادمین
    admin_test = await test_admin_services()
    print()
    
    # نتیجه کلی
    print("📊 Test Results:")
    print(f"   Database: {'✅ PASS' if db_test else '❌ FAIL'}")
    print(f"   Glass UI: {'✅ PASS' if ui_test else '❌ FAIL'}")
    print(f"   Admin Services: {'✅ PASS' if admin_test else '❌ FAIL'}")
    
    if all([db_test, ui_test, admin_test]):
        print("\n🎉 All tests passed! Bot is ready to run.")
        return True
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())