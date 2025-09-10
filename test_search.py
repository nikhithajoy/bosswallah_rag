from dotenv import load_dotenv
load_dotenv()

from src.search.google_search_service import google_search_service

import os
api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
cse_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

# Test the service
print("Testing Google Search Service:")
print(f"Enabled: {google_search_service.is_enabled()}")
if google_search_service.is_enabled():
    results = google_search_service.search("papaya seeds suppliers bangalore")
    print(f"Test results: {len(results)} found")