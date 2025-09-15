import requests
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    """Weather forecast and current conditions service"""
    
    def __init__(self, database):
        self.db = database
        self.api_keys = {
            "openweather": "",  # Add your OpenWeather API key
            "weatherapi": ""  # Add your WeatherAPI key
        }
        
        self.endpoints = {
            "openweather": "https://api.openweathermap.org/data/2.5",
            "weatherapi": "http://api.weatherapi.com/v1"
        }
        
        # Weather condition emojis
        self.weather_emojis = {
            "clear": "☀️", "clouds": "☁️", "rain": "🌧️", "snow": "❄️",
            "thunderstorm": "⛈️", "drizzle": "🌦️", "mist": "🌫️",
            "fog": "🌫️", "haze": "🌫️", "dust": "🌪️", "sand": "🌪️"
        }
    
    async def get_current_weather(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """Get current weather for a location"""
        # Check cache
        cache_key = f"weather_current_{location}_{units}_{datetime.now().strftime('%Y%m%d%H')}"
        cached_weather = self.db.get_from_cache(cache_key)
        
        if cached_weather:
            try:
                return json.loads(cached_weather)
            except json.JSONDecodeError:
                pass
        
        # Try OpenWeather API
        if self.api_keys["openweather"]:
            try:
                result = await self._get_openweather_current(location, units)
                if result["success"]:
                    # Cache for 1 hour
                    self.db.add_to_cache(cache_key, json.dumps(result), 60)
                    return result
            except Exception as e:
                logger.warning(f"OpenWeather API failed: {e}")
        
        # Try WeatherAPI as fallback
        if self.api_keys["weatherapi"]:
            try:
                result = await self._get_weatherapi_current(location, units)
                if result["success"]:
                    self.db.add_to_cache(cache_key, json.dumps(result), 60)
                    return result
            except Exception as e:
                logger.warning(f"WeatherAPI failed: {e}")
        
        return {
            "success": False,
            "error": "Weather data not available",
            "location": location
        }
    
    async def _get_openweather_current(self, location: str, units: str) -> Dict[str, Any]:
        """Get current weather from OpenWeather API"""
        url = f"{self.endpoints['openweather']}/weather"
        params = {
            "q": location,
            "appid": self.api_keys["openweather"],
            "units": units
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "location": data["name"],
                        "country": data["sys"]["country"],
                        "temperature": data["main"]["temp"],
                        "feels_like": data["main"]["feels_like"],
                        "humidity": data["main"]["humidity"],
                        "pressure": data["main"]["pressure"],
                        "description": data["weather"][0]["description"],
                        "main": data["weather"][0]["main"],
                        "wind_speed": data["wind"]["speed"],
                        "wind_direction": data["wind"].get("deg", 0),
                        "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                        "cloudiness": data["clouds"]["all"],
                        "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).isoformat(),
                        "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).isoformat(),
                        "timestamp": datetime.now().isoformat(),
                        "source": "openweather"
                    }
        
        return {"success": False, "error": "OpenWeather API failed"}
    
    async def _get_weatherapi_current(self, location: str, units: str) -> Dict[str, Any]:
        """Get current weather from WeatherAPI"""
        url = f"{self.endpoints['weatherapi']}/current.json"
        params = {
            "key": self.api_keys["weatherapi"],
            "q": location,
            "aqi": "yes"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "location": data["location"]["name"],
                        "country": data["location"]["country"],
                        "temperature": data["current"]["temp_c"],
                        "feels_like": data["current"]["feelslike_c"],
                        "humidity": data["current"]["humidity"],
                        "pressure": data["current"]["pressure_mb"],
                        "description": data["current"]["condition"]["text"],
                        "main": data["current"]["condition"]["text"],
                        "wind_speed": data["current"]["wind_kph"],
                        "wind_direction": data["current"]["wind_degree"],
                        "visibility": data["current"]["vis_km"],
                        "cloudiness": data["current"]["cloud"],
                        "uv_index": data["current"]["uv"],
                        "air_quality": data["current"].get("air_quality", {}),
                        "timestamp": datetime.now().isoformat(),
                        "source": "weatherapi"
                    }
        
        return {"success": False, "error": "WeatherAPI failed"}
    
    async def get_forecast(self, location: str, days: int = 5, units: str = "metric") -> Dict[str, Any]:
        """Get weather forecast"""
        # Check cache
        cache_key = f"weather_forecast_{location}_{days}_{units}_{datetime.now().strftime('%Y%m%d%H')}"
        cached_forecast = self.db.get_from_cache(cache_key)
        
        if cached_forecast:
            try:
                return json.loads(cached_forecast)
            except json.JSONDecodeError:
                pass
        
        # Try OpenWeather API
        if self.api_keys["openweather"]:
            try:
                result = await self._get_openweather_forecast(location, days, units)
                if result["success"]:
                    # Cache for 3 hours
                    self.db.add_to_cache(cache_key, json.dumps(result), 180)
                    return result
            except Exception as e:
                logger.warning(f"OpenWeather forecast API failed: {e}")
        
        return {
            "success": False,
            "error": "Weather forecast not available",
            "location": location
        }
    
    async def _get_openweather_forecast(self, location: str, days: int, units: str) -> Dict[str, Any]:
        """Get forecast from OpenWeather API"""
        url = f"{self.endpoints['openweather']}/forecast"
        params = {
            "q": location,
            "appid": self.api_keys["openweather"],
            "units": units
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process forecast data
                    forecast_days = {}
                    for item in data["list"]:
                        date = datetime.fromtimestamp(item["dt"]).date()
                        date_str = date.isoformat()
                        
                        if date_str not in forecast_days:
                            forecast_days[date_str] = {
                                "date": date_str,
                                "temperatures": [],
                                "descriptions": [],
                                "humidity": [],
                                "wind_speed": []
                            }
                        
                        forecast_days[date_str]["temperatures"].append(item["main"]["temp"])
                        forecast_days[date_str]["descriptions"].append(item["weather"][0]["description"])
                        forecast_days[date_str]["humidity"].append(item["main"]["humidity"])
                        forecast_days[date_str]["wind_speed"].append(item["wind"]["speed"])
                    
                    # Calculate daily averages
                    daily_forecast = []
                    for date_str, day_data in list(forecast_days.items())[:days]:
                        daily_forecast.append({
                            "date": date_str,
                            "min_temp": min(day_data["temperatures"]),
                            "max_temp": max(day_data["temperatures"]),
                            "avg_temp": sum(day_data["temperatures"]) / len(day_data["temperatures"]),
                            "description": max(set(day_data["descriptions"]), key=day_data["descriptions"].count),
                            "humidity": sum(day_data["humidity"]) / len(day_data["humidity"]),
                            "wind_speed": sum(day_data["wind_speed"]) / len(day_data["wind_speed"])
                        })
                    
                    return {
                        "success": True,
                        "location": data["city"]["name"],
                        "country": data["city"]["country"],
                        "forecast": daily_forecast,
                        "days": len(daily_forecast),
                        "timestamp": datetime.now().isoformat(),
                        "source": "openweather"
                    }
        
        return {"success": False, "error": "OpenWeather forecast API failed"}
    
    def get_weather_emoji(self, condition: str) -> str:
        """Get emoji for weather condition"""
        condition_lower = condition.lower()
        
        if "clear" in condition_lower or "sun" in condition_lower:
            return self.weather_emojis["clear"]
        elif "cloud" in condition_lower:
            return self.weather_emojis["clouds"]
        elif "rain" in condition_lower:
            return self.weather_emojis["rain"]
        elif "snow" in condition_lower:
            return self.weather_emojis["snow"]
        elif "thunder" in condition_lower or "storm" in condition_lower:
            return self.weather_emojis["thunderstorm"]
        elif "drizzle" in condition_lower:
            return self.weather_emojis["drizzle"]
        elif "mist" in condition_lower or "fog" in condition_lower or "haze" in condition_lower:
            return self.weather_emojis["mist"]
        else:
            return "🌤️"  # Default weather emoji
    
    def format_weather_result(self, result: Dict[str, Any]) -> str:
        """Format weather result for display"""
        if not result["success"]:
            return f"❌ {result['error']}"
        
        emoji = self.get_weather_emoji(result["main"])
        
        output = f"{emoji} **آب و هوای {result['location']}**\n\n"
        output += f"🌡️ دما: {result['temperature']:.1f}°C\n"
        output += f"🤔 احساس: {result['feels_like']:.1f}°C\n"
        output += f"💧 رطوبت: {result['humidity']}%\n"
        output += f"🔽 فشار: {result['pressure']} hPa\n"
        output += f"💨 باد: {result['wind_speed']:.1f} m/s\n"
        output += f"👁️ دید: {result['visibility']:.1f} km\n"
        output += f"☁️ ابری: {result['cloudiness']}%\n"
        output += f"📝 وضعیت: {result['description']}\n"
        
        if "sunrise" in result and "sunset" in result:
            sunrise_time = datetime.fromisoformat(result['sunrise']).strftime("%H:%M")
            sunset_time = datetime.fromisoformat(result['sunset']).strftime("%H:%M")
            output += f"🌅 طلوع: {sunrise_time}\n"
            output += f"🌇 غروب: {sunset_time}\n"
        
        output += f"\n🕐 زمان: {result['timestamp']}\n"
        output += f"🔗 منبع: {result['source']}"
        
        return output
    
    def format_forecast_result(self, result: Dict[str, Any]) -> str:
        """Format forecast result for display"""
        if not result["success"]:
            return f"❌ {result['error']}"
        
        output = f"📅 **پیش‌بینی آب و هوا - {result['location']}**\n\n"
        
        for day in result["forecast"]:
            emoji = self.get_weather_emoji(day["description"])
            date_obj = datetime.fromisoformat(day["date"])
            day_name = date_obj.strftime("%A")
            
            output += f"{emoji} **{day_name} ({day['date']})**\n"
            output += f"🌡️ دما: {day['min_temp']:.1f}°C - {day['max_temp']:.1f}°C\n"
            output += f"📝 وضعیت: {day['description']}\n"
            output += f"💧 رطوبت: {day['humidity']:.0f}%\n"
            output += f"💨 باد: {day['wind_speed']:.1f} m/s\n\n"
        
        output += f"🕐 زمان: {result['timestamp']}\n"
        output += f"🔗 منبع: {result['source']}"
        
        return output

