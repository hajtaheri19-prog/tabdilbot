import math
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class UnitConverter:
    """Comprehensive unit conversion system"""
    
    def __init__(self):
        # Base units and conversion factors
        self.units = {
            # Length conversions (base: meter)
            "length": {
                "mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
                "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mile": 1609.34,
                "nautical_mile": 1852, "light_year": 9.461e15,
                "parsec": 3.086e16, "angstrom": 1e-10, "micron": 1e-6
            },
            
            # Weight/Mass conversions (base: gram)
            "weight": {
                "mg": 0.001, "g": 1, "kg": 1000, "ton": 1000000,
                "oz": 28.3495, "lb": 453.592, "stone": 6350.29,
                "carat": 0.2, "grain": 0.0647989, "dram": 1.77185,
                "troy_oz": 31.1035, "troy_pound": 373.242
            },
            
            # Volume conversions (base: liter)
            "volume": {
                "ml": 0.001, "l": 1, "gal": 3.78541, "qt": 0.946353,
                "pt": 0.473176, "cup": 0.236588, "fl_oz": 0.0295735,
                "tbsp": 0.0147868, "tsp": 0.00492892, "barrel": 158.987,
                "cubic_meter": 1000, "cubic_cm": 0.001, "cubic_inch": 0.0163871
            },
            
            # Area conversions (base: square meter)
            "area": {
                "mm²": 1e-6, "cm²": 1e-4, "m²": 1, "km²": 1e6,
                "in²": 6.4516e-4, "ft²": 0.092903, "yd²": 0.836127,
                "acre": 4046.86, "hectare": 10000, "square_mile": 2.59e6
            },
            
            # Time conversions (base: second)
            "time": {
                "ns": 1e-9, "μs": 1e-6, "ms": 1e-3, "s": 1,
                "min": 60, "h": 3600, "day": 86400, "week": 604800,
                "month": 2629746, "year": 31556952, "decade": 315569520,
                "century": 3155695200
            },
            
            # Speed conversions (base: m/s)
            "speed": {
                "m/s": 1, "km/h": 0.277778, "mph": 0.44704,
                "ft/s": 0.3048, "knot": 0.514444, "mach": 343,
                "light_speed": 299792458
            },
            
            # Pressure conversions (base: pascal)
            "pressure": {
                "pa": 1, "kpa": 1000, "mpa": 1e6, "bar": 1e5,
                "atm": 101325, "torr": 133.322, "psi": 6894.76,
                "mmhg": 133.322, "inhg": 3386.39
            },
            
            # Energy conversions (base: joule)
            "energy": {
                "j": 1, "kj": 1000, "mj": 1e6, "cal": 4.184,
                "kcal": 4184, "btu": 1055.06, "kwh": 3.6e6,
                "wh": 3600, "therm": 1.055e8, "quad": 1.055e18
            },
            
            # Power conversions (base: watt)
            "power": {
                "w": 1, "kw": 1000, "mw": 1e6, "gw": 1e9,
                "hp": 745.7, "btu/h": 0.293071, "cal/s": 4.184,
                "ft-lb/s": 1.35582
            },
            
            # Data storage conversions (base: byte)
            "data": {
                "bit": 0.125, "byte": 1, "kb": 1024, "mb": 1024**2,
                "gb": 1024**3, "tb": 1024**4, "pb": 1024**5,
                "kib": 1024, "mib": 1024**2, "gib": 1024**3,
                "tib": 1024**4, "pib": 1024**5
            }
        }
        
        # Temperature conversion functions (special case)
        self.temperature_conversions = {
            "celsius": {"fahrenheit": lambda c: c * 9/5 + 32,
                       "kelvin": lambda c: c + 273.15,
                       "rankine": lambda c: (c + 273.15) * 9/5},
            
            "fahrenheit": {"celsius": lambda f: (f - 32) * 5/9,
                          "kelvin": lambda f: (f - 32) * 5/9 + 273.15,
                          "rankine": lambda f: f + 459.67},
            
            "kelvin": {"celsius": lambda k: k - 273.15,
                      "fahrenheit": lambda k: (k - 273.15) * 9/5 + 32,
                      "rankine": lambda k: k * 9/5},
            
            "rankine": {"celsius": lambda r: (r - 491.67) * 5/9,
                       "fahrenheit": lambda r: r - 459.67,
                       "kelvin": lambda r: r * 5/9}
        }
    
    def get_categories(self) -> List[str]:
        """Get all available conversion categories"""
        return list(self.units.keys()) + ["temperature"]
    
    def get_units_in_category(self, category: str) -> List[str]:
        """Get all units in a specific category"""
        if category == "temperature":
            return list(self.temperature_conversions.keys())
        return list(self.units.get(category, {}).keys())
    
    def convert(self, value: float, from_unit: str, to_unit: str, 
                category: str) -> Dict[str, any]:
        """Convert between units"""
        try:
            # Handle temperature conversion
            if category == "temperature":
                return self._convert_temperature(value, from_unit, to_unit)
            
            # Handle regular unit conversion
            if category not in self.units:
                return {
                    "success": False,
                    "error": f"Unknown category: {category}"
                }
            
            units = self.units[category]
            if from_unit not in units or to_unit not in units:
                return {
                    "success": False,
                    "error": f"Unknown units: {from_unit} or {to_unit}"
                }
            
            # Convert to base unit, then to target unit
            base_value = value * units[from_unit]
            result = base_value / units[to_unit]
            
            return {
                "success": True,
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "result": result,
                "category": category
            }
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return {
                "success": False,
                "error": f"Conversion failed: {str(e)}"
            }
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> Dict[str, any]:
        """Convert temperature between different scales"""
        if from_unit == to_unit:
            return {
                "success": True,
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "result": value,
                "category": "temperature"
            }
        
        if from_unit not in self.temperature_conversions:
            return {
                "success": False,
                "error": f"Unknown temperature unit: {from_unit}"
            }
        
        if to_unit not in self.temperature_conversions[from_unit]:
            return {
                "success": False,
                "error": f"Cannot convert from {from_unit} to {to_unit}"
            }
        
        try:
            result = self.temperature_conversions[from_unit][to_unit](value)
            return {
                "success": True,
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "result": result,
                "category": "temperature"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Temperature conversion failed: {str(e)}"
            }
    
    def get_conversion_suggestions(self, category: str) -> List[Dict[str, str]]:
        """Get common conversion suggestions for a category"""
        suggestions = {
            "length": [
                {"from": "km", "to": "mile", "description": "Kilometers to Miles"},
                {"from": "m", "to": "ft", "description": "Meters to Feet"},
                {"from": "cm", "to": "in", "description": "Centimeters to Inches"}
            ],
            "weight": [
                {"from": "kg", "to": "lb", "description": "Kilograms to Pounds"},
                {"from": "g", "to": "oz", "description": "Grams to Ounces"},
                {"from": "ton", "to": "lb", "description": "Tons to Pounds"}
            ],
            "volume": [
                {"from": "l", "to": "gal", "description": "Liters to Gallons"},
                {"from": "ml", "to": "fl_oz", "description": "Milliliters to Fluid Ounces"},
                {"from": "gal", "to": "l", "description": "Gallons to Liters"}
            ],
            "temperature": [
                {"from": "celsius", "to": "fahrenheit", "description": "Celsius to Fahrenheit"},
                {"from": "fahrenheit", "to": "celsius", "description": "Fahrenheit to Celsius"},
                {"from": "celsius", "to": "kelvin", "description": "Celsius to Kelvin"}
            ],
            "area": [
                {"from": "m²", "to": "ft²", "description": "Square Meters to Square Feet"},
                {"from": "km²", "to": "acre", "description": "Square Kilometers to Acres"},
                {"from": "hectare", "to": "acre", "description": "Hectares to Acres"}
            ],
            "speed": [
                {"from": "km/h", "to": "mph", "description": "km/h to mph"},
                {"from": "m/s", "to": "km/h", "description": "m/s to km/h"},
                {"from": "mph", "to": "km/h", "description": "mph to km/h"}
            ]
        }
        
        return suggestions.get(category, [])
    
    def format_result(self, result: Dict[str, any], precision: int = 6) -> str:
        """Format conversion result for display"""
        if not result["success"]:
            return f"❌ {result['error']}"
        
        value = result["value"]
        converted_value = result["result"]
        from_unit = result["from_unit"]
        to_unit = result["to_unit"]
        
        # Format numbers appropriately
        if abs(converted_value) < 0.001 or abs(converted_value) > 1e6:
            formatted_result = f"{converted_value:.2e}"
        else:
            formatted_result = f"{converted_value:.{precision}f}".rstrip('0').rstrip('.')
        
        return f"{value} {from_unit} = {formatted_result} {to_unit}"
    
    def get_unit_info(self, unit: str, category: str) -> Dict[str, any]:
        """Get information about a specific unit"""
        if category == "temperature":
            return {
                "unit": unit,
                "category": "temperature",
                "description": self._get_temperature_description(unit)
            }
        
        if category in self.units and unit in self.units[category]:
            factor = self.units[category][unit]
            return {
                "unit": unit,
                "category": category,
                "factor": factor,
                "description": self._get_unit_description(unit, category)
            }
        
        return {"error": "Unit not found"}
    
    def _get_temperature_description(self, unit: str) -> str:
        """Get description for temperature units"""
        descriptions = {
            "celsius": "Celsius (°C) - Metric temperature scale",
            "fahrenheit": "Fahrenheit (°F) - Imperial temperature scale",
            "kelvin": "Kelvin (K) - Absolute temperature scale",
            "rankine": "Rankine (°R) - Absolute temperature scale (Fahrenheit-based)"
        }
        return descriptions.get(unit, "Unknown temperature unit")
    
    def _get_unit_description(self, unit: str, category: str) -> str:
        """Get description for regular units"""
        descriptions = {
            "length": {
                "mm": "Millimeter - 1/1000 of a meter",
                "cm": "Centimeter - 1/100 of a meter",
                "m": "Meter - Base unit of length",
                "km": "Kilometer - 1000 meters",
                "in": "Inch - 1/12 of a foot",
                "ft": "Foot - 12 inches",
                "mile": "Mile - 5280 feet"
            },
            "weight": {
                "mg": "Milligram - 1/1000 of a gram",
                "g": "Gram - Base unit of mass",
                "kg": "Kilogram - 1000 grams",
                "ton": "Metric ton - 1000 kilograms",
                "oz": "Ounce - 1/16 of a pound",
                "lb": "Pound - 16 ounces"
            },
            "volume": {
                "ml": "Milliliter - 1/1000 of a liter",
                "l": "Liter - Base unit of volume",
                "gal": "US Gallon - 3.78541 liters",
                "qt": "US Quart - 1/4 of a gallon",
                "pt": "US Pint - 1/2 of a quart"
            }
        }
        
        return descriptions.get(category, {}).get(unit, f"{unit} unit")
    
    def batch_convert(self, value: float, from_unit: str, category: str, 
                     target_units: List[str]) -> Dict[str, any]:
        """Convert a value to multiple target units"""
        results = {}
        
        for to_unit in target_units:
            result = self.convert(value, from_unit, to_unit, category)
            if result["success"]:
                results[to_unit] = result["result"]
            else:
                results[to_unit] = None
        
        return {
            "success": True,
            "value": value,
            "from_unit": from_unit,
            "category": category,
            "results": results
        }

