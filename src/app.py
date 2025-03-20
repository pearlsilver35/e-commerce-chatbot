"""
Main application for the e-commerce customer support chatbot.
"""
import logging
import streamlit as st
import uuid
from typing import List, Dict, Optional

from src.core.config import Config
from src.models.openai_model import OpenAIModel
from src.models.gemini_model import GeminiModel
from src.agents.order_status_agent import OrderStatusAgent
from src.agents.return_policy_agent import ReturnPolicyAgent
from src.agents.human_rep_agent import HumanRepAgent
from src.services.order_service import OrderService
from src.services.policy_service import PolicyService
from src.services.customer_service import CustomerService
from src.services.conversation_service import ConversationService
from chromadb.utils import embedding_functions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEBUG_SESSION = False

class ChatbotApp:
    """Main chatbot application."""
    
    def __init__(self):
        """Initialize the chatbot application."""
        st.set_page_config(
            page_title="Insait Support",
            page_icon="🤖",
            layout="wide"
        )
        
        self.config = Config()
        self.config.validate()
        
        try:
            logger.info("Preloading ChromaDB embedding function...")
            embedding_functions.DefaultEmbeddingFunction()
            logger.info("ChromaDB embedding function loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to preload embedding function: {str(e)}")
        
        self._init_session_state()
        
        self.order_service = OrderService(self.config.ORDERS_FILE)
        self.policy_service = PolicyService(self.config.POLICIES_FILE)
        self.customer_service = CustomerService(self.config.CUSTOMER_REQUESTS_FILE)
        self.conversation_service = ConversationService(self.config)
        
        self.openai_model = OpenAIModel(self.config)
        self.gemini_model = GeminiModel(self.config)
        
        current_model = self._get_llm_model()
        self.agents = [
            OrderStatusAgent(current_model, self.order_service),
            ReturnPolicyAgent(current_model, self.policy_service),
            HumanRepAgent(current_model, self.customer_service)
        ]
        
        self._load_conversation()
        
        if DEBUG_SESSION:
            logger.info(f"Session state: {st.session_state}")
    
    def _init_session_state(self) -> None:
        """Initialize Streamlit session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        if "model" not in st.session_state:
            st.session_state.model = self.config.DEFAULT_MODEL
            
        if "user_id" not in st.session_state:
            query_params = st.query_params
            if "user_id" in query_params:
                st.session_state.user_id = query_params["user_id"]
                logger.info(f"Using user_id from query params: {st.session_state.user_id}")
            else:
                st.session_state.user_id = str(uuid.uuid4())
                st.query_params["user_id"] = st.session_state.user_id
                logger.info(f"Generated new user_id: {st.session_state.user_id}")
        
        if DEBUG_SESSION:
            logger.info(f"Session state initialized with user_id: {st.session_state.user_id}")
    
    def _load_conversation(self) -> None:
        """Load conversation history from persistent storage."""
        try:
            user_id = st.session_state.user_id
            logger.info(f"Loading conversation for user: {user_id}")
            
            messages = self.conversation_service.load_conversation(user_id)
            if messages:
                st.session_state.messages = messages
                logger.info(f"Loaded {len(messages)} messages from persistent storage")
            else:
                logger.info("No existing conversation found in persistent storage")
        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}")
    
    def _save_conversation(self) -> None:
        """Save conversation history to persistent storage."""
        try:
            if st.session_state.messages:
                user_id = st.session_state.user_id
                logger.info(f"Saving conversation for user: {user_id}")
                
                success = self.conversation_service.save_conversation(
                    user_id, 
                    st.session_state.messages
                )
                if success:
                    logger.info(f"Saved {len(st.session_state.messages)} messages to persistent storage")
                else:
                    logger.warning("Failed to save conversation to persistent storage")
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
    
    def _clear_conversation(self) -> None:
        """Clear conversation history from persistent storage and session."""
        try:
            user_id = st.session_state.user_id
            logger.info(f"Clearing conversation for user: {user_id}")
            
            success = self.conversation_service.delete_conversation(user_id)
            if success:
                logger.info("Deleted conversation from persistent storage")
            else:
                logger.warning("Failed to delete conversation from persistent storage")
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}")
        
        st.session_state.messages = []
    
    def _get_llm_model(self) -> OpenAIModel:
        """Get the current LLM model based on session state."""
        if st.session_state.model == "openai":
            return self.openai_model
        else:
            return self.gemini_model
    
    def _process_message(self, message: str) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: The user's message
            
        Returns:
            str: Generated response
        """
        try:
            current_model = self._get_llm_model()
            for agent in self.agents:
                agent.llm = current_model
            
            for agent in self.agents:
                if agent.can_handle(message):
                    logger.info(f"Agent {agent.__class__.__name__} is handling the message")
                    response = agent.handle(message, st.session_state.messages)
                    self._save_conversation()
                    return response
            
            logger.info(f"No specific agent found, using {current_model.__class__.__name__}")
            response = current_model.generate_response(message, st.session_state.messages)
            self._save_conversation()
            return response
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "I'm sorry, I'm experiencing technical difficulties. Please try again later."
    
    def run(self) -> None:
        """Run the Streamlit application."""
        st.title("Insait Support")
        st.markdown("""
        👋 Hi! I'm **Atlas**, your Insait e-commerce Support Assistant. I'm here to help you with:
        - Order tracking and status
        - Return policies and refunds
        - Connecting with our support team
        
        How can I assist you today?
        """)
        
        for message in st.session_state.messages:
            role_color = "#0084ff" if message["role"] == "assistant" else "#262730"
            role_icon = "🤖" if message["role"] == "assistant" else "👤"
            
            with st.chat_message(message["role"], avatar=role_icon):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Atlas is thinking..."):
                    response = self._process_message(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    self._save_conversation()
        
        with st.sidebar:
            st.title("Settings")
            
            model = st.selectbox(
                "Select AI Model",
                ["openai", "gemini"],
                index=0 if st.session_state.model == "openai" else 1
            )
            if model != st.session_state.model:
                st.session_state.model = model
                current_model = self._get_llm_model()
                logger.info(f"Switching model to {model}")
                for agent in self.agents:
                    agent.llm = current_model
                # We don't clear conversations when switching models anymore
                # This allows the conversation to continue with a different model
                st.rerun()
            
            if st.button("Clear Chat"):
                self._clear_conversation()
                st.rerun()
            
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

def main():
    """Main entry point for the application."""
    try:
        app = ChatbotApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An error occurred. Please try again later.")

if __name__ == "__main__":
    main() 