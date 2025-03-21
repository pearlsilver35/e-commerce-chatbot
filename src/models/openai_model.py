"""
OpenAI model implementation using LangChain with optimizations.
"""
import logging
import hashlib
import json
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from src.interfaces.llm import LLMInterface
from src.core.config import Config

logger = logging.getLogger(__name__)

class OpenAIModel(LLMInterface):
    """OpenAI model implementation using LangChain."""
    
    def __init__(self, config: Config):
        """
        Initialize OpenAI model.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.client = None
        self.response_cache = {}  # Simple in-memory cache
    
    def initialize(self) -> None:
        """Initialize OpenAI model and resources."""
        try:
            self.client = ChatOpenAI(
                api_key=self.config.OPENAI_API_KEY,
                model=self.config.OPENAI_MODEL,
                temperature=self.config.TEMPERATURE,
                max_tokens=1024
            )
            logger.info(f"Initialized OpenAI model: {self.config.OPENAI_MODEL}")
        except Exception as e:
            logger.error(f"Error initializing OpenAI model: {str(e)}")
            raise
    
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
    
    def generate_response(self, user_input: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate a response using OpenAI model with LangChain.
        
        Args:
            user_input: The user's message
            conversation_history: Optional list of previous messages
            
        Returns:
            str: Generated response
        """
        try:
            if not self.client:
                self.initialize()
            
            cache_key = self._get_cache_key(user_input, conversation_history)
            if cache_key in self.response_cache:
                logger.info("Using cached OpenAI response")
                return self.response_cache[cache_key]
            
            formatted_messages = []
            
            system_prompt = self.config.SYSTEM_PROMPT + "\n\nIMPORTANT: Always respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person. Provide only the response content, not how you would respond."
            formatted_messages.append(SystemMessage(content=system_prompt))
            
            if conversation_history:
                for message in conversation_history:
                    if message["role"] == "user":
                        formatted_messages.append(HumanMessage(content=message["content"]))
                    elif message["role"] == "assistant":
                        formatted_messages.append(AIMessage(content=message["content"]))
            
            formatted_messages.append(HumanMessage(content=user_input))
            
            response = self.client.invoke(formatted_messages)
            response_text = response.content
            
            # Cache the response
            self.response_cache[cache_key] = response_text
            
            # Keep cache size reasonable
            if len(self.response_cache) > 100:
                # Remove oldest items (simple approach)
                keys_to_remove = list(self.response_cache.keys())[:-50]  # Keep only the 50 most recent
                for key in keys_to_remove:
                    del self.response_cache[key]
            
            logger.info("Generated OpenAI response successfully")
            return response_text
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            return "I'm sorry, I'm having trouble connecting to my backend. Please try again later." 