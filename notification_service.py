import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class NotificationService:
    """Notification system for price alerts and reminders"""
    
    def __init__(self, database, bot_application):
        self.db = database
        self.bot = bot_application
        self.running = False
        self.check_interval = 60  # Check every minute
        
    async def start_notification_service(self):
        """Start the notification service"""
        if self.running:
            return
        
        self.running = True
        logger.info("Notification service started")
        
        while self.running:
            try:
                await self._check_price_alerts()
                await self._check_scheduled_notifications()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Notification service error: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_notification_service(self):
        """Stop the notification service"""
        self.running = False
        logger.info("Notification service stopped")
    
    async def _check_price_alerts(self):
        """Check price alerts and send notifications"""
        try:
            alerts = self.db.get_active_price_alerts()
            
            for alert in alerts:
                try:
                    # Get current price
                    current_price = await self._get_current_price(alert["asset_type"], alert["asset_symbol"])
                    
                    if current_price and self._should_trigger_alert(alert, current_price):
                        await self._send_price_alert(alert, current_price)
                        
                except Exception as e:
                    logger.error(f"Error checking alert {alert['id']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking price alerts: {e}")
    
    async def _get_current_price(self, asset_type: str, asset_symbol: str) -> Optional[float]:
        """Get current price for an asset"""
        try:
            if asset_type == "crypto":
                # Use price tracker for crypto
                from price_tracker import PriceTracker
                tracker = PriceTracker(self.db)
                result = await tracker.get_crypto_price(asset_symbol)
                return result.get("price") if result["success"] else None
            
            elif asset_type == "stock":
                # Use price tracker for stocks
                from price_tracker import PriceTracker
                tracker = PriceTracker(self.db)
                result = await tracker.get_stock_price(asset_symbol)
                return result.get("price") if result["success"] else None
            
            elif asset_type == "currency":
                # Use currency converter for forex
                from currency_converter import CurrencyConverter
                converter = CurrencyConverter(self.db)
                result = await converter.convert_currency(1, asset_symbol, "USD")
                return result.get("rate") if result["success"] else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price for {asset_symbol}: {e}")
            return None
    
    def _should_trigger_alert(self, alert: Dict[str, Any], current_price: float) -> bool:
        """Check if alert should be triggered"""
        target_price = alert["target_price"]
        condition = alert["condition"]
        
        if condition == "above" and current_price > target_price:
            return True
        elif condition == "below" and current_price < target_price:
            return True
        elif condition == "equals" and abs(current_price - target_price) < target_price * 0.01:  # 1% tolerance
            return True
        
        return False
    
    async def _send_price_alert(self, alert: Dict[str, Any], current_price: float):
        """Send price alert notification"""
        try:
            user_id = alert["user_id"]
            asset_symbol = alert["asset_symbol"]
            target_price = alert["target_price"]
            condition = alert["condition"]
            
            # Format message
            condition_text = {
                "above": "بالاتر از",
                "below": "پایین‌تر از",
                "equals": "برابر با"
            }.get(condition, condition)
            
            message = f"🚨 **هشدار قیمت**\n\n"
            message += f"💰 **{asset_symbol}**\n"
            message += f"📊 قیمت فعلی: ${current_price:.2f}\n"
            message += f"🎯 هدف: {condition_text} ${target_price:.2f}\n"
            message += f"⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Send notification
            await self.bot.bot.send_message(chat_id=user_id, text=message)
            
            # Deactivate alert
            self.db.deactivate_price_alert(alert["id"])
            
            logger.info(f"Price alert sent to user {user_id} for {asset_symbol}")
            
        except Exception as e:
            logger.error(f"Error sending price alert: {e}")
    
    async def _check_scheduled_notifications(self):
        """Check and send scheduled notifications"""
        try:
            notifications = self.db.get_pending_notifications()
            
            for notification in notifications:
                try:
                    await self._send_scheduled_notification(notification)
                    self.db.mark_notification_sent(notification["id"])
                    
                except Exception as e:
                    logger.error(f"Error sending notification {notification['id']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking scheduled notifications: {e}")
    
    async def _send_scheduled_notification(self, notification: Dict[str, Any]):
        """Send scheduled notification"""
        try:
            user_id = notification["user_id"]
            message = notification["message"]
            notification_type = notification["notification_type"]
            
            # Add emoji based on notification type
            emoji_map = {
                "reminder": "⏰",
                "alert": "🚨",
                "info": "ℹ️",
                "warning": "⚠️",
                "success": "✅",
                "error": "❌"
            }
            
            emoji = emoji_map.get(notification_type, "📢")
            formatted_message = f"{emoji} **{notification_type.upper()}**\n\n{message}"
            
            await self.bot.bot.send_message(chat_id=user_id, text=formatted_message)
            
            logger.info(f"Notification sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending scheduled notification: {e}")
    
    async def create_price_alert(self, user_id: int, asset_type: str, asset_symbol: str, 
                               target_price: float, condition: str) -> Dict[str, Any]:
        """Create a new price alert"""
        try:
            # Validate condition
            if condition not in ["above", "below", "equals"]:
                return {
                    "success": False,
                    "error": "Invalid condition. Use 'above', 'below', or 'equals'"
                }
            
            # Validate asset type
            if asset_type not in ["crypto", "stock", "currency"]:
                return {
                    "success": False,
                    "error": "Invalid asset type. Use 'crypto', 'stock', or 'currency'"
                }
            
            # Check if user already has too many alerts
            user_alerts = [a for a in self.db.get_active_price_alerts() if a["user_id"] == user_id]
            if len(user_alerts) >= 10:  # Limit to 10 alerts per user
                return {
                    "success": False,
                    "error": "Maximum number of alerts reached (10)"
                }
            
            # Create alert
            alert_id = self.db.add_price_alert(user_id, asset_type, asset_symbol, target_price, condition)
            
            return {
                "success": True,
                "alert_id": alert_id,
                "message": f"Price alert created for {asset_symbol} {condition} ${target_price:.2f}"
            }
            
        except Exception as e:
            logger.error(f"Error creating price alert: {e}")
            return {
                "success": False,
                "error": f"Failed to create price alert: {str(e)}"
            }
    
    async def create_reminder(self, user_id: int, message: str, 
                            scheduled_time: datetime) -> Dict[str, Any]:
        """Create a scheduled reminder"""
        try:
            # Validate scheduled time
            if scheduled_time <= datetime.now():
                return {
                    "success": False,
                    "error": "Scheduled time must be in the future"
                }
            
            # Create notification
            self.db.add_notification(user_id, "reminder", message, scheduled_time)
            
            return {
                "success": True,
                "message": f"Reminder scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            return {
                "success": False,
                "error": f"Failed to create reminder: {str(e)}"
            }
    
    async def send_immediate_notification(self, user_id: int, message: str, 
                                        notification_type: str = "info") -> Dict[str, Any]:
        """Send immediate notification to user"""
        try:
            # Add emoji based on notification type
            emoji_map = {
                "reminder": "⏰",
                "alert": "🚨",
                "info": "ℹ️",
                "warning": "⚠️",
                "success": "✅",
                "error": "❌"
            }
            
            emoji = emoji_map.get(notification_type, "📢")
            formatted_message = f"{emoji} **{notification_type.upper()}**\n\n{message}"
            
            await self.bot.bot.send_message(chat_id=user_id, text=formatted_message)
            
            return {
                "success": True,
                "message": "Notification sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Error sending immediate notification: {e}")
            return {
                "success": False,
                "error": f"Failed to send notification: {str(e)}"
            }
    
    async def get_user_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all active alerts for a user"""
        try:
            all_alerts = self.db.get_active_price_alerts()
            user_alerts = [alert for alert in all_alerts if alert["user_id"] == user_id]
            
            return user_alerts
            
        except Exception as e:
            logger.error(f"Error getting user alerts: {e}")
            return []
    
    async def cancel_alert(self, user_id: int, alert_id: int) -> Dict[str, Any]:
        """Cancel a price alert"""
        try:
            # Verify alert belongs to user
            alerts = self.db.get_active_price_alerts()
            user_alert = next((a for a in alerts if a["id"] == alert_id and a["user_id"] == user_id), None)
            
            if not user_alert:
                return {
                    "success": False,
                    "error": "Alert not found or doesn't belong to user"
                }
            
            # Deactivate alert
            self.db.deactivate_price_alert(alert_id)
            
            return {
                "success": True,
                "message": f"Alert for {user_alert['asset_symbol']} cancelled"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling alert: {e}")
            return {
                "success": False,
                "error": f"Failed to cancel alert: {str(e)}"
            }
    
    def format_alert_list(self, alerts: List[Dict[str, Any]]) -> str:
        """Format alert list for display"""
        if not alerts:
            return "📋 هیچ هشدار فعالی ندارید"
        
        output = "📋 **هشدارهای فعال شما:**\n\n"
        
        for i, alert in enumerate(alerts, 1):
            condition_text = {
                "above": "بالاتر از",
                "below": "پایین‌تر از",
                "equals": "برابر با"
            }.get(alert["condition"], alert["condition"])
            
            output += f"{i}. 💰 **{alert['asset_symbol']}**\n"
            output += f"   🎯 {condition_text} ${alert['target_price']:.2f}\n"
            output += f"   📅 ایجاد: {alert['created_at']}\n"
            output += f"   🆔 ID: {alert['id']}\n\n"
        
        return output

