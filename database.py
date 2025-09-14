"""
🗄️ Database Management - مدیریت پایگاه داده
سیستم مدیریت پایگاه داده SQLite برای ربات تبدیلا
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class Database:
    """کلاس مدیریت پایگاه داده"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """ایجاد جداول پایگاه داده"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # جدول کاربران
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_blocked BOOLEAN DEFAULT 0,
                        language TEXT DEFAULT 'fa',
                        theme TEXT DEFAULT 'modern'
                    )
                """)
                
                # جدول تاریخچه تبدیلات
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversion_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        conversion_type TEXT,
                        input_data TEXT,
                        output_data TEXT,
                        response_time REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # جدول هشدارهای قیمت
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS price_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        symbol TEXT,
                        target_price REAL,
                        current_price REAL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        triggered_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # جدول اعلان‌ها
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        notification_type TEXT,
                        message TEXT,
                        data TEXT,
                        is_sent BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        sent_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # جدول کش API
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cache_key TEXT UNIQUE,
                        cache_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP
                    )
                """)
                
                # جدول لاگ خطاها
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS error_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        error_type TEXT,
                        error_message TEXT,
                        stack_trace TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def register_user(self, user_id: int, username: str = None, 
                     first_name: str = None, last_name: str = None) -> bool:
        """ثبت کاربر جدید"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, last_activity)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (user_id, username, first_name, last_name))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """دریافت اطلاعات کاربر"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, username, first_name, last_name, 
                           created_at, last_activity, is_blocked, language, theme
                    FROM users WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "user_id": row[0],
                        "username": row[1],
                        "first_name": row[2],
                        "last_name": row[3],
                        "created_at": row[4],
                        "last_activity": row[5],
                        "is_blocked": bool(row[6]),
                        "language": row[7],
                        "theme": row[8]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user_activity(self, user_id: int) -> bool:
        """به‌روزرسانی فعالیت کاربر"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET last_activity = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """دریافت آمار کاربر"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # تعداد کل تبدیلات
                cursor.execute("""
                    SELECT COUNT(*) FROM conversion_history WHERE user_id = ?
                """, (user_id,))
                total_conversions = cursor.fetchone()[0]
                
                # تعداد هشدارهای فعال
                cursor.execute("""
                    SELECT COUNT(*) FROM price_alerts 
                    WHERE user_id = ? AND is_active = 1
                """, (user_id,))
                active_alerts = cursor.fetchone()[0]
                
                # محبوب‌ترین نوع تبدیل
                cursor.execute("""
                    SELECT conversion_type, COUNT(*) as count
                    FROM conversion_history 
                    WHERE user_id = ? 
                    GROUP BY conversion_type
                    ORDER BY count DESC
                    LIMIT 1
                """, (user_id,))
                most_used = cursor.fetchone()
                
                if most_used:
                    most_used_conversion = most_used[0]
                    most_used_count = most_used[1]
                else:
                    most_used_conversion = None
                    most_used_count = 0
                
                return {
                    "total_conversions": total_conversions,
                    "active_alerts": active_alerts,
                    "most_used_conversion": most_used_conversion,
                    "most_used_count": most_used_count
                }
                
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                "total_conversions": 0,
                "active_alerts": 0,
                "most_used_conversion": None,
                "most_used_count": 0
            }
    
    def add_conversion(self, user_id: int, conversion_type: str, 
                      input_data: str, output_data: str, 
                      response_time: float = 0.0) -> bool:
        """اضافه کردن تبدیل به تاریخچه"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversion_history 
                    (user_id, conversion_type, input_data, output_data, response_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, conversion_type, input_data, output_data, response_time))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding conversion: {e}")
            return False
    
    def get_conversion_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """دریافت تاریخچه تبدیلات کاربر"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT conversion_type, input_data, output_data, 
                           response_time, created_at
                    FROM conversion_history 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, limit))
                
                conversions = []
                for row in cursor.fetchall():
                    conversions.append({
                        "conversion_type": row[0],
                        "input_data": row[1],
                        "output_data": row[2],
                        "response_time": row[3],
                        "created_at": row[4]
                    })
                
                return conversions
        except Exception as e:
            logger.error(f"Error getting conversion history: {e}")
            return []
    
    def add_price_alert(self, user_id: int, symbol: str, target_price: float) -> bool:
        """اضافه کردن هشدار قیمت"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO price_alerts 
                    (user_id, symbol, target_price, current_price)
                    VALUES (?, ?, ?, 0)
                """, (user_id, symbol, target_price))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding price alert: {e}")
            return False
    
    def get_active_price_alerts(self) -> List[Dict[str, Any]]:
        """دریافت هشدارهای فعال"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, symbol, target_price, current_price, 
                           created_at, triggered_at
                    FROM price_alerts 
                    WHERE is_active = 1
                    ORDER BY created_at DESC
                """)
                
                alerts = []
                for row in cursor.fetchall():
                    alerts.append({
                        "id": row[0],
                        "user_id": row[1],
                        "symbol": row[2],
                        "target_price": row[3],
                        "current_price": row[4],
                        "created_at": row[5],
                        "triggered_at": row[6]
                    })
                
                return alerts
        except Exception as e:
            logger.error(f"Error getting active price alerts: {e}")
            return []
    
    def add_notification(self, user_id: int, notification_type: str, 
                        message: str, data: Dict = None) -> bool:
        """اضافه کردن اعلان"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                data_json = json.dumps(data) if data else None
                cursor.execute("""
                    INSERT INTO notifications 
                    (user_id, notification_type, message, data)
                    VALUES (?, ?, ?, ?)
                """, (user_id, notification_type, message, data_json))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding notification: {e}")
            return False
    
    def get_pending_notifications(self, limit: int = 100) -> List[Dict[str, Any]]:
        """دریافت اعلان‌های در انتظار"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, notification_type, message, data, created_at
                    FROM notifications 
                    WHERE is_sent = 0
                    ORDER BY created_at ASC
                    LIMIT ?
                """, (limit,))
                
                notifications = []
                for row in cursor.fetchall():
                    data = json.loads(row[4]) if row[4] else None
                    notifications.append({
                        "id": row[0],
                        "user_id": row[1],
                        "notification_type": row[2],
                        "message": row[3],
                        "data": data,
                        "created_at": row[5]
                    })
                
                return notifications
        except Exception as e:
            logger.error(f"Error getting pending notifications: {e}")
            return []
    
    def mark_notification_sent(self, notification_id: int) -> bool:
        """علامت‌گذاری اعلان به عنوان ارسال شده"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE notifications 
                    SET is_sent = 1, sent_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (notification_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error marking notification as sent: {e}")
            return False
    
    def add_to_cache(self, cache_key: str, cache_data: str, 
                    expires_in_minutes: int = 5) -> bool:
        """اضافه کردن به کش"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
                cursor.execute("""
                    INSERT OR REPLACE INTO api_cache 
                    (cache_key, cache_data, expires_at)
                    VALUES (?, ?, ?)
                """, (cache_key, cache_data, expires_at.isoformat()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding to cache: {e}")
            return False
    
    def get_from_cache(self, cache_key: str) -> Optional[str]:
        """دریافت از کش"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT cache_data FROM api_cache 
                    WHERE cache_key = ? AND expires_at > CURRENT_TIMESTAMP
                """, (cache_key,))
                
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def cleanup_expired_cache(self) -> int:
        """پاک کردن کش منقضی شده"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM api_cache 
                    WHERE expires_at <= CURRENT_TIMESTAMP
                """)
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {e}")
            return 0
    
    def log_error(self, user_id: int, error_type: str, 
                  error_message: str, stack_trace: str = None) -> bool:
        """ثبت خطا"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO error_logs 
                    (user_id, error_type, error_message, stack_trace)
                    VALUES (?, ?, ?, ?)
                """, (user_id, error_type, error_message, stack_trace))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging error: {e}")
            return False
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """دریافت خطاهای اخیر"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, error_type, error_message, 
                           stack_trace, created_at
                    FROM error_logs 
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
                
                errors = []
                for row in cursor.fetchall():
                    errors.append({
                        "id": row[0],
                        "user_id": row[1],
                        "error_type": row[2],
                        "error_message": row[3],
                        "stack_trace": row[4],
                        "created_at": row[5]
                    })
                
                return errors
        except Exception as e:
            logger.error(f"Error getting recent errors: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """دریافت آمار پایگاه داده"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # تعداد رکوردها در هر جدول
                tables = ['users', 'conversion_history', 'price_alerts', 
                         'notifications', 'api_cache', 'error_logs']
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
                
                # اندازه فایل پایگاه داده
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                stats["database_size_bytes"] = page_count * page_size
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}