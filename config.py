"""
Configuration settings for the Multilingual RAG Pipeline
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_PATH = DATA_DIR / "chroma_db"
COURSES_CSV_PATH = DATA_DIR / "bw_courses - Sheet1.csv"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DB_PATH.mkdir(exist_ok=True)

# Model configurations
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# LLM parameters
LLM_CONFIG = {
    "temperature": 0.0,
    "max_tokens": 512,
    "timeout": 30,
    "max_retries": 3
}

# RAG parameters
RAG_CONFIG = {
    "chunk_size": 200,
    "search_k": 3,
    "similarity_threshold": 0.7,
    "insufficient_docs_threshold": 1,  # Trigger web search if less than this many docs
    "low_confidence_threshold": 0.6    # Trigger web search if confidence below this
}

# Google Search API Configuration
GOOGLE_SEARCH_CONFIG = {
    "api_key_env": "GOOGLE_SEARCH_API_KEY",
    "search_engine_id_env": "GOOGLE_SEARCH_ENGINE_ID", 
    "max_results": 5,
    "timeout": 10,
    "safe_search": "active",
    "search_type": "searchTypeUndefined"  # Can be "image" for image search
}

# Web search integration settings
WEB_SEARCH_CONFIG = {
    "enable_web_search": True,
    "auto_trigger_conditions": {
        "insufficient_docs": True,      # Auto-trigger when few RAG results
        "general_queries": True,        # Auto-trigger for non-course specific queries
        "low_confidence": False         # Don't auto-trigger on low confidence (can be noisy)
    },
    "search_query_templates": {
        "course_related": "online courses {query} education training",
        "general": "{query} education learning",
        "specific_skill": "{query} course certification training"
    }
}

# Streamlit page configuration
PAGE_CONFIG = {
    "page_title": "Boswallah Course Assistant",
    "page_icon": "🎓",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Chat configuration
CHAT_CONFIG = {
    "max_messages": 50,
    "typing_delay": 0.02,
    "show_timestamps": True,
    "show_language_detection": True,
    "show_web_search_indicator": True
}

# Translation rate limiting
TRANSLATION_CONFIG = {
    "delay_between_requests": 0.1,
    "max_retries": 3,
    "timeout": 10
}