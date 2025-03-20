"""
Order status agent implementation.
"""
import re
import logging
from typing import Dict, Optional, List

from src.interfaces.agent import AgentInterface
from src.interfaces.llm import LLMInterface
from src.services.order_service import OrderService

logger = logging.getLogger(__name__)

class OrderStatusAgent(AgentInterface):
    """Agent for handling order status queries."""
    
    def __init__(self, llm: LLMInterface, order_service: OrderService):
        """
        Initialize order status agent.
        
        Args:
            llm: Language model for generating responses
            order_service: Service for handling order-related operations
        """
        self.llm = llm
        self.order_service = order_service
        self.order_keywords = [
            "order status",
            "track order",
            "where is my order",
            "when will my order arrive"
        ]
    
    def can_handle(self, message: str) -> bool:
        """
        Check if this agent can handle the given message.
        
        Args:
            message: The user's message
            
        Returns:
            bool: True if this agent can handle the message
        """
        prompt = f"""Determine if the following message is asking about order status or tracking.
        Message: {message}
        Respond with only 'yes' or 'no'."""
        
        response = self.llm.generate_response(prompt).strip().lower()
        return response == 'yes'
    
    def handle(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        Process order status query and generate response.
        
        Args:
            message: The user's message
            history: Chat history for context
            
        Returns:
            str: Generated response
        """
        try:
            order_match = re.search(r'(ORD\d+)', message, re.IGNORECASE)
            if order_match:
                order_id = order_match.group(1).upper()
                status = self.order_service.get_order_status(order_id)
                
                prompt = f"""You are a customer support assistant. Respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person. 
                
                The customer has order {order_id} with status: {status}
                Their message: {message}
                
                Acknowledge their order status query, provide the current status, and be professional and helpful."""
                
                return self.llm.generate_response(prompt, history)
            else:
                prompt = f"""You are a customer support assistant. Respond directly to the customer without using quotes, meta-commentary, or speaking about yourself in the third person.
                
                The customer is asking about their order status but hasn't provided an order ID.
                Their message: {message}
                
                Politely ask for their order ID, explaining it typically starts with 'ORD' followed by numbers."""
                
                return self.llm.generate_response(prompt, history)
        except Exception as e:
            logger.error(f"Error processing order status query: {str(e)}")
            return "I'm sorry, I'm having trouble checking your order status. Please try again later."
    
    def update_context(self, context: Dict) -> None:
        """
        Update the agent's context with new information.
        
        Args:
            context: New context information
        """
        # This agent doesn't need to maintain any context
        pass 