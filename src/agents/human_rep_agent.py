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
        Check if this agent can handle the given message using keyword matching and RAG.
        
        Args:
            message: The user's message
            
        Returns:
            bool: True if this agent can handle the message
        """
        message_lower = message.lower()
        
        if self.collecting_info:
            logger.info("Already collecting user information, will handle this message")
            return True
            
        human_request_keywords = [
            "speak to human", "talk to human", "human representative", "real person",
            "speak to representative", "talk to agent", "real agent", "human agent",
            "talk to someone", "speak to someone", "speak with someone", "talk with someone", 
            "in person", "connect me to a person", "connect me to a human",
            "human support", "live support", "live agent", "live representative",
            "speak with a human", "talk with a human", "human assistance"
        ]
        
        for keyword in human_request_keywords:
            if keyword in message_lower:
                logger.info(f"Found human keyword: {keyword} in message")
                self.collecting_info = True
                return True
                
        frustration_indicators = [
            "not understanding", "can't help", "don't understand", "need help", 
            "frustrated", "unhelpful", "speak with", "talk with", "connect me", 
            "get me a", "human assistant", "customer service", "not working", 
            "stop this", "this is useless", "not helping", "want to speak", 
            "want to talk", "need a person", "tired of this", "can't solve",
            "isn't solving", "cannot understand", "getting nowhere", "wasting time",
            "going in circles", "not getting", "want to connect", "can i talk to",
            "can i speak to", "is there someone", "is there a person", "is there a human"
        ]
        
        for indicator in frustration_indicators:
            if indicator in message_lower:
                logger.info(f"Found frustration indicator: {indicator} in message")
                self.collecting_info = True
                return True
                
        return False
    
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
    
    def _extract_info_from_message(self, message: str) -> None:
        """
        Extract contact information from the current message.
        
        Args:
            message: The user's message
        """
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message)
        if email_match:
            self.user_info["email"] = email_match.group(0)
            logger.info(f"Found email in message: {self.user_info['email']}")
        
        phone_match = re.search(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{10})', message)
        if phone_match:
            self.user_info["phone"] = phone_match.group(0)
            logger.info(f"Found phone in message: {self.user_info['phone']}")
        
        # Try to detect name patterns
        # Check for "Name: John Doe" pattern
        name_label_match = re.search(r'(?i)name\s*:?\s*([A-Z][a-z]+(\s+[A-Z][a-z]+)?)', message)
        if name_label_match:
            self.user_info["name"] = name_label_match.group(1)
            logger.info(f"Found labeled name in message: {self.user_info['name']}")
            return
        
        # Check if the entire message is just a name
        message_stripped = message.strip()
        name_only_match = re.match(r'^([A-Z][a-z]+(\s+[a-z]+)?(\s+[A-Z][a-z]+)?)$', message_stripped)
        if name_only_match and len(message_stripped.split()) <= 3:
            self.user_info["name"] = message_stripped
            logger.info(f"Message appears to be just a name: {self.user_info['name']}")
            return
            
        # Look for capitalized words that might be names
        words = message.split()
        for i in range(len(words)):
            if i < len(words) - 1 and words[i][0].isupper() and words[i+1].isalpha():
                self.user_info["name"] = f"{words[i]} {words[i+1]}"
                logger.info(f"Found potential full name in message: {self.user_info['name']}")
                return
        
        # If no full name found, try single capitalized word
        for word in words:
            if len(word) > 2 and word[0].isupper() and word.isalpha():
                self.user_info["name"] = word
                logger.info(f"Found potential single name in message: {self.user_info['name']}")
                return
    
    def _log_info_changes(self, before: Dict, after: Dict) -> None:
        """
        Log any changes to user information for debugging.
        
        Args:
            before: User info before extraction
            after: User info after extraction
        """
        added_keys = set(after.keys()) - set(before.keys())
        changed_keys = {k for k in before.keys() & after.keys() if before[k] != after[k]}
        
        if added_keys:
            logger.info(f"New information added: {', '.join(added_keys)}")
            for key in added_keys:
                logger.info(f"  - {key}: {after[key]}")
                
        if changed_keys:
            logger.info(f"Information updated: {', '.join(changed_keys)}")
            for key in changed_keys:
                logger.info(f"  - {key}: {before[key]} -> {after[key]}")
                
        if not (added_keys or changed_keys):
            logger.info("No new information extracted from message")
            
    def handle(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        Handle the request to speak with a human representative.
        
        Args:
            message: The user's message
            history: Chat history for context
            
        Returns:
            str: Generated response
        """
        # Save current state for debugging
        user_info_before = self.user_info.copy()
        
        # Extract info from history, but merge with existing user_info instead of replacing
        history_info = self._extract_user_info_from_history(history)
        self.user_info.update(history_info)
        
        # Then extract info from current message
        self._extract_info_from_message(message)
        
        # Log changes for debugging
        self._log_info_changes(user_info_before, self.user_info)
        
        logger.info(f"Current user info after extraction: {self.user_info}")
        
        has_email = "email" in self.user_info
        has_phone = "phone" in self.user_info
        has_name = "name" in self.user_info
        
        if has_email and has_phone and has_name:
            logger.info("All required contact information collected, saving to CSV")
            contact_info = ContactInfo(
                full_name=self.user_info["name"],
                email=self.user_info["email"],
                phone_number=self.user_info["phone"]
            )
            
            success = self.customer_service.save_contact_request(contact_info)
            if success:
                logger.info(f"Successfully saved contact request for {contact_info.full_name}")
                self.collecting_info = False
                return f"Thank you, {contact_info.full_name}. I've submitted your request to speak with a customer service representative. Someone from our team will contact you at {contact_info.email} or {contact_info.phone_number} as soon as possible. Is there anything else I can help you with in the meantime?"
            else:
                logger.error(f"Failed to save contact request for {self.user_info['name']}")
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
            greeting = ""
            if has_name:
                greeting = f", {self.user_info['name']}"
                
            logger.info(f"Still missing information: {missing_str}")
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
            logger.info(f"Updated user info with context: {context}")
    
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