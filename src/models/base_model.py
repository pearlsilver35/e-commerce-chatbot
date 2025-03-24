"""
Base model implementation for LLM models with common functionality.
"""
import logging
import hashlib
import json
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

from src.interfaces.llm import LLMInterface
from src.core.config import Config
from src.services.policy_service import PolicyService

logger = logging.getLogger(__name__)

class BaseLLMModel(LLMInterface, ABC):
    """Base class for LLM model implementations."""
    
    def __init__(self, config: Config):
        """
        Initialize base model.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.response_cache = {}  # Simple in-memory cache
        self.policy_service = PolicyService(policies_file=config.POLICIES_FILE)
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize LLM model and resources."""
        pass
    
    def _get_cache_key(self, user_input: str, conversation_history: Optional[List[Dict]]) -> str:
        """
        Generate a cache key for the given input and conversation history.
        
        Args:
            user_input: The user's message
            conversation_history: Conversation history
            
        Returns:
            str: Cache key
        """
        # Create a stable representation of inputs
        history_str = ""
        if conversation_history:
            # Use only the last few messages to keep the cache more effective
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            history_str = json.dumps(recent_history, sort_keys=True)
        
        # Create hash from inputs
        key_content = f"{user_input}|{history_str}"
        return hashlib.md5(key_content.encode()).hexdigest()
    
    def _get_enhanced_system_prompt(self) -> str:
        """
        Get enhanced system prompt with policy information.
        
        Returns:
            str: Enhanced system prompt with policy info
        """
        # Load policy information
        general_return_policy = self.policy_service.get_general_return_policy()
        return_exceptions = self.policy_service.get_return_exceptions()
        refund_policy = self.policy_service.get_refund_policy()
        shipping_policy = self.policy_service.get_shipping_policy()
        
        # Create enhanced prompt with policy information
        enhanced_prompt = self.config.SYSTEM_PROMPT + f"""
        
        IMPORTANT POLICY INFORMATION:
        
        Return Policy: {general_return_policy}
        Return Exceptions: {return_exceptions}
        
        Refund Policy: {refund_policy}
        
        Shipping Policy: {shipping_policy}
        
        HUMAN AGENT REFERRAL POLICY:
        
        Always refer customers to a human agent for:
        1. Any returns of perishable items like milk, produce, meat, or prepared foods
        2. Any returns of opened food products of any kind
        3. Items that appear to fall under exceptions but the customer has special circumstances
        4. When store policy is unclear for a specific item type
        5. When the customer is upset or frustrated
        
        When referring to a human agent, politely explain the relevant policy, why a human agent is needed, and ask if they would like to be connected to a customer service representative.
        
        When answering questions about returns, refunds, or exchanges, please use this accurate policy information. Do not make up policies or rely on general knowledge. If you are unsure about a specific policy detail, tell the customer you need to refer them to a human agent.
        """
        
        return enhanced_prompt
    
    def _manage_cache(self, cache_key: str, response_text: str) -> None:
        """
        Add response to cache and manage cache size.
        
        Args:
            cache_key: Key to store response under
            response_text: Response to cache
        """
        # Cache the response
        self.response_cache[cache_key] = response_text
        
        # Keep cache size reasonable
        if len(self.response_cache) > 100:
            # Remove oldest items (simple approach)
            keys_to_remove = list(self.response_cache.keys())[:-50]  # Keep only the 50 most recent
            for key in keys_to_remove:
                del self.response_cache[key]
    
    @abstractmethod
    def generate_response(self, user_input: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """Generate a response using the LLM model."""
        pass 