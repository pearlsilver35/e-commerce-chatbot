import streamlit as st
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages session state and rate limiting for the chat application."""
    
    def __init__(self, default_model: str):
        """
        Initialize session manager with default settings.
        
        Args:
            default_model: The default model to use from config (e.g., "gemini" or "openai")
        """
        logger.info(f"Initializing session with default model: {default_model}")
        self._init_session_state(default_model)
    
    def _init_session_state(self, default_model: str) -> None:
        """Initialize all session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        if "model" not in st.session_state:
            st.session_state.model = default_model
            
        if "user_id" not in st.session_state:
            self._init_user_id()
        
        if "active_agent" not in st.session_state:
            st.session_state.active_agent = None
            
        if "agent_user_info" not in st.session_state:
            st.session_state.agent_user_info = {}
            
        if "last_request_time" not in st.session_state:
            st.session_state.last_request_time = datetime.now() - timedelta(minutes=1)
        
        if "request_count" not in st.session_state:
            st.session_state.request_count = 0
    
    def _init_user_id(self) -> None:
        """Initialize user ID from query params or generate new one."""
        query_params = st.query_params
        if "user_id" in query_params:
            st.session_state.user_id = query_params["user_id"]
            logger.info(f"Using user_id from query params: {st.session_state.user_id}")
        else:
            st.session_state.user_id = str(uuid.uuid4())
            st.query_params["user_id"] = st.session_state.user_id
            logger.info(f"Generated new user_id: {st.session_state.user_id}")
    
    def check_rate_limit(self) -> bool:
        """Check if current request is within rate limits."""
        current_time = datetime.now()
        time_diff = (current_time - st.session_state.last_request_time).total_seconds()
        
        if time_diff > 60:  # Reset after 1 minute
            st.session_state.request_count = 0
            st.session_state.last_request_time = current_time
            return True
        
        st.session_state.request_count += 1
        if st.session_state.request_count > 8:  # Max 8 requests per minute
            logger.warning(f"Rate limit exceeded: {st.session_state.request_count} requests in under a minute")
            return False
        
        st.session_state.last_request_time = current_time
        return True
    
    @property
    def messages(self) -> List[Dict[str, str]]:
        """Get current chat messages."""
        return st.session_state.messages
    
    @property
    def user_id(self) -> str:
        """Get current user ID."""
        return st.session_state.user_id
    
    @property
    def model(self) -> str:
        """Get current model name."""
        return st.session_state.model
    
    @model.setter
    def model(self, value: str) -> None:
        """Set current model name."""
        st.session_state.model = value
    
    @property
    def active_agent(self) -> Optional[str]:
        """Get current active agent."""
        return st.session_state.active_agent
    
    @active_agent.setter
    def active_agent(self, value: Optional[str]) -> None:
        """Set current active agent."""
        st.session_state.active_agent = value
    
    def get_agent_info(self, agent_name: str) -> Dict:
        """Get stored info for specific agent."""
        return st.session_state.agent_user_info.get(agent_name, {})
    
    def set_agent_info(self, agent_name: str, info: Dict) -> None:
        """Store info for specific agent."""
        st.session_state.agent_user_info[agent_name] = info
    
    def add_message(self, role: str, content: str) -> None:
        """Add a new message to the chat history."""
        st.session_state.messages.append({"role": role, "content": content})
    
    def clear_messages(self) -> None:
        """Clear all chat messages."""
        st.session_state.messages = [] 