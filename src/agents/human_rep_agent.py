"""
Human representative agent implementation.
"""
import logging
from typing import Dict, List
import json

from src.interfaces.llm import LLMInterface
from src.interfaces.agent import AgentInterface
from src.core.conversation_manager import ConversationManager
from src.services.customer_service import CustomerService
from src.services.conversation_service import ConversationService
from src.models.contact import ContactInfo

logger = logging.getLogger(__name__)

class ContactInfoExtractor:
    """Helper class to extract contact information using LLM."""
    
    @staticmethod
    def clean_json_response(response: str) -> str:
        """Clean and normalize JSON response from LLM."""
        response = response.strip()
        response = response.replace("'", '"')
        response = response.replace("None", "null")
        response = response.replace("True", "true")
        response = response.replace("False", "false")
        
        # Try to find JSON object in response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        return response
    
    @classmethod
    def extract(cls, llm: LLMInterface, text: str, is_history: bool = False) -> Dict[str, str]:
        """Extract contact information from text using LLM."""
        prompt = f"""Extract contact information from this {'conversation history' if is_history else 'message'}. 
        Return ONLY a JSON object with these fields:
        - name: person's name (properly capitalized)
        - email: email address (must contain @)
        - phone: phone number (10+ digits, no formatting)
        
        If a field is not found, set it to null.
        Do not include any other text, only the JSON object.
        
        {'Look for names in introductions (e.g. "my name is", "I am") and take the most recent valid value if multiple are found.' if is_history else ''}
        
        Examples:
        Input: "Hi, I'm john smith, reach me at john@email.com or 555-123-4567"
        Output: {{"name": "John Smith", "email": "john@email.com", "phone": "5551234567"}}
        
        Input: "my name is maria garcia"
        Output: {{"name": "Maria Garcia", "email": null, "phone": null}}
        
        Input: "phone: 090-8876-5432"
        Output: {{"name": null, "email": null, "phone": "09088765432"}}
        
        {'Conversation history:' if is_history else 'Message:'} {text}
        """
        
        try:
            response = llm.generate_response(prompt, [])
            response = cls.clean_json_response(response)
            info = json.loads(response)
            return {k: v.strip() if isinstance(v, str) else v 
                   for k, v in info.items() 
                   if v is not None}
        except Exception as e:
            logger.error(f"Error extracting contact info: {str(e)}")
            return {}

class HumanRepAgent(AgentInterface):
    """Agent for handling customer service requests and connecting to human representatives."""
    
    def __init__(self, llm: LLMInterface, customer_service: CustomerService):
        """
        Initialize human representative agent.
        
        Args:
            llm: Language model for generating responses
            customer_service: Service for handling customer requests
        """
        self.llm = llm
        self.customer_service = customer_service
        self.user_info = {}
        self.request_submitted = False
        self.collecting_info = True  # Track whether we're still collecting information
        self.human_rep_keywords = [
            "speak to", "talk to", "human representative", "customer service", "speak with",
            "customer support", "real person", "live agent", "human agent", "speak with someone", 
            "talk to someone", "connect me to", "transfer me to", "human help", "human assistance", 
            "supervisor", "manager", "boss", "head of", "lead", "leadership", "authority", 
            "higher up", "higher authority", "someone in charge", "person in charge", 
            "superior", "escalate", "escalation", "human"
        ]

    
    def can_handle(self, message: str) -> bool:
        """
        Check if this agent can handle the given message using keyword matching.
        
        Args:
            message: The user's message
            
        Returns:
            bool: True if this agent can handle the message
        """
        message_lower = message.lower()
        return any(keyword.lower() in message_lower for keyword in self.human_rep_keywords)
    
    def update_context(self, context: Dict) -> None:
        """
        Update the agent's context with new information.
        
        Args:
            context: New context information
        """
        # Update user info if provided in context
        if "user_info" in context:
            self.user_info.update(context["user_info"])
        if "request_submitted" in context:
            self.request_submitted = context["request_submitted"]
        if "collecting_info" in context:
            self.collecting_info = context["collecting_info"]
    
    def handle(self, message: str, history: List[Dict[str, str]]) -> str:
        """Handle customer service requests and connect to human representatives."""
        try:
            # Extract contact info from history and current message
            history_info = ContactInfoExtractor.extract(self.llm, "\n".join(f"{msg['role']}: {msg['content']}" for msg in history), is_history=True)
            message_info = ContactInfoExtractor.extract(self.llm, message)
            
            # Update user info, preferring newer values
            self.user_info.update(history_info)
            self.user_info.update(message_info)
            
            # If we have all required info, submit the request
            if all(self.user_info.get(field) for field in ["name", "email", "phone"]):
                if not self.request_submitted:
                    self._submit_request()
                    self.request_submitted = True
                    self.collecting_info = False  # We're done collecting info
                    return f"Thank you {self.user_info['name']}! I've submitted your request to our customer service team. They will contact you shortly at the provided email or phone number."
            
            # Determine what information is still needed
            missing_fields = []
            if not self.user_info.get("name"):
                missing_fields.append("name")
            if not self.user_info.get("email"):
                missing_fields.append("email address")
            if not self.user_info.get("phone"):
                missing_fields.append("phone number")
            
            if missing_fields:
                return f"I'll need your {' and '.join(missing_fields)} to submit your request to our customer service team."
            
            # If we have the info but haven't submitted yet, submit
            if not self.request_submitted:
                self._submit_request()
                self.request_submitted = True
                self.collecting_info = False
                return f"Thank you {self.user_info['name']}! I've submitted your request to our customer service team. They will contact you shortly at the provided email or phone number."
            
            return "I've already submitted your request to our customer service team. They will contact you shortly at the provided email or phone number."
            
        except Exception as e:
            logger.error(f"Error in human rep agent: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again or contact us through our website."
    
    def _submit_request(self) -> None:
        """Submit the customer request to the service."""
        try:
            contact_info = ContactInfo(
                full_name=self.user_info["name"],
                email=self.user_info["email"],
                phone_number=self.user_info["phone"],
                phone=self.user_info["phone"],
                preferred_contact_method="email"
            )
            self.customer_service.save_contact_request(contact_info)
        except Exception as e:
            logger.error(f"Error submitting customer request: {str(e)}")
            raise 