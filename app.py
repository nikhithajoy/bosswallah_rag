"""
Main Streamlit application for Multilingual RAG Chatbot
"""
import streamlit as st
from datetime import datetime
import asyncio
from pathlib import Path

# Configure page settings
from config import PAGE_CONFIG
st.set_page_config(**PAGE_CONFIG)

# Import components
from ui.components.chat_interface import ChatInterface
from ui.components.sidebar import Sidebar
from core.pipeline import pipeline
from src.utils.constants import CUSTOM_CSS, ERROR_MESSAGES, SUCCESS_MESSAGES

class ChatbotApp:
    """Main chatbot application class."""
    
    def __init__(self):
        self.chat_interface = ChatInterface()
        self.sidebar = Sidebar()
        self.initialize_app_state()
    
    def initialize_app_state(self):
        """Initialize application state."""
        if 'app_initialized' not in st.session_state:
            st.session_state.app_initialized = False
            st.session_state.initialization_in_progress = False
            st.session_state.current_time = datetime.now()
        
        if 'rebuild_requested' not in st.session_state:
            st.session_state.rebuild_requested = False
    
    def run(self):
        """Main application entry point."""
        # Apply custom CSS
        st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
        
        # Initialize pipeline if not already done
        if not st.session_state.app_initialized and not st.session_state.initialization_in_progress:
            self.initialize_pipeline()
        
        # Handle rebuild request
        if st.session_state.rebuild_requested:
            self.handle_rebuild_request()
        
        # Get pipeline status
        pipeline_status = pipeline.get_system_status()
        
        # Render sidebar
        self.sidebar.render_sidebar(pipeline_status)
        
        # Main chat interface
        self.render_main_interface(pipeline_status)
    
    def initialize_pipeline(self):
        """Initialize the RAG pipeline."""
        st.session_state.initialization_in_progress = True
        
        # Show initialization progress
        with st.container():
            st.markdown("## 🚀 Initializing Boswallah Course Assistant...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Initialize LLM
            status_text.text("🔧 Setting up Gemini LLM...")
            progress_bar.progress(25)
            
            # Step 2: Load data
            status_text.text("📁 Loading course data...")
            progress_bar.progress(50)
            
            # Step 3: Setup vector database
            status_text.text("🔍 Setting up vector database...")
            progress_bar.progress(75)
            
            # Step 4: Initialize query processor
            status_text.text("🤖 Initializing query processor...")
            progress_bar.progress(90)
            
            # Actual initialization
            try:
                success = pipeline.initialize()
                
                if success:
                    progress_bar.progress(100)
                    status_text.text("✅ Initialization complete!")
                    st.session_state.app_initialized = True
                    st.success(SUCCESS_MESSAGES['initialization_complete'])
                    
                    # Small delay to show completion
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(ERROR_MESSAGES['initialization_error'])
                    st.error(f"Details: {pipeline.initialization_error}")
            
            except Exception as e:
                st.error(f"❌ Initialization failed: {str(e)}")
            
            finally:
                st.session_state.initialization_in_progress = False
    
    def handle_rebuild_request(self):
        """Handle database rebuild request."""
        st.session_state.rebuild_requested = False
        
        with st.container():
            st.warning("🔄 Rebuilding database... This may take a moment.")
            
            try:
                success = pipeline.rebuild_database()
                if success:
                    st.success("✅ Database rebuilt successfully!")
                else:
                    st.error("❌ Database rebuild failed.")
            except Exception as e:
                st.error(f"❌ Rebuild error: {str(e)}")
            
            # Refresh after rebuild
            import time
            time.sleep(2)
            st.rerun()
    
    def render_main_interface(self, pipeline_status):
        """
        Render the main chat interface.
        
        Args:
            pipeline_status: Current pipeline status
        """
        # Show header
        st.markdown("# 🎓 Boswallah Course Assistant")
        
        # Show system status if not ready
        if not pipeline_status.get('pipeline_initialized', False):
            st.warning("⚠️ System is not ready yet. Please wait for initialization to complete.")
            return
        
        # Display chat history
        self.chat_interface.display_chat_history()
        
        # Handle user input
        user_input = self.chat_interface.get_user_input()
        
        if user_input:
            self.handle_user_query(user_input)
    
    def handle_user_query(self, user_query: str):
        """
        Handle user query and generate response.
        
        Args:
            user_query (str): User's input query
        """
        if not user_query.strip():
            st.warning(ERROR_MESSAGES['empty_query'])
            return
        
        # Add user message to chat
        with st.chat_message("user", avatar="👤"):
            st.write(user_query)
        
        # Add to session state
        self.chat_interface.add_user_message(user_query)
        
        # Show typing indicator
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("🤔 Processing your question..."):
                # Process query through pipeline
                result = pipeline.query(user_query)
        
        # Handle the response
        self.display_response(result, user_query)
    
    def display_response(self, result, original_query):
        """
        Display the assistant's response.
        
        Args:
            result: Query processing result
            original_query: Original user query
        """
        if not result.get('success', False):
            # Handle error
            error_msg = result.get('error', 'Unknown error occurred')
            response_text = result.get('answer', ERROR_MESSAGES['query_processing_error'])
            
            with st.chat_message("assistant", avatar="🎓"):
                st.error(response_text)
            
            self.chat_interface.add_assistant_message(
                response_text,
                language="English",
                metadata={'error': error_msg}
            )
            return
        
        # Display successful response
        response_text = result.get('answer', '')
        detected_language = result.get('detected_language', 'Unknown')
        
        with st.chat_message("assistant", avatar="🎓"):
            st.write(response_text)
            
            # Show language detection if enabled
            if st.session_state.get('show_metadata', False):
                confidence = result.get('confidence', 0)
                if confidence:
                    st.info(f"🌐 **Response Language:** {detected_language} (Confidence: {confidence:.1%})")
                else:
                    st.info(f"🌐 **Response Language:** {detected_language}")
            
            # Show debug information if enabled
            if st.session_state.get('show_debug_info', False):
                self.chat_interface.display_query_metadata(result)
        
        # Add to session state
        self.chat_interface.add_assistant_message(
            response_text,
            language=detected_language,
            metadata=result
        )
        
        # Update query count
        st.session_state.query_count = st.session_state.get('query_count', 0) + 1
    
    def show_error_page(self, error_message: str):
        """
        Show error page when critical error occurs.
        
        Args:
            error_message (str): Error message to display
        """
        st.error("## ❌ Application Error")
        st.error(error_message)
        
        st.markdown("### 🛠️ Troubleshooting Steps:")
        st.markdown("""
        1. **Check your .env file** - Make sure GEMINI_API_KEY is set correctly
        2. **Verify data files** - Ensure the course CSV file exists in the data folder
        3. **Check internet connection** - Translation services require internet access
        4. **Restart the application** - Sometimes a fresh start helps
        """)
        
        if st.button("🔄 Retry Initialization"):
            st.session_state.app_initialized = False
            st.session_state.initialization_in_progress = False
            st.rerun()

def main():
    """Main function to run the Streamlit app."""
    try:
        app = ChatbotApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Critical application error: {str(e)}")
        st.markdown("Please check the logs and restart the application.")

if __name__ == "__main__":
    main()