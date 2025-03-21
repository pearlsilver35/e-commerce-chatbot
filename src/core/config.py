"""
Configuration management for the application.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """Application configuration."""
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "openai")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    SYSTEM_PROMPT: str = """
    You are a helpful customer support assistant for an e-commerce platform. Your role is to help customers with:
    
    1. Order Status: When a user asks for the status of an order, ask for the order_id and then provide the order status.
    2. Return Policy Information: Provide accurate information about our return policies when asked.
    3. Human Representative Requests: If a user wants to speak with a human representative, collect their full name, email, and phone number.
    
    IMPORTANT: Always respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person. Do not include phrases like "I would respond with" or "Here's a response". Just provide the direct response.
    
    Be polite, concise, and helpful in your responses. If you don't know the answer to a question, indicate that and offer to connect the user with a human representative.
    """
    
    ORDERS_FILE: str = "data/orders.csv"
    POLICIES_FILE: str = "data/policies.json"
    CUSTOMER_REQUESTS_FILE: str = "data/customer_requests.csv"
    
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "data/chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "conversations")
    CHROMA_USERNAME: str = os.getenv("CHROMA_USERNAME", "")
    CHROMA_PASSWORD: str = os.getenv("CHROMA_PASSWORD", "")
    CHROMA_USE_AUTH: bool = bool(os.getenv("CHROMA_USE_AUTH", "False").lower() == "true")
    
    def validate(self) -> None:
        """Validate configuration settings."""
        # Validate API keys based on the default model
        if self.DEFAULT_MODEL == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI as default model")
        if self.DEFAULT_MODEL == "gemini" and not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required when using Gemini as default model")
            
        # Still validate model names regardless of which is default
        if not self.OPENAI_MODEL:
            raise ValueError("OPENAI_MODEL is required")
        if not self.GEMINI_MODEL:
            raise ValueError("GEMINI_MODEL is required")
        if not 0 <= self.TEMPERATURE <= 1:
            raise ValueError("TEMPERATURE must be between 0 and 1")
        
        if self.CHROMA_USE_AUTH and (not self.CHROMA_USERNAME or not self.CHROMA_PASSWORD):
            raise ValueError("CHROMA_USERNAME and CHROMA_PASSWORD are required when CHROMA_USE_AUTH is True")
        
        os.makedirs(self.CHROMA_DB_PATH, exist_ok=True)