"""
Constants and mappings for the multilingual RAG pipeline
"""

# Language mappings for Indian languages
LANGUAGE_MAPPINGS = {
    'ml': 'Malayalam',
    'hi': 'Hindi', 
    'ta': 'Tamil',
    'te': 'Telugu',
    'kn': 'Kannada',
    'en': 'English'
}

SUPPORTED_LANGUAGES = {'ml', 'hi', 'ta', 'te', 'kn', 'en'}

# Google Translate language codes
GOOGLE_LANG_CODES = {
    'ml': 'ml',  # Malayalam
    'hi': 'hi',  # Hindi
    'ta': 'ta',  # Tamil
    'te': 'te',  # Telugu
    'kn': 'kn',  # Kannada
    'en': 'en'   # English
}

# Language code mappings for course data
COURSE_LANGUAGE_MAPPING = {
    6: "Hindi",
    7: "Kannada", 
    11: "Malayalam",
    20: "Tamil",
    21: "Telugu",
    24: "English"
}

# Unicode ranges for script-based language detection
UNICODE_RANGES = {
    'ml': r'[\u0D00-\u0D7F]',  # Malayalam
    'hi': r'[\u0900-\u097F]',  # Hindi/Devanagari
    'ta': r'[\u0B80-\u0BFF]',  # Tamil
    'te': r'[\u0C00-\u0C7F]',  # Telugu
    'kn': r'[\u0C80-\u0CFF]',  # Kannada
}

# UI Constants
WELCOME_MESSAGE = """
🎓 Welcome to Boswallah Course Assistant!

I can help you find information about courses in multiple languages including:
- English, हिंदी (Hindi), मराठी (Marathi)
- മലയാളം (Malayalam), தமிழ் (Tamil), తెలుగు (Telugu), ಕನ್ನಡ (Kannada)

Ask me anything about courses, requirements, languages, or specific topics!
"""

CHAT_PLACEHOLDER = "Ask about courses in any language... (उदाहरण: 'डेयरी फार्मिंग के बारे में बताएं' या 'ഡയറി ഫാമിങ്ങിനെ കുറിച്ച് പറയൂ')"

ERROR_MESSAGES = {
    'initialization_error': "❌ Failed to initialize the system. Please check your configuration.",
    'query_processing_error': "❌ Error processing your query. Please try again.",
    'translation_error': "⚠️ Translation service temporarily unavailable. Response provided in English.",
    'empty_query': "Please enter a question to get started!",
    'api_key_missing': "❌ API key not configured. Please check your .env file."
}

SUCCESS_MESSAGES = {
    'initialization_complete': "✅ System initialized successfully!",
    'query_processed': "✅ Query processed successfully!",
    'translation_complete': "🌐 Translation completed!"
}

# Streamlit styling
CUSTOM_CSS = """
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    
    .language-indicator {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.25rem 0;
        display: inline-block;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
    }
    
    .timestamp {
        color: #666;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    
    .sidebar-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
"""