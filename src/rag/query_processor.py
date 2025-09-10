"""
RAG query processing with multilingual support and web search integration - FIXED VERSION
"""
from typing import Dict, Any, List
from langchain.vectorstores import Chroma
from ..translation.language_detector import language_detector
from ..translation.translator import translation_service
from ..utils.constants import LANGUAGE_MAPPINGS
from ..search.google_search_service import google_search_service
from config import RAG_CONFIG, WEB_SEARCH_CONFIG

class RAGQueryProcessor:
    """Processes queries through the complete RAG pipeline with web search fallback."""
    
    def __init__(self, vectordb: Chroma, llm):
        self.vectordb = vectordb
        self.llm = llm
        self.retriever = vectordb.as_retriever(
            search_kwargs={"k": RAG_CONFIG['search_k']}
        )
        self.web_search_enabled = WEB_SEARCH_CONFIG['enable_web_search'] and google_search_service.is_enabled()
        
        # Debug logging
        print(f"🔧 DEBUG: WEB_SEARCH_CONFIG['enable_web_search'] = {WEB_SEARCH_CONFIG['enable_web_search']}")
        print(f"🔧 DEBUG: google_search_service.is_enabled() = {google_search_service.is_enabled()}")
        print(f"🔧 DEBUG: self.web_search_enabled = {self.web_search_enabled}")
        
        if self.web_search_enabled:
            print("✅ Web search integration enabled")
        else:
            print("⚠️ Web search integration disabled")
            if not WEB_SEARCH_CONFIG['enable_web_search']:
                print("   Reason: Web search disabled in config")
            if not google_search_service.is_enabled():
                print("   Reason: Google Search Service not enabled")
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline with web search fallback.
        
        Args:
            user_query (str): User's input query
            
        Returns:
            Dict[str, Any]: Complete query result with metadata
        """
        if not user_query or not user_query.strip():
            return self._create_error_response("Empty query provided")
        
        try:
            # Step 1: Language detection
            query_lang = language_detector.detect_language(user_query)
            lang_name = LANGUAGE_MAPPINGS.get(query_lang, 'Unknown')
            confidence = language_detector.get_confidence_score(user_query, query_lang)
            
            print(f"🌐 Detected language: {lang_name} ({query_lang}) - Confidence: {confidence:.2f}")
            
            # Step 2: Translation to English for retrieval
            english_query = self._translate_to_english(user_query, query_lang)
            
            # Step 3: Document retrieval from RAG
            relevant_docs = self._retrieve_documents(english_query)
            
            # Step 4: Generate initial RAG response
            print("🔧 DEBUG: Generating initial RAG response...")
            initial_rag_answer = self._generate_rag_only_response(english_query, relevant_docs)
            print(f"🔧 DEBUG: Initial RAG answer: {initial_rag_answer[:200]}...")
            
            # Step 5: Determine if web search is needed based on query and initial response
            print("🔧 DEBUG: Checking if web search should be triggered...")
            web_search_results = []
            web_search_triggered = False
            
            should_trigger = self._should_trigger_web_search(english_query, relevant_docs, initial_rag_answer)
            print(f"🔧 DEBUG: Should trigger web search: {should_trigger}")
            
            if should_trigger:
                print("🌐 DEBUG: Performing web search...")
                web_search_results = self._perform_web_search(english_query)
                web_search_triggered = True
                print(f"🔧 DEBUG: Web search results count: {len(web_search_results)}")
                
                # Step 6: Generate enhanced response with both RAG and web search context
                english_answer = self._generate_enhanced_response(english_query, relevant_docs, web_search_results)
            else:
                english_answer = initial_rag_answer
                print("🔧 DEBUG: Using initial RAG answer (no web search)")
            
            # Step 7: Translate back to original language
            final_answer = self._translate_response(english_answer, query_lang)
            
            return {
                'success': True,
                'query': user_query,
                'detected_language': lang_name,
                'language_code': query_lang,
                'confidence': confidence,
                'english_query': english_query,
                'english_answer': english_answer,
                'answer': final_answer,
                'retrieved_docs_count': len(relevant_docs),
                'retrieved_docs': [doc.page_content for doc in relevant_docs],
                'web_search_triggered': web_search_triggered,
                'web_search_results_count': len(web_search_results),
                'web_search_sources': [r.get('displayLink', 'Unknown') for r in web_search_results] if web_search_results else []
            }
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_response(str(e))
    
    def _should_trigger_web_search(self, query: str, docs: List, rag_response: str = None) -> bool:
        """
        Determine if web search should be triggered based on RAG results, query type, and response content.
        """
        print(f"🔧 DEBUG: _should_trigger_web_search called")
        print(f"🔧 DEBUG: web_search_enabled = {self.web_search_enabled}")
        
        if not self.web_search_enabled:
            print("🔧 DEBUG: Web search not enabled, returning False")
            return False
        
        conditions = WEB_SEARCH_CONFIG['auto_trigger_conditions']
        print(f"🔧 DEBUG: Auto trigger conditions: {conditions}")
        
        query_lower = query.lower()
        print(f"🔧 DEBUG: Query (lowercase): {query_lower}")
        
        # Check for insufficient documents
        if conditions.get('insufficient_docs', False):
            doc_threshold = RAG_CONFIG.get('insufficient_docs_threshold', 1)
            print(f"🔧 DEBUG: Checking insufficient docs: {len(docs)} vs threshold {doc_threshold}")
            if len(docs) < doc_threshold:
                print(f"🌐 DEBUG: Triggering web search: insufficient RAG results ({len(docs)} < {doc_threshold})")
                return True
        
        # Check for general queries (not course-specific)
        if conditions.get('general_queries', False):
            general_keywords = ['what is', 'how to', 'why', 'explain', 'definition', 'meaning', 'where can i', 'where to', 'suppliers', 'buy', 'purchase', 'stores', 'shops']
            course_keywords = ['course', 'training', 'certification', 'boswallah', 'bosswallah']
            
            is_general = any(keyword in query_lower for keyword in general_keywords)
            is_course_specific = any(keyword in query_lower for keyword in course_keywords)
            
            print(f"🔧 DEBUG: General keywords found: {[kw for kw in general_keywords if kw in query_lower]}")
            print(f"🔧 DEBUG: Course keywords found: {[kw for kw in course_keywords if kw in query_lower]}")
            print(f"🔧 DEBUG: is_general: {is_general}, is_course_specific: {is_course_specific}")
            
            if is_general and not is_course_specific:
                print("🌐 DEBUG: Triggering web search: general knowledge query detected")
                return True
        
        # Advanced: Check if RAG response indicates insufficient information
        if rag_response:
            print(f"🔧 DEBUG: Checking response insufficiency...")
            is_insufficient = self._is_response_insufficient(query, rag_response)
            print(f"🔧 DEBUG: Response insufficient: {is_insufficient}")
            if is_insufficient:
                print("🌐 DEBUG: Triggering web search: RAG response indicates insufficient information")
                return True
        
        # Check for location-specific queries
        location_keywords = ['near', 'in ', 'at ', 'bangalore', 'mumbai', 'delhi', 'chennai', 'kolkata', 'hyderabad', 'pune', 'location', 'address']
        location_matches = [kw for kw in location_keywords if kw in query_lower]
        print(f"🔧 DEBUG: Location keywords found: {location_matches}")
        if location_matches:
            print("🌐 DEBUG: Triggering web search: location-specific query detected")
            return True
        
        # Check for supplier/vendor queries
        vendor_keywords = ['supplier', 'vendor', 'dealer', 'distributor', 'retailer', 'store', 'shop', 'market', 'buy', 'purchase', 'where to get']
        vendor_matches = [kw for kw in vendor_keywords if kw in query_lower]
        print(f"🔧 DEBUG: Vendor keywords found: {vendor_matches}")
        if vendor_matches:
            print("🌐 DEBUG: Triggering web search: vendor/supplier query detected")
            return True
        
        print("🔧 DEBUG: No web search triggers matched")
        return False
    
    def _is_response_insufficient(self, query: str, response: str) -> bool:
        """
        Check if the RAG response indicates insufficient information.
        """
        response_lower = response.lower()
        query_lower = query.lower()
        
        print(f"🔧 DEBUG: Checking response insufficiency...")
        print(f"🔧 DEBUG: Response snippet: {response_lower[:100]}...")
        
        # Phrases that indicate insufficient information
        insufficient_phrases = [
            'no details available',
            'no information available',
            'not explicitly mentioned',
            'doesn\'t provide information',
            'no specific information',
            'not covered in the course',
            'beyond the scope',
            'not included in',
            'course doesn\'t mention',
            'information is not available',
            'no data about',
            'doesn\'t specify',
            'not detailed in',
            'lacks information about',
            'doesn\'t address',
            'we do not have details',
            'does not include'
        ]
        
        # Check if response contains insufficient information indicators
        found_phrases = [phrase for phrase in insufficient_phrases if phrase in response_lower]
        has_insufficient_indicators = len(found_phrases) > 0
        
        print(f"🔧 DEBUG: Insufficient phrases found: {found_phrases}")
        print(f"🔧 DEBUG: Has insufficient indicators: {has_insufficient_indicators}")
        
        # Check for specific query elements not addressed
        query_keywords = query_lower.split()
        important_keywords = [word for word in query_keywords if len(word) > 3 and word not in ['what', 'where', 'when', 'who', 'how', 'can', 'the', 'and', 'for']]
        
        # Count how many important query keywords are not mentioned in response
        missing_keywords = [keyword for keyword in important_keywords if keyword not in response_lower]
        keyword_coverage = len(missing_keywords) / len(important_keywords) if important_keywords else 0
        
        print(f"🔧 DEBUG: Important keywords: {important_keywords}")
        print(f"🔧 DEBUG: Missing keywords: {missing_keywords}")
        print(f"🔧 DEBUG: Keyword coverage ratio: {keyword_coverage}")
        
        # Trigger web search if response has insufficient indicators or poor keyword coverage
        result = has_insufficient_indicators or keyword_coverage > 0.5
        print(f"🔧 DEBUG: Response insufficient result: {result}")
        return result
    
    def _perform_web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search for additional context.
        """
        try:
            print(f"🔧 DEBUG: Starting web search for: {query}")
            print(f"🔧 DEBUG: Google search service enabled: {google_search_service.is_enabled()}")
            
            # Use educational content search for better results
            results = google_search_service.search_educational_content(query)
            
            print(f"🔧 DEBUG: Raw search results: {len(results)} items")
            
            if results:
                print(f"🌐 Web search found {len(results)} results")
                summary = google_search_service.get_search_summary(results)
                print(f"🌐 Top sources: {', '.join(summary['sources'][:3])}")
                
                # Debug: Print first result
                if len(results) > 0:
                    print(f"🔧 DEBUG: First result: {results[0].get('title', 'No title')[:100]}")
            else:
                print("🌐 No web search results found")
            
            return results
            
        except Exception as e:
            print(f"❌ Web search failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _translate_to_english(self, query: str, source_lang: str) -> str:
        """Translate query to English for retrieval."""
        if source_lang == 'en':
            return query
        
        english_query = translation_service.robust_translate(
            query, 'en', source_lang, self.llm
        )
        
        if not english_query or english_query.strip() == "":
            print("⚠️ Translation to English failed, using original query")
            return query
        
        print(f"📝 English query: {english_query}")
        return english_query
    
    def _retrieve_documents(self, query: str) -> List:
        """Retrieve relevant documents from vector database."""
        print("🔍 Searching for relevant courses...")
        
        try:
            docs = self.retriever.get_relevant_documents(query)
            print(f"📄 Retrieved {len(docs)} relevant documents")
            return docs
        except Exception as e:
            print(f"⚠️ Document retrieval error: {e}")
            return []
    
    def _generate_rag_only_response(self, query: str, docs: List) -> str:
        """Generate response using only retrieved documents (for initial assessment)."""
        if not docs:
            return "I couldn't find specific information about your question in the available course data."
        
        context = "\n\n".join([doc.page_content for doc in docs])
        print(f"📄 RAG context length: {len(context)} characters")
        
        # Simple prompt for initial RAG assessment
        prompt = f"""Based on the provided course information, answer the user's question.

Course Information:
{context}

User Question: {query}

Answer:"""
        
        try:
            response = self.llm.invoke(prompt)
            answer = response.content.strip()
            print(f"📝 Initial RAG response: {answer[:100]}{'...' if len(answer) > 100 else ''}")
            return answer or "Unable to generate response from course data."
        except Exception as e:
            print(f"❌ Error generating RAG response: {e}")
            return "Unable to generate response from course data."
    
    def _generate_enhanced_response(self, query: str, docs: List, web_results: List[Dict]) -> str:
        print("🔧 DEBUG: Starting _generate_enhanced_response")
        initial_rag_answer = self._generate_rag_only_response(query, docs)

        # Define course_context and web_context before using them
        course_context = "\n\n".join([doc.page_content for doc in docs[:2]]) if docs else ""
        web_context = google_search_service.format_search_results_for_llm(web_results)[:200] if web_results else ""

        try:
            simple_prompt = f"""Answer this question: {query}

    Course information: {course_context[:500]}

    Web information: {web_context[:500]}

    Answer:"""
            simple_response = self.llm.invoke(simple_prompt)
            answer = ""
            if hasattr(simple_response, 'content') and isinstance(simple_response.content, str):
                answer = simple_response.content.strip()
            elif hasattr(simple_response, 'text') and isinstance(simple_response.text, str):
                answer = simple_response.text.strip()
            elif isinstance(simple_response, str):
                answer = simple_response.strip()
            else:
                print(f"❌ ERROR: Response is not a string or does not have .content/.text")
                answer = ""

            # Check for MAX_TOKENS issue or empty response
            finish_reason = getattr(simple_response, "response_metadata", {}).get("finish_reason", "")
            if not answer or finish_reason == "MAX_TOKENS":
                print("❌ Gemini returned empty response due to MAX_TOKENS.")
                custom_msg = (
                    "\n\n⚠️ Unable to provide a web search answer due to token limitations in the free Gemini API. "
                    "Please try with the paid version for longer queries, or visit [Google.com](https://www.google.com) directly for more information."
                )
                return initial_rag_answer + custom_msg

            print(f"✅ Generated enhanced answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
            # Always append Google search suggestion if web search was used
            answer += "\n\nFor more information, you can also search on [Google.com](https://www.google.com)."
            return answer

        except Exception as e:
            print(f"❌ Error in _generate_enhanced_response: {e}")
            import traceback
            traceback.print_exc()
            custom_msg = (
                "\n\n⚠️ Unable to provide a web search answer due to token limitations in the free Gemini API. "
                "Please try with the paid version for longer queries, or visit [Google.com](https://www.google.com) directly for more information."
            )
            return initial_rag_answer + custom_msg
    
    def _generate_fallback_response(self, query: str, docs: List, web_results: List[Dict]) -> str:
        """Generate a simple fallback response when the main LLM call fails."""
        try:
            print("🔧 DEBUG: Generating fallback response...")
            
            # Create a simple response combining available information
            response_parts = []
            
            if docs:
                response_parts.append("Based on the available course information:")
                for i, doc in enumerate(docs[:2]):  # Limit to 2 docs
                    content_preview = doc.page_content[:200].strip()
                    response_parts.append(f"{i+1}. {content_preview}...")
            
            if web_results:
                response_parts.append("\nAdditional information from web search:")
                for i, result in enumerate(web_results[:2]):  # Limit to 2 results
                    title = result.get('title', 'No title')
                    snippet = result.get('snippet', 'No snippet')[:150]
                    response_parts.append(f"{i+1}. {title}: {snippet}...")
            
            if not response_parts:
                return "I couldn't find specific information to answer your question. Please try rephrasing or contact support."
            
            # Add a helpful conclusion
            response_parts.append(f"\nFor your question about '{query}', I recommend reviewing the information above or contacting our support team for more detailed assistance.")
            
            fallback_response = "\n\n".join(response_parts)
            print(f"🔧 DEBUG: Fallback response generated: {len(fallback_response)} chars")
            return fallback_response
            
        except Exception as fallback_error:
            print(f"❌ Even fallback failed: {fallback_error}")
            return "I encountered a technical issue while processing your request. Please try again later or contact support."
    
    def _create_enhanced_rag_prompt(self, query: str, course_context: str, web_context: str = "") -> str:
        """Create an enhanced RAG prompt that combines course data and web search results."""
        
        base_prompt = """You are the Bosswallah Course Assistant, an expert educational advisor specializing in helping users find and understand available courses.

Your primary responsibilities:
1. Answer user queries based on the provided course data with accuracy and completeness
2. Provide comprehensive, helpful responses that guide users toward the most suitable learning paths
3. Maintain a friendly, professional, specific and supportive tone

Guidelines for responses:
- Always prioritize information from Bosswallah course data when available
- Use web search information to provide additional context and general knowledge
- Write comprehensive responses (minimum 2-3 sentences)
- Clearly distinguish between Bosswallah course information and general web information
- Format information clearly and logically"""
        
        # Add course information section
        if course_context:
            base_prompt += f"\n\nBosswallah Course Information Available:\n{course_context}"
        else:
            base_prompt += "\n\nNo specific Bosswallah course information found for this query."
        
        # Add web search information section
        if web_context:
            base_prompt += f"\n\nAdditional Information from Web Search:\n{web_context}"
        
        # Add query and instructions
        base_prompt += f"""

User Query: {query}

Instructions:
- Provide a complete, helpful response combining both course information and web knowledge
- If Bosswallah courses are relevant, highlight them prominently
- Use web information to provide broader context and educational guidance
- Be clear about which information comes from Bosswallah vs. general sources
- Focus on being helpful and informative for the user's learning goals

Complete Answer:"""
        
        return base_prompt
    
    def _translate_response(self, response: str, target_lang: str) -> str:
        """Translate response back to user's language."""
        if target_lang == 'en':
            return response
        
        print(f"🔄 Translating response to {LANGUAGE_MAPPINGS.get(target_lang, 'Unknown')}...")
        
        final_answer = translation_service.robust_translate(
            response, target_lang, 'en', self.llm
        )
        
        if not final_answer or final_answer.strip() == "":
            print("⚠️ Response translation failed, providing English with note")
            return f"[English response - translation unavailable]: {response}"
        
        return final_answer
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            'success': False,
            'error': error_msg,
            'answer': f"❌ Error: {error_msg}",
            'detected_language': 'Unknown',
            'retrieved_docs_count': 0,
            'web_search_triggered': False,
            'web_search_results_count': 0
        }
    
    def get_similar_courses(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Get similar courses based on query."""
        try:
            docs = self.vectordb.similarity_search(query, k=k)
            return [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata
                }
                for doc in docs
            ]
        except Exception as e:
            print(f"⚠️ Error getting similar courses: {e}")
            return []
    
    def manual_web_search(self, query: str) -> Dict[str, Any]:
        """
        Perform manual web search (for testing or explicit user requests).
        """
        if not self.web_search_enabled:
            return {
                'success': False,
                'message': 'Web search is not enabled',
                'results': []
            }
        
        try:
            results = google_search_service.search_educational_content(query)
            summary = google_search_service.get_search_summary(results)
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'summary': summary,
                'formatted_results': google_search_service.format_search_results_for_llm(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Web search failed: {e}',
                'results': []
            }