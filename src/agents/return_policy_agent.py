"""
Return policy agent implementation.
"""
import logging
from typing import Dict, List

from src.interfaces.agent import AgentInterface
from src.interfaces.llm import LLMInterface
from src.services.policy_service import PolicyService

logger = logging.getLogger(__name__)

class ReturnPolicyAgent(AgentInterface):
    """Agent for handling return policy queries."""
    
    def __init__(self, llm: LLMInterface, policy_service: PolicyService):
        """
        Initialize return policy agent.
        
        Args:
            llm: Language model for generating responses
            policy_service: Service for handling policy-related operations
        """
        self.llm = llm
        self.policy_service = policy_service
    
    def can_handle(self, message: str) -> bool:
        """
        Check if this agent can handle the given message.
        
        Args:
            message: The user's message
            
        Returns:
            bool: True if this agent can handle the message
        """
        prompt = f"""Determine if the following message is asking about return policies, refunds, shipping policies, or product returns.
        Message: {message}
        Respond with only 'yes' or 'no'."""
        
        response = self.llm.generate_response(prompt).strip().lower()
        return response == 'yes'
    
    def handle(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        Process return policy query and generate response.
        
        Args:
            message: The user's message
            history: Chat history for context
            
        Returns:
            str: Generated response
        """
        try:
            message_lower = message.lower()
            
            if "return policy" in message_lower or "how to return" in message_lower:
                policy = self.policy_service.get_general_return_policy()
                prompt = f"""You are a customer support assistant. Respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person.
                
                The customer is asking about our general return policy: {policy}
                Their message: {message}
                
                Acknowledge their query and explain the general return policy clearly and concisely."""
                
            elif "can't be returned" in message_lower or "can not return" in message_lower or "non-returnable" in message_lower:
                exceptions = self.policy_service.get_return_exceptions()
                prompt = f"""You are a customer support assistant. Respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person.
                
                The customer is asking about items that cannot be returned. Here are the exceptions: {exceptions}
                Their message: {message}
                
                Explain which items cannot be returned in a clear and helpful way."""
                
            elif "refund" in message_lower:
                refund_policy = self.policy_service.get_refund_policy()
                prompt = f"""You are a customer support assistant. Respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person.
                
                The customer is asking about our refund policy: {refund_policy}
                Their message: {message}
                
                Explain the refund process clearly and concisely."""
                
            elif any(keyword in message_lower for keyword in ["shipping", "delivery", "ship", "deliver"]):
                shipping_policy = self.policy_service.get_shipping_policy()
                prompt = f"""You are a customer support assistant. Respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person.
                
                The customer is asking about our shipping policy: {shipping_policy}
                Their message: {message}
                
                Explain the shipping policy clearly and concisely."""
                
            else:
                prompt = f"""You are a customer support assistant. Respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person.
                
                The customer has a question that might require human assistance.
                Their message: {message}
                
                Acknowledge their question and explain that you'll connect them with a representative."""
            
            return self.llm.generate_response(prompt, history)
            
        except Exception as e:
            logger.error(f"Error processing policy query: {str(e)}")
            return "I'm sorry, I'm having trouble accessing our policies. Please try again later."
    
    def update_context(self, context: Dict) -> None:
        """
        Update the agent's context with new information.
        
        Args:
            context: New context information
        """
        # This agent doesn't need to maintain any context
        pass 