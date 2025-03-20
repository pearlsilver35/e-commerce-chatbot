"""
Base interface for LLM implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class LLMInterface(ABC):
    """Abstract base class for LLM implementations."""
    
    @abstractmethod
    def generate_response(self, user_input: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate a response using the LLM model.
        
        Args:
            user_input: The user's message
            conversation_history: Optional list of previous messages
            
        Returns:
            str: Generated response
        """
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the LLM model and any required resources."""
        pass 