"""
Vector database creation and management
"""
import os
from typing import List, Dict, Any, Tuple
from textwrap import wrap
import pandas as pd
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from config import RAG_CONFIG, EMBEDDING_MODEL_NAME

class VectorDBCreator:
    """Creates and manages the vector database for course data."""
    
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self.embedding_model = None
        self.vectordb = None
        
        # Ensure persist directory exists
        os.makedirs(persist_dir, exist_ok=True)
    
    def initialize_embeddings(self):
        """Initialize the embedding model."""
        if self.embedding_model is None:
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_NAME
            )
        return self.embedding_model
    
    def create_documents(self, df: pd.DataFrame) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Create document chunks from course data.
        
        Args:
            df (pd.DataFrame): Course data
            
        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: Documents and metadata
        """
        documents = []
        metadata_list = []
        
        chunk_size = RAG_CONFIG['chunk_size']
        
        for _, row in df.iterrows():
            # Create description chunks to handle long descriptions
            description = str(row.get('Course Description', ''))
            description_chunks = wrap(description, chunk_size) if description else [""]
            
            for desc_chunk in description_chunks:
                # Create comprehensive document text
                text = self._create_document_text(row, desc_chunk)
                documents.append(text)
                
                # Create metadata
                metadata = self._create_metadata(row)
                metadata_list.append(metadata)
        
        return documents, metadata_list
    
    def _create_document_text(self, row: pd.Series, description_chunk: str) -> str:
        """
        Create formatted document text from course data.
        
        Args:
            row (pd.Series): Course row data
            description_chunk (str): Description chunk
            
        Returns:
            str: Formatted document text
        """
        # Handle missing or NaN values
        title = str(row.get('Course Title', 'Untitled'))
        who_for = str(row.get('Who This Course is For', 'Not specified'))
        languages = row.get('Released Languages', ['English'])
        
        if isinstance(languages, list):
            languages_str = ', '.join(languages)
        else:
            languages_str = str(languages)
        
        text = f"""Course Title: {title}
Description: {description_chunk}
Who This Course is For: {who_for}
Languages: {languages_str}"""
        
        return text
    
    def _create_metadata(self, row: pd.Series) -> Dict[str, Any]:
        """
        Create metadata dictionary from course data.
        
        Args:
            row (pd.Series): Course row data
            
        Returns:
            Dict[str, Any]: Metadata dictionary
        """
        languages = row.get('Released Languages', ['English'])
        if isinstance(languages, list):
            languages_str = ', '.join(languages)
        else:
            languages_str = str(languages)
        
        return {
            "course_no": int(row.get('Course No', 0)),
            "course_title": str(row.get('Course Title', 'Untitled')),
            "released_languages": languages_str,
            "who_for": str(row.get('Who This Course is For', 'Not specified'))
        }
    
    def create_vectordb(self, documents: List[str], metadata_list: List[Dict[str, Any]]) -> Chroma:
        """
        Create vector database from documents and metadata.
        
        Args:
            documents (List[str]): List of document texts
            metadata_list (List[Dict[str, Any]]): List of metadata dictionaries
            
        Returns:
            Chroma: Created vector database
        """
        # Initialize embeddings
        embeddings = self.initialize_embeddings()
        
        # Create vector database
        self.vectordb = Chroma.from_texts(
            texts=documents,
            embedding=embeddings,
            metadatas=metadata_list,
            persist_directory=self.persist_dir
        )
        
        # Persist the database
        self.vectordb.persist()
        
        return self.vectordb
    
    def load_existing_vectordb(self) -> Chroma:
        """
        Load existing vector database from disk.
        
        Returns:
            Chroma: Loaded vector database
        """
        embeddings = self.initialize_embeddings()
        
        self.vectordb = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=embeddings
        )
        
        return self.vectordb
    
    def vectordb_exists(self) -> bool:
        """
        Check if vector database exists on disk.
        
        Returns:
            bool: True if database exists
        """
        return os.path.exists(self.persist_dir) and len(os.listdir(self.persist_dir)) > 0
    
    def get_vectordb_stats(self) -> Dict[str, Any]:
        """
        Get vector database statistics.
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        if self.vectordb is None:
            return {"status": "not_initialized"}
        
        try:
            # Try to get collection info
            collection = self.vectordb._collection
            count = collection.count()
            
            return {
                "status": "ready",
                "document_count": count,
                "persist_directory": self.persist_dir,
                "embedding_model": EMBEDDING_MODEL_NAME
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_or_load_vectordb(self, df: pd.DataFrame) -> Chroma:
        """
        Create new vector database or load existing one.
        
        Args:
            df (pd.DataFrame): Course data (only used if creating new)
            
        Returns:
            Chroma: Vector database instance
        """
        if self.vectordb_exists():
            print("📂 Loading existing vector database...")
            return self.load_existing_vectordb()
        else:
            print("🔨 Creating new vector database...")
            documents, metadata_list = self.create_documents(df)
            return self.create_vectordb(documents, metadata_list)
    
    def rebuild_vectordb(self, df: pd.DataFrame) -> Chroma:
        """
        Force rebuild of vector database.
        
        Args:
            df (pd.DataFrame): Course data
            
        Returns:
            Chroma: Rebuilt vector database
        """
        print("🔄 Rebuilding vector database...")
        
        # Remove existing database
        if os.path.exists(self.persist_dir):
            import shutil
            shutil.rmtree(self.persist_dir)
        
        # Create new database
        documents, metadata_list = self.create_documents(df)
        return self.create_vectordb(documents, metadata_list)