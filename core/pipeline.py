"""
Main multilingual RAG pipeline orchestrator
"""
from typing import Dict, Any, Optional, List
from src.data_processing.data_loader import CourseDataLoader
from src.data_processing.vectordb_creator import VectorDBCreator
from src.rag.llm_setup import llm_manager
from src.rag.query_processor import RAGQueryProcessor
from config import COURSES_CSV_PATH, CHROMA_DB_PATH

class MultilingualRAGPipeline:
    """Complete multilingual RAG pipeline for Boswallah courses."""
    
    def __init__(self, csv_path: str = None, persist_dir: str = None):
        self.csv_path = csv_path or str(COURSES_CSV_PATH)
        self.persist_dir = persist_dir or str(CHROMA_DB_PATH)
        
        # Components
        self.data_loader = None
        self.vectordb_creator = None
        self.query_processor = None
        self.llm = None
        self.vectordb = None
        
        # State
        self.is_initialized = False
        self.initialization_error = None
    
    def initialize(self, force_rebuild: bool = False) -> bool:
        """
        Initialize the complete pipeline.
        
        Args:
            force_rebuild (bool): Force rebuild of vector database
            
        Returns:
            bool: True if initialization successful
        """
        try:
            print("🚀 Initializing Multilingual RAG Pipeline...")
            
            # Step 1: Initialize LLM
            print("🔧 Setting up Gemini LLM...")
            self.llm = llm_manager.initialize_gemini()
            
            # Test LLM connection
            if not llm_manager.test_connection():
                raise Exception("LLM connection test failed")
            
            print("✅ LLM initialized and tested successfully!")
            
            # Step 2: Load and process data
            print("📁 Loading course data...")
            self.data_loader = CourseDataLoader(self.csv_path)
            df = self.data_loader.load_data()
            df = self.data_loader.preprocess_data()
            print(f"✅ Loaded {len(df)} courses")
            
            # Step 3: Create or load vector database
            print("🔍 Setting up vector database...")
            self.vectordb_creator = VectorDBCreator(self.persist_dir)
            
            if force_rebuild:
                self.vectordb = self.vectordb_creator.rebuild_vectordb(df)
            else:
                self.vectordb = self.vectordb_creator.create_or_load_vectordb(df)
            
            print("✅ Vector database ready!")
            
            # Step 4: Initialize query processor
            print("🤖 Setting up query processor...")
            self.query_processor = RAGQueryProcessor(self.vectordb, self.llm)
            print("✅ Query processor initialized!")
            
            self.is_initialized = True
            self.initialization_error = None
            
            print("🎉 Pipeline initialization complete!")
            return True
            
        except Exception as e:
            error_msg = f"Pipeline initialization failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.initialization_error = error_msg
            self.is_initialized = False
            return False
    
    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query through the pipeline.
        
        Args:
            user_query (str): User's input query
            
        Returns:
            Dict[str, Any]: Query result with metadata
        """
        if not self.is_initialized:
            return {
                'success': False,
                'error': 'Pipeline not initialized',
                'answer': '❌ System not ready. Please wait for initialization to complete.',
                'detected_language': 'Unknown',
                'retrieved_docs_count': 0
            }
        
        if not self.query_processor:
            return {
                'success': False,
                'error': 'Query processor not available',
                'answer': '❌ Query processor not available.',
                'detected_language': 'Unknown',
                'retrieved_docs_count': 0
            }
        
        return self.query_processor.process_query(user_query)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            Dict[str, Any]: System status information
        """
        status = {
            'pipeline_initialized': self.is_initialized,
            'initialization_error': self.initialization_error,
            'components': {
                'llm': llm_manager.is_initialized(),
                'data_loader': self.data_loader is not None,
                'vectordb': self.vectordb is not None,
                'query_processor': self.query_processor is not None
            }
        }
        
        # Add data statistics if available
        if self.data_loader:
            try:
                status['data_stats'] = self.data_loader.get_stats()
            except Exception:
                status['data_stats'] = {'error': 'Failed to get data stats'}
        
        # Add vector database statistics if available
        if self.vectordb_creator:
            try:
                status['vectordb_stats'] = self.vectordb_creator.get_vectordb_stats()
            except Exception:
                status['vectordb_stats'] = {'error': 'Failed to get vectordb stats'}
        
        # Add LLM information
        status['llm_info'] = llm_manager.get_model_info()
        
        return status
    
    def get_course_suggestions(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Get course suggestions based on similarity search.
        
        Args:
            query (str): Search query
            k (int): Number of suggestions to return
            
        Returns:
            List[Dict[str, Any]]: Course suggestions
        """
        if not self.is_initialized or not self.query_processor:
            return []
        
        return self.query_processor.get_similar_courses(query, k)
    
    def search_courses_by_language(self, language: str) -> List[Dict[str, Any]]:
        """
        Search courses by language.
        
        Args:
            language (str): Language name
            
        Returns:
            List[Dict[str, Any]]: Courses in the specified language
        """
        if not self.data_loader:
            return []
        
        return self.data_loader.get_courses_by_language(language)
    
    def rebuild_database(self) -> bool:
        """
        Rebuild the vector database.
        
        Returns:
            bool: True if rebuild successful
        """
        return self.initialize(force_rebuild=True)

# Global pipeline instance
pipeline = MultilingualRAGPipeline()