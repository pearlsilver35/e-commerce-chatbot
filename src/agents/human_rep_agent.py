"""
Human representative agent implementation.
"""
import re
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass

from src.interfaces.agent import AgentInterface
from src.interfaces.llm import LLMInterface
from src.services.customer_service import CustomerService
from src.models.contact import ContactInfo

logger = logging.getLogger(__name__)

class HumanRepAgent(AgentInterface):
    """Agent for handling requests to speak with a human representative."""
    
    def __init__(self, llm: LLMInterface, customer_service: CustomerService):
        """
        Initialize human representative agent.
        
        Args:
            llm: Language model for generating responses
            customer_service: Service for handling customer-related operations
        """
        self.llm = llm
        self.customer_service = customer_service
        self.human_keywords = [
            "speak to human",
            "talk to agent",
            "human representative",
            "real person",
            "speak to representative"
        ]
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
        message_lower = message.lower()
        for keyword in self.human_keywords:
            if keyword in message_lower:
                return True
        
        prompt = f"""You are a classifier. Is the following customer message requesting to speak with a human representative?
        
        Message: {message}
        
        Respond with only 'yes' or 'no' without any other text."""
        
        response = self.llm.generate_response(prompt).strip().lower()
        return response == 'yes'
    
    def _extract_user_info_from_history(self, history: List[Dict[str, str]]) -> Dict:
        """
        Extract user information from conversation history.
        
        Args:
            history: Conversation history
            
        Returns:
            Dict: Dictionary containing user information
        """
        user_info = {}
        
        for message in history:
            if message["role"] == "user":
                name_patterns = [
                    r"(?i)my name is ([A-Z][a-z]+ [A-Z][a-z]+)",
                    r"(?i)my name is ([A-Z][a-z]+)",
                    r"(?i)i am ([A-Z][a-z]+ [A-Z][a-z]+)",
                    r"(?i)i am ([A-Z][a-z]+)",
                    r"(?i)this is ([A-Z][a-z]+ [A-Z][a-z]+)",
                    r"(?i)this is ([A-Z][a-z]+)",
                    r"(?i)I'm ([A-Z][a-z]+ [A-Z][a-z]+)",
                    r"(?i)I'm ([A-Z][a-z]+)",
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, message["content"])
                    if match:
                        user_info["name"] = match.group(1)
                        break
                
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message["content"])
                if email_match:
                    user_info["email"] = email_match.group(0)
                
                phone_match = re.search(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{10})', message["content"])
                if phone_match:
                    user_info["phone"] = phone_match.group(0)
        
        if history and len(history) >= 2:
            last_user_messages = [m for m in history[-3:] if m["role"] == "user"]
            for message in last_user_messages:
                content = message["content"].strip()
                if re.match(r'^[A-Z][a-z]+( [A-Z][a-z]+)?$', content) and len(content.split()) <= 2:
                    user_info["name"] = content
                    break
        
        logger.info(f"Extracted user info from history: {user_info}")
        return user_info
    
    def handle(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        Handle the request to speak with a human representative.
        
        Args:
            message: The user's message
            history: Chat history for context
            
        Returns:
            str: Generated response
        """
        self.user_info = self._extract_user_info_from_history(history)
        
        has_email = "email" in self.user_info
        has_phone = "phone" in self.user_info
        has_name = "name" in self.user_info
        
        if has_email and has_phone and has_name:
            contact_info = ContactInfo(
                full_name=self.user_info["name"],
                email=self.user_info["email"],
                phone_number=self.user_info["phone"]
            )
            
            success = self.customer_service.save_contact_request(contact_info)
            if success:
                return f"Thank you, {contact_info.full_name}. I've submitted your request to speak with a customer service representative. Someone from our team will contact you at {contact_info.email} or {contact_info.phone_number} as soon as possible. Is there anything else I can help you with in the meantime?"
            else:
                return "I'm having trouble submitting your request. Please try again later or contact our customer service directly."
        
        missing_info = []
        if not has_name:
            missing_info.append("full name")
        if not has_email:
            missing_info.append("email address")
        if not has_phone:
            missing_info.append("phone number")
        
        if missing_info:
            missing_str = ", ".join(missing_info)
            greeting = ""
            if has_name:
                greeting = f", {self.user_info['name']}"
                
            return f"I'd be happy to connect you with a human representative{greeting}. I'll need your {missing_str} to complete this request. This information will be used to have a representative contact you directly."
        
        greeting = ""
        if has_name:
            greeting = f", {self.user_info['name']}"
            
        return f"I'd be happy to connect you with a human representative{greeting}. Could you please provide your full name, email address, and phone number? This information will be used to have a representative contact you."
    
    def update_context(self, context: Dict) -> None:
        """
        Update the agent's context with new information.
        
        Args:
            context: New context information
        """
        if context:
            self.user_info.update(context)
    
    def _extract_contact_info(self, message: str) -> Optional[ContactInfo]:
        """
        Extract contact information from message.
        
        Args:
            message: The user's message
            
        Returns:
            Optional[ContactInfo]: Extracted contact information if found
        """
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message)
        if email_match:
            self.user_info["email"] = email_match.group(0)
        
        phone_match = re.search(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{10})', message)
        if phone_match:
            self.user_info["phone"] = phone_match.group(0)
        
        words = message.split()
        potential_names = []
        for i in range(len(words)-1):
            if words[i][0].isupper() and words[i+1][0].isupper():
                potential_names.append(f"{words[i]} {words[i+1]}")
        
        if potential_names:
            self.user_info["name"] = potential_names[0]
        
        if "email" in self.user_info and "phone" in self.user_info and "name" in self.user_info:
            contact_info = ContactInfo(
                full_name=self.user_info["name"],
                email=self.user_info["email"],
                phone_number=self.user_info["phone"]
            )
            return contact_info
        
        return None 