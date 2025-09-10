"""
Sidebar components for the chat interface
"""
import streamlit as st
from typing import Dict, Any

class Sidebar:
    """Manages sidebar components and settings."""
    
    def __init__(self):
        pass
    
    def render_sidebar(self, pipeline_status: Dict[str, Any] = None):
        """
        Render the complete sidebar.
        
        Args:
            pipeline_status (Dict[str, Any]): Current pipeline status
        """
        with st.sidebar:
            self._render_header()
            self._render_system_status(pipeline_status)
            self._render_settings()
            self._render_conversation_info()
            self._render_actions()
            self._render_help()
    
    def _render_header(self):
        """Render sidebar header."""
        st.markdown("# 🎓 Course Assistant")
        st.markdown("### Multilingual Support")
        st.markdown("""
        **Supported Languages:**
        - 🇮🇳 हिंदी (Hindi)
        - 🇮🇳 मराठी (Marathi)  
        - 🇮🇳 മലയാളം (Malayalam)
        - 🇮🇳 தமிழ் (Tamil)
        - 🇮🇳 తెలుగు (Telugu)
        - 🇮🇳 ಕನ್ನಡ (Kannada)
        - 🇺🇸 English
        """)
        
        st.divider()
    
    def _render_system_status(self, pipeline_status: Dict[str, Any] = None):
        """Render system status section."""
        st.markdown("### 📊 System Status")
        
        if pipeline_status:
            # Overall status
            is_ready = pipeline_status.get('pipeline_initialized', False)
            status_color = "🟢" if is_ready else "🔴"
            status_text = "Ready" if is_ready else "Not Ready"
            st.markdown(f"{status_color} **Status:** {status_text}")
            
            # Component status
            components = pipeline_status.get('components', {})
            
            with st.expander("🔧 Component Details"):
                for component, status in components.items():
                    icon = "✅" if status else "❌"
                    st.write(f"{icon} {component.upper()}")
            
            # Data statistics
            data_stats = pipeline_status.get('data_stats', {})
            if data_stats and 'total_courses' in data_stats:
                st.metric(
                    label="📚 Total Courses",
                    value=data_stats['total_courses']
                )
                
                languages_count = len(data_stats.get('languages_supported', []))
                st.metric(
                    label="🌐 Languages",
                    value=languages_count
                )
            
            # Show initialization error if any
            init_error = pipeline_status.get('initialization_error')
            if init_error:
                st.error(f"⚠️ **Error:** {init_error}")
        else:
            st.info("Loading system status...")
        
        st.divider()
    
    def _render_settings(self):
        """Render settings section."""
        st.markdown("### ⚙️ Settings")
        
        # Chat settings
        show_metadata = st.checkbox(
            "Show message metadata",
            value=st.session_state.get('show_metadata', False),
            help="Display language and timestamp for each message"
        )
        st.session_state.show_metadata = show_metadata
        
        show_debug = st.checkbox(
            "Show debug information",
            value=st.session_state.get('show_debug_info', False),
            help="Display query processing details"
        )
        st.session_state.show_debug_info = show_debug
        
        # Language detection confidence threshold
        confidence_threshold = st.slider(
            "Language detection confidence",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get('confidence_threshold', 0.8),
            step=0.1,
            help="Minimum confidence for language detection"
        )
        st.session_state.confidence_threshold = confidence_threshold
        
        st.divider()
    
    def _render_conversation_info(self):
        """Render conversation information."""
        st.markdown("### 💬 Conversation Info")
        
        if 'messages' in st.session_state:
            total_messages = len(st.session_state.messages)
            user_messages = len([msg for msg in st.session_state.messages if msg['role'] == 'user'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", total_messages)
            with col2:
                st.metric("Questions", user_messages)
            
            # Languages used in conversation
            languages_used = set()
            for msg in st.session_state.messages:
                if 'language' in msg and msg['language'] != 'Unknown':
                    languages_used.add(msg['language'])
            
            if languages_used:
                st.write("**Languages Used:**")
                for lang in sorted(languages_used):
                    st.write(f"• {lang}")
        
        st.divider()
    
    def _render_actions(self):
        """Render action buttons."""
        st.markdown("### 🛠️ Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = [{
                    'role': 'assistant',
                    'content': "Chat cleared! How can I help you today?",
                    'timestamp': st.session_state.get('current_time'),
                    'language': 'English'
                }]
                st.rerun()
        
        with col2:
            if st.button("📁 Export Chat", use_container_width=True):
                # Create export content
                export_content = self._create_export_content()
                st.download_button(
                    label="📥 Download",
                    data=export_content,
                    file_name="chat_history.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        # Rebuild database button (admin feature)
        if st.session_state.get('show_admin_features', False):
            st.markdown("#### 🔧 Admin Actions")
            if st.button("🔄 Rebuild Database", use_container_width=True):
                st.session_state.rebuild_requested = True
                st.info("Database rebuild requested...")
        
        st.divider()
    
    def _render_help(self):
        """Render help section."""
        st.markdown("### ❓ Help")
        
        with st.expander("🎯 How to Use"):
            st.markdown("""
            **Getting Started:**
            1. Type your question in any supported language
            2. Press Enter or click Send
            3. The assistant will detect your language and respond accordingly
            
            **Example Questions:**
            - "Which courses are available in Tamil?"
            - "डेयरी फार्मिंग के बारे में बताएं"
            - "ഡയറി ഫാമിങ്ങിനെ കുറിച്ച് പറയൂ"
            """)
        
        with st.expander("🌐 Language Support"):
            st.markdown("""
            **Automatic Detection:** The system automatically detects your language and provides responses in the same language.
            
            **Supported Scripts:**
            - Devanagari (Hindi)
            - Malayalam Script
            - Tamil Script
            - Telugu Script
            - Kannada Script
            - Roman (English)
            """)
        
        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common Issues:**
            - If responses are in English instead of your language, try typing more text for better detection
            - For mixed-language queries, the system will use the dominant language
            - If translation fails, you'll receive an English response with a note
            """)
        
        st.markdown("---")
        st.markdown("*Made with ❤️ for Boswallah*")
    
    def _create_export_content(self) -> str:
        """Create content for chat export."""
        if 'messages' not in st.session_state:
            return "No chat history to export."
        
        export_lines = [
            "# Boswallah Course Assistant - Chat Export",
            f"# Exported on: {st.session_state.get('current_time', 'Unknown')}",
            f"# Total Messages: {len(st.session_state.messages)}",
            "",
            "=" * 50,
            ""
        ]
        
        for i, msg in enumerate(st.session_state.messages, 1):
            role = "👤 You" if msg['role'] == 'user' else "🎓 Assistant"
            timestamp = msg.get('timestamp', 'Unknown')
            language = msg.get('language', 'Unknown')
            
            export_lines.extend([
                f"Message {i}: {role}",
                f"Time: {timestamp}",
                f"Language: {language}",
                f"Content: {msg['content']}",
                "",
                "-" * 30,
                ""
            ])
        
        return "\n".join(export_lines)
    
    def show_admin_panel(self):
        """Show admin panel toggle."""
        with st.sidebar:
            st.markdown("### 👑 Admin Panel")
            admin_mode = st.checkbox(
                "Enable admin features",
                value=st.session_state.get('show_admin_features', False)
            )
            st.session_state.show_admin_features = admin_mode
            
            if admin_mode:
                st.info("Admin features enabled. Additional options are now available.")