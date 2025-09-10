"""
RAG query processing with multilingual support
"""
from typing import Dict, Any, List
from langchain.vectorstores import Chroma
from ..translation.language_detector import language_detector
from ..translation.translator import translation_service
from ..utils.constants import LANGUAGE_MAPPINGS
from config import RAG_CONFIG

class RAGQueryProcessor:
    """Processes queries through the complete RAG pipeline."""
    
    def __init__(self, vectordb: Chroma, llm):
        self.vectordb = vectordb
        self.llm = llm
        self.retriever = vectordb.as_retriever(
            search_kwargs={"k": RAG_CONFIG['search_k']}
        )
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline.
        
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
            
            # Step 3: Document retrieval
            relevant_docs = self._retrieve_documents(english_query)
            
            # Step 4: Generate response
            english_answer = self._generate_response(english_query, relevant_docs)
            
            # Step 5: Translate back to original language
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
                'retrieved_docs': [doc.page_content for doc in relevant_docs]
            }
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return self._create_error_response(str(e))
    
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
    
    def _generate_response(self, query: str, docs: List) -> str:
        """Generate response using retrieved documents."""
        if not docs:
            return "I couldn't find specific information about your question in the available course data. Please try rephrasing your question or contact support for more details."
        
        context = "\n\n".join([doc.page_content for doc in docs])
        print(f"📄 Context length: {len(context)} characters")
        
        prompt = self._create_rag_prompt(query, context)
        
        try:
            print("🤖 Generating response...")
            response = self.llm.invoke(prompt)
            answer = response.content.strip()
            
            if not answer:
                return "I encountered an issue while generating a response. Please try again."
            
            print(f"✅ Generated answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
            return answer
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "I encountered an error while processing your question. Please try again."
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create the RAG prompt for the LLM."""
        return f"""You are a helpful assistant for Boswallah courses. Based on the provided course information, answer the user's question completely and accurately.

Course Information Available:
{context}

User Question: {query}

Instructions:
- Provide a complete, detailed answer based on the course information
- If the exact information isn't available, explain what related information is available
- When course data doesn't fully address a query, supplement with relevant general knowledge in the web
- Be specific about course names, details, and requirements
- Write a comprehensive response (at least 2-3 sentences)
- Focus on being helpful and informative
- If multiple courses are relevant, mention them all

Complete Answer:"""
    
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
            'retrieved_docs_count': 0
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