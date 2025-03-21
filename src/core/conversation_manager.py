import logging
from typing import List, Dict, Optional

from src.core.session_manager import SessionManager
from src.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversation loading, saving, and clearing."""
    
    def __init__(self, session_manager: SessionManager, conversation_service: ConversationService):
        """
        Initialize the conversation manager.
        
        Args:
            session_manager: Session manager instance
            conversation_service: Service for persistence
        """
        self.session_manager = session_manager
        self.conversation_service = conversation_service
    
    def load_conversation(self) -> None:
        """Load conversation history from persistent storage."""
        try:
            user_id = self.session_manager.user_id
            messages = self.conversation_service.load_conversation(user_id)
            if messages:
                for message in messages:
                    self.session_manager.add_message(message["role"], message["content"])
                logger.info(f"Loaded {len(messages)} messages from persistent storage")
            else:
                logger.info("No existing conversation found in persistent storage")
        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}")
    
    def save_conversation(self) -> None:
        """Save conversation history to persistent storage."""
        try:
            messages = self.session_manager.messages
            if messages:
                user_id = self.session_manager.user_id
                success = self.conversation_service.save_conversation(user_id, messages)
                if success:
                    logger.info(f"Saved {len(messages)} messages to persistent storage")
                else:
                    logger.warning("Failed to save conversation to persistent storage")
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
    
    def clear_conversation(self) -> None:
        """Clear conversation history from persistent storage and session."""
        try:
            user_id = self.session_manager.user_id
            success = self.conversation_service.delete_conversation(user_id)
            if success:
                logger.info("Deleted conversation from persistent storage")
            else:
                logger.warning("Failed to delete conversation from persistent storage")
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}")
        
        self.session_manager.clear_messages() 