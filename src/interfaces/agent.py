"""
Base interface for conversation agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class AgentInterface(ABC):
    """Abstract base class for conversation agents."""
    
    @abstractmethod
    def handle(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: The user's message
            history: Chat history for context
            
        Returns:
            str: Generated response
        """
        pass
    
    @abstractmethod
    def update_context(self, context: Dict) -> None:
        """
        Update the agent's context with new information.
        
        Args:
            context: New context information
        """
        pass
    
    @abstractmethod
    def can_handle(self, message: str) -> bool:
        """
        Check if this agent can handle the given message.
        
        Args:
            message: The user's message
            
        Returns:
            bool: True if this agent can handle the message
        """
        pass 