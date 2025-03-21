import logging
from typing import Tuple, Dict, Optional, Callable

from src.core.session_manager import SessionManager
from src.core.message_processor import MessageProcessor
from src.ui.chat_ui import ChatUI

logger = logging.getLogger(__name__)

class InputHandler:
    """Handles user input and processing."""
    
    def __init__(self, session_manager: SessionManager, message_processor: MessageProcessor):
        """
        Initialize the input handler.
        
        Args:
            session_manager: Session manager instance
            message_processor: Message processor for handling messages
        """
        self.session_manager = session_manager
        self.message_processor = message_processor
    
    def handle_user_input(self, prompt: str, ui: ChatUI) -> Optional[str]:
        """
        Process user input and generate a response.
        
        Args:
            prompt: User's message
            ui: UI component for rendering
            
        Returns:
            Generated response or None if rate limited
        """
        # Add user message to session
        self.session_manager.add_message("user", prompt)
        
        # Render user message
        ui.render_messages([{"role": "user", "content": prompt}])
        
        # Check rate limit
        if not self.session_manager.check_rate_limit():
            rate_limit_message = "I'm receiving too many requests right now. Please wait a moment before sending another message."
            self.session_manager.add_message("assistant", rate_limit_message)
            return None
        
        # Process message and render response
        response = ui.render_assistant_response(
            lambda msg: self._process_message(msg),
            prompt
        )
        
        # Add response to session
        self.session_manager.add_message("assistant", response)
        return response
    
    def _process_message(self, message: str) -> str:
        """
        Process a message through the message processor and update session state.
        
        Args:
            message: User message to process
            
        Returns:
            Generated response
        """
        response, new_active_agent, new_agent_info = self.message_processor.process_message(
            message,
            self.session_manager.messages,
            self.session_manager.active_agent,
            self.session_manager.get_agent_info(self.session_manager.active_agent) 
                if self.session_manager.active_agent else None
        )
        
        # Update agent state
        self.session_manager.active_agent = new_active_agent
        if new_agent_info and new_active_agent:
            self.session_manager.set_agent_info(new_active_agent, new_agent_info)
        
        return response 