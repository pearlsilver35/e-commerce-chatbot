"""
OpenAI model implementation using LangChain with optimizations.
"""
import logging
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from src.models.base_model import BaseLLMModel
from src.core.config import Config

logger = logging.getLogger(__name__)

class OpenAIModel(BaseLLMModel):
    """OpenAI model implementation using LangChain."""
    
    def __init__(self, config: Config):
        """
        Initialize OpenAI model.
        
        Args:
            config: Application configuration
        """
        super().__init__(config)
        self.client = None
    
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
            
            # Use enhanced system prompt with policy information
            system_prompt = self._get_enhanced_system_prompt() + "\n\nIMPORTANT: Always respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person. Provide only the response content, not how you would respond."
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
            
            # Manage cache
            self._manage_cache(cache_key, response_text)
            
            logger.info("Generated OpenAI response successfully")
            return response_text
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            return "I'm sorry, I'm having trouble connecting to my backend. Please try again later." 