"""
Return policy agent implementation.
"""
import logging
from typing import Dict, Optional, List

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
        self.policy_keywords = [
            "return policy", 
            "how to return", 
            "can I return", 
            "refund", 
            "money back",
            "return item",
            "return product",
            "return an item",
            "shipping policy",
            "return period",
            "return window",
            "exchange policy",
            "warranty",
            "damaged item",
            "return address",
            "return shipping"
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
        return any(keyword.lower() in message_lower for keyword in self.policy_keywords)
    
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
                
                The customer is asking about our return policy.
                Return Policy: {policy}
                Their message: {message}
                
                Explain our return policy clearly and be helpful."""
                
                return self.llm.generate_response(prompt, history)
            
            elif "shipping policy" in message_lower:
                policy = self.policy_service.get_shipping_policy()
                prompt = f"""You are a customer support assistant. Respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person.
                
                The customer is asking about our shipping policy.
                Shipping Policy: {policy}
                Their message: {message}
                
                Explain our shipping policy clearly and be helpful."""
                
                return self.llm.generate_response(prompt, history)
            
            elif "refund" in message_lower:
                policy = self.policy_service.get_refund_policy()
                prompt = f"""You are a customer support assistant. Respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person.
                
                The customer is asking about our refund policy.
                Refund Policy: {policy}
                Their message: {message}
                
                Explain our refund policy clearly and be helpful."""
                
                return self.llm.generate_response(prompt, history)
            
            else:
                policy = self.policy_service.get_general_return_policy()
                prompt = f"""You are a customer support assistant. Respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person.
                
                The customer appears to be asking about some aspect of our policies.
                Return Policy: {policy}
                Their message: {message}
                
                Based on their query, provide the most relevant information about our policies in a helpful manner."""
                
                return self.llm.generate_response(prompt, history)
        except Exception as e:
            logger.error(f"Error processing return policy query: {str(e)}")
            return "I'm sorry, I'm having trouble retrieving our policy information. Please try again later."
    
    def update_context(self, context: Dict) -> None:
        """
        Update the agent's context with new information.
        
        Args:
            context: New context information
        """
        # This agent doesn't need to maintain any context
        pass 