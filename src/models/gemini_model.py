"""
Google Gemini model implementation.
"""
import logging
from typing import List, Dict, Optional
import google.generativeai as genai

from src.interfaces.llm import LLMInterface
from src.core.config import Config

logger = logging.getLogger(__name__)

class GeminiModel(LLMInterface):
    """Google Gemini model implementation."""
    
    def __init__(self, config: Config):
        """
        Initialize Gemini model.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.model = None
    
    def initialize(self) -> None:
        """Initialize Gemini model and resources."""
        try:
            genai.configure(api_key=self.config.GOOGLE_API_KEY)
            
            # Set up the generation config
            generation_config = {
                "temperature": self.config.TEMPERATURE,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 1024,
            }
            
            # Initialize the model with the updated settings
            self.model = genai.GenerativeModel(
                model_name=self.config.GEMINI_MODEL,
                generation_config=generation_config
            )
            logger.info(f"Initialized Gemini model: {self.config.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {str(e)}")
            raise
    
    def generate_response(self, user_input: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate a response using Gemini model.
        
        Args:
            user_input: The user's message
            conversation_history: Optional list of previous messages
            
        Returns:
            str: Generated response
        """
        try:
            if not self.model:
                self.initialize()
            
            # Create a new chat session
            chat = self.model.start_chat()
            
            # Add system prompt with direct response instructions
            system_prompt = self.config.SYSTEM_PROMPT + "\n\nIMPORTANT: Always respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person. Provide only the response content, not how you would respond."
            chat.send_message(system_prompt)
            
            # Add conversation history if provided
            if conversation_history:
                for message in conversation_history:
                    if message["role"] == "user":
                        chat.send_message(message["content"])
                    else:
                        # For assistant messages, we just simulate the response
                        # since we can't directly send assistant messages
                        pass
            
            # Send the user's message and get response
            response = chat.send_message(user_input)
            logger.info("Generated Gemini response successfully")
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            return "I'm sorry, I'm having trouble connecting to my backend. Please try again later." 