"""
Google Gemini model implementation using LangChain.
"""
import logging
import hashlib
import json
from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import google.generativeai as genai

from src.interfaces.llm import LLMInterface
from src.core.config import Config

logger = logging.getLogger(__name__)

class GeminiModel(LLMInterface):
    """Google Gemini model implementation using LangChain."""
    
    def __init__(self, config: Config):
        """
        Initialize Gemini model.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.model = None
        self.response_cache = {}  # Simple in-memory cache
    
    def initialize(self) -> None:
        """Initialize Gemini model and resources."""
        try:
            genai.configure(api_key=self.config.GOOGLE_API_KEY)
            
            self.model = ChatGoogleGenerativeAI(
                model=self.config.GEMINI_MODEL,
                google_api_key=self.config.GOOGLE_API_KEY,
                temperature=self.config.TEMPERATURE,
                convert_system_message_to_human=True,
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ],
                top_p=0.95,
                top_k=64,
                max_output_tokens=1024
            )
            logger.info(f"Initialized Gemini model: {self.config.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {str(e)}")
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
            
            # Check cache first
            cache_key = self._get_cache_key(user_input, conversation_history)
            if cache_key in self.response_cache:
                logger.info("Using cached Gemini response")
                return self.response_cache[cache_key]
                
            # Format messages for LangChain ChatGoogleGenerativeAI
            formatted_messages = []
            
            # Add system message
            system_prompt = self.config.SYSTEM_PROMPT + "\n\nIMPORTANT: Always respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person. Provide only the response content, not how you would respond."
            formatted_messages.append(HumanMessage(content=f"System instructions: {system_prompt}"))
            
            # Add conversation history
            if conversation_history:
                for message in conversation_history:
                    if message["role"] == "user":
                        formatted_messages.append(HumanMessage(content=message["content"]))
                    elif message["role"] == "assistant":
                        formatted_messages.append(AIMessage(content=message["content"]))
            
            # Add current user message
            formatted_messages.append(HumanMessage(content=user_input))
            
            # Generate response
            response = self.model.invoke(formatted_messages)
            response_text = response.content
            
            # Cache the response
            self.response_cache[cache_key] = response_text
            
            # Keep cache size reasonable
            if len(self.response_cache) > 100:
                # Remove oldest items (simple approach)
                keys_to_remove = list(self.response_cache.keys())[:-50]  # Keep only the 50 most recent
                for key in keys_to_remove:
                    del self.response_cache[key]
            
            logger.info("Generated Gemini response successfully")
            return response_text
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            return "I'm sorry, I'm having trouble connecting to my backend. Please try again later." 