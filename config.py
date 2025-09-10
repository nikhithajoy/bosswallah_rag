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
    "similarity_threshold": 0.7
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
    "show_language_detection": True
}

# Translation rate limiting
TRANSLATION_CONFIG = {
    "delay_between_requests": 0.1,
    "max_retries": 3,
    "timeout": 10
}