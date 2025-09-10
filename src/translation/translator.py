"""
Translation services with Google Translate and Gemini fallback
"""
import time
from typing import Optional
from googletrans import Translator
from ..utils.constants import GOOGLE_LANG_CODES, LANGUAGE_MAPPINGS
from config import TRANSLATION_CONFIG

class TranslationService:
    """Translation service with multiple backends and fallback support."""
    
    def __init__(self):
        self.google_translator = Translator()
        self.config = TRANSLATION_CONFIG
    
    def translate_with_google(
        self, 
        text: str, 
        target_lang: str, 
        source_lang: str = 'en'
    ) -> Optional[str]:
        """
        Translate text using Google Translate.
        
        Args:
            text (str): Text to translate
            target_lang (str): Target language code
            source_lang (str): Source language code
            
        Returns:
            Optional[str]: Translated text or None if failed
        """
        if source_lang == target_lang or not text.strip():
            return text
        
        source_code = GOOGLE_LANG_CODES.get(source_lang, 'en')
        target_code = GOOGLE_LANG_CODES.get(target_lang, 'en')
        
        try:
            # Add delay to avoid rate limiting
            time.sleep(self.config['delay_between_requests'])
            
            result = self.google_translator.translate(
                text, 
                src=source_code, 
                dest=target_code
            )
            
            translated = result.text
            
            if not translated or not translated.strip():
                return None
                
            return translated
            
        except Exception as e:
            print(f"⚠️ Google Translate error: {e}")
            return None
    
    def translate_with_gemini(
        self, 
        text: str, 
        target_lang: str, 
        source_lang: str = 'en',
        llm=None
    ) -> Optional[str]:
        """
        Translate text using Gemini LLM as fallback.
        
        Args:
            text (str): Text to translate
            target_lang (str): Target language code
            source_lang (str): Source language code
            llm: Gemini LLM instance
            
        Returns:
            Optional[str]: Translated text or None if failed
        """
        if source_lang == target_lang or not text.strip():
            return text
        
        if not llm:
            return None
        
        source_name = LANGUAGE_MAPPINGS.get(source_lang, 'English')
        target_name = LANGUAGE_MAPPINGS.get(target_lang, 'English')
        
        translation_prompt = f"""You are a professional translator. Translate the following text accurately from {source_name} to {target_name}.

Rules:
1. Provide ONLY the translation, no explanations
2. Maintain the original meaning and context
3. Use natural, fluent {target_name}
4. Do not add any prefixes, suffixes, or explanations

Text to translate: {text}

Translation:"""
        
        try:
            response = llm.invoke(translation_prompt)
            translated = response.content.strip()
            
            if not translated or not translated.strip():
                return None
                
            return translated
            
        except Exception as e:
            print(f"⚠️ Gemini translation error: {e}")
            return None
    
    def robust_translate(
        self, 
        text: str, 
        target_lang: str, 
        source_lang: str = 'en',
        llm=None
    ) -> str:
        """
        Robust translation with fallback strategies.
        
        Args:
            text (str): Text to translate
            target_lang (str): Target language code
            source_lang (str): Source language code
            llm: Optional Gemini LLM for fallback
            
        Returns:
            str: Translated text (original text if all methods fail)
        """
        if source_lang == target_lang or not text.strip():
            return text
        
        # Try Google Translate first
        google_result = self.translate_with_google(text, target_lang, source_lang)
        if google_result and google_result.strip() and google_result != text:
            return google_result
        
        # Try Gemini as fallback
        if llm:
            gemini_result = self.translate_with_gemini(text, target_lang, source_lang, llm)
            if gemini_result and gemini_result.strip():
                return gemini_result
        
        # Return original text if all methods fail
        return text
    
    def get_language_name(self, lang_code: str) -> str:
        """Get human-readable language name from code."""
        return LANGUAGE_MAPPINGS.get(lang_code, f"Unknown ({lang_code})")
    
    def is_translation_needed(self, source_lang: str, target_lang: str) -> bool:
        """Check if translation is needed between two languages."""
        return (
            source_lang != target_lang and
            source_lang in GOOGLE_LANG_CODES and
            target_lang in GOOGLE_LANG_CODES
        )

# Global instance
translation_service = TranslationService()