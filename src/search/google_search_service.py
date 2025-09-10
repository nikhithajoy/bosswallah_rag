"""
Google Search API integration for web search functionality
"""
import os
import json
import time
import requests
from typing import List, Dict, Optional, Any
from urllib.parse import quote_plus
from config import GOOGLE_SEARCH_CONFIG, WEB_SEARCH_CONFIG

class GoogleSearchService:
    """Service for performing web searches using Google Custom Search API."""
    
    def __init__(self):
        self.api_key = os.getenv(GOOGLE_SEARCH_CONFIG['api_key_env'])
        self.search_engine_id = os.getenv(GOOGLE_SEARCH_CONFIG['search_engine_id_env'])
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        # Validate credentials
        if not self.api_key or not self.search_engine_id:
            print("⚠️ Google Search API credentials not found. Web search will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            print("✅ Google Search API initialized successfully")
    
    def is_enabled(self) -> bool:
        """Check if the search service is enabled."""
        return self.enabled
    
    def search(self, query: str, num_results: int = 2) -> List[Dict[str, Any]]:
        """
        Perform a web search using Google Custom Search API.
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return (default from config)
            
        Returns:
            List[Dict]: List of search results with title, snippet, and link
        """
        if not self.enabled:
            print("❌ Google Search is not enabled")
            return []
        
        if not query or not query.strip():
            print("❌ Empty search query")
            return []
        
        num_results = num_results or GOOGLE_SEARCH_CONFIG['max_results']
        
        try:
            print(f"🔍 Searching web for: {query}")
            
            # Prepare search parameters
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10),  # Google API limit is 10 per request
                'safe': GOOGLE_SEARCH_CONFIG['safe_search'],
                'searchType': GOOGLE_SEARCH_CONFIG['search_type']
            }
            
            # Make API request
            response = requests.get(
                self.base_url,
                params=params,
                timeout=GOOGLE_SEARCH_CONFIG['timeout']
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse results
            results = []
            if 'items' in data:
                for item in data['items']:
                    result = {
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'link': item.get('link', ''),
                        'displayLink': item.get('displayLink', ''),
                        'formattedUrl': item.get('formattedUrl', '')
                    }
                    results.append(result)
                
                print(f"✅ Found {len(results)} web search results")
            else:
                print("⚠️ No search results found")
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Google Search API request failed: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Google Search API response: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error during web search: {e}")
            return []
    
    def search_educational_content(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for educational content with optimized query.
        
        Args:
            query (str): Original search query
            
        Returns:
            List[Dict]: Search results focused on educational content
        """
        # Enhance query for educational content
        educational_query = f"{query} education learning course training"
        return self.search(educational_query)
    
    def search_with_template(self, query: str, template_type: str = "general") -> List[Dict[str, Any]]:
        """
        Search using predefined query templates.
        
        Args:
            query (str): Base query
            template_type (str): Template type from WEB_SEARCH_CONFIG
            
        Returns:
            List[Dict]: Search results
        """
        templates = WEB_SEARCH_CONFIG.get('search_query_templates', {})
        template = templates.get(template_type, "{query}")
        
        formatted_query = template.format(query=query)
        return self.search(formatted_query)
    
    def format_search_results_for_llm(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results for inclusion in LLM prompt.
        
        Args:
            results (List[Dict]): Search results from Google API
            
        Returns:
            str: Formatted search results text
        """
        if not results:
            return "No relevant web search results found."
        
        formatted = "Web Search Results:\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('snippet', 'No description available')
            source = result.get('displayLink', result.get('link', 'Unknown source'))
            
            formatted += f"{i}. **{title}**\n"
            formatted += f"   Source: {source}\n"
            formatted += f"   {snippet}\n\n"
        
        return formatted
    
    def get_search_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary information about search results.
        
        Args:
            results (List[Dict]): Search results
            
        Returns:
            Dict: Summary information
        """
        if not results:
            return {
                'total_results': 0,
                'sources': [],
                'has_results': False
            }
        
        sources = list(set([r.get('displayLink', 'Unknown') for r in results]))
        
        return {
            'total_results': len(results),
            'sources': sources,
            'has_results': True,
            'top_source': sources[0] if sources else 'Unknown'
        }

# Global service instance
google_search_service = GoogleSearchService()