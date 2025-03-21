import streamlit as st
from typing import List, Dict, Optional, Callable

class ChatUI:
    """Handles all Streamlit UI rendering for the chat application."""
    
    def __init__(self):
        self._setup_page_config()
    
    def _setup_page_config(self):
        """Configure the Streamlit page."""
        st.set_page_config(
            page_title="Insait Support",
            page_icon="🤖",
            layout="wide"
        )
    
    def render_header(self):
        """Render the chat header."""
        st.title("Insait Support")
        st.markdown("""
        👋 Hi! I'm **Atlas**, your Insait e-commerce Support Assistant. I'm here to help you with:
        - Order tracking and status
        - Return policies and refunds
        - Connecting with our support team
        
        How can I assist you today?
        """)
    
    def render_messages(self, messages: List[Dict[str, str]]):
        """Render chat messages."""
        for message in messages:
            role_color = "#0084ff" if message["role"] == "assistant" else "#262730"
            role_icon = "🤖" if message["role"] == "assistant" else "👤"
            
            with st.chat_message(message["role"], avatar=role_icon):
                st.markdown(message["content"])
    
    def render_chat_input(self) -> Optional[str]:
        """Render chat input and return user message if any."""
        return st.chat_input("Type your message here...")
    
    def render_assistant_response(self, process_message_callback: Callable[[str], str], message: str):
        """Render assistant's response with loading state."""
        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            with placeholder:
                with st.spinner("Atlas is thinking..."):
                    response = process_message_callback(message)
            placeholder.markdown(response)
            return response
    
    def render_sidebar(self, current_model: str, on_model_change: Callable[[str], None], on_clear_chat: Callable[[], None], available_models: List[str] = None):
        """
        Render the settings sidebar.
        
        Args:
            current_model: Currently selected model
            on_model_change: Callback when model changes
            on_clear_chat: Callback to clear chat
            available_models: List of available model names (e.g., ["openai", "gemini"])
        """
        with st.sidebar:
            st.title("Settings")
            
            # Default to all models if none specified
            model_options = available_models or ["openai", "gemini"]
            
            if len(model_options) > 1:
                # Only show model selector if we have multiple models
                model = st.selectbox(
                    "Select AI Model",
                    model_options,
                    index=model_options.index(current_model) if current_model in model_options else 0
                )
                if model != current_model:
                    on_model_change(model)
            else:
                # If only one model, just show it
                st.info(f"Using model: {model_options[0]}")
            
            if st.button("Clear Chat"):
                on_clear_chat()
            
            self._render_sidebar_help()
    
    def _render_sidebar_help(self):
        """Render help content in sidebar."""
        st.markdown("### Example Messages")
        st.markdown("""
        **Order Status:**
        - "What's the status of my order ORD12345?"
        - "Where is my order ORD67890?"
        - "When will my order arrive?"
        
        **Return Policy:**
        - "What's your return policy?"
        - "How do I return an item?"
        - "What items can't be returned?"
        - "What's your shipping policy?"
        
        **Human Representative:**
        - "I need to speak with a human"
        - "Can I talk to a customer service representative?"
        - "I want to speak with someone in person"
        """)
        
        st.markdown("### Valid Order IDs")
        st.markdown("""
        - ORD12345 (Shipped)
        - ORD67890 (Processing)
        - ORD13579 (Pending)
        - ORD86420 (Cancelled)
        """)
        
        st.markdown("### About Insait")
        st.markdown("""
        Insait is your trusted partner in E-commerce solutions. 
        We're committed to providing exceptional customer service 
        and ensuring a seamless shopping experience.
        """) 