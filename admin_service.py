"""
👑 Admin Service - سرویس مدیریت
سرویس‌های مدیریتی برای ربات تبدیلا
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class AdminService:
    """سرویس مدیریت ربات"""
    
    def __init__(self, database):
        self.db = database
        self.admin_commands = {
            "stats": self.get_bot_statistics,
            "users": self.get_user_list,
            "user": self.get_user_details,
            "broadcast": self.broadcast_message,
            "maintenance": self.toggle_maintenance_mode,
            "cache": self.manage_cache,
            "alerts": self.get_all_alerts,
            "logs": self.get_recent_logs
        }
    
    async def is_admin(self, user_id: int) -> bool:
        """بررسی دسترسی ادمین"""
        try:
            from config import Config
            return user_id in Config.ADMIN_USER_IDS
        except:
            return False
    
    async def get_bot_statistics(self) -> Dict[str, Any]:
        """دریافت آمار جامع ربات"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # کل کاربران
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                # کاربران فعال (24 ساعت)
                cursor.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity > datetime('now', '-1 day')
                """)
                active_users_24h = cursor.fetchone()[0]
                
                # کاربران فعال (7 روز)
                cursor.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity > datetime('now', '-7 days')
                """)
                active_users_7d = cursor.fetchone()[0]
                
                # کل تبدیلات
                cursor.execute("SELECT COUNT(*) FROM conversion_history")
                total_conversions = cursor.fetchone()[0]
                
                # هشدارهای فعال
                cursor.execute("SELECT COUNT(*) FROM price_alerts WHERE is_active = 1")
                active_alerts = cursor.fetchone()[0]
                
                # اعلان‌های در انتظار
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
                
                # کاربران جدید (24 ساعت)
                cursor.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE created_at > datetime('now', '-1 day')
                """)
                new_users_24h = cursor.fetchone()[0]
                
                return {
                    "success": True,
                    "statistics": {
                        "total_users": total_users,
                        "active_users_24h": active_users_24h,
                        "active_users_7d": active_users_7d,
                        "new_users_24h": new_users_24h,
                        "total_conversions": total_conversions,
                        "active_alerts": active_alerts,
                        "pending_notifications": pending_notifications,
                        "top_conversions": top_conversions
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting bot statistics: {e}")
            return {
                "success": False,
                "error": f"Failed to get statistics: {str(e)}"
            }
    
    async def get_user_list(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """دریافت لیست کاربران با صفحه‌بندی"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # دریافت کاربران با صفحه‌بندی
                cursor.execute("""
                    SELECT user_id, username, first_name, last_name, 
                           created_at, last_activity 
                    FROM users 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                users = cursor.fetchall()
                
                # تعداد کل
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                return {
                    "success": True,
                    "users": [
                        {
                            "user_id": user[0],
                            "username": user[1],
                            "first_name": user[2],
                            "last_name": user[3],
                            "created_at": user[4],
                            "last_activity": user[5]
                        }
                        for user in users
                    ],
                    "total_users": total_users,
                    "limit": limit,
                    "offset": offset
                }
                
        except Exception as e:
            logger.error(f"Error getting user list: {e}")
            return {
                "success": False,
                "error": f"Failed to get user list: {str(e)}"
            }
    
    async def get_user_details(self, user_id: int) -> Dict[str, Any]:
        """دریافت جزئیات کاربر"""
        try:
            user = self.db.get_user(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # آمار کاربر
            stats = self.db.get_user_stats(user_id)
            
            # تبدیلات اخیر
            recent_conversions = self.db.get_conversion_history(user_id, 10)
            
            # هشدارهای کاربر
            alerts = [a for a in self.db.get_active_price_alerts() if a["user_id"] == user_id]
            
            return {
                "success": True,
                "user": user,
                "statistics": stats,
                "recent_conversions": recent_conversions,
                "active_alerts": alerts
            }
            
        except Exception as e:
            logger.error(f"Error getting user details: {e}")
            return {
                "success": False,
                "error": f"Failed to get user details: {str(e)}"
            }
    
    async def broadcast_message(self, message: str, target_users: Optional[List[int]] = None) -> Dict[str, Any]:
        """ارسال پیام گروهی"""
        try:
            if target_users is None:
                # ارسال به همه کاربران
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT user_id FROM users")
                    target_users = [row[0] for row in cursor.fetchall()]
            
            success_count = 0
            failed_count = 0
            
            for user_id in target_users:
                try:
                    # اضافه کردن اعلان به پایگاه داده
                    self.db.add_notification(user_id, "broadcast", message)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to add broadcast notification for user {user_id}: {e}")
                    failed_count += 1
            
            return {
                "success": True,
                "message": f"Broadcast queued for {success_count} users",
                "success_count": success_count,
                "failed_count": failed_count,
                "total_targeted": len(target_users)
            }
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            return {
                "success": False,
                "error": f"Failed to broadcast message: {str(e)}"
            }
    
    async def toggle_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """تغییر حالت تعمیر"""
        try:
            # اینجا می‌توانید حالت تعمیر را در پایگاه داده ذخیره کنید
            maintenance_status = "enabled" if enabled else "disabled"
            
            return {
                "success": True,
                "message": f"Maintenance mode {maintenance_status}",
                "maintenance_mode": enabled
            }
            
        except Exception as e:
            logger.error(f"Error toggling maintenance mode: {e}")
            return {
                "success": False,
                "error": f"Failed to toggle maintenance mode: {str(e)}"
            }
    
    async def manage_cache(self, action: str) -> Dict[str, Any]:
        """مدیریت کش"""
        try:
            if action == "clear":
                # پاک کردن کش منقضی شده
                deleted_count = self.db.cleanup_expired_cache()
                
                return {
                    "success": True,
                    "message": f"Expired cache entries cleared: {deleted_count}"
                }
            
            elif action == "stats":
                # آمار کش
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
                        "success": True,
                        "cache_stats": {
                            "total_entries": total_entries,
                            "active_entries": active_entries,
                            "expired_entries": total_entries - active_entries
                        }
                    }
            
            else:
                return {
                    "success": False,
                    "error": "Invalid cache action. Use 'clear' or 'stats'"
                }
                
        except Exception as e:
            logger.error(f"Error managing cache: {e}")
            return {
                "success": False,
                "error": f"Failed to manage cache: {str(e)}"
            }
    
    async def get_all_alerts(self) -> Dict[str, Any]:
        """دریافت تمام هشدارهای فعال"""
        try:
            alerts = self.db.get_active_price_alerts()
            
            # گروه‌بندی بر اساس کاربر
            user_alerts = {}
            for alert in alerts:
                user_id = alert["user_id"]
                if user_id not in user_alerts:
                    user_alerts[user_id] = []
                user_alerts[user_id].append(alert)
            
            return {
                "success": True,
                "total_alerts": len(alerts),
                "users_with_alerts": len(user_alerts),
                "alerts_by_user": user_alerts
            }
            
        except Exception as e:
            logger.error(f"Error getting all alerts: {e}")
            return {
                "success": False,
                "error": f"Failed to get alerts: {str(e)}"
            }
    
    async def get_recent_logs(self, limit: int = 100) -> Dict[str, Any]:
        """دریافت لاگ‌های اخیر"""
        try:
            # این یک پیاده‌سازی ساده است
            # در نسخه‌های آینده می‌توانید از فایل‌های لاگ واقعی استفاده کنید
            return {
                "success": True,
                "message": "Log viewing not implemented in this version",
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
            return {
                "success": False,
                "error": f"Failed to get logs: {str(e)}"
            }
    
    def format_statistics(self, stats: Dict[str, Any]) -> str:
        """فرمت کردن آمار برای نمایش"""
        if not stats["success"]:
            return f"❌ {stats['error']}"
        
        data = stats["statistics"]
        
        output = "📊 **آمار ربات**\n\n"
        output += f"👥 **کاربران:**\n"
        output += f"   • کل کاربران: {data['total_users']:,}\n"
        output += f"   • فعال (24 ساعت): {data['active_users_24h']:,}\n"
        output += f"   • فعال (7 روز): {data['active_users_7d']:,}\n"
        output += f"   • جدید (24 ساعت): {data['new_users_24h']:,}\n\n"
        
        output += f"🔄 **تبدیلات:**\n"
        output += f"   • کل تبدیلات: {data['total_conversions']:,}\n\n"
        
        output += f"🚨 **هشدارها:**\n"
        output += f"   • هشدارهای فعال: {data['active_alerts']:,}\n"
        output += f"   • اعلان‌های در انتظار: {data['pending_notifications']:,}\n\n"
        
        if data['top_conversions']:
            output += f"📈 **محبوب‌ترین تبدیلات:**\n"
            for conv_type, count in data['top_conversions']:
                output += f"   • {conv_type}: {count:,}\n"
        
        output += f"\n🕐 زمان: {stats['timestamp']}"
        
        return output
    
    def format_user_list(self, user_data: Dict[str, Any]) -> str:
        """فرمت کردن لیست کاربران برای نمایش"""
        if not user_data["success"]:
            return f"❌ {user_data['error']}"
        
        users = user_data["users"]
        total_users = user_data["total_users"]
        
        output = f"👥 **لیست کاربران** ({len(users)}/{total_users})\n\n"
        
        for i, user in enumerate(users, 1):
            username = user["username"] or "بدون نام کاربری"
            name = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip() or "بدون نام"
            
            output += f"{i}. **{name}** (@{username})\n"
            output += f"   🆔 ID: {user['user_id']}\n"
            output += f"   📅 عضویت: {user['created_at']}\n"
            output += f"   🕐 آخرین فعالیت: {user['last_activity']}\n\n"
        
        return output