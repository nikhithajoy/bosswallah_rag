"""
ChatGPT-like chat interface components for Streamlit
"""
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
import time

from src.utils.constants import CHAT_PLACEHOLDER, WELCOME_MESSAGE

class ChatInterface:
    """Manages the chat interface and conversation flow."""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables for chat."""
        if 'messages' not in st.session_state:
            st.session_state.messages = [
                {
                    'role': 'assistant',
                    'content': WELCOME_MESSAGE,
                    'timestamp': datetime.now(),
                    'language': 'English'
                }
            ]
        
        if 'query_count' not in st.session_state:
            st.session_state.query_count = 0
    
    def display_chat_history(self):
        """Display the complete chat history."""
        for message in st.session_state.messages:
            self.display_message(message)
    
    def display_message(self, message: Dict[str, Any]):
        """
        Display a single chat message.
        
        Args:
            message (Dict[str, Any]): Message dictionary
        """
        role = message['role']
        content = message['content']
        timestamp = message.get('timestamp', datetime.now())
        language = message.get('language', 'Unknown')
        
        # Choose appropriate avatar and styling
        if role == 'user':
            with st.chat_message("user", avatar="👤"):
                st.write(content)
                if st.session_state.get('show_metadata', False):
                    self._display_message_metadata(language, timestamp)
        else:
            with st.chat_message("assistant", avatar="🎓"):
                st.write(content)
                if st.session_state.get('show_metadata', False):
                    self._display_message_metadata(language, timestamp)
                
                # Add copy button for assistant messages
                if st.button("📋 Copy", key=f"copy_{timestamp.timestamp()}", help="Copy response"):
                    st.toast("Response copied to clipboard!", icon="✅")
    
    def _display_message_metadata(self, language: str, timestamp: datetime):
        """Display message metadata (language and timestamp)."""
        col1, col2 = st.columns([1, 1])
        with col1:
            st.caption(f"🌐 **Language:** {language}")
        with col2:
            st.caption(f"🕐 **Time:** {timestamp.strftime('%H:%M:%S')}")
    
    def get_user_input(self) -> str:
        """
        Get user input from chat input widget.
        
        Returns:
            str: User's input query
        """
        return st.chat_input(
            placeholder=CHAT_PLACEHOLDER,
            key="user_input"
        )
    
    def add_user_message(self, content: str, detected_language: str = "Unknown"):
        """
        Add user message to chat history.
        
        Args:
            content (str): User's message content
            detected_language (str): Detected language of the message
        """
        message = {
            'role': 'user',
            'content': content,
            'timestamp': datetime.now(),
            'language': detected_language
        }
        st.session_state.messages.append(message)
    
    def add_assistant_message(self, content: str, language: str = "English", metadata: Dict = None):
        """
        Add assistant message to chat history.
        
        Args:
            content (str): Assistant's response content
            language (str): Language of the response
            metadata (Dict): Additional metadata about the response
        """
        message = {
            'role': 'assistant',
            'content': content,
            'timestamp': datetime.now(),
            'language': language,
            'metadata': metadata or {}
        }
        st.session_state.messages.append(message)
    
    def display_typing_indicator(self):
        """Display typing indicator while processing."""
        with st.chat_message("assistant", avatar="🎓"):
            typing_placeholder = st.empty()
            
            # Simulate typing with dots
            for i in range(3):
                dots = "." * (i + 1)
                typing_placeholder.markdown(f"*Thinking{dots}*")
                time.sleep(0.5)
            
            typing_placeholder.empty()
    
    def display_language_detection(self, detected_lang: str, confidence: float = None):
        """
        Display language detection information.
        
        Args:
            detected_lang (str): Detected language
            confidence (float): Detection confidence score
        """
        if confidence:
            st.info(f"🌐 **Detected Language:** {detected_lang} (Confidence: {confidence:.1%})")
        else:
            st.info(f"🌐 **Detected Language:** {detected_lang}")
    
    def display_query_metadata(self, result: Dict[str, Any]):
        """
        Display detailed query processing metadata.
        
        Args:
            result (Dict[str, Any]): Query processing result
        """
        if not st.session_state.get('show_debug_info', False):
            return
        
        with st.expander("🔍 Query Processing Details"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Language Detection:**")
                st.write(f"- Detected: {result.get('detected_language', 'Unknown')}")
                if 'confidence' in result:
                    st.write(f"- Confidence: {result['confidence']:.1%}")
                
                st.write("**Translation:**")
                english_query = result.get('english_query', '')
                if english_query != result.get('query', ''):
                    st.write(f"- English: {english_query}")
                else:
                    st.write("- No translation needed")
            
            with col2:
                st.write("**Document Retrieval:**")
                st.write(f"- Documents found: {result.get('retrieved_docs_count', 0)}")
                
                if result.get('retrieved_docs'):
                    with st.expander("View Retrieved Documents"):
                        for i, doc in enumerate(result['retrieved_docs'][:3], 1):
                            st.write(f"**Document {i}:**")
                            st.write(doc[:200] + "..." if len(doc) > 200 else doc)
                            st.write("---")
    
    def clear_chat_history(self):
        """Clear the chat history."""
        st.session_state.messages = [
            {
                'role': 'assistant',
                'content': WELCOME_MESSAGE,
                'timestamp': datetime.now(),
                'language': 'English'
            }
        ]
        st.session_state.query_count = 0
        st.rerun()
    
    def export_chat_history(self) -> str:
        """
        Export chat history as formatted text.
        
        Returns:
            str: Formatted chat history
        """
        export_text = "# Boswallah Course Assistant - Chat History\n\n"
        
        for message in st.session_state.messages:
            role = "You" if message['role'] == 'user' else "Assistant"
            timestamp = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            language = message.get('language', 'Unknown')
            
            export_text += f"## {role} ({language}) - {timestamp}\n"
            export_text += f"{message['content']}\n\n"
        
        return export_text
    
    def get_message_count(self) -> int:
        """Get total number of messages in chat."""
        return len(st.session_state.messages)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the conversation."""
        messages = st.session_state.messages
        
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        assistant_messages = [msg for msg in messages if msg['role'] == 'assistant']
        
        # Count languages used
        languages_used = set()
        for msg in messages:
            if 'language' in msg:
                languages_used.add(msg['language'])
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'languages_used': list(languages_used),
            'conversation_duration': self._get_conversation_duration()
        }
    
    def _get_conversation_duration(self) -> str:
        """Calculate conversation duration."""
        if len(st.session_state.messages) < 2:
            return "0 minutes"
        
        start_time = st.session_state.messages[0]['timestamp']
        end_time = st.session_state.messages[-1]['timestamp']
        duration = end_time - start_time
        
        total_minutes = int(duration.total_seconds() / 60)
        if total_minutes < 1:
            return "< 1 minute"
        elif total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"