"""
👑 Advanced Admin Panel - پنل مدیریت پیشرفته
سیستم مدیریت کامل برای ادمین‌های ربات تبدیلا
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from glass_ui import GlassUI
from database import Database

logger = logging.getLogger(__name__)

class AdvancedAdminPanel:
    """پنل مدیریت پیشرفته با قابلیت‌های کامل"""
    
    def __init__(self, database: Database):
        self.db = database
        self.maintenance_mode = False
        self.broadcast_queue = []
        self.admin_sessions = {}  # user_id -> session_data
        
    async def is_admin(self, user_id: int) -> bool:
        """بررسی دسترسی ادمین"""
        try:
            from config import Config
            return user_id in Config.ADMIN_USER_IDS
        except:
            return False
    
    async def get_admin_dashboard(self, user_id: int) -> Dict[str, Any]:
        """داشبورد اصلی ادمین"""
        try:
            # آمار کلی
            stats = await self.get_comprehensive_stats()
            
            # وضعیت سیستم
            system_status = await self.get_system_status()
            
            # هشدارهای مهم
            critical_alerts = await self.get_critical_alerts()
            
            # فعالیت‌های اخیر
            recent_activities = await self.get_recent_activities(limit=5)
            
            return {
                "success": True,
                "dashboard": {
                    "stats": stats,
                    "system_status": system_status,
                    "critical_alerts": critical_alerts,
                    "recent_activities": recent_activities,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting admin dashboard: {e}")
            return {
                "success": False,
                "error": f"Failed to get dashboard: {str(e)}"
            }
    
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """آمار جامع سیستم"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # آمار کاربران
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity > datetime('now', '-1 day')
                """)
                active_users_24h = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity > datetime('now', '-7 days')
                """)
                active_users_7d = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE created_at > datetime('now', '-1 day')
                """)
                new_users_24h = cursor.fetchone()[0]
                
                # آمار تبدیلات
                cursor.execute("SELECT COUNT(*) FROM conversion_history")
                total_conversions = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM conversion_history 
                    WHERE created_at > datetime('now', '-1 day')
                """)
                conversions_24h = cursor.fetchone()[0]
                
                # آمار هشدارها
                cursor.execute("SELECT COUNT(*) FROM price_alerts WHERE is_active = 1")
                active_alerts = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_sent = 0")
                pending_notifications = cursor.fetchone()[0]
                
                # محبوب‌ترین تبدیلات
                cursor.execute("""
                    SELECT conversion_type, COUNT(*) as count 
                    FROM conversion_history 
                    GROUP BY conversion_type 
                    ORDER BY count DESC 
                    LIMIT 5
                """)
                top_conversions = cursor.fetchall()
                
                # آمار عملکرد
                cursor.execute("""
                    SELECT AVG(response_time) FROM conversion_history 
                    WHERE created_at > datetime('now', '-1 day')
                """)
                avg_response_time = cursor.fetchone()[0] or 0
                
                return {
                    "users": {
                        "total": total_users,
                        "active_24h": active_users_24h,
                        "active_7d": active_users_7d,
                        "new_24h": new_users_24h
                    },
                    "conversions": {
                        "total": total_conversions,
                        "last_24h": conversions_24h,
                        "avg_response_time": round(avg_response_time, 2)
                    },
                    "alerts": {
                        "active": active_alerts,
                        "pending_notifications": pending_notifications
                    },
                    "top_conversions": top_conversions
                }
                
        except Exception as e:
            logger.error(f"Error getting comprehensive stats: {e}")
            return {
                "users": {"total": 0, "active_24h": 0, "active_7d": 0, "new_24h": 0},
                "conversions": {"total": 0, "last_24h": 0, "avg_response_time": 0},
                "alerts": {"active": 0, "pending_notifications": 0},
                "top_conversions": []
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """وضعیت سیستم"""
        try:
            # وضعیت پایگاه داده
            db_status = await self.check_database_status()
            
            # وضعیت API ها
            api_status = await self.check_api_status()
            
            # وضعیت کش
            cache_status = await self.check_cache_status()
            
            # وضعیت حافظه
            memory_status = await self.check_memory_status()
            
            return {
                "database": db_status,
                "apis": api_status,
                "cache": cache_status,
                "memory": memory_status,
                "maintenance_mode": self.maintenance_mode,
                "uptime": await self.get_uptime()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    async def check_database_status(self) -> Dict[str, Any]:
        """بررسی وضعیت پایگاه داده"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return {"status": "healthy", "connected": True}
        except Exception as e:
            return {"status": "error", "error": str(e), "connected": False}
    
    async def check_api_status(self) -> Dict[str, Any]:
        """بررسی وضعیت API ها"""
        # این بخش را می‌توانید با API های واقعی تکمیل کنید
        return {
            "exchange_rate_api": {"status": "healthy", "response_time": 0.5},
            "weather_api": {"status": "healthy", "response_time": 0.8},
            "crypto_api": {"status": "healthy", "response_time": 0.3}
        }
    
    async def check_cache_status(self) -> Dict[str, Any]:
        """بررسی وضعیت کش"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM api_cache")
                total_entries = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM api_cache 
                    WHERE expires_at > CURRENT_TIMESTAMP
                """)
                active_entries = cursor.fetchone()[0]
                
                return {
                    "total_entries": total_entries,
                    "active_entries": active_entries,
                    "hit_rate": 0.85  # این را می‌توانید محاسبه کنید
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def check_memory_status(self) -> Dict[str, Any]:
        """بررسی وضعیت حافظه"""
        import psutil
        try:
            memory = psutil.virtual_memory()
            return {
                "total": memory.total,
                "available": memory.available,
                "used_percent": memory.percent,
                "status": "healthy" if memory.percent < 80 else "warning"
            }
        except ImportError:
            return {"status": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_uptime(self) -> str:
        """زمان فعالیت سیستم"""
        try:
            import time
            uptime_seconds = time.time() - self.start_time if hasattr(self, 'start_time') else 0
            uptime_hours = uptime_seconds / 3600
            return f"{uptime_hours:.1f} hours"
        except:
            return "Unknown"
    
    async def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """هشدارهای مهم"""
        alerts = []
        
        try:
            # بررسی خطاهای سیستم
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM error_logs 
                    WHERE created_at > datetime('now', '-1 hour')
                """)
                recent_errors = cursor.fetchone()[0]
                
                if recent_errors > 10:
                    alerts.append({
                        "type": "error",
                        "message": f"تعداد خطاهای زیاد در ساعت گذشته: {recent_errors}",
                        "severity": "high"
                    })
            
            # بررسی استفاده از حافظه
            memory_status = await self.check_memory_status()
            if memory_status.get("used_percent", 0) > 90:
                alerts.append({
                    "type": "memory",
                    "message": f"استفاده از حافظه بالا: {memory_status.get('used_percent', 0)}%",
                    "severity": "high"
                })
            
            # بررسی هشدارهای قیمت
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM price_alerts 
                    WHERE triggered_at IS NOT NULL 
                    AND triggered_at > datetime('now', '-1 hour')
                """)
                triggered_alerts = cursor.fetchone()[0]
                
                if triggered_alerts > 0:
                    alerts.append({
                        "type": "alerts",
                        "message": f"{triggered_alerts} هشدار قیمت در ساعت گذشته فعال شده",
                        "severity": "medium"
                    })
            
        except Exception as e:
            logger.error(f"Error getting critical alerts: {e}")
        
        return alerts
    
    async def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """فعالیت‌های اخیر"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT u.username, u.first_name, ch.conversion_type, 
                           ch.input_data, ch.created_at
                    FROM conversion_history ch
                    JOIN users u ON ch.user_id = u.user_id
                    ORDER BY ch.created_at DESC
                    LIMIT ?
                """, (limit,))
                
                activities = []
                for row in cursor.fetchall():
                    activities.append({
                        "username": row[0] or "Unknown",
                        "first_name": row[1] or "Unknown",
                        "conversion_type": row[2],
                        "input_data": row[3],
                        "created_at": row[4]
                    })
                
                return activities
                
        except Exception as e:
            logger.error(f"Error getting recent activities: {e}")
            return []
    
    async def manage_users(self, action: str, user_id: Optional[int] = None, 
                          data: Optional[Dict] = None) -> Dict[str, Any]:
        """مدیریت کاربران"""
        try:
            if action == "list":
                return await self.get_user_list_with_pagination(
                    page=data.get("page", 1),
                    limit=data.get("limit", 20)
                )
            elif action == "details":
                return await self.get_user_details(user_id)
            elif action == "block":
                return await self.block_user(user_id)
            elif action == "unblock":
                return await self.unblock_user(user_id)
            elif action == "delete":
                return await self.delete_user(user_id)
            else:
                return {"success": False, "error": "Invalid action"}
                
        except Exception as e:
            logger.error(f"Error managing users: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_list_with_pagination(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """لیست کاربران با صفحه‌بندی"""
        try:
            offset = (page - 1) * limit
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # دریافت کاربران
                cursor.execute("""
                    SELECT user_id, username, first_name, last_name, 
                           created_at, last_activity, is_blocked
                    FROM users 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        "user_id": row[0],
                        "username": row[1],
                        "first_name": row[2],
                        "last_name": row[3],
                        "created_at": row[4],
                        "last_activity": row[5],
                        "is_blocked": bool(row[6])
                    })
                
                # تعداد کل کاربران
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                return {
                    "success": True,
                    "users": users,
                    "pagination": {
                        "current_page": page,
                        "total_pages": (total_users + limit - 1) // limit,
                        "total_users": total_users,
                        "limit": limit
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting user list: {e}")
            return {"success": False, "error": str(e)}
    
    async def block_user(self, user_id: int) -> Dict[str, Any]:
        """مسدود کردن کاربر"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET is_blocked = 1 
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()
                
                return {
                    "success": True,
                    "message": f"User {user_id} blocked successfully"
                }
                
        except Exception as e:
            logger.error(f"Error blocking user: {e}")
            return {"success": False, "error": str(e)}
    
    async def unblock_user(self, user_id: int) -> Dict[str, Any]:
        """رفع مسدودیت کاربر"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET is_blocked = 0 
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()
                
                return {
                    "success": True,
                    "message": f"User {user_id} unblocked successfully"
                }
                
        except Exception as e:
            logger.error(f"Error unblocking user: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        """حذف کاربر"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # حذف داده‌های مرتبط
                cursor.execute("DELETE FROM conversion_history WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM price_alerts WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                
                conn.commit()
                
                return {
                    "success": True,
                    "message": f"User {user_id} deleted successfully"
                }
                
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return {"success": False, "error": str(e)}
    
    async def broadcast_message(self, message: str, target_type: str = "all", 
                               target_data: Optional[Dict] = None) -> Dict[str, Any]:
        """ارسال پیام گروهی"""
        try:
            # تعیین کاربران هدف
            if target_type == "all":
                target_users = await self.get_all_user_ids()
            elif target_type == "active":
                target_users = await self.get_active_user_ids()
            elif target_type == "new":
                target_users = await self.get_new_user_ids()
            elif target_type == "custom":
                target_users = target_data.get("user_ids", [])
            else:
                return {"success": False, "error": "Invalid target type"}
            
            # اضافه کردن پیام به صف
            broadcast_id = f"broadcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            for user_id in target_users:
                self.db.add_notification(user_id, "broadcast", message, {
                    "broadcast_id": broadcast_id,
                    "target_type": target_type
                })
            
            return {
                "success": True,
                "message": f"Broadcast queued for {len(target_users)} users",
                "broadcast_id": broadcast_id,
                "target_count": len(target_users)
            }
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_all_user_ids(self) -> List[int]:
        """دریافت شناسه تمام کاربران"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE is_blocked = 0")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all user IDs: {e}")
            return []
    
    async def get_active_user_ids(self) -> List[int]:
        """دریافت شناسه کاربران فعال"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id FROM users 
                    WHERE is_blocked = 0 
                    AND last_activity > datetime('now', '-7 days')
                """)
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting active user IDs: {e}")
            return []
    
    async def get_new_user_ids(self) -> List[int]:
        """دریافت شناسه کاربران جدید"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id FROM users 
                    WHERE is_blocked = 0 
                    AND created_at > datetime('now', '-7 days')
                """)
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting new user IDs: {e}")
            return []
    
    async def toggle_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """تغییر حالت تعمیر"""
        try:
            self.maintenance_mode = enabled
            
            # اگر حالت تعمیر فعال شد، پیام اطلاع‌رسانی ارسال کن
            if enabled:
                await self.broadcast_message(
                    "🔧 ربات در حال تعمیر است. به زودی بازمی‌گردد!",
                    "all"
                )
            
            return {
                "success": True,
                "message": f"Maintenance mode {'enabled' if enabled else 'disabled'}",
                "maintenance_mode": enabled
            }
            
        except Exception as e:
            logger.error(f"Error toggling maintenance mode: {e}")
            return {"success": False, "error": str(e)}
    
    async def manage_cache(self, action: str) -> Dict[str, Any]:
        """مدیریت کش"""
        try:
            if action == "clear":
                # پاک کردن کش منقضی شده
                self.db.cleanup_expired_cache()
                
                return {
                    "success": True,
                    "message": "Expired cache entries cleared"
                }
            
            elif action == "clear_all":
                # پاک کردن تمام کش
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM api_cache")
                    conn.commit()
                
                return {
                    "success": True,
                    "message": "All cache entries cleared"
                }
            
            elif action == "stats":
                # آمار کش
                cache_stats = await self.check_cache_status()
                return {
                    "success": True,
                    "cache_stats": cache_stats
                }
            
            else:
                return {
                    "success": False,
                    "error": "Invalid cache action"
                }
                
        except Exception as e:
            logger.error(f"Error managing cache: {e}")
            return {"success": False, "error": str(e)}
    
    def format_dashboard_message(self, dashboard_data: Dict[str, Any]) -> str:
        """فرمت کردن پیام داشبورد"""
        if not dashboard_data.get("success"):
            return f"❌ خطا: {dashboard_data.get('error', 'Unknown error')}"
        
        dashboard = dashboard_data["dashboard"]
        stats = dashboard["stats"]
        system_status = dashboard["system_status"]
        critical_alerts = dashboard["critical_alerts"]
        
        message = "👑 **داشبورد مدیریت**\n\n"
        
        # آمار کاربران
        message += "👥 **آمار کاربران:**\n"
        message += f"   • کل کاربران: {stats['users']['total']:,}\n"
        message += f"   • فعال (24 ساعت): {stats['users']['active_24h']:,}\n"
        message += f"   • فعال (7 روز): {stats['users']['active_7d']:,}\n"
        message += f"   • جدید (24 ساعت): {stats['users']['new_24h']:,}\n\n"
        
        # آمار تبدیلات
        message += "🔄 **آمار تبدیلات:**\n"
        message += f"   • کل تبدیلات: {stats['conversions']['total']:,}\n"
        message += f"   • تبدیلات (24 ساعت): {stats['conversions']['last_24h']:,}\n"
        message += f"   • میانگین زمان پاسخ: {stats['conversions']['avg_response_time']}s\n\n"
        
        # آمار هشدارها
        message += "🚨 **آمار هشدارها:**\n"
        message += f"   • هشدارهای فعال: {stats['alerts']['active']:,}\n"
        message += f"   • اعلان‌های در انتظار: {stats['alerts']['pending_notifications']:,}\n\n"
        
        # وضعیت سیستم
        message += "⚙️ **وضعیت سیستم:**\n"
        message += f"   • پایگاه داده: {system_status['database']['status']}\n"
        message += f"   • حالت تعمیر: {'فعال' if system_status['maintenance_mode'] else 'غیرفعال'}\n"
        message += f"   • زمان فعالیت: {system_status['uptime']}\n\n"
        
        # هشدارهای مهم
        if critical_alerts:
            message += "⚠️ **هشدارهای مهم:**\n"
            for alert in critical_alerts[:3]:  # فقط 3 هشدار اول
                severity_emoji = "🔴" if alert["severity"] == "high" else "🟡"
                message += f"   {severity_emoji} {alert['message']}\n"
            message += "\n"
        
        # محبوب‌ترین تبدیلات
        if stats['top_conversions']:
            message += "📈 **محبوب‌ترین تبدیلات:**\n"
            for conv_type, count in stats['top_conversions'][:3]:
                message += f"   • {conv_type}: {count:,}\n"
        
        message += f"\n🕐 آخرین به‌روزرسانی: {dashboard['timestamp']}"
        
        return message
    
    def get_admin_keyboard(self) -> InlineKeyboardMarkup:
        """کیبورد مدیریت"""
        return GlassUI.get_admin_glass_keyboard()
    
    def get_user_management_keyboard(self, page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
        """کیبورد مدیریت کاربران"""
        keyboard = [
            [
                GlassUI.get_glass_button("📊 آمار کاربران", "admin_user_stats", emoji="📊"),
                GlassUI.get_glass_button("🔍 جستجوی کاربر", "admin_search_user", emoji="🔍")
            ],
            [
                GlassUI.get_glass_button("📋 لیست کاربران", "admin_user_list", emoji="📋"),
                GlassUI.get_glass_button("➕ کاربر جدید", "admin_add_user", emoji="➕")
            ]
        ]
        
        # صفحه‌بندی
        if total_pages > 1:
            pagination = GlassUI.get_pagination_glass_keyboard(page, total_pages, "admin_users")
            keyboard.extend(pagination.inline_keyboard)
        
        keyboard.append([
            GlassUI.get_glass_button("🔙 بازگشت", "back_to_admin", emoji="🔙")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_broadcast_keyboard(self) -> InlineKeyboardMarkup:
        """کیبورد ارسال پیام گروهی"""
        keyboard = [
            [
                GlassUI.get_glass_button("📢 ارسال به همه", "admin_broadcast_all", emoji="📢"),
                GlassUI.get_glass_button("👥 کاربران فعال", "admin_broadcast_active", emoji="👥")
            ],
            [
                GlassUI.get_glass_button("🆕 کاربران جدید", "admin_broadcast_new", emoji="🆕"),
                GlassUI.get_glass_button("🎯 انتخابی", "admin_broadcast_custom", emoji="🎯")
            ],
            [
                GlassUI.get_glass_button("📊 آمار ارسال", "admin_broadcast_stats", emoji="📊"),
                GlassUI.get_glass_button("📋 تاریخچه", "admin_broadcast_history", emoji="📋")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت", "back_to_admin", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_system_settings_keyboard(self) -> InlineKeyboardMarkup:
        """کیبورد تنظیمات سیستم"""
        keyboard = [
            [
                GlassUI.get_glass_button("🔧 حالت تعمیر", "admin_maintenance", emoji="🔧"),
                GlassUI.get_glass_button("💾 مدیریت کش", "admin_cache", emoji="💾")
            ],
            [
                GlassUI.get_glass_button("📊 آمار سیستم", "admin_system_stats", emoji="📊"),
                GlassUI.get_glass_button("🔒 امنیت", "admin_security", emoji="🔒")
            ],
            [
                GlassUI.get_glass_button("📋 لاگ‌ها", "admin_logs", emoji="📋"),
                GlassUI.get_glass_button("🔄 پشتیبان‌گیری", "admin_backup", emoji="🔄")
            ],
            [
                GlassUI.get_glass_button("🔙 بازگشت", "back_to_admin", emoji="🔙")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

