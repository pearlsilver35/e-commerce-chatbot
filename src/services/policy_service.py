"""
Policy service implementation.
"""
import logging
from typing import Dict
import json
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class PolicyService:
    """Service for handling policy-related operations."""
    
    def __init__(self, policies_file: str = "data/policies.json"):
        """
        Initialize policy service.
        
        Args:
            policies_file: Path to the policies JSON file
        """
        self.policies_file = Path(policies_file)
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.policies_file), exist_ok=True)
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict:
        """
        Load policies from JSON file.
        
        Returns:
            Dict: Loaded policies
        """
        try:
            if self.policies_file.exists():
                with open(self.policies_file, 'r') as f:
                    return json.load(f)
            else:
                # Default policies
                policies = {
                    "return_policy": {
                        "general": "You can return most items within 30 days of purchase for a full refund or exchange. Items must be in their original condition, with all tags and packaging intact. Please bring your receipt or proof of purchase when returning items.",
                        "exceptions": "Certain items such as clearance merchandise, perishable goods, and personal care items are non-returnable. Please check the product description or ask a store associate for more details."
                    },
                    "refund_policy": {
                        "general": "Refunds will be issued to the original form of payment. If you paid by credit card, the refund will be credited to your card. If you paid by cash or check, you will receive a cash refund."
                    }
                }
                # Save default policies
                with open(self.policies_file, 'w') as f:
                    json.dump(policies, f, indent=2)
                return policies
        except Exception as e:
            logger.error(f"Error loading policies: {str(e)}")
            # Return default policies instead of raising an exception
            return {
                "return_policy": {
                    "general": "You can return most items within 30 days of purchase.",
                    "exceptions": "Some items cannot be returned."
                },
                "refund_policy": {
                    "general": "Refunds will be issued to the original form of payment."
                }
            }
    
    def get_general_return_policy(self) -> str:
        """
        Get the general return policy.
        
        Returns:
            str: General return policy text
        """
        try:
            return self.policies.get("return_policy", {}).get("general", 
                "You can return most items within 30 days of purchase for a full refund or exchange.")
        except Exception as e:
            logger.error(f"Error retrieving general return policy: {str(e)}")
            return "You can return most items within 30 days of purchase for a full refund or exchange."
    
    def get_return_exceptions(self) -> str:
        """
        Get the return policy exceptions.
        
        Returns:
            str: Return policy exceptions text
        """
        try:
            return self.policies.get("return_policy", {}).get("exceptions", 
                "Certain items such as clearance merchandise, perishable goods, and personal care items are non-returnable.")
        except Exception as e:
            logger.error(f"Error retrieving return exceptions: {str(e)}")
            return "Certain items such as clearance merchandise, perishable goods, and personal care items are non-returnable."
    
    def get_refund_policy(self) -> str:
        """
        Get the refund policy.
        
        Returns:
            str: Refund policy text
        """
        try:
            return self.policies.get("refund_policy", {}).get("general", 
                "Refunds will be issued to the original form of payment.")
        except Exception as e:
            logger.error(f"Error retrieving refund policy: {str(e)}")
            return "Refunds will be issued to the original form of payment."
            
    def get_shipping_policy(self) -> str:
        """
        Get the shipping policy.
        
        Returns:
            str: Shipping policy text
        """
        try:
            return self.policies.get("shipping_policy", {}).get("standard", 
                "Standard shipping (3-5 business days) is free on orders over $35.")
        except Exception as e:
            logger.error(f"Error retrieving shipping policy: {str(e)}")
            return "Standard shipping (3-5 business days) is free on orders over $35." 