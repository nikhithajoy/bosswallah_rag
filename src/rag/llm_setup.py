"""
LLM initialization and configuration
"""
import os
from typing import Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_MODEL_NAME, LLM_CONFIG

class LLMManager:
    """Manages LLM initialization and configuration."""
    
    def __init__(self):
        self.llm = None
        self._load_environment()
    
    def _load_environment(self):
        """Load environment variables."""
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
    
    def initialize_gemini(self) -> ChatGoogleGenerativeAI:
        """
        Initialize Gemini LLM.
        
        Returns:
            ChatGoogleGenerativeAI: Initialized Gemini LLM
            
        Raises:
            ValueError: If API key is not found
        """
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please check your .env file."
            )
        
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL_NAME,
            google_api_key=self.api_key,
            **LLM_CONFIG
        )
        
        return self.llm
    
    def get_llm(self) -> Optional[ChatGoogleGenerativeAI]:
        """
        Get initialized LLM instance.
        
        Returns:
            Optional[ChatGoogleGenerativeAI]: LLM instance or None
        """
        return self.llm
    
    def is_initialized(self) -> bool:
        """
        Check if LLM is initialized.
        
        Returns:
            bool: True if LLM is initialized
        """
        return self.llm is not None
    
    def test_connection(self) -> bool:
        """
        Test LLM connection with a simple query.
        
        Returns:
            bool: True if connection successful
        """
        if not self.is_initialized():
            return False
        
        try:
            response = self.llm.invoke("Hello, please respond with 'OK' if you can hear me.")
            return bool(response and response.content)
        except Exception as e:
            print(f"❌ LLM connection test failed: {e}")
            return False
    
    def get_model_info(self) -> dict:
        """
        Get model configuration information.
        
        Returns:
            dict: Model configuration details
        """
        return {
            "model_name": GEMINI_MODEL_NAME,
            "is_initialized": self.is_initialized(),
            "has_api_key": bool(self.api_key),
            "config": LLM_CONFIG
        }

# Global instance
llm_manager = LLMManager()