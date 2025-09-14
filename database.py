import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database manager for user data, settings, and history"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT DEFAULT 'fa',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                settings TEXT DEFAULT '{}'
            )
        """)
        
        # Conversion history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversion_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                conversion_type TEXT,
                input_data TEXT,
                output_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Price alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                asset_type TEXT,
                asset_symbol TEXT,
                target_price REAL,
                condition TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                notification_type TEXT,
                message TEXT,
                is_sent BOOLEAN DEFAULT 0,
                scheduled_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Cache table for API responses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_cache (
                cache_key TEXT PRIMARY KEY,
                data TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, language_code: str = "fa"):
        """Add or update user information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, language_code, last_activity)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, username, first_name, last_name, language_code))
            conn.commit()
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def update_user_activity(self, user_id: int):
        """Update user's last activity timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET last_activity = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
    
    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user settings"""
        user = self.get_user(user_id)
        if user and user.get('settings'):
            try:
                return json.loads(user['settings'])
            except json.JSONDecodeError:
                return {}
        return {}
    
    def update_user_settings(self, user_id: int, settings: Dict[str, Any]):
        """Update user settings"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET settings = ? WHERE user_id = ?
            """, (json.dumps(settings), user_id))
            conn.commit()
    
    def add_conversion_history(self, user_id: int, conversion_type: str, 
                              input_data: str, output_data: str):
        """Add conversion to history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversion_history 
                (user_id, conversion_type, input_data, output_data)
                VALUES (?, ?, ?, ?)
            """, (user_id, conversion_type, input_data, output_data))
            conn.commit()
    
    def get_conversion_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's conversion history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversion_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def add_price_alert(self, user_id: int, asset_type: str, asset_symbol: str, 
                       target_price: float, condition: str) -> int:
        """Add price alert"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO price_alerts 
                (user_id, asset_type, asset_symbol, target_price, condition)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, asset_type, asset_symbol, target_price, condition))
            conn.commit()
            return cursor.lastrowid
    
    def get_active_price_alerts(self) -> List[Dict[str, Any]]:
        """Get all active price alerts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM price_alerts WHERE is_active = 1
            """)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def deactivate_price_alert(self, alert_id: int):
        """Deactivate price alert"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE price_alerts SET is_active = 0 WHERE id = ?
            """, (alert_id,))
            conn.commit()
    
    def add_notification(self, user_id: int, notification_type: str, 
                       message: str, scheduled_time: datetime = None):
        """Add notification"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notifications 
                (user_id, notification_type, message, scheduled_time)
                VALUES (?, ?, ?, ?)
            """, (user_id, notification_type, message, scheduled_time))
            conn.commit()
    
    def get_pending_notifications(self) -> List[Dict[str, Any]]:
        """Get pending notifications"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notifications 
                WHERE is_sent = 0 AND 
                (scheduled_time IS NULL OR scheduled_time <= CURRENT_TIMESTAMP)
            """)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def mark_notification_sent(self, notification_id: int):
        """Mark notification as sent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notifications SET is_sent = 1 WHERE id = ?
            """, (notification_id,))
            conn.commit()
    
    def cache_api_response(self, cache_key: str, data: str, expires_in_minutes: int = 30):
        """Cache API response"""
        expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO api_cache 
                (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, (cache_key, data, expires_at))
            conn.commit()
    
    def get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached API response"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data FROM api_cache 
                WHERE cache_key = ? AND expires_at > CURRENT_TIMESTAMP
            """, (cache_key,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM api_cache WHERE expires_at <= CURRENT_TIMESTAMP
            """)
            conn.commit()
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total conversions
            cursor.execute("""
                SELECT COUNT(*) FROM conversion_history WHERE user_id = ?
            """, (user_id,))
            total_conversions = cursor.fetchone()[0]
            
            # Active alerts
            cursor.execute("""
                SELECT COUNT(*) FROM price_alerts WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            active_alerts = cursor.fetchone()[0]
            
            # Most used conversion type
            cursor.execute("""
                SELECT conversion_type, COUNT(*) as count 
                FROM conversion_history 
                WHERE user_id = ? 
                GROUP BY conversion_type 
                ORDER BY count DESC 
                LIMIT 1
            """, (user_id,))
            most_used = cursor.fetchone()
            
            return {
                "total_conversions": total_conversions,
                "active_alerts": active_alerts,
                "most_used_conversion": most_used[0] if most_used else None,
                "most_used_count": most_used[1] if most_used else 0
            }
