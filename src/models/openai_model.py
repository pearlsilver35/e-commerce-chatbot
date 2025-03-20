"""
OpenAI model implementation.
"""
import logging
from typing import List, Dict, Optional
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

from src.interfaces.llm import LLMInterface
from src.core.config import Config

logger = logging.getLogger(__name__)

class OpenAIModel(LLMInterface):
    """OpenAI model implementation."""
    
    def __init__(self, config: Config):
        """
        Initialize OpenAI model.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.client = None
        self.memory = None
        self.chain = None
    
    def initialize(self) -> None:
        """Initialize OpenAI model and resources."""
        try:
            self.client = ChatOpenAI(
                api_key=self.config.OPENAI_API_KEY,
                model=self.config.OPENAI_MODEL,
                temperature=self.config.TEMPERATURE
            )
            self.memory = ConversationBufferMemory()
            self.chain = ConversationChain(
                llm=self.client,
                memory=self.memory
            )
            logger.info(f"Initialized OpenAI model: {self.config.OPENAI_MODEL}")
        except Exception as e:
            logger.error(f"Error initializing OpenAI model: {str(e)}")
            raise
    
    def generate_response(self, user_input: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate a response using OpenAI model.
        
        Args:
            user_input: The user's message
            conversation_history: Optional list of previous messages
            
        Returns:
            str: Generated response
        """
        try:
            if not self.chain:
                self.initialize()
            
            # Set up conversation history if provided
            if conversation_history:
                self.memory.clear()
                for message in conversation_history:
                    if message["role"] == "user":
                        self.memory.chat_memory.add_user_message(message["content"])
                    else:
                        self.memory.chat_memory.add_ai_message(message["content"])
            
            # Add system instructions for direct responses
            system_instruction = "Always respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person. Provide only the response content, not how you would respond."
            self.memory.chat_memory.add_system_message(system_instruction)
            
            # Generate response
            response = self.chain.predict(input=user_input)
            logger.info("Generated OpenAI response successfully")
            return response
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            return "I'm sorry, I'm having trouble connecting to my backend. Please try again later." 