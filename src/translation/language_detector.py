"""
Language detection utilities for multilingual support
"""
import re
from typing import Optional
from langdetect import detect, DetectorFactory
from ..utils.constants import SUPPORTED_LANGUAGES, UNICODE_RANGES

# Set seed for consistent language detection
DetectorFactory.seed = 0

class LanguageDetector:
    """Enhanced language detection with fallbacks for Indian languages."""
    
    def __init__(self):
        self.unicode_patterns = {
            lang: re.compile(pattern) 
            for lang, pattern in UNICODE_RANGES.items()
        }
    
    def detect_by_script(self, text: str) -> Optional[str]:
        """Detect language based on Unicode script ranges."""
        for lang_code, pattern in self.unicode_patterns.items():
            if pattern.search(text):
                return lang_code
        return None
    
    def detect_by_langdetect(self, text: str) -> Optional[str]:
        """Detect language using langdetect library."""
        try:
            detected = detect(text)
            return detected if detected in SUPPORTED_LANGUAGES else None
        except Exception:
            return None
    
    def detect_language(self, text: str) -> str:
        """
        Enhanced language detection with multiple fallback strategies.
        
        Args:
            text (str): Text to detect language for
            
        Returns:
            str: Detected language code (defaults to 'en')
        """
        if not text or not text.strip():
            return 'en'
        
        # Strategy 1: Script-based detection (most reliable for Indian languages)
        script_lang = self.detect_by_script(text)
        if script_lang:
            return script_lang
        
        # Strategy 2: Statistical detection using langdetect
        statistical_lang = self.detect_by_langdetect(text)
        if statistical_lang:
            return statistical_lang
        
        # Strategy 3: Check for common English patterns
        if self._is_likely_english(text):
            return 'en'
        
        # Default fallback
        return 'en'
    
    def _is_likely_english(self, text: str) -> bool:
        """Check if text is likely English based on character patterns."""
        # Count ASCII characters
        ascii_chars = sum(1 for char in text if ord(char) < 128)
        total_chars = len(text.replace(' ', ''))  # Ignore spaces
        
        if total_chars == 0:
            return True
        
        # If more than 70% ASCII characters, likely English
        ascii_ratio = ascii_chars / total_chars
        return ascii_ratio > 0.7
    
    def get_confidence_score(self, text: str, detected_lang: str) -> float:
        """
        Get confidence score for language detection.
        
        Args:
            text (str): Input text
            detected_lang (str): Detected language code
            
        Returns:
            float: Confidence score between 0 and 1
        """
        if not text.strip():
            return 0.0
        
        # For script-based detection, high confidence
        if self.detect_by_script(text) == detected_lang:
            return 0.95
        
        # For statistical detection, medium confidence
        if self.detect_by_langdetect(text) == detected_lang:
            return 0.8
        
        # For English fallback, lower confidence
        if detected_lang == 'en' and self._is_likely_english(text):
            return 0.6
        
        return 0.3

# Global instance
language_detector = LanguageDetector()