"""
🧠 Smart Text Processor - پردازشگر هوشمند متن
یک سیستم پیشرفته برای تشخیص خودکار نوع درخواست کاربر
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SmartTextProcessor:
    """کلاس پردازشگر هوشمند متن"""
    
    def __init__(self):
        # الگوهای تشخیص ارز
        self.currency_patterns = {
            'symbols': r'\b(USD|EUR|GBP|JPY|CHF|CAD|AUD|CNY|SEK|NZD|MXN|SGD|HKD|NOK|TRY|RUB|INR|BRL|ZAR|KRW|IRR|AED|SAR|QAR|KWD|BHD|OMR|JOD|LBP|EGP)\b',
            'crypto': r'\b(BTC|ETH|BNB|XRP|ADA|SOL|DOT|DOGE|AVAX|MATIC|LTC|BCH|UNI|LINK|ATOM|XLM|VET|FIL|TRX|ETC|USDT|USDC|DAI|BUSD)\b',
            'keywords': ['دلار', 'یورو', 'پوند', 'ین', 'فرانک', 'دلار کانادا', 'دلار استرالیا', 'یوان', 'کرون', 'لیر', 'روبل', 'روپیه', 'ریال', 'درهم', 'ریال سعودی', 'ریال قطر', 'دینار', 'دینار بحرین', 'ریال عمان', 'دینار اردن', 'لیر لبنان', 'پوند مصر'],
            'crypto_keywords': ['بیت کوین', 'اتریوم', 'بایننس', 'ریپل', 'کاردانو', 'سولانا', 'پولکادات', 'دوج کوین', 'آوالانچ', 'پالیگان', 'لایت کوین', 'بیت کوین کش', 'یونی سواپ', 'چین لینک', 'اتم', 'استلار', 'وی چین', 'فایل کوین', 'ترون', 'اتریوم کلاسیک']
        }
        
        # الگوهای تشخیص واحد
        self.unit_patterns = {
            'length': {
                'units': ['mm', 'cm', 'm', 'km', 'in', 'ft', 'yd', 'mile', 'متر', 'سانتی متر', 'کیلومتر', 'اینچ', 'فوت', 'یارد', 'مایل'],
                'keywords': ['طول', 'فاصله', 'مسافت', 'اندازه']
            },
            'weight': {
                'units': ['mg', 'g', 'kg', 'ton', 'oz', 'lb', 'stone', 'میلی گرم', 'گرم', 'کیلوگرم', 'تن', 'اونس', 'پوند'],
                'keywords': ['وزن', 'جرم', 'سنگینی']
            },
            'temperature': {
                'units': ['celsius', 'fahrenheit', 'kelvin', 'c', 'f', 'k', 'سانتی گراد', 'فارنهایت', 'کلوین'],
                'keywords': ['دما', 'حرارت', 'گرما', 'سرما']
            },
            'volume': {
                'units': ['ml', 'l', 'gal', 'qt', 'pt', 'cup', 'میلی لیتر', 'لیتر', 'گالن', 'کوارت', 'پینت', 'فنجان'],
                'keywords': ['حجم', 'ظرفیت', 'مایع']
            },
            'area': {
                'units': ['m2', 'km2', 'ft2', 'yd2', 'acre', 'hectare', 'متر مربع', 'کیلومتر مربع', 'فوت مربع', 'یارد مربع', 'جریب', 'هکتار'],
                'keywords': ['مساحت', 'سطح', 'زمین']
            },
            'time': {
                'units': ['s', 'min', 'h', 'day', 'week', 'month', 'year', 'ثانیه', 'دقیقه', 'ساعت', 'روز', 'هفته', 'ماه', 'سال'],
                'keywords': ['زمان', 'مدت', 'طول']
            }
        }
        
        # الگوهای تشخیص تاریخ
        self.date_patterns = {
            'gregorian': [
                r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',  # 2024-01-15 or 2024/01/15
                r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b',  # 15-01-2024 or 15/01/2024
                r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',  # 15 Jan 2024
            ],
            'persian': [
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # 1403/01/15
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',  # 15/01/1403
            ],
            'keywords': ['تاریخ', 'روز', 'ماه', 'سال', 'امروز', 'دیروز', 'فردا', 'هفته', 'ماه', 'سال']
        }
        
        # الگوهای تشخیص قیمت
        self.price_patterns = {
            'stocks': r'\b[A-Z]{1,5}\b',  # Stock symbols like AAPL, GOOGL
            'crypto': r'\b(BTC|ETH|BNB|XRP|ADA|SOL|DOT|DOGE|AVAX|MATIC|LTC|BCH|UNI|LINK|ATOM|XLM|VET|FIL|TRX|ETC)\b',
            'commodities': ['gold', 'silver', 'oil', 'copper', 'platinum', 'palladium', 'طلا', 'نقره', 'نفت', 'مس', 'پلاتین', 'پالادیوم'],
            'keywords': ['قیمت', 'نرخ', 'ارزش', 'هزینه', 'بهای', 'قیمت لحظه‌ای', 'قیمت زنده']
        }
        
        # الگوهای تشخیص آب و هوا
        self.weather_patterns = {
            'keywords': ['هوا', 'آب و هوا', 'باران', 'برف', 'آفتاب', 'ابری', 'گرم', 'سرد', 'مرطوب', 'خشک', 'باد', 'طوفان', 'مه', 'رطوبت', 'دما', 'فشار', 'پیش‌بینی'],
            'cities': ['تهران', 'اصفهان', 'مشهد', 'شیراز', 'تبریز', 'کرج', 'اهواز', 'قم', 'کرمانشاه', 'ارومیه', 'زاهدان', 'رشت', 'کرمان', 'همدان', 'یزد', 'اردبیل', 'بندرعباس', 'کرمانشاه', 'گرگان', 'ساری', 'بابول', 'قزوین', 'زنجان', 'سمنان', 'بیرجند', 'بوشهر', 'ایلام', 'خرم‌آباد', 'سنندج', 'یاسوج', 'زابل', 'بیرجند', 'بندرعباس', 'گرگان', 'ساری', 'بابول', 'قزوین', 'زنجان', 'سمنان', 'بیرجند', 'بوشهر', 'ایلام', 'خرم‌آباد', 'سنندج', 'یاسوج', 'زابل']
        }
        
        # الگوهای تشخیص محاسبه
        self.calculation_patterns = {
            'operators': r'[+\-*/^()]',
            'functions': r'\b(sin|cos|tan|log|ln|sqrt|abs|ceil|floor|round)\b',
            'constants': r'\b(pi|e)\b',
            'keywords': ['محاسبه', 'حساب', 'جمع', 'تفریق', 'ضرب', 'تقسیم', 'ریشه', 'توان', 'لگاریتم', 'سینوس', 'کسینوس', 'تانژانت']
        }
        
        # الگوهای تشخیص ترجمه
        self.translation_patterns = {
            'persian': r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]',
            'english': r'[a-zA-Z]',
            'keywords': ['ترجمه', 'ترجمه کن', 'معنی', 'به انگلیسی', 'به فارسی', 'translate']
        }
    
    def detect_request_type(self, text: str) -> Dict[str, Any]:
        """تشخیص نوع درخواست کاربر"""
        text_lower = text.lower().strip()
        text_upper = text.upper().strip()
        
        # تشخیص تبدیل واحد (اولویت بالاتر برای جلوگیری از تداخل با ارز)
        unit_type = self._is_unit_conversion(text, text_lower)
        if unit_type:
            return {
                'type': 'unit',
                'subtype': unit_type,
                'confidence': 0.8,
                'data': self._extract_unit_data(text, text_lower, unit_type)
            }
        
        # تشخیص تبدیل ارز
        if self._is_currency_conversion(text, text_lower, text_upper):
            return {
                'type': 'currency',
                'confidence': 0.9,
                'data': self._extract_currency_data(text, text_upper)
            }
        
        # تشخیص تبدیل تاریخ
        if self._is_date_conversion(text, text_lower):
            return {
                'type': 'date',
                'confidence': 0.8,
                'data': self._extract_date_data(text)
            }
        
        # تشخیص قیمت
        if self._is_price_request(text, text_lower, text_upper):
            return {
                'type': 'price',
                'confidence': 0.7,
                'data': self._extract_price_data(text, text_upper)
            }
        
        # تشخیص آب و هوا
        if self._is_weather_request(text, text_lower):
            return {
                'type': 'weather',
                'confidence': 0.8,
                'data': self._extract_weather_data(text, text_lower)
            }
        
        # تشخیص محاسبه
        if self._is_calculation(text, text_lower):
            return {
                'type': 'calculation',
                'confidence': 0.9,
                'data': {'expression': text}
            }
        
        # تشخیص ترجمه
        if self._is_translation_request(text, text_lower):
            return {
                'type': 'translation',
                'confidence': 0.8,
                'data': {'text': text}
            }
        
        return {
            'type': 'unknown',
            'confidence': 0.0,
            'data': {}
        }
    
    def _is_currency_conversion(self, text: str, text_lower: str, text_upper: str) -> bool:
        """تشخیص تبدیل ارز"""
        # بررسی وجود کلمات کلیدی تبدیل
        conversion_keywords = ['to', 'تبدیل', 'به', 'convert']
        has_conversion_keyword = any(keyword in text_lower for keyword in conversion_keywords)
        
        # بررسی وجود نمادهای ارز
        has_currency_symbols = bool(re.search(self.currency_patterns['symbols'], text_upper))
        has_crypto_symbols = bool(re.search(self.currency_patterns['crypto'], text_upper))
        
        # بررسی وجود کلمات کلیدی ارز
        has_currency_keywords = any(keyword in text_lower for keyword in self.currency_patterns['keywords'])
        has_crypto_keywords = any(keyword in text_lower for keyword in self.currency_patterns['crypto_keywords'])
        
        # بررسی وجود عدد
        has_number = bool(re.search(r'\d+', text))
        
        # اگر کلمه "قیمت" در متن باشد، احتمالاً درخواست قیمت است نه تبدیل ارز
        if 'قیمت' in text_lower:
            return False
        
        return (has_conversion_keyword and (has_currency_symbols or has_crypto_symbols or has_currency_keywords or has_crypto_keywords) and has_number) or \
               (has_currency_symbols and has_crypto_symbols) or \
               (has_currency_keywords and has_crypto_keywords)
    
    def _is_unit_conversion(self, text: str, text_lower: str) -> Optional[str]:
        """تشخیص تبدیل واحد"""
        conversion_keywords = ['to', 'تبدیل', 'به', 'convert']
        has_conversion_keyword = any(keyword in text_lower for keyword in conversion_keywords)
        
        if not has_conversion_keyword:
            return None
        
        # بررسی اینکه آیا متن شامل نمادهای ارز است (اگر بله، احتمالاً تبدیل ارز است)
        currency_symbols = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'CNY', 'SEK', 'NZD', 'MXN', 'SGD', 'HKD', 'NOK', 'TRY', 'RUB', 'INR', 'BRL', 'ZAR', 'KRW', 'IRR', 'AED', 'SAR', 'QAR', 'KWD', 'BHD', 'OMR', 'JOD', 'LBP', 'EGP']
        crypto_symbols = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'DOGE', 'AVAX', 'MATIC', 'LTC', 'BCH', 'UNI', 'LINK', 'ATOM', 'XLM', 'VET', 'FIL', 'TRX', 'ETC']
        
        text_upper = text.upper()
        has_currency_symbols = any(symbol in text_upper for symbol in currency_symbols)
        has_crypto_symbols = any(symbol in text_upper for symbol in crypto_symbols)
        
        # اگر نمادهای ارز دارد، احتمالاً تبدیل ارز است نه واحد
        if has_currency_symbols or has_crypto_symbols:
            return None
        
        for unit_type, patterns in self.unit_patterns.items():
            # بررسی وجود واحدها
            has_units = any(unit in text_lower for unit in patterns['units'])
            # بررسی وجود کلمات کلیدی
            has_keywords = any(keyword in text_lower for keyword in patterns['keywords'])
            
            if has_units or has_keywords:
                return unit_type
        
        # بررسی خاص برای تبدیل واحد فارسی
        if 'به' in text_lower:
            # بررسی کلمات فارسی واحدها
            persian_units = {
                'length': ['متر', 'سانتی متر', 'کیلومتر', 'اینچ', 'فوت', 'یارد', 'مایل'],
                'weight': ['گرم', 'کیلوگرم', 'تن', 'اونس', 'پوند'],
                'temperature': ['سانتی گراد', 'فارنهایت', 'کلوین'],
                'volume': ['لیتر', 'میلی لیتر', 'گالن', 'فنجان'],
                'area': ['متر مربع', 'کیلومتر مربع', 'فوت مربع', 'هکتار'],
                'time': ['ثانیه', 'دقیقه', 'ساعت', 'روز', 'هفته', 'ماه', 'سال']
            }
            
            for unit_type, units in persian_units.items():
                if any(unit in text_lower for unit in units):
                    return unit_type
        
        return None
    
    def _is_date_conversion(self, text: str, text_lower: str) -> bool:
        """تشخیص تبدیل تاریخ"""
        # بررسی الگوهای تاریخ
        for pattern_list in self.date_patterns.values():
            if isinstance(pattern_list, list):
                for pattern in pattern_list:
                    if re.search(pattern, text, re.IGNORECASE):
                        return True
        
        # بررسی کلمات کلیدی تاریخ
        has_date_keywords = any(keyword in text_lower for keyword in self.date_patterns['keywords'])
        
        # بررسی وجود عدد و جداکننده
        has_date_format = bool(re.search(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}', text))
        
        return has_date_keywords or has_date_format
    
    def _is_price_request(self, text: str, text_lower: str, text_upper: str) -> bool:
        """تشخیص درخواست قیمت"""
        # بررسی نمادهای سهام
        has_stock_symbols = bool(re.search(self.price_patterns['stocks'], text_upper))
        
        # بررسی نمادهای کریپتو
        has_crypto_symbols = bool(re.search(self.price_patterns['crypto'], text_upper))
        
        # بررسی کالاها
        has_commodities = any(commodity in text_lower for commodity in self.price_patterns['commodities'])
        
        # بررسی کلمات کلیدی قیمت
        has_price_keywords = any(keyword in text_lower for keyword in self.price_patterns['keywords'])
        
        return has_stock_symbols or has_crypto_symbols or has_commodities or has_price_keywords
    
    def _is_weather_request(self, text: str, text_lower: str) -> bool:
        """تشخیص درخواست آب و هوا"""
        # بررسی کلمات کلیدی آب و هوا
        has_weather_keywords = any(keyword in text_lower for keyword in self.weather_patterns['keywords'])
        
        # بررسی نام شهرها
        has_city_names = any(city in text_lower for city in self.weather_patterns['cities'])
        
        return has_weather_keywords or has_city_names
    
    def _is_calculation(self, text: str, text_lower: str) -> bool:
        """تشخیص محاسبه ریاضی"""
        # بررسی وجود عملگرها
        has_operators = bool(re.search(self.calculation_patterns['operators'], text))
        
        # بررسی وجود توابع ریاضی
        has_functions = bool(re.search(self.calculation_patterns['functions'], text_lower))
        
        # بررسی وجود ثابت‌ها
        has_constants = bool(re.search(self.calculation_patterns['constants'], text_lower))
        
        # بررسی کلمات کلیدی محاسبه
        has_calc_keywords = any(keyword in text_lower for keyword in self.calculation_patterns['keywords'])
        
        # بررسی وجود عدد
        has_number = bool(re.search(r'\d+', text))
        
        # بررسی اینکه آیا متن فقط شامل حروف بزرگ است (احتمالاً نماد سهام)
        is_all_uppercase = text.isupper() and len(text) <= 5 and not has_operators
        
        # اگر همه حروف بزرگ است و عملگر ندارد، احتمالاً نماد سهام است
        if is_all_uppercase:
            return False
        
        return (has_operators and has_number) or has_functions or has_constants or has_calc_keywords
    
    def _is_translation_request(self, text: str, text_lower: str) -> bool:
        """تشخیص درخواست ترجمه"""
        # بررسی کلمات کلیدی ترجمه
        has_translation_keywords = any(keyword in text_lower for keyword in self.translation_patterns['keywords'])
        
        # بررسی وجود متن فارسی و انگلیسی
        has_persian = bool(re.search(self.translation_patterns['persian'], text))
        has_english = bool(re.search(self.translation_patterns['english'], text))
        
        # اگر فقط متن فارسی است و کلمات کلیدی ترجمه ندارد، احتمالاً درخواست ترجمه نیست
        if has_persian and not has_english and not has_translation_keywords:
            return False
        
        return has_translation_keywords or (has_persian and has_english)
    
    def _extract_currency_data(self, text: str, text_upper: str) -> Dict[str, Any]:
        """استخراج داده‌های تبدیل ارز"""
        # جستجوی الگوی تبدیل ارز انگلیسی
        pattern = r'(\d+(?:\.\d+)?)\s+([A-Z]{3,4})\s+to\s+([A-Z]{3,4})'
        match = re.search(pattern, text_upper)
        
        if match:
            return {
                'amount': float(match.group(1)),
                'from_currency': match.group(2),
                'to_currency': match.group(3)
            }
        
        # جستجوی الگوی تبدیل ارز فارسی
        persian_pattern = r'(\d+(?:\.\d+)?)\s+(.+?)\s+به\s+(.+)'
        persian_match = re.search(persian_pattern, text)
        
        if persian_match:
            amount = float(persian_match.group(1))
            from_curr_text = persian_match.group(2).strip()
            to_curr_text = persian_match.group(3).strip()
            
            # تبدیل کلمات فارسی به نمادهای ارز
            from_currency = self._persian_to_currency_symbol(from_curr_text)
            to_currency = self._persian_to_currency_symbol(to_curr_text)
            
            return {
                'amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'original_text': text
            }
        
        # جستجوی نمادهای ارز در متن
        currency_symbols = re.findall(self.currency_patterns['symbols'], text_upper)
        crypto_symbols = re.findall(self.currency_patterns['crypto'], text_upper)
        
        # جستجوی عدد
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        
        return {
            'amount': float(numbers[0]) if numbers else 1.0,
            'from_currency': currency_symbols[0] if currency_symbols else None,
            'to_currency': currency_symbols[1] if len(currency_symbols) > 1 else None,
            'crypto_symbols': crypto_symbols,
            'all_symbols': currency_symbols + crypto_symbols
        }
    
    def _persian_to_currency_symbol(self, text: str) -> Optional[str]:
        """تبدیل کلمات فارسی به نمادهای ارز"""
        text_lower = text.lower().strip()
        
        # نقشه کلمات فارسی به نمادهای ارز
        persian_to_symbol = {
            'دلار': 'USD',
            'یورو': 'EUR', 
            'پوند': 'GBP',
            'ین': 'JPY',
            'فرانک': 'CHF',
            'دلار کانادا': 'CAD',
            'دلار استرالیا': 'AUD',
            'یوان': 'CNY',
            'کرون': 'SEK',
            'لیر': 'TRY',
            'روبل': 'RUB',
            'روپیه': 'INR',
            'ریال': 'IRR',
            'درهم': 'AED',
            'ریال سعودی': 'SAR',
            'ریال قطر': 'QAR',
            'دینار': 'KWD',
            'دینار بحرین': 'BHD',
            'ریال عمان': 'OMR',
            'دینار اردن': 'JOD',
            'لیر لبنان': 'LBP',
            'پوند مصر': 'EGP',
            'بیت کوین': 'BTC',
            'اتریوم': 'ETH',
            'بایننس': 'BNB',
            'ریپل': 'XRP',
            'کاردانو': 'ADA',
            'سولانا': 'SOL',
            'پولکادات': 'DOT',
            'دوج کوین': 'DOGE',
            'آوالانچ': 'AVAX',
            'پالیگان': 'MATIC',
            'لایت کوین': 'LTC',
            'بیت کوین کش': 'BCH',
            'یونی سواپ': 'UNI',
            'چین لینک': 'LINK',
            'اتم': 'ATOM',
            'استلار': 'XLM',
            'وی چین': 'VET',
            'فایل کوین': 'FIL',
            'ترون': 'TRX',
            'اتریوم کلاسیک': 'ETC'
        }
        
        return persian_to_symbol.get(text_lower)
    
    def _extract_unit_data(self, text: str, text_lower: str, unit_type: str) -> Dict[str, Any]:
        """استخراج داده‌های تبدیل واحد"""
        # جستجوی الگوی تبدیل واحد انگلیسی
        pattern = r'(\d+(?:\.\d+)?)\s+(\w+)\s+to\s+(\w+)'
        match = re.search(pattern, text_lower)
        
        if match:
            return {
                'amount': float(match.group(1)),
                'from_unit': match.group(2),
                'to_unit': match.group(3),
                'unit_type': unit_type
            }
        
        # جستجوی الگوی تبدیل واحد فارسی
        persian_pattern = r'(\d+(?:\.\d+)?)\s+(.+?)\s+به\s+(.+)'
        persian_match = re.search(persian_pattern, text)
        
        if persian_match:
            amount = float(persian_match.group(1))
            from_unit_text = persian_match.group(2).strip()
            to_unit_text = persian_match.group(3).strip()
            
            # تبدیل کلمات فارسی به نمادهای واحد
            from_unit = self._persian_to_unit_symbol(from_unit_text, unit_type)
            to_unit = self._persian_to_unit_symbol(to_unit_text, unit_type)
            
            return {
                'amount': amount,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'unit_type': unit_type,
                'original_text': text
            }
        
        # جستجوی واحدها در متن
        units = []
        for unit in self.unit_patterns[unit_type]['units']:
            if unit in text_lower:
                units.append(unit)
        
        # جستجوی عدد
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        
        return {
            'amount': float(numbers[0]) if numbers else 1.0,
            'units': units,
            'unit_type': unit_type
        }
    
    def _persian_to_unit_symbol(self, text: str, unit_type: str) -> Optional[str]:
        """تبدیل کلمات فارسی به نمادهای واحد"""
        text_lower = text.lower().strip()
        
        # نقشه کلمات فارسی به نمادهای واحد
        persian_to_symbol = {
            'length': {
                'متر': 'm',
                'سانتی متر': 'cm',
                'میلی متر': 'mm',
                'کیلومتر': 'km',
                'اینچ': 'in',
                'فوت': 'ft',
                'یارد': 'yd',
                'مایل': 'mile'
            },
            'weight': {
                'گرم': 'g',
                'میلی گرم': 'mg',
                'کیلوگرم': 'kg',
                'تن': 'ton',
                'اونس': 'oz',
                'پوند': 'lb',
                'سنگ': 'stone'
            },
            'temperature': {
                'سانتی گراد': 'celsius',
                'فارنهایت': 'fahrenheit',
                'کلوین': 'kelvin'
            },
            'volume': {
                'لیتر': 'l',
                'میلی لیتر': 'ml',
                'گالن': 'gal',
                'کوارت': 'qt',
                'پینت': 'pt',
                'فنجان': 'cup'
            },
            'area': {
                'متر مربع': 'm2',
                'کیلومتر مربع': 'km2',
                'فوت مربع': 'ft2',
                'یارد مربع': 'yd2',
                'جریب': 'acre',
                'هکتار': 'hectare'
            },
            'time': {
                'ثانیه': 's',
                'دقیقه': 'min',
                'ساعت': 'h',
                'روز': 'day',
                'هفته': 'week',
                'ماه': 'month',
                'سال': 'year'
            }
        }
        
        unit_map = persian_to_symbol.get(unit_type, {})
        return unit_map.get(text_lower)
    
    def _extract_date_data(self, text: str) -> Dict[str, Any]:
        """استخراج داده‌های تاریخ"""
        # جستجوی الگوهای مختلف تاریخ
        for pattern in self.date_patterns['gregorian']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'date_string': match.group(0),
                    'format': 'gregorian',
                    'pattern': pattern
                }
        
        for pattern in self.date_patterns['persian']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'date_string': match.group(0),
                    'format': 'persian',
                    'pattern': pattern
                }
        
        return {
            'date_string': text,
            'format': 'unknown',
            'pattern': None
        }
    
    def _extract_price_data(self, text: str, text_upper: str) -> Dict[str, Any]:
        """استخراج داده‌های قیمت"""
        # جستجوی نمادهای سهام
        stock_symbols = re.findall(self.price_patterns['stocks'], text_upper)
        
        # جستجوی نمادهای کریپتو
        crypto_symbols = re.findall(self.price_patterns['crypto'], text_upper)
        
        # جستجوی کالاها
        commodities = []
        for commodity in self.price_patterns['commodities']:
            if commodity in text.lower():
                commodities.append(commodity)
        
        return {
            'stock_symbols': stock_symbols,
            'crypto_symbols': crypto_symbols,
            'commodities': commodities,
            'all_symbols': stock_symbols + crypto_symbols + commodities
        }
    
    def _extract_weather_data(self, text: str, text_lower: str) -> Dict[str, Any]:
        """استخراج داده‌های آب و هوا"""
        # جستجوی نام شهرها
        cities = []
        for city in self.weather_patterns['cities']:
            if city in text_lower:
                cities.append(city)
        
        return {
            'cities': cities,
            'location': cities[0] if cities else text.strip()
        }
    
    def format_response(self, request_type: str, data: Dict[str, Any]) -> str:
        """فرمت کردن پاسخ بر اساس نوع درخواست"""
        if request_type == 'currency':
            if data.get('amount') and data.get('from_currency') and data.get('to_currency'):
                return f"💱 تبدیل ارز: {data['amount']} {data['from_currency']} به {data['to_currency']}"
            else:
                return f"💱 درخواست تبدیل ارز: {data.get('all_symbols', [])}"
        
        elif request_type == 'unit':
            if data.get('amount') and data.get('from_unit') and data.get('to_unit'):
                return f"📏 تبدیل {data['unit_type']}: {data['amount']} {data['from_unit']} به {data['to_unit']}"
            else:
                return f"📏 درخواست تبدیل {data['unit_type']}: {data.get('units', [])}"
        
        elif request_type == 'date':
            return f"📅 تبدیل تاریخ: {data.get('date_string', '')}"
        
        elif request_type == 'price':
            return f"💰 درخواست قیمت: {data.get('all_symbols', [])}"
        
        elif request_type == 'weather':
            return f"🌤️ آب و هوای: {data.get('location', '')}"
        
        elif request_type == 'calculation':
            return f"🧮 محاسبه: {data.get('expression', '')}"
        
        elif request_type == 'translation':
            return f"🌐 ترجمه: {data.get('text', '')}"
        
        else:
            return "❓ نوع درخواست تشخیص داده نشد"
