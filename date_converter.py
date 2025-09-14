import jdatetime
from hijridate import Gregorian
from datetime import datetime, timezone, timedelta
import pytz
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DateConverter:
    """Advanced date conversion with multiple calendar systems and timezone support"""
    
    def __init__(self):
        # Supported calendar systems
        self.calendars = {
            "gregorian": "Gregorian Calendar",
            "persian": "Persian/Jalali Calendar", 
            "hijri": "Islamic/Hijri Calendar",
            "hebrew": "Hebrew Calendar",
            "chinese": "Chinese Calendar",
            "julian": "Julian Calendar"
        }
        
        # Common timezones
        self.timezones = {
            "UTC": "UTC",
            "GMT": "GMT",
            "EST": "America/New_York",
            "PST": "America/Los_Angeles",
            "CET": "Europe/Paris",
            "JST": "Asia/Tokyo",
            "IST": "Asia/Kolkata",
            "IRST": "Asia/Tehran",
            "MSK": "Europe/Moscow",
            "AEST": "Australia/Sydney",
            "BST": "Europe/London",
            "CST": "Asia/Shanghai",
            "KST": "Asia/Seoul",
            "AST": "Asia/Riyadh",
            "EET": "Europe/Athens"
        }
        
        # Persian month names
        self.persian_months = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        # Persian day names
        self.persian_days = [
            "شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"
        ]
        
        # Hijri month names
        self.hijri_months = [
            "محرم", "صفر", "ربیع‌الاول", "ربیع‌الثانی", "جمادی‌الاول", "جمادی‌الثانی",
            "رجب", "شعبان", "رمضان", "شوال", "ذی‌القعده", "ذی‌الحجه"
        ]
    
    def convert_date(self, date_str: str, from_format: str = "auto", 
                    to_calendars: List[str] = None) -> Dict[str, any]:
        """Convert date between different calendar systems"""
        try:
            # Parse input date
            parsed_date = self._parse_date(date_str, from_format)
            if not parsed_date:
                return {
                    "success": False,
                    "error": "Unable to parse input date"
                }
            
            # Default calendars to convert to
            if to_calendars is None:
                to_calendars = ["persian", "hijri", "gregorian"]
            
            results = {}
            
            for calendar in to_calendars:
                try:
                    converted = self._convert_to_calendar(parsed_date, calendar)
                    if converted:
                        results[calendar] = converted
                except Exception as e:
                    logger.warning(f"Failed to convert to {calendar}: {e}")
                    results[calendar] = {"error": str(e)}
            
            return {
                "success": True,
                "input_date": date_str,
                "parsed_date": parsed_date.isoformat(),
                "conversions": results
            }
            
        except Exception as e:
            logger.error(f"Date conversion error: {e}")
            return {
                "success": False,
                "error": f"Date conversion failed: {str(e)}"
            }
    
    def _parse_date(self, date_str: str, format_type: str) -> Optional[datetime]:
        """Parse date string into datetime object"""
        try:
            # Auto-detect format
            if format_type == "auto":
                formats_to_try = [
                    "%Y-%m-%d",      # 2024-01-15
                    "%d/%m/%Y",      # 15/01/2024
                    "%m/%d/%Y",      # 01/15/2024
                    "%Y/%m/%d",      # 2024/01/15
                    "%d-%m-%Y",      # 15-01-2024
                    "%Y-%m-%d %H:%M:%S",  # 2024-01-15 14:30:00
                    "%d/%m/%Y %H:%M",     # 15/01/2024 14:30
                ]
                
                for fmt in formats_to_try:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                
                # Try Persian date format
                if "/" in date_str and len(date_str.split("/")) == 3:
                    try:
                        parts = date_str.split("/")
                        if len(parts[0]) == 4:  # Year first
                            year, month, day = map(int, parts)
                            return jdatetime.date(year, month, day).togregorian()
                        else:  # Day first
                            day, month, year = map(int, parts)
                            return jdatetime.date(year, month, day).togregorian()
                    except:
                        pass
            
            # Specific format
            else:
                return datetime.strptime(date_str, format_type)
                
        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            return None
    
    def _convert_to_calendar(self, date_obj: datetime, calendar: str) -> Dict[str, any]:
        """Convert datetime to specific calendar system"""
        if calendar == "gregorian":
            return {
                "calendar": "Gregorian",
                "date": date_obj.strftime("%Y-%m-%d"),
                "formatted": date_obj.strftime("%A, %B %d, %Y"),
                "day_of_week": date_obj.strftime("%A"),
                "month_name": date_obj.strftime("%B"),
                "year": date_obj.year,
                "month": date_obj.month,
                "day": date_obj.day
            }
        
        elif calendar == "persian":
            try:
                persian_date = jdatetime.date.fromgregorian(date=date_obj.date())
                return {
                    "calendar": "Persian/Jalali",
                    "date": f"{persian_date.year}/{persian_date.month:02d}/{persian_date.day:02d}",
                    "formatted": f"{persian_date.day} {self.persian_months[persian_date.month-1]} {persian_date.year}",
                    "day_of_week": self.persian_days[persian_date.weekday()],
                    "month_name": self.persian_months[persian_date.month-1],
                    "year": persian_date.year,
                    "month": persian_date.month,
                    "day": persian_date.day
                }
            except Exception as e:
                return {"error": f"Persian conversion failed: {e}"}
        
        elif calendar == "hijri":
            try:
                greg = Gregorian(date_obj.year, date_obj.month, date_obj.day)
                hijri_date = greg.to_hijri()
                return {
                    "calendar": "Islamic/Hijri",
                    "date": f"{hijri_date.year}/{hijri_date.month:02d}/{hijri_date.day:02d}",
                    "formatted": f"{hijri_date.day} {self.hijri_months[hijri_date.month-1]} {hijri_date.year}",
                    "month_name": self.hijri_months[hijri_date.month-1],
                    "year": hijri_date.year,
                    "month": hijri_date.month,
                    "day": hijri_date.day
                }
            except Exception as e:
                return {"error": f"Hijri conversion failed: {e}"}
        
        elif calendar == "hebrew":
            # Note: Hebrew calendar conversion would require additional library
            return {"error": "Hebrew calendar conversion not implemented"}
        
        elif calendar == "chinese":
            # Note: Chinese calendar conversion would require additional library
            return {"error": "Chinese calendar conversion not implemented"}
        
        else:
            return {"error": f"Unknown calendar: {calendar}"}
    
    def convert_timezone(self, date_str: str, from_tz: str, to_tz: str) -> Dict[str, any]:
        """Convert datetime between timezones"""
        try:
            # Parse input date
            parsed_date = self._parse_date(date_str, "auto")
            if not parsed_date:
                return {
                    "success": False,
                    "error": "Unable to parse input date"
                }
            
            # Get timezone objects
            from_timezone = pytz.timezone(self.timezones.get(from_tz, from_tz))
            to_timezone = pytz.timezone(self.timezones.get(to_tz, to_tz))
            
            # Localize to source timezone
            if parsed_date.tzinfo is None:
                localized_date = from_timezone.localize(parsed_date)
            else:
                localized_date = parsed_date.astimezone(from_timezone)
            
            # Convert to target timezone
            converted_date = localized_date.astimezone(to_timezone)
            
            return {
                "success": True,
                "original_date": date_str,
                "from_timezone": from_tz,
                "to_timezone": to_tz,
                "converted_date": converted_date.strftime("%Y-%m-%d %H:%M:%S"),
                "formatted": converted_date.strftime("%A, %B %d, %Y at %I:%M %p"),
                "timezone_offset": converted_date.strftime("%z"),
                "utc_offset": str(converted_date.utcoffset())
            }
            
        except Exception as e:
            logger.error(f"Timezone conversion error: {e}")
            return {
                "success": False,
                "error": f"Timezone conversion failed: {str(e)}"
            }
    
    def get_current_time(self, timezone_name: str = "UTC") -> Dict[str, any]:
        """Get current time in specified timezone"""
        try:
            tz = pytz.timezone(self.timezones.get(timezone_name, timezone_name))
            now = datetime.now(tz)
            
            return {
                "success": True,
                "timezone": timezone_name,
                "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
                "formatted": now.strftime("%A, %B %d, %Y at %I:%M %p"),
                "timestamp": now.timestamp(),
                "utc_offset": str(now.utcoffset())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get current time: {str(e)}"
            }
    
    def calculate_date_difference(self, date1_str: str, date2_str: str) -> Dict[str, any]:
        """Calculate difference between two dates"""
        try:
            date1 = self._parse_date(date1_str, "auto")
            date2 = self._parse_date(date2_str, "auto")
            
            if not date1 or not date2:
                return {
                    "success": False,
                    "error": "Unable to parse one or both dates"
                }
            
            # Calculate difference
            diff = abs(date2 - date1)
            
            # Extract components
            days = diff.days
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Calculate years, months, weeks
            years = days // 365
            months = days // 30
            weeks = days // 7
            
            return {
                "success": True,
                "date1": date1_str,
                "date2": date2_str,
                "difference": {
                    "total_days": days,
                    "total_hours": days * 24 + hours,
                    "total_minutes": (days * 24 + hours) * 60 + minutes,
                    "total_seconds": diff.total_seconds(),
                    "years": years,
                    "months": months,
                    "weeks": weeks,
                    "days": days % 7,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds
                },
                "formatted": f"{days} days, {hours} hours, {minutes} minutes"
            }
            
        except Exception as e:
            logger.error(f"Date difference calculation error: {e}")
            return {
                "success": False,
                "error": f"Date difference calculation failed: {str(e)}"
            }
    
    def add_subtract_days(self, date_str: str, days: int, operation: str = "add") -> Dict[str, any]:
        """Add or subtract days from a date"""
        try:
            parsed_date = self._parse_date(date_str, "auto")
            if not parsed_date:
                return {
                    "success": False,
                    "error": "Unable to parse input date"
                }
            
            if operation == "add":
                result_date = parsed_date + timedelta(days=days)
            elif operation == "subtract":
                result_date = parsed_date - timedelta(days=days)
            else:
                return {
                    "success": False,
                    "error": "Operation must be 'add' or 'subtract'"
                }
            
            return {
                "success": True,
                "original_date": date_str,
                "operation": operation,
                "days": days,
                "result_date": result_date.strftime("%Y-%m-%d"),
                "formatted": result_date.strftime("%A, %B %d, %Y")
            }
            
        except Exception as e:
            logger.error(f"Date arithmetic error: {e}")
            return {
                "success": False,
                "error": f"Date arithmetic failed: {str(e)}"
            }
    
    def get_week_info(self, date_str: str) -> Dict[str, any]:
        """Get week information for a date"""
        try:
            parsed_date = self._parse_date(date_str, "auto")
            if not parsed_date:
                return {
                    "success": False,
                    "error": "Unable to parse input date"
                }
            
            # Get week start (Monday) and end (Sunday)
            week_start = parsed_date - timedelta(days=parsed_date.weekday())
            week_end = week_start + timedelta(days=6)
            
            # Get week number
            week_number = parsed_date.isocalendar()[1]
            year = parsed_date.isocalendar()[0]
            
            return {
                "success": True,
                "date": date_str,
                "week_number": week_number,
                "year": year,
                "week_start": week_start.strftime("%Y-%m-%d"),
                "week_end": week_end.strftime("%Y-%m-%d"),
                "day_of_week": parsed_date.strftime("%A"),
                "day_of_year": parsed_date.timetuple().tm_yday
            }
            
        except Exception as e:
            logger.error(f"Week info error: {e}")
            return {
                "success": False,
                "error": f"Week info calculation failed: {str(e)}"
            }
    
    def get_supported_calendars(self) -> Dict[str, str]:
        """Get list of supported calendar systems"""
        return self.calendars
    
    def get_supported_timezones(self) -> Dict[str, str]:
        """Get list of supported timezones"""
        return self.timezones
    
    def format_date_for_display(self, conversion_result: Dict[str, any]) -> str:
        """Format date conversion result for display"""
        if not conversion_result["success"]:
            return f"❌ {conversion_result['error']}"
        
        output = f"📅 **تاریخ اصلی:** {conversion_result['input_date']}\n\n"
        
        for calendar, data in conversion_result["conversions"].items():
            if "error" in data:
                output += f"❌ **{calendar}:** {data['error']}\n"
            else:
                output += f"📆 **{data['calendar']}:**\n"
                output += f"   📅 {data['formatted']}\n"
                output += f"   📊 {data['date']}\n"
                output += f"   📝 {data['day_of_week']}\n\n"
        
        return output

