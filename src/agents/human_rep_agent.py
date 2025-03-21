"""
Human representative agent implementation.
"""
import re
import logging
from typing import Dict, List, Optional

from src.interfaces.agent import AgentInterface
from src.interfaces.llm import LLMInterface
from src.services.customer_service import CustomerService
from src.models.contact import ContactInfo

logger = logging.getLogger(__name__)

class ContactInfoExtractor:
    """Responsible for extracting contact information from messages."""
    
    # Regex patterns
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    PHONE_PATTERN = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{10})'
    NAME_LABEL_PATTERN = r'(?i)name\s*:?\s*([A-Z][a-z]+(\s+[A-Z][a-z]+)?)'
    NAME_ONLY_PATTERN = r'^([A-Z][a-z]+(\s+[a-z]+)?(\s+[A-Z][a-z]+)?)$'
    
    @classmethod
    def extract_email(cls, message: str) -> Optional[str]:
        """Extract email from message."""
        match = re.search(cls.EMAIL_PATTERN, message)
        return match.group(0) if match else None
    
    @classmethod
    def extract_phone(cls, message: str) -> Optional[str]:
        """Extract phone number from message."""
        match = re.search(cls.PHONE_PATTERN, message)
        return match.group(0) if match else None
    
    @classmethod
    def extract_name(cls, message: str) -> Optional[str]:
        """Extract name from message."""
        # Check for "Name: John Doe" pattern
        name_label_match = re.search(cls.NAME_LABEL_PATTERN, message)
        if name_label_match:
            return name_label_match.group(1)
        
        # Check if the entire message is just a name
        message_stripped = message.strip()
        name_only_match = re.match(cls.NAME_ONLY_PATTERN, message_stripped)
        if name_only_match and len(message_stripped.split()) <= 3:
            return message_stripped
        
        # Look for capitalized words that might be names
        words = message.split()
        for i in range(len(words)-1):
            if i < len(words) - 1 and words[i][0].isupper() and words[i+1].isalpha():
                return f"{words[i]} {words[i+1]}"
        
        # If no full name found, try single capitalized word
        for word in words:
            if len(word) > 2 and word[0].isupper() and word.isalpha():
                return word
        
        return None
    
    @classmethod
    def extract_from_message(cls, message: str) -> Dict[str, str]:
        """Extract all contact information from a message."""
        info = {}
        
        email = cls.extract_email(message)
        if email:
            info["email"] = email
            
        phone = cls.extract_phone(message)
        if phone:
            info["phone"] = phone
            
        name = cls.extract_name(message)
        if name:
            info["name"] = name
            
        return info
    
    @classmethod
    def extract_from_history(cls, history: List[Dict[str, str]]) -> Dict[str, str]:
        """Extract contact information from conversation history."""
        info = {}
        
        for message in history:
            if message["role"] == "user":
                message_info = cls.extract_from_message(message["content"])
                info.update(message_info)
        
        return info


class HumanRepKeywordDetector:
    """Responsible for detecting human representative requests."""
    
    # Keywords that indicate a user wants to speak with a human
    HUMAN_REQUEST_KEYWORDS = [
        "speak to human", "talk to human", "human representative", "real person",
        "speak to representative", "talk to agent", "real agent", "human agent",
        "talk to someone", "speak to someone", "speak with someone", "talk with someone", 
        "in person", "connect me to a person", "connect me to a human",
        "human support", "live support", "live agent", "live representative",
        "speak with a human", "talk with a human", "human assistance"
    ]
    
    # Indicators of user frustration that might warrant human intervention
    FRUSTRATION_INDICATORS = [
        "not understanding", "can't help", "don't understand", "need help", 
        "frustrated", "unhelpful", "speak with", "talk with", "connect me", 
        "get me a", "human assistant", "customer service", "not working", 
        "stop this", "this is useless", "not helping", "want to speak", 
        "want to talk", "need a person", "tired of this", "can't solve",
        "isn't solving", "cannot understand", "getting nowhere", "wasting time",
        "going in circles", "not getting", "want to connect", "can i talk to",
        "can i speak to", "is there someone", "is there a person", "is there a human"
    ]
    
    @classmethod
    def is_human_request(cls, message: str) -> bool:
        """Determine if the message is a request to speak with a human."""
        message_lower = message.lower()
        
        # Check for keywords
        for keyword in cls.HUMAN_REQUEST_KEYWORDS:
            if keyword in message_lower:
                return True
                
        # Check for frustration indicators
        for indicator in cls.FRUSTRATION_INDICATORS:
            if indicator in message_lower:
                return True
                
        return False


class HumanRepAgent(AgentInterface):
    """Agent for handling requests to speak with a human representative."""
    
    def __init__(self, llm: LLMInterface, customer_service: CustomerService):
        """
        Initialize human representative agent.
        
        Args:
            llm: Language model for generating responses
            customer_service: Service for handling customer-related operations
        """
        self.customer_service = customer_service
        self.collecting_info = False
        self.user_info = {}
    
    def can_handle(self, message: str) -> bool:
        """
        Check if this agent can handle the given message.
        
        Args:
            message: The user's message
            
        Returns:
            bool: True if this agent can handle the message
        """
        if self.collecting_info:
            return True
            
        is_human_request = HumanRepKeywordDetector.is_human_request(message)
        if is_human_request:
            self.collecting_info = True
            return True
                
        return False
    
    def handle(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        Handle the request to speak with a human representative.
        
        Args:
            message: The user's message
            history: Chat history for context
            
        Returns:
            str: Generated response
        """
        # Extract info from history and current message
        history_info = ContactInfoExtractor.extract_from_history(history)
        message_info = ContactInfoExtractor.extract_from_message(message)
        
        # Update user info
        self.user_info.update(history_info)
        self.user_info.update(message_info)
        
        # Check if we have all required information
        has_email = "email" in self.user_info
        has_phone = "phone" in self.user_info
        has_name = "name" in self.user_info
        
        if has_email and has_phone and has_name:
            # Create contact info
            contact_info = ContactInfo(
                full_name=self.user_info["name"],
                email=self.user_info["email"],
                phone_number=self.user_info["phone"]
            )
            
            # Save contact request
            success = self.customer_service.save_contact_request(contact_info)
            if success:
                self.collecting_info = False
                return f"Thank you, {contact_info.full_name}. I've submitted your request to speak with a customer service representative. Someone from our team will contact you at {contact_info.email} or {contact_info.phone_number} as soon as possible. Is there anything else I can help you with in the meantime?"
            else:
                return "I'm having trouble submitting your request. Please try again later or contact our customer service directly."
        
        # We need to collect more information
        missing_info = []
        if not has_name:
            missing_info.append("full name")
        if not has_email:
            missing_info.append("email address")
        if not has_phone:
            missing_info.append("phone number")
        
        if missing_info:
            missing_str = ", ".join(missing_info)
            greeting = f", {self.user_info['name']}" if has_name else ""
            return f"I'd be happy to connect you with a human representative{greeting}. I'll need your {missing_str} to complete this request. This information will be used to have a representative contact you directly."
        
        greeting = f", {self.user_info['name']}" if has_name else ""
        return f"I'd be happy to connect you with a human representative{greeting}. Could you please provide your full name, email address, and phone number? This information will be used to have a representative contact you."
    
    def update_context(self, context: Dict) -> None:
        """
        Update the agent's context with new information.
        
        Args:
            context: New context information
        """
        if context:
            self.user_info.update(context) 