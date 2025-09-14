import requests
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    """Multi-language translation service"""
    
    def __init__(self, database):
        self.db = database
        self.api_keys = {
            "google": "",  # Add your Google Translate API key
            "microsoft": "",  # Add your Microsoft Translator API key
            "libre": ""  # LibreTranslate API endpoint
        }
        
        self.endpoints = {
            "google": "https://translation.googleapis.com/language/translate/v2",
            "microsoft": "https://api.cognitive.microsofttranslator.com/translate",
            "libre": "https://libretranslate.com/translate"
        }
        
        # Supported languages
        self.languages = {
            "fa": "فارسی", "en": "English", "ar": "العربية", "zh": "中文",
            "es": "Español", "fr": "Français", "de": "Deutsch", "ru": "Русский",
            "ja": "日本語", "ko": "한국어", "it": "Italiano", "pt": "Português",
            "hi": "हिन्दी", "tr": "Türkçe", "ur": "اردو", "bn": "বাংলা",
            "th": "ไทย", "vi": "Tiếng Việt", "id": "Bahasa Indonesia",
            "ms": "Bahasa Melayu", "tl": "Filipino", "sw": "Kiswahili"
        }
        
        # Language detection patterns
        self.language_patterns = {
            "fa": r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]",
            "ar": r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]",
            "zh": r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]",
            "ja": r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]",
            "ko": r"[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]",
            "hi": r"[\u0900-\u097f\u1cd0-\u1cff]",
            "th": r"[\u0e00-\u0e7f]",
            "ru": r"[\u0400-\u04ff]",
            "he": r"[\u0590-\u05ff]",
            "bn": r"[\u0980-\u09ff]",
            "ur": r"[\u0600-\u06ff\u0750-\u077f]"
        }
    
    async def translate_text(self, text: str, target_lang: str, source_lang: str = "auto") -> Dict[str, Any]:
        """Translate text to target language"""
        if not text.strip():
            return {
                "success": False,
                "error": "No text provided"
            }
        
        # Check cache
        cache_key = f"translate_{hash(text)}_{source_lang}_{target_lang}"
        cached_translation = self.db.get_cached_response(cache_key)
        
        if cached_translation:
            try:
                return json.loads(cached_translation)
            except json.JSONDecodeError:
                pass
        
        # Try multiple translation services
        services = [
            self._translate_google,
            self._translate_microsoft,
            self._translate_libre
        ]
        
        for service_func in services:
            try:
                result = await service_func(text, target_lang, source_lang)
                if result["success"]:
                    # Cache for 24 hours
                    self.db.cache_api_response(cache_key, json.dumps(result), 1440)
                    return result
            except Exception as e:
                logger.warning(f"Translation service failed: {e}")
                continue
        
        return {
            "success": False,
            "error": "All translation services failed",
            "text": text,
            "target_lang": target_lang
        }
    
    async def _translate_google(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        """Translate using Google Translate API"""
        if not self.api_keys["google"]:
            return {"success": False, "error": "Google Translate API key not configured"}
        
        url = self.endpoints["google"]
        params = {
            "key": self.api_keys["google"],
            "q": text,
            "target": target_lang,
            "format": "text"
        }
        
        if source_lang != "auto":
            params["source"] = source_lang
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "data" in data and "translations" in data["data"]:
                        translation = data["data"]["translations"][0]
                        
                        return {
                            "success": True,
                            "original_text": text,
                            "translated_text": translation["translatedText"],
                            "source_lang": translation.get("detectedSourceLanguage", source_lang),
                            "target_lang": target_lang,
                            "source": "google"
                        }
        
        return {"success": False, "error": "Google Translate API failed"}
    
    async def _translate_microsoft(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        """Translate using Microsoft Translator API"""
        if not self.api_keys["microsoft"]:
            return {"success": False, "error": "Microsoft Translator API key not configured"}
        
        url = f"{self.endpoints['microsoft']}?api-version=3.0&to={target_lang}"
        if source_lang != "auto":
            url += f"&from={source_lang}"
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_keys["microsoft"],
            "Content-Type": "application/json"
        }
        
        body = [{"text": text}]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        result = data[0]
                        
                        return {
                            "success": True,
                            "original_text": text,
                            "translated_text": result["translations"][0]["text"],
                            "source_lang": result["detectedLanguage"].get("language", source_lang),
                            "target_lang": target_lang,
                            "source": "microsoft"
                        }
        
        return {"success": False, "error": "Microsoft Translator API failed"}
    
    async def _translate_libre(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        """Translate using LibreTranslate (free service)"""
        url = self.endpoints["libre"]
        data = {
            "q": text,
            "source": source_lang if source_lang != "auto" else "auto",
            "target": target_lang,
            "format": "text"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    return {
                        "success": True,
                        "original_text": text,
                        "translated_text": result["translatedText"],
                        "source_lang": result.get("detectedLanguage", source_lang),
                        "target_lang": target_lang,
                        "source": "libre"
                    }
        
        return {"success": False, "error": "LibreTranslate API failed"}
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text"""
        if not text.strip():
            return {
                "success": False,
                "error": "No text provided"
            }
        
        # Simple pattern-based detection
        detected_langs = []
        
        for lang_code, pattern in self.language_patterns.items():
            if re.search(pattern, text):
                detected_langs.append(lang_code)
        
        # If no patterns match, assume English
        if not detected_langs:
            detected_langs = ["en"]
        
        # Return the most likely language
        primary_lang = detected_langs[0] if detected_langs else "en"
        
        return {
            "success": True,
            "text": text,
            "detected_language": primary_lang,
            "language_name": self.languages.get(primary_lang, "Unknown"),
            "confidence": "medium",  # Simple detection, not very accurate
            "all_detected": detected_langs
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.languages
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language name from code"""
        return self.languages.get(lang_code, "Unknown")
    
    async def translate_multiple(self, texts: List[str], target_lang: str, source_lang: str = "auto") -> Dict[str, Any]:
        """Translate multiple texts"""
        results = []
        
        for text in texts:
            result = await self.translate_text(text, target_lang, source_lang)
            results.append(result)
        
        return {
            "success": True,
            "results": results,
            "total_texts": len(texts),
            "successful_translations": sum(1 for r in results if r["success"])
        }
    
    def format_translation_result(self, result: Dict[str, Any]) -> str:
        """Format translation result for display"""
        if not result["success"]:
            return f"❌ {result['error']}"
        
        source_lang_name = self.get_language_name(result["source_lang"])
        target_lang_name = self.get_language_name(result["target_lang"])
        
        output = f"🌐 **ترجمه**\n\n"
        output += f"📝 **متن اصلی ({source_lang_name}):**\n{result['original_text']}\n\n"
        output += f"🔄 **ترجمه ({target_lang_name}):**\n{result['translated_text']}\n\n"
        output += f"🔗 **منبع:** {result['source']}"
        
        return output
    
    async def get_translation_suggestions(self, text: str, target_lang: str) -> Dict[str, Any]:
        """Get translation suggestions for common phrases"""
        # Common phrases database
        common_phrases = {
            "fa": {
                "سلام": "Hello",
                "خداحافظ": "Goodbye",
                "متشکرم": "Thank you",
                "لطفاً": "Please",
                "ببخشید": "Excuse me",
                "آیا می‌توانید کمکم کنید؟": "Can you help me?",
                "کجا هستم؟": "Where am I?",
                "چقدر قیمت دارد؟": "How much does it cost?",
                "من گم شده‌ام": "I'm lost",
                "آیا انگلیسی صحبت می‌کنید؟": "Do you speak English?"
            },
            "en": {
                "Hello": "سلام",
                "Goodbye": "خداحافظ",
                "Thank you": "متشکرم",
                "Please": "لطفاً",
                "Excuse me": "ببخشید",
                "Can you help me?": "آیا می‌توانید کمکم کنید؟",
                "Where am I?": "کجا هستم؟",
                "How much does it cost?": "چقدر قیمت دارد؟",
                "I'm lost": "من گم شده‌ام",
                "Do you speak English?": "آیا انگلیسی صحبت می‌کنید؟"
            }
        }
        
        # Detect source language
        lang_detection = self.detect_language(text)
        source_lang = lang_detection["detected_language"]
        
        suggestions = []
        
        # Look for exact matches
        if source_lang in common_phrases:
            for phrase, translation in common_phrases[source_lang].items():
                if phrase.lower() in text.lower():
                    suggestions.append({
                        "phrase": phrase,
                        "translation": translation,
                        "match_type": "exact"
                    })
        
        # Look for partial matches
        if source_lang in common_phrases:
            for phrase, translation in common_phrases[source_lang].items():
                if any(word in text.lower() for word in phrase.lower().split()):
                    suggestions.append({
                        "phrase": phrase,
                        "translation": translation,
                        "match_type": "partial"
                    })
        
        return {
            "success": True,
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "suggestions": suggestions[:5]  # Limit to 5 suggestions
        }

